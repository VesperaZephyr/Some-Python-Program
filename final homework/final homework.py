import sys
from datetime import datetime
from PIL import Image
from sympy import *
from sympy.parsing.sympy_parser import parse_expr
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QComboBox, QGridLayout,
    QTabWidget, QFrame, QScrollArea, QMessageBox, QFileDialog,
    QDialog,        # 用于创建对话框
    QScrollArea   # 滚动区域
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import  QThread, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QAction

class CalculationThread(QThread):
    finished = pyqtSignal(str, str)  # (full_latex, full_text)

    def __init__(self, operation, data):
        super().__init__()
        self.operation = operation
        self.data = data

    def run(self):
        try:
            x, y, z, t = symbols('x y z t')
            full_latex = ""
            full_text = ""
            
            if self.operation == "求导":
                expr = parse_expr(self.data['expression'])
                var = symbols(self.data['variable'])
                result = diff(expr, var)
                
                # 生成原始表达式
                expr_tex = latex(expr)
                var_tex = latex(var)
                original_tex = rf"\frac{{\mathrm d}}{{\mathrm d{var_tex}}} \left({expr_tex}\right)"
                original_text = f"d/d{self.data['variable']} ({self.data['expression']})"
                
                # 组合结果
                full_latex = f"{original_tex} = {latex(result)}"
                full_text = f"{original_text} = {str(result).replace('**','^')}"

            elif self.operation == "不定积分":
                expr = parse_expr(self.data['expression'])
                var = symbols(self.data['variable'])
                result = integrate(expr, var)
                
                expr_tex = latex(expr)
                var_tex = latex(var)
                original_tex = rf"\int {expr_tex} \, \mathrm d{var_tex}"
                original_text = f"∫ {self.data['expression']} \\mathrm d{self.data['variable']}"
                
                full_latex = f"{original_tex} = {latex(result)}"
                full_text = f"{original_text} = {str(result).replace('**','^')}"

            elif self.operation == "定积分与反常积分":
                expr = parse_expr(self.data['expression'])
                var = symbols(self.data['variable'])
                lower = parse_expr(self.data['lower'])
                upper = parse_expr(self.data['upper'])
                result = integrate(expr, (var, lower, upper))
                
                # 生成原始表达式
                expr_tex = latex(expr)
                var_tex = latex(var)
                lower_tex = latex(lower)
                upper_tex = latex(upper)
                original_tex = rf"\int_{{{lower_tex}}}^{{{upper_tex}}} {expr_tex} \, \mathrm d{var_tex}"
                
                # 文本表达式处理
                lower_text = str(lower).replace('oo','∞')
                upper_text = str(upper).replace('oo','∞')
                original_text = f"∫_{lower_text}^{upper_text} {self.data['expression']} \\mathrm d{self.data['variable']}"
                
                full_latex = f"{original_tex} = {latex(result)}"
                full_text = f"{original_text} = {str(result).replace('**','^')}"

            elif self.operation == "极限":
                expr = parse_expr(self.data['expression'])
                var = symbols(self.data['variable'])
                point = parse_expr(self.data['point'])
                result = limit(expr, var, point)
                
                expr_tex = latex(expr)
                var_tex = latex(var)
                point_tex = latex(point)
                original_tex = rf"\lim_{{{var_tex} \to {point_tex}}} {expr_tex}"
                original_text = f"lim_{self.data['variable']}→{self.data['point']} ({self.data['expression']})"
                
                full_latex = f"{original_tex} = {latex(result)}"
                full_text = f"{original_text.replace('**','^')} = {str(result).replace('**','^')}"

            elif self.operation == "化简":
                expr = parse_expr(self.data['expression'])
                result = simplify(expr)
                
                original_tex = latex(expr)
                original_text = self.data['expression'].replace('**','^')
                full_latex = f"{original_tex} = {latex(result)}"
                full_text = f"{original_text} = {str(result).replace('**','^')}"

            self.finished.emit(full_latex, full_text)
            
        except Exception as e:
            self.finished.emit("", f"计算错误：{str(e)}")

class HelpDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("符号输入规则说明")
        self.setFixedSize(800, 600)
        
        layout = QVBoxLayout()
        
         # 使用WebEngineView显示帮助内容
        self.web_view = QWebEngineView()
        self.web_view.setHtml(self.help_content())
        
        # 添加滚动区域
        scroll = QScrollArea()
        scroll.setWidget(self.web_view)
        scroll.setWidgetResizable(True)
        
        layout.addWidget(scroll)
        self.setLayout(layout)

        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
            
        self.setLayout(layout)
        
    def help_content(self):
        return f"""
        <html>
        <head>
            <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
            <script id="MathJax-script" async
                    src="https://cdn.bootcdn.net/ajax/libs/mathjax/3.2.0/es5/tex-mml-chtml.js"></script>
            <style>
                body {{
                    font-family: '华文楷体', STKaiti;
                    font-size: 14px;
                    line-height: 1.6;
                    padding: 20px;
                }}
                h2 {{ color: #2c3e50; }}
                pre {{ 
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 5px;
                }}
                .math-example {{ color: #27ae60; }}
            </style>
        </head>
        <body>
        <h1 style="font-family: 'SimHei';">符号输入规则说明</h1>
        <h2 style="font-family: 'SimHei';">基本运算符：</h2>
        <ul>
            <li style="font-family: 'KaiTi'; font-size: 16px;">加/减：+ - （正常数学符号）</li>
            <li style="font-family: 'KaiTi'; font-size: 16px;">乘：*（例如：$2*x$）</li>
            <li style="font-family: 'KaiTi'; font-size: 16px;">除：/</li>
            <li style="font-family: 'KaiTi'; font-size: 16px;">幂运算：**（例如：$x^2 \\to x**2$）</li>
        </ul>
        <h2 style="font-family: 'SimHei';">常用函数格式：</h2>
        <table border="1" cellpadding="5">
            <tr><th>数学符号</th><th>输入格式</th><th>示例</th></tr>
            <tr><td>$\\arcsin(x)$</td><td>asin(x)</td><td>asin(0.5)</td></tr>
            <tr><td>$\\arccos(x)$</td><td>acos(x)</td><td>acos(1)</td></tr>
            <tr><td>$\\arctan(x)$</td><td>atan(x)</td><td>atan(1)</td></tr>
            <tr><td>自然对数$\\ln(x)$</td><td>ln(x)或log(x)</td><td>ln(E)</td></tr>
            <tr><td>绝对值</td><td>Abs(x)</td><td>Abs(-5)</td></tr>
            <tr><td>平方根$\\sqrt x$</td><td>sqrt(x)</td><td>sqrt(2)</td></tr>
        </table>

        <h3>特殊常数：</h3>
        <ul>
            <li>圆周率 $\\pi$ → pi</li>
            <li>自然对数的底 $\\mathrm e$ → E</li>
            <li>无穷大 $\\infty$ → oo（两个小写字母o）</li>
            <li>虚数单位 $i$ → I（大写字母）</li>
        </ul>
        
        <p style="color: #d32f2f; font-family='SimHei'">注意：所有函数参数必须用括号包裹，如sin x → sin(x)</p>
            
        <script>
                MathJax = {{
                    tex: {{
                        inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
                        displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']],
                        processEscapes: true
                    }},
                    options: {{
                        skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre']
                    }}
                }};
            </script>
        </body>
        </html>
        """

