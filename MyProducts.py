import sqlite3
from openpyxl import Workbook
from openpyxl.styles import Font
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QFileDialog,
    QHeaderView,
    QFormLayout,
)
from PyQt6.QtCore import Qt


DB_NAME = "products.db"


def connect_db(db_name=DB_NAME):
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn


def create_table():
    conn = connect_db()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS Products (
                productID INTEGER PRIMARY KEY AUTOINCREMENT,
                productName TEXT NOT NULL,
                productPrice INTEGER NOT NULL,
                productCategory TEXT,
                productStock INTEGER DEFAULT 0,
                createdAt TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def insert_product(product_name, product_price, product_category="", product_stock=0):
    conn = connect_db()
    try:
        cursor = conn.execute(
            """
            INSERT INTO Products (productName, productPrice, productCategory, productStock)
            VALUES (?, ?, ?, ?)
            """,
            (product_name, product_price, product_category, product_stock),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def update_product(product_id, product_name, product_price, product_category, product_stock):
    conn = connect_db()
    try:
        conn.execute(
            """
            UPDATE Products
            SET productName = ?, productPrice = ?, productCategory = ?, productStock = ?
            WHERE productID = ?
            """,
            (product_name, product_price, product_category, product_stock, product_id),
        )
        conn.commit()
    finally:
        conn.close()


def delete_product(product_id):
    conn = connect_db()
    try:
        conn.execute("DELETE FROM Products WHERE productID = ?", (product_id,))
        conn.commit()
    finally:
        conn.close()


def get_products():
    conn = connect_db()
    try:
        rows = conn.execute(
            "SELECT * FROM Products ORDER BY productID"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


class ProductManagerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("제품 관리 프로그램")
        self.resize(980, 660)
        self.setStyleSheet(
            """
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #f5f7ff, stop:1 #eef7ff);
                color: #1a1d29;
                font-family: 'Malgun Gothic';
                font-size: 12px;
            }
            QLabel {
                color: #1f2a44;
                font-weight: bold;
            }
            QLineEdit {
                background: #ffffff;
                border: 1px solid #c8d4ff;
                border-radius: 10px;
                padding: 8px 10px;
                selection-background-color: #7c9cff;
            }
            QLineEdit:focus {
                border: 2px solid #6a7cff;
            }
            QPushButton {
                border: none;
                border-radius: 12px;
                padding: 10px 16px;
                font-weight: bold;
                color: white;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #6a7cff, stop:1 #8d5cf6);
                min-width: 90px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #5f6ef0, stop:1 #7c4ae8);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #4d5fe7, stop:1 #693ddd);
            }
            QTableWidget {
                background: rgba(255, 255, 255, 0.8);
                border: 1px solid #d8e2ff;
                border-radius: 12px;
                gridline-color: #dfe9ff;
                alternate-background-color: #f7f9ff;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #7d86ff, stop:1 #6d7cfb);
                color: white;
                padding: 8px;
                border: 1px solid #6d7cfb;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #edf1ff;
            }
            QTableWidget::item:selected {
                background: #dfe7ff;
                color: #1d2b57;
            }
            """
        )

        title_label = QLabel("PRODUCT MANAGEMENT")
        title_label.setStyleSheet(
            """
            QLabel {
                color: #3d4cc7;
                font-size: 24px;
                font-weight: bold;
                padding: 8px 0 12px 0;
            }
            """
        )

        self.name_input = QLineEdit()
        self.price_input = QLineEdit()
        self.category_input = QLineEdit()
        self.stock_input = QLineEdit()

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID",
            "상품명",
            "가격",
            "카테고리",
            "재고",
            "등록일",
        ])
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.clicked.connect(self.fill_form_from_selected_row)

        self.add_button = QPushButton("추가")
        self.update_button = QPushButton("수정")
        self.delete_button = QPushButton("삭제")
        self.refresh_button = QPushButton("새로고침")
        self.export_button = QPushButton("엑셀 저장")

        self.add_button.clicked.connect(self.add_product)
        self.update_button.clicked.connect(self.update_product)
        self.delete_button.clicked.connect(self.delete_product)
        self.refresh_button.clicked.connect(self.load_products)
        self.export_button.clicked.connect(self.export_to_excel)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.setContentsMargins(18, 10, 18, 10)
        form_layout.addRow("상품명:", self.name_input)
        form_layout.addRow("가격:", self.price_input)
        form_layout.addRow("카테고리:", self.category_input)
        form_layout.addRow("재고:", self.stock_input)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.export_button)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)
        main_layout.addWidget(title_label)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.table)

        self.setLayout(main_layout)
        self.load_products()

    def clear_form(self):
        self.name_input.clear()
        self.price_input.clear()
        self.category_input.clear()
        self.stock_input.clear()
        self.table.clearSelection()

    def validate_inputs(self):
        name = self.name_input.text().strip()
        price_text = self.price_input.text().strip()
        category = self.category_input.text().strip()
        stock_text = self.stock_input.text().strip()

        if not name:
            QMessageBox.warning(self, "입력 오류", "상품명을 입력해주세요.")
            return None, None, None, None

        try:
            price = int(price_text)
            stock = int(stock_text)
        except ValueError:
            QMessageBox.warning(self, "입력 오류", "가격과 재고는 숫자로 입력해주세요.")
            return None, None, None, None

        return name, price, category, stock

    def add_product(self):
        name, price, category, stock = self.validate_inputs()
        if name is None:
            return

        insert_product(name, price, category, stock)
        self.clear_form()
        self.load_products()
        QMessageBox.information(self, "성공", "제품이 추가되었습니다.")

    def update_product(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "선택 오류", "수정할 제품을 선택해주세요.")
            return

        product_id = int(self.table.item(selected_row, 0).text())
        name, price, category, stock = self.validate_inputs()
        if name is None:
            return

        update_product(product_id, name, price, category, stock)
        self.clear_form()
        self.load_products()
        QMessageBox.information(self, "성공", "제품 정보가 수정되었습니다.")

    def delete_product(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "선택 오류", "삭제할 제품을 선택해주세요.")
            return

        product_id = int(self.table.item(selected_row, 0).text())
        reply = QMessageBox.question(
            self,
            "삭제 확인",
            f"ID {product_id} 제품을 삭제하시겠습니까?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            delete_product(product_id)
            self.clear_form()
            self.load_products()
            QMessageBox.information(self, "성공", "제품이 삭제되었습니다.")

    def fill_form_from_selected_row(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            return

        self.name_input.setText(self.table.item(selected_row, 1).text())
        self.price_input.setText(self.table.item(selected_row, 2).text())
        self.category_input.setText(self.table.item(selected_row, 3).text())
        self.stock_input.setText(self.table.item(selected_row, 4).text())

    def load_products(self):
        products = get_products()
        self.table.setRowCount(len(products))

        for row_index, product in enumerate(products):
            values = [
                str(product["productID"]),
                product["productName"],
                str(product["productPrice"]),
                product["productCategory"] or "",
                str(product["productStock"]),
                product["createdAt"] or "",
            ]

            for col_index, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row_index, col_index, item)

    def export_to_excel(self):
        products = get_products()
        if not products:
            QMessageBox.warning(self, "엑셀 저장", "저장할 데이터가 없습니다.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "엑셀 파일 저장",
            "products.xlsx",
            "Excel Files (*.xlsx)",
        )

        if not file_path:
            return

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Products"

        headers = ["productID", "productName", "productPrice", "productCategory", "productStock", "createdAt"]
        sheet.append(headers)

        for product in products:
            sheet.append([
                product["productID"],
                product["productName"],
                product["productPrice"],
                product["productCategory"] or "",
                product["productStock"],
                product["createdAt"] or "",
            ])

        header_font = Font(bold=True)
        for cell in sheet[1]:
            cell.font = header_font

        for column_cells in sheet.columns:
            max_length = 0
            column = column_cells[0].column_letter
            for cell in column_cells:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except TypeError:
                    pass
            adjusted_width = max_length + 2
            sheet.column_dimensions[column].width = adjusted_width

        workbook.save(file_path)
        QMessageBox.information(self, "저장 완료", f"엑셀 파일이 저장되었습니다:\n{file_path}")


if __name__ == "__main__":
    create_table()
    app = QApplication([])
    window = ProductManagerWindow()
    window.show()
    app.exec()
