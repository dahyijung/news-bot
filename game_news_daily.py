from datetime import datetime, timedelta, timezone
import feedparser
import os
import re
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ========== 설정 ==========
now = datetime.now(timezone.utc)
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
    "넥슨": [
        "넥슨", "nexon", "넥슨게임즈", "nexon games", "데브캣", "devcat", "던전앤파이터", "던파", "dnf",
        "블루 아카이브", "blue archive", "카트라이더", "카트", "kartrider", "hit2", "마비노기", "mabinogi",
        "서든어택", "sudden attack", "빈딕투스", "vindictus", "네오플", "퍼스트 버서커", "카잔",
        "fc온라인", "fc online", "피파온라인", "fifa online", "메이플스토리", "maplestory", "메이플",
        "v4", "프라시아 전기", "프라시아", "워헤이븐", "warhaven", "베일드 엑스퍼트", "veiled experts"
    ],
    "크래프톤": [
        "크래프톤", "krafton", "펍지", "pubg", "pubg studios", "pubg mobile", "화평정영", "和平精英", "bgmi",
        "더 칼리스토 프로토콜", "the callisto protocol", "칼리스토", "ttbt",
        "눈물을 마시는 새", "김창한", "뉴스테이트", "new state mobile", "new state",
        "striking distance", "스트라이킹 디스턴스", "subnautica", "서브노티카", "unknown worlds", "언노운월즈"
    ],
    "시프트업": [
        "시프트업", "shift up", "스텔라 블레이드", "stellar blade", "스텔블",
        "데스티니 차일드", "destiny child", "니케", "승리의 여신: 니케", "goddess of victory nikke", "김형태"
    ],
    "스마일게이트": [
        "스마일게이트", "smilegate", "스마일게이트 rpg", "스마일게이트 메가포트", "smilegate rpg", "megaport",
        "로스트아크", "lost ark", "로아", "에픽세븐", "epic seven", "수퍼크리에이티브", "super creative",
        "크로스파이어", "crossfire", "cf", "cfx", "소울워커", "soulworker", "스토브", "stove", "테일즈런너"
    ],
    "ncsoft": [
        "ncsoft", "nc", "엔씨소프트", "엔씨", "리니지", "lineage", "리니지m", "lineage m", "리니지w", "lineage w",
        "블레이드 앤 소울", "blade & soul", "블소", "아이온", "aion", "tl", "throne and liberty",
        "트릭스터", "유니버스", "universe", "퍼플", "purple", "퓨저"
    ],
    "넷마블": [
        "넷마블", "netmarble", "넷마블넥서스", "넷마블몬스터", "넷마블에프앤씨", "netmarble nexus", "netmarble monster",
        "세븐나이츠", "seven knights", "세나", "나 혼자만 레벨업", "나혼렙", "solo leveling",
        "a3", "a3 still alive", "모두의마블", "모마", "제2의 나라", "second country", "7ds", "일곱 개의 대죄",
        "seven deadly sins", "bts island", "마블 퓨처파이트", "marvel future fight", "마퓨파",
        "오버프라임", "킹오파", "더 킹 오브 파이터즈", "the king of fighters", "뱀피르", "vampire"
    ],
    "펄어비스": [
        "펄어비스", "pearl abyss", "검은사막", "black desert", "bdo", "검은사막 모바일", "black desert mobile",
        "붉은사막", "crimson desert", "도깨비", "dokev", "정경인", "cco", "플랜8", "plan 8"
    ],
    "컴투스": [
        "컴투스", "com2us", "컴투스홀딩스", "com2us holdings", "서머너즈 워", "서머너즈워", "summoners war",
        "크로니클", "서머너즈워: 크로니클", "summoners war: chronicles", "스타라이트", "스타시드", "starseed",
        "mlb9이닝스", "mlb 9 innings", "컴투버스", "com2verse", "버추얼플레이", "워킹데드", "the walking dead"
    ],
    "네오위즈": [
        "네오위즈", "neowiz", "네오위즈게임즈", "p의 거짓", "lies of p", "브라운더스트", "brown dust",
        "bd2", "아바", "ava", "디제이맥스", "djmax", "스컬", "skul"
    ],
    "카카오게임즈": [
        "카카오게임즈", "kakao games", "크로노 오디세이", "chrono odyssey", "우마무스메", "uma musume",
        "가디언 테일즈", "guardian tales", "에버소울", "eversoul", "카겜"
    ],
    "데브시스터즈": [
        "데브시스터즈", "devsisters", "쿠키런", "cookierun", "쿠키런 킹덤", "cookie run kingdom", "브레이버스",
        "브레이버스: 다크라이즈", "오븐브레이크", "ovenbreak", "쿠런"
    ],
    "위메이드": [
        "위메이드", "wemade", "위메이드맥스", "wemade max", "위메이드플레이", "wemade play",
        "미르", "미르의 전설", "legend of mir", "미르m", "미르4", "전기아이피", "장현국",
        "위믹스", "wemix", "wemix play", "wcd"
    ]
}



exclude_keywords = [
    "블록체인", "web3", "웹3", "마브렉스", "포커", "맞고", "골프", "오늘의 주요일정", "msi",
    "카지노", "사행성", "도박", "경마", "경륜", "룰렛", "nft", "가상자산", "암호화폐", "코인"
]

update_keywords = [
    "출시", "론칭", "런칭", "발표", "공개", "업데이트", "데모", "신작", "신규", "베타",
    "얼리", "cbt", "obt", "사전예약", "사전 등록"
]

industry_keywords = [
    "파업", "한한령", "규제", "판매량", "개최", "모집", "홍콩", "대만", "시정", "게임 업계",
    "매출", "시장", "주가", "리스크", "해외 진출", "정책", "인수합병", "m&a", "펀딩", "정부"
]


news_data = {k: [] for k in game_companies}
news_data["<신작/업데이트>"] = []
news_data["<업계>"] = []
news_data["<기타>"] = []

# 중복 필터용
seen_titles = []
duplicate_candidates = []

def is_similar_cosine(new_title):
    if not seen_titles:
        return False
    vectorizer = TfidfVectorizer().fit(seen_titles + [new_title])
    vectors = vectorizer.transform(seen_titles + [new_title])
    similarities = cosine_similarity(vectors[-1], vectors[:-1])
    return max(similarities[0]) >= 0.5

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

        if is_similar_cosine(title):
            duplicate_candidates.append(f"{title}<br>🔗 <a href='{link}'>{link}</a>")
            continue
        seen_titles.append(title)

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

# ========== HTML 출력 ==========
output_lines = ["<hr>"]
for section in list(game_companies.keys()) + ["<신작/업데이트>", "<업계>", "<기타>"]:
    if news_data[section]:
        output_lines.append(f"<h2>🔺 {section}</h2>")
        for item in news_data[section]:
            output_lines.append(f"<p>{item}</p><br>")
        output_lines.append("<hr>")

# 중복 의심 뉴스 표시
if duplicate_candidates:
    output_lines.append(f"<h2>⚠️ 중복 의심 뉴스</h2>")
    for item in duplicate_candidates:
        output_lines.append(f"<p>{item}</p><br>")
    output_lines.append("<hr>")

html_output = "<html><body>" + "".join(output_lines) + "</body></html>"

# ========== Teams 전송 ==========
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

webhook_url = "https://prod-64.westus.logic.azure.com:443/workflows/2433824cc25c4585bb0c18d716bfc3f0/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=oXU7IMET52YHW6AhexHeyX7oPmJZJcTksUvbVrmOfIY"
print(html_output)
send_to_teams(webhook_url, html_output)
