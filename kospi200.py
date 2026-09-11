import sys
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QLabel,
)

URL = "https://finance.naver.com/sise/entryJongmok.naver?type=KPI200"


def clean_text(text):
    return " ".join(text.replace("\xa0", " ").split())


def fetch_kospi200_top_stocks():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    response = requests.get(URL, headers=headers, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.select_one("div.box_type_m table.type_1")
    if table is None:
        raise RuntimeError("편입종목 상위 테이블을 찾을 수 없습니다.")

    rows = table.select("tr")
    if len(rows) < 3:
        raise RuntimeError("테이블 데이터가 없습니다.")

    columns = [clean_text(th.get_text()) for th in rows[0].select("th")]
    data = []

    for row in rows[2:-1]:
        cells = row.select("td")
        if len(cells) < 7:
            continue

        row_values = [clean_text(cell.get_text()) for cell in cells[:7]]
        item = {key: value for key, value in zip(columns, row_values)}
        data.append(item)

    return columns, data


class Kospi200Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("코스피200 편입종목 상위")
        self.resize(1200, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout()
        central_widget.setLayout(root_layout)

        title = QLabel("코스피200 편입종목 상위")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 8px;")
        root_layout.addWidget(title)

        button_layout = QHBoxLayout()
        self.refresh_button = QPushButton("새로고침")
        self.export_button = QPushButton("Excel 저장")
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.export_button)
        root_layout.addLayout(button_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(self.table.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(0, self.table.horizontalHeader().ResizeMode.Stretch)
        root_layout.addWidget(self.table)

        self.refresh_button.clicked.connect(self.load_data)
        self.export_button.clicked.connect(self.export_to_excel)

        self.load_data()

    def load_data(self):
        try:
            columns, data = fetch_kospi200_top_stocks()

            self.table.setRowCount(len(data))
            self.table.setColumnCount(len(columns))
            self.table.setHorizontalHeaderLabels(columns)

            for row_idx, row in enumerate(data):
                for col_idx, key in enumerate(columns):
                    value = row.get(key, "")
                    item = QTableWidgetItem(value)
                    self.table.setItem(row_idx, col_idx, item)

            self.table.resizeColumnsToContents()
            self.table.resizeRowsToContents()

        except Exception as e:
            self.table.setRowCount(1)
            self.table.setColumnCount(1)
            self.table.setHorizontalHeaderLabels(["오류"])
            self.table.setItem(0, 0, QTableWidgetItem(str(e)))

    def export_to_excel(self):
        try:
            columns = [self.table.horizontalHeaderItem(col).text() for col in range(self.table.columnCount())]
            rows = []
            for row in range(self.table.rowCount()):
                rows.append([self.table.item(row, col).text() if self.table.item(row, col) is not None else "" for col in range(self.table.columnCount())])

            wb = Workbook()
            ws = wb.active
            ws.title = "코스피200"
            ws.append(columns)
            for row in rows:
                ws.append(row)

            file_name = "kospi200.xlsx"
            wb.save(file_name)

            QMessageBox.information(self, "저장 완료", f"엑셀 파일이 저장되었습니다.\n{file_name}")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"저장 중 오류가 발생했습니다.\n{e}")


def main():
    app = QApplication(sys.argv)
    window = Kospi200Window()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
