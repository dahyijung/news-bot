
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

save_path = r"C:\\Users\\dahyijung\\OneDrive - Tencent Overseas\\tencentoverseas - News clipping - backup"
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
        "v4", "프라시아 전기", "프라시아", "워헤이븐", "warhaven", "베일드 엑스퍼트", "veiled experts", "낙원", "데이브", "데더다", "nakwon", 
        "민트로켓", "니트로", "프로젝트 오버킬", "엠바크"
    ],
    "크래프톤": [
        "크래프톤", "krafton", "펍지", "pubg", "pubg studios", "pubg mobile", "화평정영", "bgmi", "배그", "배틀그라운드",
        "더 칼리스토 프로토콜", "the callisto protocol", "칼리스토", "ttbt",
        "눈물을 마시는 새", "김창한", "뉴스테이트", "new state mobile", "new state",
        "striking distance", "스트라이킹 디스턴스", "subnautica", "서브노티카", "unknown worlds", "언노운월즈",
        "인조이", "inzoi", "다크앤다커 모바일", "어비스 오브 던전", "다크앤다커모바일", "Abyss of", "딩컴", "서브노티카",
        "테라", "디펜스 더비", "inZOI", "마이 리틀 퍼피", "팰월드 모바일", "BLACK BUDGET", "블랙버짓", "블라인드스팟", "발러", "블루홀",
        "라이징윙스", "드림모션", "렐루", "몬트리올", "네온 자이언트", "5민랩", "5minlab", "띵스플로우", "플라이웨이"
    ],
    "시프트업": [
        "시프트업", "shift up", "스텔라 블레이드", "stellar blade", "스텔블",
        "데스티니 차일드", "destiny child", "니케", "승리의 여신: 니케", "nikke", "김형태",
        "프로젝트 스피릿", "스피릿", "데차", "스피릿", "프로젝트 위치스"
    ],
    "스마일게이트": [
        "스마일게이트", "smilegate",
        "로스트아크", "lost ark", "로아", "에픽세븐", "epic seven", "수퍼크리에이티브", "슈퍼크리에이티브",
        "크로스파이어", "crossfire", "cf", "cfx", "소울워커", "soulworker", "스토브", "stove", "테일즈런너",
        "크로스 파이어", "로스트 아크", "에픽 세븐", "스토브", "로드나인", "카오스 제로 나이트메어", "카제나", "이클립스"
    ],
    "ncsoft": [
        "ncsoft", "nc", "엔씨소프트", "엔씨", "리니지", "lineage", "리니지m", "lineage m", "리니지w", "lineage w",
        "아이온", "aion", "tl", "throne and liberty",
        "유니버스", "universe", "퍼플", "purple", "퓨저", "쓰론 앤 리버티", "티엘", "호연", "배틀크러쉬"
    ],
    "넷마블": [
        "넷마블", "netmarble", "에프앤씨", "F&C",
        "세븐나이츠", "seven knights", "세나", "나 혼자만 레벨업", "나혼렙", "solo leveling",
        "a3", "a3 still alive", "모모", "제2의 나라", "7ds", "일곱 개의 대죄", "칠대죄",
        "seven deadly sins", "bts island", "퓨처파이트", "marvel future fight", "마퓨파",
        "오버프라임", "킹오파", "the king of fighters", "뱀피르", "vampire",
        "쿵야", "레이븐", "아스달", "킹 아서", "왕좌의 게임", "몬길", "코웨이"
    ],
    "펄어비스": [
        "펄어비스", "pearl abyss", "검은사막", "black desert", "bdo", "검은사막 모바일", "black desert mobile",
        "붉은사막", "crimson desert", "도깨비", "dokev", "플랜8", "plan 8"
    ],
    "컴투스": [
        "컴투스", "com2us", "컴투스홀딩스", "com2us holdings", "서머너즈 워", "summoners war",
        "크로니클", "summoners war: chronicles", "스타라이트", "starseed",
        "mlb 9 innings", "컴투버스", "미니게임천국", "더 스트라이트"
    ],
    "네오위즈": [
        "네오위즈", "neowiz", "네오위즈게임즈", "브라운더스트", "brown dust",
        "디제이맥스", "djmax", "스컬", "피의거짓", "안녕서울", "영웅전설"
    ],
    "카카오게임즈": [
        "카카오게임즈", "kakao games", "크로노 오디세이", "chrono odyssey", "우마무스메", "uma musume",
        "가디언 테일즈", "guardian tales", "에버소울", "eversoul", "카겜", "말딸",
        "오딘", "아레스", "롬", "스톰게이트", "엑스엘", "라이온하트"
    ],
    "데브시스터즈": [
        "데브시스터즈", "cookierun", "쿠키런", "쿠키런 킹덤", "오븐브레이크"
    ],
    "위메이드": [
        "위메이드", "wemade", "미르", "전기아이피", "나이트 크로우", "위믹스"
    ]
}

