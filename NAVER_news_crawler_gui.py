import re
import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QMessageBox,
    QFileDialog,
)
from PyQt6.QtCore import Qt

NAVER_SEARCH_BASE = "https://search.naver.com/search.naver?where=nexearch&sm=tab_hty.top&query="

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://search.naver.com/",
}


class NaverNewsCrawlerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("네이버 뉴스 크롤러")
        self.resize(900, 700)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("검색어를 입력하세요 (예: AI, 반도체)")

        self.search_button = QPushButton("검색")
        self.search_button.clicked.connect(self.run_crawler)

        self.save_button = QPushButton("엑셀 저장")
        self.save_button.clicked.connect(self.save_to_excel)

        self.status_label = QLabel("상태: 대기 중")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)

        top_layout = QHBoxLayout()
        top_layout.addWidget(self.search_input)
        top_layout.addWidget(self.search_button)
        top_layout.addWidget(self.save_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.log_area)
        self.setLayout(main_layout)

        self.results = []

    def clean_title(self, text):
        if not text:
            return ""
        text = text.replace("\xa0", " ")
        text = text.replace("Naver News", "")
        text = text.replace("네이버뉴스", "")
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def get_news_titles_and_links(self, query):
        url = NAVER_SEARCH_BASE + requests.utils.quote(query)
        response = requests.get(url, headers=HEADERS, timeout=20)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        for a_tag in soup.select("a[href]"):
            href = a_tag.get("href", "")
            if not href:
                continue

            if "news.naver.com" not in href and "n.news.naver.com" not in href:
                continue

            title = (
                a_tag.get("title")
                or a_tag.get("aria-label")
                or a_tag.get("data-title")
            )

            if not title:
                span_title = a_tag.select_one("span[data-title]")
                if span_title:
                    title = span_title.get("data-title")

            if not title:
                title = a_tag.get_text(" ", strip=True)

            title = self.clean_title(title)
            if title:
                results.append({"title": title, "link": href})

        seen = set()
        unique_results = []
        for item in results:
            if item["link"] not in seen:
                seen.add(item["link"])
                unique_results.append(item)

        return unique_results

    def get_article_text(self, article_url):
        response = requests.get(article_url, headers=HEADERS, timeout=20)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        selectors = [
            "#dic_area",
            "article",
            ".article_view",
            ".newsct_article",
            ".go_trans._article_content",
            "div.newsct_article",
        ]

        for selector in selectors:
            content = soup.select_one(selector)
            if content:
                paragraphs = content.select("p")
                if paragraphs:
                    text = " ".join(
                        p.get_text(" ", strip=True) for p in paragraphs if p.get_text(strip=True)
                    )
                    cleaned = re.sub(r"\s+", " ", text).strip()
                    if cleaned:
                        return cleaned

        body_text = soup.get_text(" ", strip=True)
        cleaned = re.sub(r"\s+", " ", body_text).strip()
        return cleaned

    def run_crawler(self):
        query = self.search_input.text().strip()
        if not query:
            QMessageBox.warning(self, "입력 오류", "검색어를 입력하세요.")
            return

        try:
            self.status_label.setText("상태: 크롤링 중...")
            self.log_area.clear()
            self.log_area.append(f"검색어: {query}\n")

            articles = self.get_news_titles_and_links(query)
            if not articles:
                self.status_label.setText("상태: 결과 없음")
                self.log_area.append("뉴스 링크를 찾지 못했습니다. 검색어를 바꾸거나 네이버 페이지 구조를 확인해 주세요.")
                return

            self.results = []

            for idx, article in enumerate(articles[:10], start=1):
                title = article["title"]
                link = article["link"]

                try:
                    content = self.get_article_text(link)
                except Exception:
                    content = "본문 추출 실패"

                row = {
                    "title": title,
                    "link": link,
                    "content": content,
                }
                self.results.append(row)

                self.log_area.append(f"[{idx}] {title}\n{link}\n")

            self.status_label.setText(f"상태: {len(self.results)}건 수집 완료")

        except Exception as e:
            self.status_label.setText("상태: 오류 발생")
            self.log_area.append(f"오류: {e}")
            QMessageBox.critical(self, "오류", str(e))

    def save_to_excel(self):
        if not self.results:
            QMessageBox.warning(self, "저장 오류", "먼저 검색을 실행해 주세요.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "엑셀 파일 저장",
            "naverResult.xlsx",
            "Excel Files (*.xlsx)",
        )

        if not file_path:
            return

        try:
            wb = Workbook()
            ws = wb.active
            ws.title = "Naver News"
            ws.append(["번호", "제목", "링크", "본문"])

            for idx, row in enumerate(self.results, start=1):
                ws.append([idx, row["title"], row["link"], row["content"]])

            ws.column_dimensions["A"].width = 8
            ws.column_dimensions["B"].width = 50
            ws.column_dimensions["C"].width = 80
            ws.column_dimensions["D"].width = 120

            wb.save(file_path)
            self.status_label.setText("상태: 엑셀 저장 완료")
            QMessageBox.information(self, "완료", f"엑셀 파일이 저장되었습니다.\n{file_path}")
        except Exception as e:
            self.status_label.setText("상태: 저장 실패")
            QMessageBox.critical(self, "저장 실패", str(e))


if __name__ == "__main__":
    app = QApplication([])
    window = NaverNewsCrawlerGUI()
    window.show()
    app.exec()
