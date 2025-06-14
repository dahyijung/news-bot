
from datetime import datetime, timedelta, timezone
import feedparser
import os
import re
import requests


# ========== 설정 ==========
now = datetime.now(timezone.utc)  # 기준 시간을 UTC로 설정
time_threshold = now - timedelta(hours=30)

save_path = r"C:\Users\dahyijung\OneDrive - Tencent Overseas\tencentoverseas - News clipping - backup"
html_file = os.path.join(save_path, "game_news_today.html")

rss_feeds = {
    "Inven": "http://feeds.feedburner.com/inven",
    "GameMeca": "https://politepol.com/fd/DSTJAWihranz.xml",
    "MK": "https://www.mk.co.kr/rss/50700001/",
    "Newsis": "https://politepol.com/fd/Z6T2aIbkTe0U.xml",
    "Nate": "https://politepol.com/fd/zTPzbnZy6IQu.xml"
}

game_companies = {
    "넥슨": ["넥슨", "Nexon", "던파", "DNF", "블루 아카이브", "Blue Archive", "카트라이더", "Hit2", "마비노기", "서든어택", "빈딕투스", "네오플", "퍼스트 버서커", "카잔", "FC온라인", "MapleStory", "메이플스토리", "메이플"],
    "크래프톤": ["크래프톤", "Krafton", "배틀그라운드", "PUBG", "칼리스토", "The Callisto Protocol", "TTBT", "눈물을 마시는 새", "김창한", "뉴스테이트", "NEW STATE", "Striking Distance", "Subnautica", "언노운월즈"],
    "시프트업": ["시프트업", "Shift Up", "스텔라 블레이드", "Stellar Blade", "스텔블", "데스티니 차일드", "프로젝트 위치스", "스피릿", "김형태"],
    "스마일게이트": ["스마일게이트", "Smilegate", "로스트아크", "Lost Ark", "로아", "에픽세븐", "Epic Seven", "이클립스", "크로스파이어", "CF", "CFX", "소울워커", "Stove"],
    "NCSoft": ["NCSoft", "NC", "엔씨", "리니지", "Lineage", "블소", "Blade & Soul", "아이온", "Aion", "TL", "Throne and Liberty", "트릭스터", "유니버스", "Purple"],
    "넷마블": ["넷마블", "Netmarble", "세븐나이츠", "세나", "나 혼자만 레벨업", "나혼렙", "Solo Leveling", "A3", "모두의마블", "모마", "제2의나라", "7DS", "일곱 개의 대죄", "BTS Island", "마블 퓨처파이트", "마퓨파", "오버프라임", "킹오파", "뱀피르"],
    "펄어비스": ["펄어비스", "Pearl Abyss", "검은사막", "Black Desert", "붉은사막", "Crimson Desert", "도깨비", "DokeV", "정경인", "이재명 대표", "CCO"],
    "컴투스": ["컴투스", "Com2uS", "서머너즈워", "Summoners War", "서머너즈워: 크로니클", "크로니클", "스타라이트", "스타시드", "MLB9이닝스", "버추얼플레이"],
    "네오위즈": ["네오위즈", "Neowiz", "P의 거짓", "Lies of P", "라이어P", "브라운더스트", "Brown Dust", "아바", "AVA", "디제이맥스", "DJMAX"],
"카카오게임즈": ["카카오게임즈", "Kakao Games", "크로노 오디세이", "Chrono Odyssey"],
    "데브시스터즈": ["데브시스터즈", "DevSisters", "쿠키런", "CookieRun", "쿠키RUN 킹덤", "킹덤", "브레이버스", "브레이버스: 다크라이즈", "데브", "쿠런"],
    "위메이드": ["위메이드", "Wemade", "위메이드맥스", "Wemade Max", "미르", "미르M", "미르4", "Legend of Mir", "전기아이피", "장현국", "위믹스", "WEMIX"]
}

exclude_keywords = ["블록체인", "Web3", "마브렉스", "포커", "맞고", "골프", "웹3", "오늘의 주요일정", "MSI"]
update_keywords = ["출시", "론칭", "데모", "업데이트", "런칭", "발표", "공개"]
industry_keywords = ["파업", "한한령", "규제", "판매량", "개최", "모집", "홍콩", "대만", "시정", "게임 업계"]

news_data = {k: [] for k in game_companies}
news_data["<신작/업데이트>"] = []
news_data["<업계>"] = []
news_data["<기타>"] = []

seen_titles_tokens = []

def tokenize(text):
    return set(re.findall(r'\b[\w가-힣]+\b', text.lower()))

def is_similar(title_tokens):
    for tokens in seen_titles_tokens:
        if len(title_tokens & tokens) >= 3:
            return True
    return False

# ========== 수집 ==========
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
        if is_similar(title_tokens):
            continue
        seen_titles_tokens.append(title_tokens)

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
# ========== Teams 웹훅 전송 ==========

# output_lines = [f"<font size=25><b>📰 게임 뉴스 요약 - {now.astimezone(timezone(timedelta(hours=9))).strftime('%Y-%m-%d')}</b></font><hr>"]
output_lines = ["<hr>"]
for section in list(game_companies.keys()) + ["<신작/업데이트>", "<업계>", "<기타>"]:
    if news_data[section]:
        output_lines.append(f"<h2>🔺 {section}</h2>")
        for item in news_data[section]:
            output_lines.append(f"<p>{item}</p><br>")
        output_lines.append("<hr>")

html_output = "<html><body>" + "".join(output_lines) + "</body></html>"


def send_to_teams(webhook_url, message_text):
    payload = {
        "text": message_text
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(webhook_url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"❌ Teams 전송 실패: {response.status_code}, {response.text}")
    else:
        print("✅ Teams 전송 완료")


# 전송 실행
webhook_url = "https://prod-64.westus.logic.azure.com:443/workflows/2433824cc25c4585bb0c18d716bfc3f0/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=oXU7IMET52YHW6AhexHeyX7oPmJZJcTksUvbVrmOfIY"
print(html_output)
send_to_teams(webhook_url, html_output)