exclude_keywords = [
    "마브렉스", "포커", "맞고", "골프", "오늘의 주요일정", "msi", "야구", "농구", "축구",
    "카지노", "도박", "경마", "경륜", "룰렛", "nft", "가상자산", "암호화폐", "코인", "챔피언십", "FSL"
]

update_keywords = [
    "출시", "론칭", "런칭", "발표", "공개", "업데이트", "데모", "신작", "신규", "베타",
    "얼리", "cbt", "obt", "사전", "등록", "예약"
]

industry_keywords = [
    "파업", "한한령", "규제", "판매량", "개최", "모집", "홍콩", "대만", "게임 업계", "매출", "시장", "주가", "m&a"
]

news_data = {k: [] for k in game_companies}
news_data["신작/업데이트"] = []
news_data["업계"] = []
news_data["기타"] = []

seen_titles = []
duplicate_candidates = []

def is_similar_cosine(new_title):
    if not seen_titles:
        return False
    vectorizer = TfidfVectorizer().fit(seen_titles + [new_title])
    vectors = vectorizer.transform(seen_titles + [new_title])
    similarities = cosine_similarity(vectors[-1], vectors[:-1])
    return max(similarities[0]) >= 0.5

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
        # exclude_keywords 뉴스도 low priority로 분류
        if any(x in title for x in exclude_keywords):
            duplicate_candidates.append(f"{title}<br>🔗 <a href='{link}'>{link}</a>")
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
                news_data["신작/업데이트"].append(line)
            elif any(k in title for k in industry_keywords):
                news_data["업계"].append(line)
            else:
                news_data["기타"].append(line)

output_lines = ["<hr>"]
for section in list(game_companies.keys()) + ["신작/업데이트", "업계", "기타"]:
    if news_data[section]:
        output_lines.append(f"<h2>🕹️ {section}</h2>")
        for item in news_data[section]:
            output_lines.append(f"<p>{item}</p><br>")
        output_lines.append("<hr>")

# 중복 / low priority 뉴스 표시
if duplicate_candidates:
    output_lines.append(f"<h2>⚠️ 중복 / low priority</h2>")
    for item in duplicate_candidates:
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

