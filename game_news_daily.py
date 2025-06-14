
from datetime import datetime, timedelta, timezone
import feedparser
import re
import requests

# 시간 설정
now_utc = datetime.now(timezone.utc)
now_kst = now_utc.astimezone(timezone(timedelta(hours=9)))
time_threshold = now_utc - timedelta(hours=30)

# RSS 피드
rss_feeds = {
    "Inven": "http://feeds.feedburner.com/inven",
    "GameMeca": "https://politepol.com/fd/DSTJAWihranz.xml",
    "MK": "https://www.mk.co.kr/rss/50700001/",
    "Newsis": "https://politepol.com/fd/Z6T2aIbkTe0U.xml",
    "Nate": "https://politepol.com/fd/zTPzbnZy6IQu.xml"
}

# 게임사 키워드 예시 (필요시 전체 버전으로 교체)
game_companies = {
    "넥슨": ["넥슨", "Nexon", "던파", "MapleStory", "메이플"],
    "컴투스": ["컴투스", "서머너즈워", "Summoners War", "서머너즈"]
}

exclude_keywords = ["블록체인", "포커", "맞고", "골프"]
update_keywords = ["출시", "론칭", "데모", "업데이트", "런칭", "발표", "공개"]
industry_keywords = ["파업", "한한령", "규제", "판매량", "개최", "모집", "홍콩", "대만", "시정", "게임 업계"]

news_data = {k: [] for k in game_companies}
news_data["<신작/업데이트>"] = []
news_data["<업계>"] = []
news_data["<기타>"] = []

def tokenize(text):
    return set(re.findall(r'\b[\w가-힣]+\b', text.lower()))

def is_jaccard_similar(new_tokens, seen_tokens_list, threshold=0.4):
    for tokens in seen_tokens_list:
        inter = new_tokens & tokens
        union = new_tokens | tokens
        if len(union) > 0 and len(inter) / len(union) >= threshold:
            return True
    return False

seen_title_tokens = []

# 뉴스 수집
for source, url in rss_feeds.items():
    feed = feedparser.parse(url)
    for entry in feed.entries:
        title = entry.title.strip()
        link = entry.link
        published = entry.get("published_parsed")
        if not published:
            continue

        pub_datetime_kst = datetime(*published[:6], tzinfo=timezone(timedelta(hours=9)))
        pub_datetime_utc = pub_datetime_kst.astimezone(timezone.utc)
        if pub_datetime_utc < time_threshold:
            continue

        title_tokens = tokenize(title)
        if is_jaccard_similar(title_tokens, seen_title_tokens, threshold=0.4):
            continue
        seen_title_tokens.append(title_tokens)

        if any(x in title for x in exclude_keywords):
            continue

        line = f"{title}<br>🔗 <a href='{link}'>{link}</a>"

        matched = False
        for company, keywords in game_companies.items():
            if any(k in title for k in keywords):
                news_data[company].append(line)
                matched = True
                break

        if not matched:
            if any(k in title for k in update_keywords):
                news_data["<신작/업데이트>"].append(line)
            elif any(k in title for k in industry_keywords):
                news_data["<업계>"].append(line)
            else:
                news_data["<기타>"].append(line)

# HTML 출력
output_lines = ["<hr>"]
for section in list(game_companies.keys()) + ["<신작/업데이트>", "<업계>", "<기타>"]:
    if news_data[section]:
        output_lines.append(f"<h2>🔺 {section}</h2>")
        for item in news_data[section]:
            output_lines.append(f"<p>{item}</p><br>")
        output_lines.append("<hr>")

html_output = "<html><body>" + "".join(output_lines) + "</body></html>"

# Teams 전송 함수
def send_to_teams(webhook_url, message_text):
    payload = { "text": message_text }
    headers = { "Content-Type": "application/json" }
    response = requests.post(webhook_url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"❌ Teams 전송 실패: {response.status_code}, {response.text}")
    else:
        print("✅ Teams 전송 완료")

# 전송 실행
webhook_url = "https://prod-64.westus.logic.azure.com:443/workflows/2433824cc25c4585bb0c18d716bfc3f0/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=oXU7IMET52YHW6AhexHeyX7oPmJZJcTksUvbVrmOfIY"
print(html_output)
send_to_teams(webhook_url, html_output)
