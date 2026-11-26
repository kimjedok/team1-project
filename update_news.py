import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json
import re
from datetime import datetime, timezone, timedelta

def get_real_url(google_rss_url, title):
    # 1. Google News 리다이렉트 URL에서 실제 언론사 주소 추적 시도
    try:
        req = urllib.request.Request(
            google_rss_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            final_url = resp.geturl()
            if "news.google.com" not in final_url:
                return final_url
            html = resp.read().decode("utf-8", errors="ignore")
            # HTML 내 실제 원문 링크 추출
            match = re.search(r'data-n-au="([^"]+)"', html)
            if match:
                return match.group(1)
    except Exception:
        pass

    # 2. 추적 실패 시 해당 기사 정확한 제목으로 네이버 뉴스 최상단 검색 결과 연결
    encoded_title = urllib.parse.quote(title)
    return f"https://search.naver.com/search.naver?where=news&query={encoded_title}&sort=0"

# 구글 뉴스 RSS('해군' 검색 결과)
url = "https://news.google.com/rss/search?q=%ED%95%B4%EA%B5%B0&hl=ko&gl=KR&ceid=KR:ko"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
xml_data = urllib.request.urlopen(req, timeout=15).read()

root = ET.fromstring(xml_data)
items = root.findall("./channel/item")[:4]

kst = timezone(timedelta(hours=9))
news_list = []

for item in items:
    raw_title = item.findtext("title", default="해군 관련 주요 보도")
    raw_link = item.findtext("link", default="")
    raw_date = item.findtext("pubDate", default="")
    source = item.findtext("source", default="언론사")

    clean_title = re.sub(r"\s-\s[^-]+$", "", raw_title).strip()
    real_link = get_real_url(raw_link, clean_title) if raw_link else f"https://search.naver.com/search.naver?where=news&query={urllib.parse.quote(clean_title)}"

    formatted_date = datetime.now(kst).strftime("%Y.%m.%d")
    if raw_date:
        try:
            dt = datetime.strptime(raw_date, "%a, %d %b %Y %H:%M:%S %Z").replace(tzinfo=timezone.utc).astimezone(kst)
            formatted_date = dt.strftime("%Y.%m.%d")
        except ValueError:
            pass

    news_list.append({
        "meta": f"{source} · {formatted_date}",
        "title": clean_title,
        "link": real_link,
        "summary": "클릭하여 해당 기사 원문을 확인하세요."
    })

with open("news.json", "w", encoding="utf-8") as f:
    json.dump(news_list, f, ensure_ascii=False, indent=2)