save_path = r"C:\\Users\\dahyijung\\OneDrive - Tencent Overseas\\tencentoverseas - News clipping - backup"
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
        "v4", "프라시아 전기", "프라시아", "워헤이븐", "warhaven", "베일드 엑스퍼트", "veiled experts", "낙원", "데이브", "데더다", "nakwon", 
        "민트로켓", "니트로", "프로젝트 오버킬", "엠바크"
    ],
    "크래프톤": [
        "크래프톤", "krafton", "펍지", "pubg", "pubg studios", "pubg mobile", "화평정영", "bgmi", "배그", "배틀그라운드",
        "더 칼리스토 프로토콜", "the callisto protocol", "칼리스토", "ttbt",
        "눈물을 마시는 새", "김창한", "뉴스테이트", "new state mobile", "new state",
        "striking distance", "스트라이킹 디스턴스", "subnautica", "서브노티카", "unknown worlds", "언노운월즈",
        "인조이", "inzoi", "다크앤다커 모바일", "어비스 오브 던전", "다크앤다커모바일", "Abyss of", "딩컴", "서브노티카",
        "테라", "디펜스 더비", "inZOI", "마이 리틀 퍼피", "팰월드 모바일", "BLACK BUDGET", "블랙버짓", "블라인드스팟", "발러", "블루홀",
        "라이징윙스", "드림모션", "렐루", "몬트리올", "네온 자이언트", "5민랩", "5minlab", "띵스플로우", "플라이웨이"
    ],
    "시프트업": [
        "시프트업", "shift up", "스텔라 블레이드", "stellar blade", "스텔블",
        "데스티니 차일드", "destiny child", "니케", "승리의 여신: 니케", "nikke", "김형태",
        "프로젝트 스피릿", "스피릿", "데차", "스피릿", "프로젝트 위치스"
    ],
    "스마일게이트": [
        "스마일게이트", "smilegate",
        "로스트아크", "lost ark", "로아", "에픽세븐", "epic seven", "수퍼크리에이티브", "슈퍼크리에이티브",
        "크로스파이어", "crossfire", "cf", "cfx", "소울워커", "soulworker", "스토브", "stove", "테일즈런너",
        "크로스 파이어", "로스트 아크", "에픽 세븐", "스토브", "로드나인", "카오스 제로 나이트메어", "카제나", "이클립스"
    ],
    "ncsoft": [
        "ncsoft", "nc", "엔씨소프트", "엔씨", "리니지", "lineage", "리니지m", "lineage m", "리니지w", "lineage w",
        "아이온", "aion", "tl", "throne and liberty",
        "유니버스", "universe", "퍼플", "purple", "퓨저", "쓰론 앤 리버티", "티엘", "호연", "배틀크러쉬"
    ],
    "넷마블": [
        "넷마블", "netmarble", "에프앤씨", "F&C",
        "세븐나이츠", "seven knights", "세나", "나 혼자만 레벨업", "나혼렙", "solo leveling",
        "a3", "a3 still alive", "모모", "제2의 나라", "7ds", "일곱 개의 대죄", "칠대죄",
        "seven deadly sins", "bts island", "퓨처파이트", "marvel future fight", "마퓨파",
        "오버프라임", "킹오파", "the king of fighters", "뱀피르", "vampire",
        "쿵야", "레이븐", "아스달", "킹 아서", "왕좌의 게임", "몬길", "코웨이"
    ],
    "펄어비스": [
        "펄어비스", "pearl abyss", "검은사막", "black desert", "bdo", "검은사막 모바일", "black desert mobile",
        "붉은사막", "crimson desert", "도깨비", "dokev", "플랜8", "plan 8"
    ],
    "컴투스": [
        "컴투스", "com2us", "컴투스홀딩스", "com2us holdings", "서머너즈 워", "summoners war",
        "크로니클", "summoners war: chronicles", "스타라이트", "starseed",
        "mlb 9 innings", "컴투버스", "미니게임천국", "더 스트라이트"
    ],
    "네오위즈": [
        "네오위즈", "neowiz", "네오위즈게임즈", "브라운더스트", "brown dust",
        "디제이맥스", "djmax", "스컬", "피의거짓", "안녕서울", "영웅전설"
    ],
    "카카오게임즈": [
        "카카오게임즈", "kakao games", "크로노 오디세이", "chrono odyssey", "우마무스메", "uma musume",
        "가디언 테일즈", "guardian tales", "에버소울", "eversoul", "카겜", "말딸",
        "오딘", "아레스", "롬", "스톰게이트", "엑스엘", "라이온하트"
    ],
    "데브시스터즈": [
        "데브시스터즈", "cookierun", "쿠키런", "쿠키런 킹덤", "오븐브레이크"
    ],
    "위메이드": [
        "위메이드", "wemade", "미르", "전기아이피", "나이트 크로우", "위믹스"
    ]
}

exclude_keywords = [
    "마브렉스", "포커", "맞고", "골프", "오늘의 주요일정", "msi",
    "카지노", "도박", "경마", "경륜", "룰렛", "nft", "가상자산", "암호화폐", "코인", "챔피언십", "FSL"
]

update_keywords = [
    "출시", "론칭", "런칭", "발표", "공개", "업데이트", "데모", "신작", "신규", "베타",
    "얼리", "cbt", "obt", "사전", "등록", "예약"
]

industry_keywords = [
    "파업", "한한령", "규제", "판매량", "개최", "모집", "홍콩", "대만", "게임 업계", "매출", "시장", "주가", "m&a"
]

news_data = {k: [] for k in game_companies}
news_data["신작/업데이트"] = []
news_data["업계"] = []
news_data["기타"] = []

seen_titles = []
duplicate_candidates = []

def is_similar_cosine(new_title):
    if not seen_titles:
        return False
    vectorizer = TfidfVectorizer().fit(seen_titles + [new_title])
    vectors = vectorizer.transform(seen_titles + [new_title])
    similarities = cosine_similarity(vectors[-1], vectors[:-1])
    return max(similarities[0]) >= 0.5

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
        # exclude_keywords 뉴스도 low priority로 분류
        if any(x.lower() in title.lower() for x in exclude_keywords):
            duplicate_candidates.append(f"{title}<br>🔗 <a href='{link}'>{link}</a>")
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
                news_data["신작/업데이트"].append(line)
            elif any(k in title for k in industry_keywords):
                news_data["업계"].append(line)
            else:
                news_data["기타"].append(line)

output_lines = ["<hr>"]
for section in list(game_companies.keys()) + ["신작/업데이트", "업계", "기타"]:
    if news_data[section]:
        output_lines.append(f"<h2>🕹️ {section}</h2>")
        for item in news_data[section]:
            output_lines.append(f"<p>{item}</p><br>")
        output_lines.append("<hr>")

# 중복 / low priority 뉴스 표시
if duplicate_candidates:
    output_lines.append(f"<h2>⚠️ 중복 / low priority</h2>")
    for item in duplicate_candidates:
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
