import urllib.request
import urllib.parse
import json
import re
from html import unescape
from datetime import datetime, timezone, timedelta

# 네이버 뉴스 검색: '해군' 키워드 + 관련도순(sort=0)
query = urllib.parse.quote("해군")
url = f"https://search.naver.com/search.naver?where=news&query={query}&sort=0"

req = urllib.request.Request(
    url,
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "ko-KR,ko;q=0.9"
    }
)

html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", errors="ignore")

kst = timezone(timedelta(hours=9))
today_str = datetime.now(kst).strftime("%Y.%m.%d")

def clean_html(text):
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", unescape(text)).strip()

news_list = []
seen_titles = set()

# 네이버 뉴스 검색 결과에서 개별 뉴스 영역(bx) 단위로 추출
blocks = re.findall(r'<li class="bx"[^>]*>(.*?)</li>\s*(?=<li class="bx"|</ul>)', html, re.S)

for block in blocks:
    # 기사 제목과 링크 추출 (news_tit 클래스)
    tit_match = re.search(r'<a[^>]*class="[^"]*news_tit[^"]*"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', block, re.S)
    if not tit_match:
        continue

    link = unescape(tit_match.group(1)).strip()
    title = clean_html(tit_match.group(2))

    if not title or title in seen_titles:
        continue
    seen_titles.add(title)

    # 네이버 뉴스 인링크(n.news.naver.com)가 있으면 우선 사용
    naver_link_match = re.search(r'href="(https://n\.news\.naver\.com/mnews/article/[^"]+)"', block)
    if naver_link_match:
        link = unescape(naver_link_match.group(1)).strip()

    # 언론사명 추출
    press_match = re.search(r'class="[^"]*info press[^"]*"[^>]*>(.*?)</a>', block, re.S)
    press = clean_html(press_match.group(1)).replace("언론사 선정", "").strip() if press_match else "주요 언론사"

    # 본문 요약문 추출
    dsc_match = re.search(r'class="[^"]*news_dsc[^"]*"[^>]*>(.*?)</div>', block, re.S)
    summary = clean_html(dsc_match.group(1)) if dsc_match else "클릭하여 기사 원문을 확인하세요."
    if len(summary) > 95:
        summary = summary[:92] + "..."

    news_list
