import urllib.request
import xml.etree.ElementTree as ET
import json
import re
from datetime import datetime, timezone, timedelta

# 구글 뉴스 RSS('해군' 검색 결과 - 이슈/관련도 기준)
url = "https://news.google.com/rss/search?q=%ED%95%B4%EA%B5%B0&hl=ko&gl=KR&ceid=KR:ko"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
xml_data = urllib.request.urlopen(req, timeout=15).read()

root = ET.fromstring(xml_data)
items = root.findall("./channel/item")[:4]

kst = timezone(timedelta(hours=9))
news_list = []

for item in items:
    raw_title = item.findtext("title", default="해군 관련 주요 보도")
    raw_link = item.findtext("link", default="https://search.naver.com/search.naver?where=news&query=%ED%95%B4%EA%B5%B0&sort=0")
    raw_date = item.findtext("pubDate", default="")
    source = item.findtext("source", default="언론사")

    # 기사 제목 끝에 붙는 ' - 언론사명' 제거
    clean_title = re.sub(r"\s-\s[^-]+$", "", raw_title).strip()

    # 발행일을 한국 시간(KST) YYYY.MM.DD로 변환
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
        "link": raw_link,
        "summary": "클릭하여 해당 기사 원문을 확인하세요."
    })

with open("news.json", "w", encoding="utf-8") as f:
    json.dump(news_list, f, ensure_ascii=False, indent=2)
