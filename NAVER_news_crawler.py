import re
import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook

NAVER_SEARCH_URL = "https://search.naver.com/search.naver?sm=tab_hty.top&where=nexearch&ssc=tab.nx.all&query=AI&oquery=AI%5C&tqi=jbh9Cdqo1SCssDDWnaGssssstIN-045342&ackey=r0afict9"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://search.naver.com/",
}


def clean_title(text):
    if not text:
        return ""

    text = text.replace("\xa0", " ")
    text = text.replace("Naver News", "")
    text = text.replace("네이버뉴스", "")
    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    return text


def get_news_titles_and_links(search_url):
    response = requests.get(search_url, headers=HEADERS, timeout=20)
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

        title = clean_title(title)

        if title:
            results.append({"title": title, "link": href})

    seen = set()
    unique_results = []
    for item in results:
        link = item["link"]
        if link not in seen:
            seen.add(link)
            unique_results.append(item)

    if not unique_results:
        print("디버그: 기사 링크를 찾지 못했습니다.")
        print("디버그: 링크 수 =", len(soup.select("a[href]")))
        print("디버그: HTML 일부 =", response.text[:800])

    return unique_results


def get_article_text(article_url):
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


def save_to_excel(rows, filename="naverResult.xlsx"):
    wb = Workbook()
    ws = wb.active
    ws.title = "Naver News"

    ws.append(["번호", "제목", "링크", "본문"])

    for idx, row in enumerate(rows, start=1):
        ws.append([idx, row["title"], row["link"], row["content"]])

    ws.column_dimensions["A"].width = 8
    ws.column_dimensions["B"].width = 50
    ws.column_dimensions["C"].width = 80
    ws.column_dimensions["D"].width = 120

    wb.save(filename)
    print(f"엑셀 저장 완료: {filename}")


def main():
    try:
        articles = get_news_titles_and_links(NAVER_SEARCH_URL)

        if not articles:
            print("뉴스 제목을 찾지 못했습니다. Naver 페이지 구조가 바뀌었거나 검색 결과가 비어 있을 수 있습니다.")
            return

        result_rows = []

        for idx, article in enumerate(articles[:10], start=1):
            title = article["title"]
            link = article["link"]

            try:
                content = get_article_text(link)
            except Exception:
                content = "본문 추출 실패"

            result_rows.append({
                "title": title,
                "link": link,
                "content": content,
            })

            print(f"[{idx}] 제목: {title}")
            print(f"본문 길이: {len(content)}")

        save_to_excel(result_rows)

    except Exception as e:
        print("오류 발생:", e)


if __name__ == "__main__":
    main()