class MathAssistantPro(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_style()
        self.setWindowTitle("一元微积分计算器")
        self.setGeometry(100, 100, 800, 600)
        self.current_operation = ""
        self.extra_fields = {}
        self.setup_help_button()
        self.setup_save_button()  # 初始化保存按钮
        self.current_result = ("", "")  # 保存最新结果（latex, text）
    def setup_help_button(self):
        # 在顶部工具栏添加帮助按钮
        help_action = QAction("帮助", self)
        help_action.triggered.connect(self.show_help)
        self.toolbar = self.addToolBar("帮助")
        self.toolbar.addAction(help_action)
    def setup_save_button(self):
        """添加保存按钮到工具栏"""
        save_action = QAction("保存计算结果为txt", self)
        save_action.triggered.connect(self.save_to_txt)
        self.toolbar.addAction(save_action)
    def show_help(self):
        dialog = HelpDialog()
        dialog.exec()
    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # 操作选择区
        self.operation_combo = QComboBox()
        operations = [
            "求导", "不定积分", "定积分与反常积分", 
            "极限", "化简"
        ]
        self.operation_combo.addItems(operations)
        self.operation_combo.currentTextChanged.connect(self.update_input_fields)
        main_layout.addWidget(self.operation_combo)

        # 动态输入区
        self.dynamic_input_frame = QFrame()
        self.dynamic_layout = QGridLayout()
        self.dynamic_input_frame.setLayout(self.dynamic_layout)
        main_layout.addWidget(self.dynamic_input_frame)

        # 公共输入区
        self.expression_input = QLineEdit()
        self.expression_input.setPlaceholderText("输入数学表达式，例如：exp(x)*sin(x)")
        main_layout.addWidget(self.expression_input)

        # 按钮组
        btn_layout = QHBoxLayout()
        self.calc_btn = QPushButton("开始计算")
        self.calc_btn.clicked.connect(self.validate_inputs)
        self.render_btn = QPushButton("渲染表达式")
        self.render_btn.clicked.connect(self.render_expression)
        btn_layout.addWidget(self.calc_btn)
        btn_layout.addWidget(self.render_btn)
        main_layout.addLayout(btn_layout)

        # 结果展示区
        result_tabs = QTabWidget()
        self.text_result = QLabel()
        self.text_result.setWordWrap(True)
        self.web_view = QWebEngineView()
        self.web_view.setHtml(self.base_html(""))
        result_tabs.addTab(self.text_result, "文本结果")
        result_tabs.addTab(self.web_view, "公式渲染")
        main_layout.addWidget(result_tabs)

        # 初始化动态字段
        self.init_dynamic_fields()

    def init_dynamic_fields(self):
        """创建所有可能的额外输入组件"""
        self.extra_components = {
            'variable': (QLineEdit, "积分/求导变量（默认x）:", 'x'),
            'lower': (QLineEdit, "下限:", '0'),
            'upper': (QLineEdit, "上限:", '1'),
            'point': (QLineEdit, "趋近点:", '0'),
        }
        
        for key, (widget_type, label, placeholder) in self.extra_components.items():
            setattr(self, f"{key}_label", QLabel(label))
            field = widget_type()
            field.setPlaceholderText(placeholder)
            setattr(self, f"{key}_field", field)

    def update_input_fields(self, operation):
        """根据操作类型显示对应输入字段"""
        self.clear_dynamic_layout()
        
        row = 0
        if operation in ["求导", "不定积分"]:
            self.add_dynamic_row(row, 'variable')
            row += 1
            
        if operation == "定积分与反常积分":
            self.add_dynamic_row(row, 'variable')
            self.add_dynamic_row(row+1, 'lower')
            self.add_dynamic_row(row+2, 'upper')
            
        if operation == "极限":
            self.add_dynamic_row(row, 'variable')
            self.add_dynamic_row(row+1, 'point')

    def add_dynamic_row(self, row, field_key):
        """添加一行动态输入组件"""
        label = getattr(self, f"{field_key}_label")
        field = getattr(self, f"{field_key}_field")
        self.dynamic_layout.addWidget(label, row, 0)
        self.dynamic_layout.addWidget(field, row, 1)

    def clear_dynamic_layout(self):
        """清空动态布局"""
        while self.dynamic_layout.count():
            item = self.dynamic_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

    def validate_inputs(self):
        """收集并验证输入参数"""
        operation = self.operation_combo.currentText()
        data = {'expression': self.expression_input.text().strip()}
        
        if not data['expression']:
            QMessageBox.critical(
                self, 
                "输入错误", 
                "必须输入数学表达式！", 
                QMessageBox.StandardButton.Ok
            )
            return  # 阻止后续执行
        # 收集额外参数
        if operation in ["求导", "不定积分", "定积分与反常积分", "极限"]:
            data['variable'] = getattr(self, 'variable_field').text().strip() or 'x'
            
        if operation == "定积分与反常积分":
            data['lower'] = getattr(self, 'lower_field').text().strip() or '0'
            data['upper'] = getattr(self, 'upper_field').text().strip() or '1'
            
        if operation == "极限":
            data['point'] = getattr(self, 'point_field').text().strip() or '0'
        
        # 启动计算线程
        self.start_calculation(operation, data)

    @pyqtSlot(str, str)
    def handle_result(self, full_latex, full_text):
        self.calc_btn.setEnabled(True)
        self.calc_btn.setText("开始计算")
        self.current_result = (full_latex, full_text)  # 存储最新结果
        if full_latex:
            self.web_view.setHtml(self.base_html(full_latex))
            self.text_result.setText(f"计算结果：\n{full_text}")
        else:
            self.text_result.setText(full_text)
            self.web_view.setHtml(self.base_html(""))

    def start_calculation(self, operation, data):
        """启动计算线程"""
        if not data['expression']:
            self.show_result("", "请输入数学表达式！")
            return
            
        self.calc_btn.setText("计算中...")
        self.calc_btn.setEnabled(False)
        
        self.thread = CalculationThread(operation, data)
        self.thread.finished.connect(self.handle_result)
        self.thread.start()

    def render_expression(self):
        """仅渲染表达式"""
        expr = self.expression_input.text().strip()
        if not expr:
            return
            
        try:
            parsed = parse_expr(expr)
            self.web_view.setHtml(self.base_html(latex(parsed)))
            self.text_result.setText(f"原始表达式：{str(parsed).replace('**', '^')}")
        except Exception as e:
            self.text_result.setText(f"渲染错误：{str(e)}")

    def base_html(self, latex_code):
        return f"""
        <html>
        <head>
            <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
            <script id="MathJax-script" async
                    src="https://cdn.bootcdn.net/ajax/libs/mathjax/3.2.0/es5/tex-mml-chtml.js">
            </script>
        </head>
        <body>
            <div style="font-size: 20px; padding: 20px; background: #C1FFC1;">
                $${latex_code}$$
            </div>
            <p>不定积分默认省略常数\\(C\\)</p>
        </body>
        </html>
        """

    def setup_style(self):
        self.setStyleSheet("""
            QWidget {
                font-family: '华文楷体', 'STKaiti', '楷体';
                font-size: 15px;
                padding: 5px;
            }
            QComboBox, QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                min-width: 200px;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 4px;
                background-color: #2196F3;
                color: white;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QTabWidget::pane {
                border-top: 2px solid #E0E0E0;
            }
            QLabel {
                padding: 5px 0;
            }
        """)
    def save_to_txt(self):
        """保存结果到文本文件"""
        if not self.current_result[0] and not self.current_result[1]:
            QMessageBox.critical(self, "保存错误", "没有可保存的结果！")
            return

        # 获取保存路径
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存计算结果",
            "",
            "文本文件 (*.txt)"
        )
        
        if not file_path:  # 用户取消选择
            return

        try:
            # 组织保存内容
            content = f"""计算时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            
原始表达式：{self.expression_input.text()}
操作类型：{self.operation_combo.currentText()}
            
LaTeX公式：
{self.current_result[0]}
            
文本结果：
{self.current_result[1]}
            """
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
                
            QMessageBox.information(self, "保存成功", f"结果已保存至：\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "保存失败",
                f"文件保存失败：\n{str(e)}"
            )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MathAssistantPro()
    window.show()
    sys.exit(app.exec())