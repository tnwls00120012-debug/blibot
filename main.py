import json
import os
import random
import threading
import time
from datetime import datetime, timedelta
import websocket
import requests
import tkinter as tk
from tkinter import messagebox, scrolledtext

CONFIG_FILE = "config.txt"
SPECIAL_FILE = "special_welcome.json"
DATA_FILE = "users.json"
SONGS_FILE = "songs.json"
ROULETTE_FILE = "roulette.json"
ROULETTE_SAVED_FILE = "roulette_saved.json"
MISSION_FILE = "missions.json"
BLIDUNGI_FILE = "blidungi.json"
CHANNEL_ID = "41532275"

# 회장님 고정 닉네임
CHAIRMAN_NICK = "슥삭이"

DEFAULT_CONFIG = """\
# ────────────────────────────────────────────
#  블리 ♡ 설정 파일
# ────────────────────────────────────────────

# 채널 설정
DJ_USER_ID = 
DJ_NICK = 
CHANNEL_ID = 

# 도네이션 기준 스푼 수
DONATION_MIN = 100

# 입장 환영 메시지
WELCOME_MSG = 어서오세요! 💕 {nickname}님 정블리 방송에 오신 걸 환영해요~

# 스푼 반응 메시지
SPOON_REACTIONS = 💕 감사해요!!, 🎉 와앙!! 스푼 감사!!, 💖 블리가 행복해졌어요~!

# 룰렛 스푼 설정
ROULETTE_SPOON = 30
ROULETTE_SPOON_TYPE = 비행기

# 복권 당첨 포인트 설정
LOTTERY_EXP_3 = 5000
LOTTERY_EXP_2 = 1000
LOTTERY_EXP_1 = 100
LOTTERY_EXP_0 = 1

# 포인트 획득 설정
ATTENDANCE_POINT = 30

# EXP 획득 설정
CHAT_EXP = 10
LIKE_EXP = 5

# 레벨업 포인트 기준 (레벨 x 설정값)
LEVEL_POINT = 100

# 타이머 멘트 간격 (분)
TIMER_INTERVAL = 10

# 타이머 멘트 (쉼표로 구분)
TIMER_MESSAGES = 💕 블리 생일은 OO월 OO일이에요!, 🎉 지금 방송 중이에요~ 놀러오세요!
"""

DEFAULT_ROULETTE = [
    {"item": "전화데이트 5분", "weight": 0.3},
    {"item": "아봉 1분", "weight": 2.7},
    {"item": "커플프사 1일", "weight": 1.1},
    {"item": "지정프사로 바꿔주기", "weight": 0.8},
    {"item": "짧은 손편지 사진찍어 보내주기", "weight": 0.2},
    {"item": "술방송", "weight": 0.5},
    {"item": "웅옹앵체 1분", "weight": 1.7},
    {"item": "정블리한테 팬보드 써주기", "weight": 2.8},
    {"item": "외국어금지 1분", "weight": 3.4},
    {"item": "실깍 1000", "weight": 3.7},
    {"item": "실드 500", "weight": 3.6},
    {"item": "명령어 추가하기", "weight": 3.9},
    {"item": "디제이가 팬보드 쓰러가기", "weight": 1.4},
    {"item": "말끝마다 ~요옹 붙이기", "weight": 2.1},
    {"item": "정블리에게 장미꽃 한송이 주기", "weight": 4.0},
    {"item": "물 3모금 마시기", "weight": 2.4},
    {"item": "냥체 1분", "weight": 3.1},
    {"item": "방제변경권 20분", "weight": 1.9},
    {"item": "역닉변이지롱~ (방어스푼 100스푼)", "weight": 2.2},
    {"item": "혀봉 1분", "weight": 2.6},
    {"item": "블리에게 보이스카드 보내기", "weight": 1.3},
    {"item": "원하는체 1분", "weight": 2.4},
    {"item": "애교멘트 1번", "weight": 2.5},
    {"item": "산책방송하기", "weight": 0.4},
    {"item": "계단오르기 방송", "weight": 0.6},
    {"item": "공지사항 하루 변경권", "weight": 1.0},
    {"item": "30분 연장하기", "weight": 0.5},
    {"item": "디제이가 보이스 카드 전하러 가기", "weight": 0.9},
    {"item": "정블리 하루 닉변", "weight": 0.8},
    {"item": "배통통 5번 들려주기", "weight": 0.7},
    {"item": "동요 1개 부르기", "weight": 3.1},
    {"item": "1분동안 20스푼으로 바꾸기", "weight": 2.2},
    {"item": "리방", "weight": 1.5},
    {"item": "방종", "weight": 0.1},
    {"item": "코노방송", "weight": 0.4},
    {"item": "노래 캐스트권", "weight": 0.1},
    {"item": "치킨 기프트콘", "weight": 0.5},
    {"item": "스쿼트 10회", "weight": 3.6},
    {"item": "정블리의 사랑♥", "weight": 8.0},
    {"item": "블리방 플랜 구독하기!", "weight": 3.3},
    {"item": "실추/실깍 2배 이벤트!!!!!", "weight": 1.8},
    {"item": "1분동안 영어만 사용하기", "weight": 1.6},
    {"item": "업로드된 노래캐스트 중에 하나 틀어주기", "weight": 0.7},
    {"item": "입장멘트 추가하기", "weight": 2.8},
    {"item": "커피 기프티콘", "weight": 0.9},
    {"item": "꽝이지롱~ 메롱!", "weight": 4.0},
    {"item": "깃발 게이지 채워주기♥", "weight": 0.5},
    {"item": "청취자 닉네임으로 엔행시 해주기", "weight": 1.0},
    {"item": "사투리 랜덤 1분 (경상/전라/충청/강원/서울)", "weight": 1.0},
    {"item": "팬이 정한 단어 금지어 1분", "weight": 1.0},
    {"item": "닉네임 불러주기 타임 30초", "weight": 1.0},
    {"item": "스트레칭 30초", "weight": 1.2},
    {"item": "룰렛 한번 더 당첨★", "weight": 0.8},
    {"item": "점심메뉴 하나 골라주기!", "weight": 1.3},
    {"item": "프로필사진 그림 그려주기", "weight": 1.1},
    {"item": "복권 10장", "weight": 1.0},
]

# 스푼 룰렛 티어 (한 번에 쏜 스푼 기준)
SPOON_ROULETTE_TIERS = [
    (20000, 50), (10000, 30), (7000, 20), (5000, 15),
    (3000, 10), (1000, 5), (600, 2), (300, 1),
]

SHOP_ITEMS = [
    {"name": "신청곡하이패스", "price": 2000,  "emoji": "🎶", "desc": "내가 신청한 노래 바로 듣기"},
    {"name": "룰렛항목교체권", "price": 3000,  "emoji": "✨", "desc": "룰렛 당첨 목록 하나 제거"},
    {"name": "닉네임칭호",     "price": 5000,  "emoji": "🛍️", "desc": "하루동안 특수 칭호 부여"},
    {"name": "일일매니저",     "price": 7000,  "emoji": "🛎️", "desc": "하루 동안 매니저 권한 부여"},
    {"name": "박제편지신청",   "price": 8000,  "emoji": "💌", "desc": "정성 담긴 박제 편지 작성"},
    {"name": "노래",           "price": 10000, "emoji": "🎸", "desc": "DJ가 라이브 한 곡 부르기"},
    {"name": "모닝콜",         "price": 15000, "emoji": "📞", "desc": "DJ의 ASMR 모닝콜 녹음본"},
    {"name": "단독박제",       "price": 20000, "emoji": "📝", "desc": "나만의 단독박제 만들어주기"},
    {"name": "고민상담",       "price": 50000, "emoji": "🔋", "desc": "30분 1:1 고민 상담"},
]

AUTO_RESPONSES = {
    "졸려":       "😴 졸려?\n지금 자면…\n나 삐질건데?\n끝까지 있어줘💖",
    "졸립":       "😴 졸려?\n지금 자면…\n나 삐질건데?\n끝까지 있어줘💖",
    "사랑해":     "💖 헉🙈\n…나도 이미 너에게 넘어갔는데??\n나도 알라뷰😘",
    "사랑합니다": "💖 헉🙈\n…나도 이미 너에게 넘어갔는데??\n나도 알라뷰😘",
}

# ──────────────────────────────────────────────────────────
# 블리둥이
# ──────────────────────────────────────────────────────────
def load_blidungi():
    if os.path.exists(BLIDUNGI_FILE):
        with open(BLIDUNGI_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_blidungi(lst):
    with open(BLIDUNGI_FILE, "w", encoding="utf-8") as f:
        json.dump(lst, f, ensure_ascii=False, indent=4)

def is_blidungi(nickname):
    return nickname in load_blidungi()

# ──────────────────────────────────────────────────────────
# 설정 파일
# ──────────────────────────────────────────────────────────
def load_config():
    if not os.path.exists(CONFIG_FILE):
        return None
    cfg = {}
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, val = line.partition("=")
                cfg[key.strip()] = val.strip()
    return cfg

def save_config_value(key, value):
    if not os.path.exists(CONFIG_FILE):
        return
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        for line in lines:
            if line.strip().startswith(key):
                f.write(f"{key} = {value}\n")
            else:
                f.write(line)

def create_default_config():
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write(DEFAULT_CONFIG)

# ──────────────────────────────────────────────────────────
# 데이터 유틸
# ──────────────────────────────────────────────────────────
def save_data(data):
    tmp_file = DATA_FILE + ".tmp"
    try:
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        os.replace(tmp_file, DATA_FILE)
    except Exception as e:
        print(f"⚠️ 데이터 저장 오류: {e}")

def backup_data():
    if not os.path.exists(DATA_FILE):
        return
    backup_dir = "backup"
    os.makedirs(backup_dir, exist_ok=True)
    backup_file = os.path.join(backup_dir, f"users_{datetime.now().strftime('%Y%m%d')}.json")
    if not os.path.exists(backup_file):
        import shutil
        shutil.copy2(DATA_FILE, backup_file)
        backups = sorted(os.listdir(backup_dir))
        while len(backups) > 7:
            os.remove(os.path.join(backup_dir, backups.pop(0)))
        print(f"💾 데이터 백업 완료: {backup_file}")

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            print("⚠️ users.json 손상됨! 백업에서 복구 시도...")
            backup_dir = "backup"
            if os.path.exists(backup_dir):
                backups = sorted(os.listdir(backup_dir), reverse=True)
                for b in backups:
                    try:
                        with open(os.path.join(backup_dir, b), "r", encoding="utf-8") as f:
                            data = json.load(f)
                        print(f"✅ 백업 복구 성공: {b}")
                        return data
                    except:
                        continue
            print("❌ 복구 실패! 빈 데이터로 시작합니다.")
            return {}
    return {}

def load_roulette():
    if os.path.exists(ROULETTE_FILE):
        with open(ROULETTE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    with open(ROULETTE_FILE, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_ROULETTE, f, ensure_ascii=False, indent=4)
    return DEFAULT_ROULETTE

def save_roulette(items):
    with open(ROULETTE_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=4)

def load_roulette_saved():
    if os.path.exists(ROULETTE_SAVED_FILE):
        with open(ROULETTE_SAVED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_roulette_saved(saved):
    with open(ROULETTE_SAVED_FILE, "w", encoding="utf-8") as f:
        json.dump(saved, f, ensure_ascii=False, indent=4)

def load_songs():
    if os.path.exists(SONGS_FILE):
        with open(SONGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_songs(songs):
    with open(SONGS_FILE, "w", encoding="utf-8") as f:
        json.dump(songs, f, ensure_ascii=False, indent=4)

def load_special():
    if os.path.exists(SPECIAL_FILE):
        with open(SPECIAL_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_special(data):
    with open(SPECIAL_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_missions():
    if os.path.exists(MISSION_FILE):
        with open(MISSION_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_missions(missions):
    with open(MISSION_FILE, "w", encoding="utf-8") as f:
        json.dump(missions, f, ensure_ascii=False, indent=4)

# ──────────────────────────────────────────────────────────
# 레벨 / 칭호
# ──────────────────────────────────────────────────────────
def get_next_level_point(level):
    return level * int(cfg.get("LEVEL_POINT", 100))

def get_all_achieved_titles(user):
    """유저가 달성한 모든 칭호 목록 반환"""
    attendance       = user.get("attendance", 0)
    spoon_total      = user.get("spoon_total", 0)
    like_count       = user.get("like_count", 0)
    chat_count       = user.get("chat_count", 0)
    mission_count    = user.get("mission_count", 0)
    roulette_count   = user.get("roulette_count", 0)
    song_req_count   = user.get("song_request_count", 0)
    consecutive_days = user.get("consecutive_days", 0)
    level            = user.get("level", 1)

    titles = ["🐣 뉴비"]

    if level >= 11 and attendance >= 10:
        titles.append("🌱 스며드는 중")
    if level >= 31 and attendance >= 30 and spoon_total >= 1000 and like_count >= 50:
        titles.append("💖 단골")
    if level >= 101 and attendance >= 100 and spoon_total >= 3000 and like_count >= 100:
        titles.append("💎 블리식구")

    if chat_count >= 30000:    titles.append("🔥 채팅왕")
    if mission_count >= 10:    titles.append("🎯 미션왕")
    if song_req_count >= 30:   titles.append("🎤 신청곡 장인")
    if roulette_count >= 50:   titles.append("🎲 룰렛 중독자")
    if attendance >= 100:      titles.append("✅ 출석왕")
    if consecutive_days >= 30: titles.append("🏆 개근상")
    if consecutive_days >= 10: titles.append("💖 자주 오는 너")
    if like_count >= 3000:     titles.append("🫶 마음 주는 너")
    if spoon_total >= 30000:   titles.append("💌 내 편인 너")
    if is_blidungi(user.get("nickname", "")):
        titles.append("😍 넌 내 사람")

    for t in user.get("extra_titles", []):
        if t not in titles:
            titles.append(t)

    return titles

def get_title(user):
    """칭호 우선순위: 수동칭호 > 회장님 > 장착칭호 > 자동칭호"""
    manual_title = user.get("manual_title", "")
    if manual_title:
        return manual_title

    if user.get("nickname", "") == CHAIRMAN_NICK:
        return "👑 회장님"

    equipped = user.get("equipped_title", "")
    if equipped:
        return equipped

    chat_count       = user.get("chat_count", 0)
    attendance       = user.get("attendance", 0)
    spoon_total      = user.get("spoon_total", 0)
    like_count       = user.get("like_count", 0)
    mission_count    = user.get("mission_count", 0)
    roulette_count   = user.get("roulette_count", 0)
    song_req_count   = user.get("song_request_count", 0)
    consecutive_days = user.get("consecutive_days", 0)
    level            = user.get("level", 1)

    if chat_count >= 30000:    return "🔥 채팅왕"
    if mission_count >= 10:    return "🎯 미션왕"
    if song_req_count >= 30:   return "🎤 신청곡 장인"
    if roulette_count >= 50:   return "🎲 룰렛 중독자"
    if attendance >= 100:      return "✅ 출석왕"
    if consecutive_days >= 10: return "💖 자주 오는 너"
    if like_count >= 3000:     return "🫶 마음 주는 너"
    if spoon_total >= 30000:   return "💌 내 편인 너"

    if level >= 101 and attendance >= 100 and spoon_total >= 3000 and like_count >= 100:
        return "💎 블리식구"
    if level >= 31 and attendance >= 30 and spoon_total >= 1000 and like_count >= 50:
        return "💖 단골"
    if level >= 11 and attendance >= 10:
        return "🌱 스며드는 중"

    return "🐣 뉴비"

def check_special_titles(ws, user, nickname):
    achieved = user.get("achieved_titles", [])

    checks = [
        (user.get("chat_count", 0) >= 30000,        "채팅왕",      "🔥 채팅왕"),
        (user.get("mission_count", 0) >= 10,         "미션왕",      "🎯 미션왕"),
        (user.get("song_request_count", 0) >= 30,    "신청곡 장인", "🎤 신청곡 장인"),
        (user.get("roulette_count", 0) >= 50,        "룰렛 중독자", "🎲 룰렛 중독자"),
        (user.get("attendance", 0) >= 100,           "출석왕",      "✅ 출석왕"),
        (user.get("consecutive_days", 0) >= 30,      "개근상",      "🏆 개근상"),
        (user.get("consecutive_days", 0) >= 10,      "자주 오는 너","💖 자주 오는 너"),
        (user.get("like_count", 0) >= 3000,          "마음 주는 너","🫶 마음 주는 너"),
        (user.get("spoon_total", 0) >= 30000,        "내 편인 너",  "💌 내 편인 너"),
    ]

    for condition, key, title in checks:
        if condition and key not in achieved:
            achieved.append(key)
            user["achieved_titles"] = achieved
            send_chat(ws, f"🎊 {nickname}님 새 칭호 달성! [{title}]")
            break

def get_or_create_user(user_id, nickname, data):
    if user_id not in data:
        data[user_id] = {
            "nickname": nickname, "level": 1, "exp": 0, "point": 0,
            "attendance": 0, "consecutive_days": 0, "last_attendance_date": "",
            "chat_count": 0, "chat_count_today": 0,
            "like_count": 0, "like_count_today": 0,
            "lottery": 0, "spoon_total": 0, "spoon_today": 0,
            "attended_sessions": [], "mission_count": 0, "roulette_count": 0,
            "song_request_count": 0, "join_count": 0,
            "new_today": datetime.now().strftime("%Y-%m-%d"),
            "manual_title": "", "achieved_titles": [],
            "equipped_title": "",
            "extra_titles": [],
            "flag_count": 0,
            "event_win_count": 0,
        }
        return data[user_id], True
    data[user_id]["nickname"] = nickname
    return data[user_id], False

def process_levelup(user):
    msg = ""
    while user["point"] >= get_next_level_point(user["level"]):
        user["point"] -= get_next_level_point(user["level"])
        user["level"] += 1
        msg += f"\n🎊 레벨업! → Lv.{user['level']} ({get_title(user)})"
        msg += f"\n💝 호감도 상승! 정블리가 더 기억해버렸어요...♥️"
    return msg

# ──────────────────────────────────────────────────────────
# 채널 검색 / 로그인
# ──────────────────────────────────────────────────────────
def find_channel_by_nick(nick, log_func=print):
    try:
        nick = nick.lstrip("@").strip()
        url = f"https://www.spooncast.net/api/v1/search/user?query={nick}&page=1&page_size=10"
        headers = {"User-Agent": "Mozilla/5.0", "Origin": "https://www.spooncast.net", "Referer": "https://www.spooncast.net"}
        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()
        users = data.get("results", []) or data.get("data", []) or []
        for user in users:
            u_nick = user.get("unique_id", "") or user.get("nick", "")
            if u_nick.lower() == nick.lower():
                cast = user.get("cast", {}) or {}
                cast_id = cast.get("id") or user.get("cast_id")
                if cast_id:
                    log_func(f"✅ 방송 찾음! 채널 ID: {cast_id}")
                    return str(cast_id)
        url2 = f"https://www.spooncast.net/api/v1/search/cast?query={nick}&page=1&page_size=10"
        res2 = requests.get(url2, headers=headers, timeout=10)
        data2 = res2.json()
        casts = data2.get("results", []) or data2.get("data", []) or []
        for cast in casts:
            dj = cast.get("dj", {}) or {}
            if dj.get("unique_id", "").lower() == nick.lower():
                cast_id = cast.get("id")
                if cast_id:
                    log_func(f"✅ 방송 찾음! 채널 ID: {cast_id}")
                    return str(cast_id)
    except Exception as e:
        log_func(f"⚠️ 채널 검색 오류: {e}")
    return None

def spoon_auto_login(spoon_id, spoon_pw, log_func=print):
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
    except ImportError:
        log_func("❌ selenium/webdriver-manager 설치 필요!")
        return None

    log_func("🌐 브라우저 실행 중...")
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--window-size=500,700")
    profile_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chrome_profile")
    os.makedirs(profile_dir, exist_ok=True)
    options.add_argument(f"--user-data-dir={profile_dir}")
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        log_func(f"❌ 브라우저 실행 오류: {e}")
        return None

    ws_url = None
    try:
        log_func("⏳ Chrome에서 로그인해주세요!")
        driver.get("https://www.spooncast.net/kr")
        time.sleep(3)
        log_func("🔐 로그인 대기 중... (애플/카카오/구글 로그인 해주세요)")

        for _ in range(180):
            time.sleep(1)
            try:
                cookies = driver.get_cookies()
                cookie_names = [c.get("name", "") for c in cookies]
                cookie_values = [c.get("value", "") for c in cookies]
                logged_in = any(name in ["jwt", "access_token", "Authorization", "spoon_token", "token"] for name in cookie_names) or any(val.startswith("eyJ") and len(val) > 50 for val in cookie_values)
                if logged_in:
                    log_func("✅ 로그인 감지! 방송으로 이동 중...")
                    time.sleep(2)
                    break
                token_check = driver.execute_script("""
                    try {
                        for(let k of Object.keys(localStorage)) {
                            let v = localStorage.getItem(k);
                            if(v && v.startsWith('eyJ') && v.length > 50) return true;
                            try { let j = JSON.parse(v); if(j && (j.token || j.access_token || j.jwt)) return true; } catch(e) {}
                        }
                    } catch(e) {}
                    return false;
                """)
                if token_check:
                    log_func("✅ 로그인 감지! 방송으로 이동 중...")
                    time.sleep(2)
                    break
            except:
                pass
        else:
            log_func("❌ 시간 초과! 다시 시도해주세요.")
            driver.quit()
            return None

        global CHANNEL_ID
        channel_id = cfg.get("CHANNEL_ID", CHANNEL_ID)
        dj_nick = cfg.get("DJ_NICK", "").strip()
        if dj_nick:
            log_func(f"🔍 @{dj_nick} 방송 검색 중...")
            found_id = find_channel_by_nick(dj_nick, log_func)
            if found_id:
                channel_id = found_id
                CHANNEL_ID = channel_id
                cfg["CHANNEL_ID"] = channel_id
                save_config_value("CHANNEL_ID", channel_id)
            else:
                log_func(f"⚠️ 방송 검색 실패! 저장된 채널 ID 사용: {channel_id}")

        driver.get(f"https://www.spooncast.net/kr/live/{channel_id}")
        time.sleep(5)

        for _ in range(30):
            time.sleep(1)
            try:
                if "kr/live" in driver.current_url and "spoon" in driver.page_source.lower():
                    log_func("✅ 방송 화면 감지! 토큰 추출 시작...")
                    time.sleep(3)
                    break
            except:
                pass
        else:
            log_func("❌ 방송 진입 실패!")
            driver.quit()
            return None

        import re
        for _ in range(30):
            time.sleep(1)
            try:
                perf_logs = driver.get_log("performance")
                for entry in perf_logs:
                    try:
                        msg_data = json.loads(entry.get("message", "{}"))
                        params = msg_data.get("message", {}).get("params", {})
                        url = params.get("url", "") or params.get("request", {}).get("url", "")
                        if "wala.spooncast" in url and "token=" in url:
                            ws_url = url
                            break
                        if "wala.spooncast" in str(params) and "token=" in str(params):
                            m = re.search(r'wss://[^\s"\'<>{}]+token=[^\s"\'<>{}]+', str(params))
                            if m:
                                ws_url = m.group(0)
                                break
                    except:
                        msg = entry.get("message", "")
                        if "wala.spooncast" in msg and "token=" in msg:
                            m = re.search(r'wss://[^\s"\'\\<>]+token=[^\s"\'\\<>]+', msg)
                            if m:
                                ws_url = m.group(0).strip('"\'\\}')
                                break
                if ws_url:
                    break
            except:
                pass

            try:
                token = driver.execute_script("""
                    try {
                        for(let k of Object.keys(localStorage)) {
                            let v = localStorage.getItem(k);
                            if(!v) continue;
                            if(v.startsWith('eyJ')) return v;
                            try {
                                let j = JSON.parse(v);
                                if(j && j.token && j.token.startsWith('eyJ')) return j.token;
                                if(j && j.access_token && j.access_token.startsWith('eyJ')) return j.access_token;
                                if(j && j.jwt && j.jwt.startsWith('eyJ')) return j.jwt;
                            } catch(e) {}
                        }
                        for(let k of Object.keys(sessionStorage)) {
                            let v = sessionStorage.getItem(k);
                            if(!v) continue;
                            if(v.startsWith('eyJ')) return v;
                        }
                    } catch(e) {}
                    return null;
                """)
                if token and len(token) > 50:
                    ws_url = f"wss://kr-wala.spooncast.net/ws?token={token}"
                    log_func(f"✅ 토큰 추출 성공!")
                    break
            except:
                pass

        if ws_url:
            log_func("✅ 웹소켓 토큰 추출 성공!")
        else:
            log_func("⚠️ 자동 추출 실패 → F12 > Network > Socket 탭에서 wss:// 주소를 복사해주세요")

    except Exception as e:
        log_func(f"❌ 오류 발생: {e}")
    finally:
        try:
            driver.quit()
        except:
            pass

    return ws_url

# ──────────────────────────────────────────────────────────
# BGM / TTS
# ──────────────────────────────────────────────────────────
def load_bgm_map():
    bgm_dir = "songs/bgm"
    os.makedirs(bgm_dir, exist_ok=True)
    bgm_map = {}
    if os.path.exists(bgm_dir):
        for f in os.listdir(bgm_dir):
            if f.endswith(".mp3"):
                name = os.path.splitext(f)[0]
                bgm_map[name] = os.path.join(bgm_dir, f)
    return bgm_map

def play_bgm(spoon_type):
    bgm_map = load_bgm_map()
    path = bgm_map.get(spoon_type)
    if path and os.path.exists(path):
        def _p():
            try:
                import pygame
                pygame.mixer.init()
                pygame.mixer.music.load(path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
            except Exception as e:
                print(f"🎵 BGM 재생 오류: {e}")
        threading.Thread(target=_p, daemon=True).start()

def play_tts(text):
    def _t():
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"🔊 TTS 오류: {e}")
    threading.Thread(target=_t, daemon=True).start()

# ──────────────────────────────────────────────────────────
# 전역 상태
# ──────────────────────────────────────────────────────────
cfg = {}
ws_app = None
recent_chatters = []
broadcast_start_time = None

def send_chat(ws, text):
    try:
        payload = json.dumps({"command": "MESSAGE", "payload": {"text": text}})
        ws.send(payload)
        print(f"🤖 [블리봇]: {text}")
    except Exception as e:
        print(f"⚠️ 채팅 전송 오류: {e}")

# ──────────────────────────────────────────────────────────
# 복권 (포인트 지급)
# ──────────────────────────────────────────────────────────
def draw_lottery(numbers, winning_numbers):
    matched = len(set(numbers) & set(winning_numbers))
    point_map = {
        3: int(cfg.get("LOTTERY_EXP_3", 5000)),
        2: int(cfg.get("LOTTERY_EXP_2", 1000)),
        1: int(cfg.get("LOTTERY_EXP_1", 100)),
        0: int(cfg.get("LOTTERY_EXP_0", 1)),
    }
    return matched, point_map[matched]

# ──────────────────────────────────────────────────────────
# 룰렛
# ──────────────────────────────────────────────────────────
def do_roulette(ws, u_id, nick, count=1):
    items = load_roulette()
    if not items:
        return
    weights = [it.get("weight", 1) for it in items]
    saved = load_roulette_saved()
    results = []
    for _ in range(count):
        chosen = random.choices(items, weights=weights, k=1)[0]
        saved.append({"user_id": u_id, "nickname": nick, "item": chosen["item"], "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M")})
        results.append(chosen["item"])
    save_roulette_saved(saved)

    user_data = load_data()
    if u_id in user_data:
        user_data[u_id]["roulette_count"] = user_data[u_id].get("roulette_count", 0) + count
        check_special_titles(ws, user_data[u_id], nick)
        save_data(user_data)

    if count == 1:
        send_chat(ws, f"🎡 {nick}님 룰렛 결과: 【{results[0]}】 💾 저장됐어요!")
    else:
        result_text = "\n".join([f"{i+1}. 【{r}】" for i, r in enumerate(results)])
        send_chat(ws, f"🎡 {nick}님 룰렛 {count}회 결과:\n{result_text}\n💾 전부 저장됐어요!")

# ──────────────────────────────────────────────────────────
# 타이머
# ──────────────────────────────────────────────────────────
def start_timer(ws):
    def _timer():
        while True:
            interval = int(cfg.get("TIMER_INTERVAL", 10)) * 60
            time.sleep(interval)
            try:
                messages = cfg.get("TIMER_MESSAGES", "").split(",")
                messages = [m.strip() for m in messages if m.strip()]
                if messages:
                    send_chat(ws, random.choice(messages))
            except Exception as e:
                print(f"⚠️ 타이머 오류: {e}")
    threading.Thread(target=_timer, daemon=True).start()

# ──────────────────────────────────────────────────────────
# 상점
# ──────────────────────────────────────────────────────────
def handle_shop(ws, user_id, nickname, item_name, data):
    item = next((i for i in SHOP_ITEMS if i["name"] == item_name), None)
    if not item:
        return False
    user = data.get(user_id)
    if not user:
        send_chat(ws, f"💕 {nickname}님 먼저 !내정보로 등록해주세요!")
        return True
    price = item["price"]
    if user.get("point", 0) < price:
        send_chat(ws, f"💸 {nickname}님 포인트가 부족해요! (필요: {price:,}P / 보유: {user.get('point', 0):,}P)")
        return True
    user["point"] -= price
    save_data(data)
    send_chat(ws, f"{item['emoji']} {nickname}님이 [{item['name']}]을 구매했어요! (-{price:,}P)\n현재 포인트: {user['point']:,}P")
    send_chat(ws, f"📢 DJ님! {nickname}님이 [{item['name']}] 구매했어요! 확인해주세요 💕")
    return True

# ──────────────────────────────────────────────────────────
# 청취자 명령어
# ──────────────────────────────────────────────────────────
def handle_command(ws, user_id, nickname, message):
    data = load_data()
    user, is_new = get_or_create_user(user_id, nickname, data)
    response = None

    if message == "!내정보":
        spoon_total = user.get("spoon_total", 0)
        spoon_display = f"{spoon_total % 100}/100"
        title = get_title(user)
        dungi_line = "🌟 블리둥이 ✨\n" if is_blidungi(nickname) else ""
        response = (
            f"{nickname}({user_id})님 정보\n"
            f"━━━━━━━━━━━━━━━\n"
            f"{dungi_line}"
            f"👑 칭호: {title}\n"
            f"⭐ 레벨: Lv.{user['level']}\n"
            f"💰 포인트: {user['point']:,}/{get_next_level_point(user['level']):,}\n"
            f"🗓 출석: {user['attendance']}일 (연속: {user.get('consecutive_days', 0)}일)\n"
            f"💬 채팅: {user['chat_count']}회\n"
            f"💖 좋아요: {user.get('like_count', 0)}\n"
            f"🥄 스푼: {spoon_display}\n"
            f"🎟 복권: {user['lottery']}장\n"
            f"━━━━━━━━━━━━━━━"
        )

    elif message == "!내정보 삭제":
        if user_id in data:
            del data[user_id]
            save_data(data)
            send_chat(ws, f"💕 {nickname}님 정보가 삭제됐어요!")
            return

    elif message == "!복권 자동":
        if user["lottery"] < 1:
            response = "🎟️ 보유 복권이 없어요!"
        else:
            count = user["lottery"]
            user["lottery"] = 0
            results = {3: 0, 2: 0, 1: 0, 0: 0}
            total_point = 0
            for _ in range(count):
                winning = random.sample(range(1, 11), 3)
                my_numbers = random.sample(range(1, 11), 3)
                matched, pt = draw_lottery(my_numbers, winning)
                results[matched] += 1
                total_point += pt
            user["point"] = user.get("point", 0) + total_point
            lv_msg = process_levelup(user)
            response = (
                f"🎰 {nickname}님의 복권 {count}장 자동 결과\n"
                f"🥇 1등(3개): {results[3]}회 (+{cfg.get('LOTTERY_EXP_3', 5000)}P)\n"
                f"🥈 2등(2개): {results[2]}회 (+{cfg.get('LOTTERY_EXP_2', 1000)}P)\n"
                f"🥉 3등(1개): {results[1]}회 (+{cfg.get('LOTTERY_EXP_1', 100)}P)\n"
                f"💀 꽝(0개): {results[0]}회 (+{cfg.get('LOTTERY_EXP_0', 1)}P)\n"
                f"🎁 총 획득 포인트: +{total_point:,}P{lv_msg}"
            )

    elif message.startswith("!복권 "):
        parts = message.split()
        if len(parts) == 4:
            try:
                numbers = [int(parts[1]), int(parts[2]), int(parts[3])]
                if all(1 <= n <= 10 for n in numbers) and len(set(numbers)) == 3:
                    if user["lottery"] < 1:
                        response = "🎟️ 보유 복권이 없어요!"
                    else:
                        user["lottery"] -= 1
                        winning = random.sample(range(1, 11), 3)
                        matched, pt = draw_lottery(numbers, winning)
                        user["point"] = user.get("point", 0) + pt
                        lv_msg = process_levelup(user)
                        winning_str = " ".join(map(str, winning))
                        numbers_str = " ".join(map(str, numbers))
                        if matched == 0:   result_msg = f"😅 아쉽게도 꽝입니다. (+{pt}P)"
                        elif matched == 1: result_msg = f"✨ 3등 당첨! (+{pt:,}P)"
                        elif matched == 2: result_msg = f"🎉 2등 당첨! (+{pt:,}P)"
                        else:              result_msg = f"🎰 1등 당첨!! (+{pt:,}P)"
                        response = (
                            f"🎰 {nickname}님의 복권 결과\n"
                            f"🎯 선택: {numbers_str} | 당첨: {winning_str}\n"
                            f"{result_msg}{lv_msg}"
                        )
                else:
                    response = "1~10 사이 숫자 3개를 중복 없이 입력해주세요! 예) !복권 4 8 6"
            except:
                response = "숫자 형식이 잘못됐어요! 예) !복권 4 8 6"

    elif message == "!킵":
        saved = load_roulette_saved()
        my_saved = [s for s in saved if s["user_id"] == user_id]
        if not my_saved:
            response = f"💕 {nickname}님 저장된 룰렛 결과가 없어요!"
        else:
            lines = [f"{i+1}. 【{s['item']}】 ({s['saved_at']})" for i, s in enumerate(my_saved)]
            response = f"💾 {nickname}님의 저장된 룰렛:\n" + "\n".join(lines)

    elif message.startswith("!신청곡 "):
        song = message[5:].strip()
        songs = load_songs()
        songs.append({"nickname": nickname, "song": song, "time": datetime.now().strftime("%H:%M")})
        save_songs(songs)
        user["song_request_count"] = user.get("song_request_count", 0) + 1
        check_special_titles(ws, user, nickname)
        response = f"🎵 {nickname}님의 신청곡 [{song}] 추가됐어요!"

    elif message == "!신청목록":
        songs = load_songs()
        if not songs:
            response = "📋 신청곡 목록이 비어있어요!"
        else:
            lines = [f"{i+1}. {s['nickname']} - {s['song']}" for i, s in enumerate(songs)]
            response = "🎵 신청곡 목록:\n" + "\n".join(lines)

    elif message == "!상점":
        lines = ["🏦 블리네 포인트 상점 🏦\n━━━━━━━━━━━━━━━"]
        for item in SHOP_ITEMS:
            lines.append(f"{item['emoji']} [{item['price']:,}P] !{item['name']}\n   └ {item['desc']}")
        lines.append("━━━━━━━━━━━━━━━")
        response = "\n".join(lines)

    elif message.startswith("!") and any(message[1:] == item["name"] for item in SHOP_ITEMS):
        handle_shop(ws, user_id, nickname, message[1:], data)
        return

    elif message == "!랭킹":
        all_users = load_data()
        sorted_users = sorted(all_users.values(), key=lambda x: (x["level"], x.get("point", 0)), reverse=True)[:5]
        def rank_line(i, u):
            dungi = " 🌟블리둥이" if is_blidungi(u["nickname"]) else ""
            chair = " 👑" if u["nickname"] == CHAIRMAN_NICK else ""
            return f"{i+1}위 {u['nickname']}{dungi}{chair} Lv.{u['level']} ({get_title(u)})"
        lines = [rank_line(i, u) for i, u in enumerate(sorted_users)]
        response = "🏆 레벨 TOP5:\n" + "\n".join(lines)

    elif message == "!채팅랭킹":
        all_users = load_data()
        sorted_users = sorted(all_users.values(), key=lambda x: x.get("chat_count", 0), reverse=True)[:5]
        lines = [f"{i+1}위 {u['nickname']} {u.get('chat_count', 0)}회" for i, u in enumerate(sorted_users)]
        response = "💬 채팅 TOP5:\n" + "\n".join(lines)

    elif message == "!레벨":
        title = get_title(user)
        response = f"⭐ {nickname}님 {title} Lv.{user['level']} | 포인트: {user['point']:,}/{get_next_level_point(user['level']):,}"

    # 칭호 선택 (서든처럼)
    elif message == "!칭호목록":
        titles = get_all_achieved_titles(user)
        equipped = user.get("equipped_title", "")
        lines = []
        for i, t in enumerate(titles):
            mark = " ◀ 장착중" if t == equipped else ""
            lines.append(f"{i+1}. {t}{mark}")
        response = (
                f"🏅 {nickname}님의 달성 칭호\n"
                f"━━━━━━━━━━━━━━━\n"
                + "\n".join(lines) +
                f"\n━━━━━━━━━━━━━━━\n"
                f"💡 !칭호장착 번호 로 바꿔요!"
        )

    elif message.startswith("!칭호장착 "):
        parts2 = message.split()
        if len(parts2) == 2:
            try:
                idx = int(parts2[1]) - 1
                titles = get_all_achieved_titles(user)
                if 0 <= idx < len(titles):
                    user["equipped_title"] = titles[idx]
                    response = f"✨ {nickname}님 칭호 [{titles[idx]}] 장착 완료!"
                else:
                    response = "번호가 잘못됐어요! !칭호목록 으로 확인해주세요."
            except:
                response = "예) !칭호장착 2"
        else:
            response = "예) !칭호장착 2"

    elif message == "!칭호해제":
        user["equipped_title"] = ""
        response = f"🔄 {nickname}님 칭호가 기본값으로 돌아갔어요!"

    elif message == "!도움말":
        response = (
            "📖 명령어 목록\n"
            "━━━━━━━━━━━━━━━\n"
            "!내정보 !내정보 삭제\n"
            "!복권 4 8 6 !복권 자동\n"
            "!킵 !신청곡 제목-가수\n"
            "!신청목록 !상점\n"
            "!랭킹 !채팅랭킹 !레벨\n"
            "!칭호목록 !칭호장착 번호\n"
            "!칭호해제 !도움말\n"
            "━━━━━━━━━━━━━━━"
        )

    if response:
        save_data(data)
        send_chat(ws, response)

# ──────────────────────────────────────────────────────────
# DJ 전용 명령어
# ──────────────────────────────────────────────────────────
def handle_dj(ws, user_id, nickname, message):
    dj_id = cfg.get("DJ_USER_ID", "")
    if str(user_id) != str(dj_id):
        return

    data = load_data()
    response = None
    parts = message.split()

    if len(parts) == 2 and parts[0] == "!유저":
        target_nick = parts[1]
        target = next((u for u in data.values() if u["nickname"] == target_nick), None)
        if target:
            spoon_total = target.get("spoon_total", 0)
            spoon_display = f"{spoon_total % 100}/100"
            title = get_title(target)
            dungi_line = "🌟 블리둥이 ✨\n" if is_blidungi(target_nick) else ""
            response = (
                f"{target_nick}님 정보\n"
                f"━━━━━━━━━━━━━━━\n"
                f"{dungi_line}"
                f"👑 칭호: {title}\n"
                f"⭐ 레벨: Lv.{target['level']}\n"
                f"💰 포인트: {target['point']:,}/{get_next_level_point(target['level']):,}\n"
                f"🗓 출석: {target['attendance']}일\n"
                f"💬 채팅: {target.get('chat_count', 0)}회\n"
                f"💖 좋아요: {target.get('like_count', 0)}\n"
                f"🥄 스푼: {spoon_display}\n"
                f"🎟 복권: {target['lottery']}장\n"
                f"━━━━━━━━━━━━━━━"
            )
        else:
            response = f"유저 {target_nick}를 찾을 수 없어요!"

    elif len(parts) == 2 and parts[0] == "!유저삭제":
        target_nick = parts[1]
        uid = next((k for k, v in data.items() if v["nickname"] == target_nick), None)
        if uid:
            del data[uid]
            save_data(data)
            response = f"🗑️ {target_nick}님 데이터 삭제됐어요!"
        else:
            response = f"유저 {target_nick}를 찾을 수 없어요!"

    elif len(parts) == 3 and parts[0] == "!포인트":
        target_nick, amount_str = parts[1], parts[2]
        target = next((u for u in data.values() if u["nickname"] == target_nick), None)
        if target:
            try:
                amount = int(amount_str)
                target["point"] = max(0, target["point"] + amount)
                save_data(data)
                action = "지급" if amount > 0 else "차감"
                response = f"💰 {target_nick}님 포인트 {abs(amount):,} {action}! 현재 포인트: {target['point']:,}"
            except:
                response = "숫자 형식이 잘못됐어요!"
        else:
            response = f"유저 {target_nick}를 찾을 수 없어요!"

    elif len(parts) == 3 and parts[0] == "!레벨":
        target_nick, amount_str = parts[1], parts[2]
        target = next((u for u in data.values() if u["nickname"] == target_nick), None)
        if target:
            try:
                amount = int(amount_str)
                target["level"] = max(1, target["level"] + amount)
                save_data(data)
                action = "올림" if amount > 0 else "내림"
                response = f"⭐ {target_nick}님 레벨 {action}! 현재 레벨: {target['level']}"
            except:
                response = "숫자 형식이 잘못됐어요!"
        else:
            response = f"유저 {target_nick}를 찾을 수 없어요!"

    elif len(parts) == 3 and parts[0] == "!복권":
        target_nick, amount_str = parts[1], parts[2]
        target = next((u for u in data.values() if u["nickname"] == target_nick), None)
        if target:
            try:
                amount = int(amount_str)
                target["lottery"] = max(0, target["lottery"] + amount)
                save_data(data)
                action = "지급" if amount > 0 else "차감"
                response = f"🎟️ {target_nick}님 복권 {abs(amount)}장 {action}! 현재 복권: {target['lottery']}장"
            except:
                response = "숫자 형식이 잘못됐어요!"
        else:
            response = f"유저 {target_nick}를 찾을 수 없어요!"

    elif len(parts) == 3 and parts[0] == "!킵삭제":
        target_nick, num_str = parts[1], parts[2]
        saved = load_roulette_saved()
        my_saved = [(i, s) for i, s in enumerate(saved) if s["nickname"] == target_nick]
        if not my_saved:
            response = f"{target_nick}님의 저장된 룰렛 결과가 없어요!"
        else:
            try:
                num = int(num_str) - 1
                if 0 <= num < len(my_saved):
                    real_idx = my_saved[num][0]
                    del saved[real_idx]
                    save_roulette_saved(saved)
                    response = f"🗑️ {target_nick}님의 {num_str}번 룰렛 결과 삭제됐어요!"
                else:
                    response = "번호가 잘못됐어요!"
            except:
                response = "숫자 형식이 잘못됐어요!"

    elif len(parts) == 2 and parts[0] == "!실드":
        dj_data = data.get(str(dj_id), {})
        try:
            amount = int(parts[1])
            dj_data["shield"] = dj_data.get("shield", 0) + amount
            data[str(dj_id)] = dj_data
            save_data(data)
            action = "추가" if amount > 0 else "차감"
            response = f"🛡️ 실드 {action}! 현재 실드: {dj_data['shield']}개"
        except:
            response = "숫자 형식이 잘못됐어요!"

    elif len(parts) >= 3 and parts[0] == "!칭호":
        target_nick = parts[1]
        title_name = " ".join(parts[2:])
        target = next((u for u in data.values() if u["nickname"] == target_nick), None)
        if target:
            target["manual_title"] = title_name
            save_data(data)
            response = f"👑 {target_nick}님 칭호 [{title_name}] 지급됐어요!"
        else:
            response = f"유저 {target_nick}를 찾을 수 없어요!"

    elif len(parts) == 2 and parts[0] == "!칭호삭제":
        target_nick = parts[1]
        target = next((u for u in data.values() if u["nickname"] == target_nick), None)
        if target:
            target["manual_title"] = ""
            save_data(data)
            response = f"🗑️ {target_nick}님 수동 칭호 삭제됐어요!"
        else:
            response = f"유저 {target_nick}를 찾을 수 없어요!"

    elif len(parts) >= 3 and parts[0] == "!입장멘트":
        target_nick = parts[1]
        ment = " ".join(parts[2:])
        special = load_special()
        special[target_nick] = ment
        save_special(special)
        response = f"💌 {target_nick}님 입장멘트 저장됐어요!"

    elif len(parts) == 2 and parts[0] == "!입장멘트삭제":
        target_nick = parts[1]
        special = load_special()
        if target_nick in special:
            del special[target_nick]
            save_special(special)
            response = f"🗑️ {target_nick}님 입장멘트 삭제됐어요!"
        else:
            response = "입장멘트가 없어요!"

    elif message.startswith("!룰렛추가 "):
        item_name = message[7:].strip()
        items = load_roulette()
        items.append({"item": item_name, "weight": 3})
        save_roulette(items)
        response = f"🎡 룰렛 항목 추가됨: [{item_name}]"

    elif message.startswith("!룰렛삭제 "):
        item_name = message[7:].strip()
        items = load_roulette()
        new_items = [it for it in items if it["item"] != item_name]
        if len(new_items) < len(items):
            save_roulette(new_items)
            response = f"🗑️ 룰렛 항목 삭제됨: [{item_name}]"
        else:
            response = f"항목 [{item_name}]을 찾을 수 없어요!"

    elif message == "!룰렛목록":
        items = load_roulette()
        lines = [f"{i+1}. {it['item']}" for i, it in enumerate(items)]
        response = "🎡 룰렛 목록:\n" + "\n".join(lines)

    elif message == "!신청곡 초기화":
        save_songs([])
        response = "🎵 신청곡 목록이 초기화됐어요!"

    # 블리둥이 관리
    elif len(parts) == 2 and parts[0] == "!블리둥이추가":
        target_nick = parts[1]
        lst = load_blidungi()
        if target_nick not in lst:
            lst.append(target_nick)
            save_blidungi(lst)
            response = f"🌟 {target_nick}님 블리둥이 등록됐어요! ✨"
        else:
            response = f"이미 블리둥이예요! 💕"

    elif len(parts) == 2 and parts[0] == "!블리둥이삭제":
        target_nick = parts[1]
        lst = load_blidungi()
        if target_nick in lst:
            lst.remove(target_nick)
            save_blidungi(lst)
            response = f"🗑️ {target_nick}님 블리둥이 해제됐어요!"
        else:
            response = f"{target_nick}님은 블리둥이가 아니에요!"

    elif message == "!블리둥이목록":
        lst = load_blidungi()
        if not lst:
            response = "🌟 등록된 블리둥이가 없어요!"
        else:
            response = "🌟 블리둥이 목록:\n" + "\n".join([f"✨ {n}" for n in lst])

    # 랜덤채팅 / 럭키타임
    elif message in ("!랜덤채팅", "!럭키타임"):
        if len(recent_chatters) < 1:
            response = "최근 채팅한 유저가 없어요!"
        else:
            lucky_users = random.sample(recent_chatters, min(3, len(recent_chatters)))
            winners = []
            for u_id, u_nick in lucky_users:
                target = data.get(u_id)
                if target:
                    target["point"] = target.get("point", 0) + 30
                    winners.append(u_nick)
            save_data(data)
            send_chat(ws, "🎉럭키타임\n지금 채팅 친 사람 3분에게\n보너스 혜택 줄게요~🎁\n언능 채팅 쳐야겠찌??😉")
            time.sleep(2)
            response = f"🎁 럭키타임 당첨! {', '.join(winners)}님에게 포인트 +30!"

    elif len(parts) == 2 and parts[0] == "!선물":
        try:
            amount = int(parts[1])
            if recent_chatters:
                lucky_id, lucky_nick = random.choice(recent_chatters)
                target = data.get(lucky_id)
                if target:
                    target["point"] = target.get("point", 0) + amount
                    save_data(data)
                    response = f"🎁 럭키! {lucky_nick}님에게 포인트 {amount:,} 지급됐어요!"
            else:
                response = "최근 채팅한 유저가 없어요!"
        except:
            response = "숫자 형식이 잘못됐어요! 예) !선물 100"

    elif message.startswith("!미션추가 "):
        mission_text = message[6:].strip()
        m_parts = mission_text.split()
        if len(m_parts) >= 2:
            try:
                point = int(m_parts[-1])
                name = " ".join(m_parts[:-1])
                missions = load_missions()
                missions.append({"name": name, "point": point, "active": True})
                save_missions(missions)
                response = f"✅ 미션 추가됨: [{name}] 달성시 포인트 +{point}"
            except:
                response = "형식이 잘못됐어요! 예) !미션추가 노래 3곡 부르기 500"
        else:
            response = "형식이 잘못됐어요!"

    elif len(parts) == 2 and parts[0] == "!미션완료":
        target_nick = parts[1]
        target = next((u for u in data.values() if u["nickname"] == target_nick), None)
        missions = load_missions()
        active_missions = [m for m in missions if m.get("active")]
        if target and active_missions:
            mission = active_missions[0]
            target["point"] = target.get("point", 0) + mission["point"]
            target["mission_count"] = target.get("mission_count", 0) + 1
            check_special_titles(ws, target, target_nick)
            save_data(data)
            response = f"🎯 {target_nick}님 미션 [{mission['name']}] 완료! 포인트 +{mission['point']}"
        else:
            response = "유저 또는 활성 미션을 찾을 수 없어요!"

    # 이벤트 1등 / 깃발 횟수 기록
    elif len(parts) == 2 and parts[0] == "!이벤트1등":
        target_nick = parts[1]
        target = next((u for u in data.values() if u["nickname"] == target_nick), None)
        if target:
            target["event_win_count"] = target.get("event_win_count", 0) + 1
            save_data(data)
            response = f"🏅 {target_nick}님 이벤트 1등 {target['event_win_count']}회!"
        else:
            response = f"유저 {target_nick}를 찾을 수 없어요!"

    elif len(parts) == 2 and parts[0] == "!깃발":
        target_nick = parts[1]
        target = next((u for u in data.values() if u["nickname"] == target_nick), None)
        if target:
            target["flag_count"] = target.get("flag_count", 0) + 1
            save_data(data)
            response = f"🚩 {target_nick}님 깃발 게이지 달성 {target['flag_count']}회!"
        else:
            response = f"유저 {target_nick}를 찾을 수 없어요!"

    elif message == "!방종":
        all_users = load_data()
        today = datetime.now().strftime("%Y-%m-%d")
        top_spoon = max(all_users.values(), key=lambda x: x.get("spoon_today", 0), default=None)
        top_chat  = max(all_users.values(), key=lambda x: x.get("chat_count_today", 0), default=None)
        top_like  = max(all_users.values(), key=lambda x: x.get("like_count_today", 0), default=None)
        new_users = [u["nickname"] for u in all_users.values() if u.get("new_today") == today]

        def dn(u):
            return f"{u['nickname']}{'(👑회장님)' if u['nickname'] == CHAIRMAN_NICK else ''}"

        result = "📊 오늘 방송 정산!\n━━━━━━━━━━━━━━━\n"
        if top_spoon and top_spoon.get("spoon_today", 0) > 0:
            result += f"💰 오늘의 큰손: {dn(top_spoon)} ({top_spoon.get('spoon_today', 0):,}스푼)\n"
        if top_chat and top_chat.get("chat_count_today", 0) > 0:
            result += f"💬 오늘의 소통왕: {dn(top_chat)} ({top_chat.get('chat_count_today', 0)}회)\n"
        if top_like and top_like.get("like_count_today", 0) > 0:
            result += f"💖 오늘의 하트왕: {dn(top_like)} ({top_like.get('like_count_today', 0)}개)\n"
        result += f"🌟 오늘 새로 온 팬: {', '.join(new_users[:5]) if new_users else '없음'}\n"
        result += "━━━━━━━━━━━━━━━"

        for u in all_users.values():
            u["spoon_today"]      = 0
            u["chat_count_today"] = 0
            u["like_count_today"] = 0
        save_data(all_users)
        response = result

    if response:
        save_data(data)
        send_chat(ws, response)

# ──────────────────────────────────────────────────────────
# WebSocket 이벤트
# ──────────────────────────────────────────────────────────
def on_message(ws, message):
    global recent_chatters
    try:
        print(f"📨 RAW: {message[:500]}")
        data = json.loads(message)
        cmd = data.get("command", "")
        print(f"📌 CMD: {cmd}")

        if cmd == "MESSAGE":
            p = data.get("payload", {})
            u_id = str(p.get("userId", ""))
            nick = p.get("nickname", "")
            txt = p.get("text", "")
            print(f"📩 [{nick}]: {txt}")

            user_data = load_data()
            if u_id in user_data:
                user_data[u_id]["chat_count"]      = user_data[u_id].get("chat_count", 0) + 1
                user_data[u_id]["chat_count_today"] = user_data[u_id].get("chat_count_today", 0) + 1
                chat_exp = int(cfg.get("CHAT_EXP", 10))
                user_data[u_id]["exp"] = user_data[u_id].get("exp", 0) + chat_exp

                # 채팅 50회마다 +100포인트
                chat_count = user_data[u_id]["chat_count"]
                if chat_count % 50 == 0:
                    user_data[u_id]["point"] = user_data[u_id].get("point", 0) + 100
                    send_chat(ws, f"🎉 {nick}님 채팅 {chat_count}회 달성! 포인트 +100 지급됐어요!")

                check_special_titles(ws, user_data[u_id], nick)
                save_data(user_data)

            recent_chatters = [(uid, n) for uid, n in recent_chatters if uid != u_id]
            recent_chatters.insert(0, (u_id, nick))
            if len(recent_chatters) > 20:
                recent_chatters = recent_chatters[:20]

            for keyword, response_msg in AUTO_RESPONSES.items():
                if keyword in txt:
                    send_chat(ws, response_msg)
                    break

            if txt.startswith("!"):
                handle_command(ws, u_id, nick, txt)
                handle_dj(ws, u_id, nick, txt)

        elif cmd == "JOIN":
            p = data.get("payload", {})
            u_id = str(p.get("userId", ""))
            nick = p.get("nickname", "")
            cast_id = str(p.get("castId", ""))
            if not nick:
                return

            user_data = load_data()
            user, is_new = get_or_create_user(u_id, nick, user_data)

            session_key = f"{cast_id}_{datetime.now().strftime('%Y%m%d')}"
            attended_sessions = user.get("attended_sessions", [])

            if session_key not in attended_sessions:
                attended_sessions.append(session_key)
                user["attended_sessions"] = attended_sessions
                attendance_point = int(cfg.get("ATTENDANCE_POINT", 30))
                user["point"]      = user.get("point", 0) + attendance_point
                user["attendance"] = user.get("attendance", 0) + 1

                today     = datetime.now().strftime("%Y-%m-%d")
                yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                last_date = user.get("last_attendance_date", "")

                if last_date == yesterday:
                    user["consecutive_days"] = user.get("consecutive_days", 0) + 1
                elif last_date != today:
                    user["consecutive_days"] = 1
                user["last_attendance_date"] = today

                consecutive = user.get("consecutive_days", 1)
                bonus_msg = ""
                if consecutive == 3:
                    user["point"] = user.get("point", 0) + 100
                    bonus_msg = "\n🎁 3일 연속 출석! 포인트 +100!"
                elif consecutive == 7:
                    user["lottery"] = user.get("lottery", 0) + 5
                    bonus_msg = "\n🎁 7일 연속 출석! 복권 5장 지급!"
                elif consecutive == 30:
                    bonus_msg = "\n🎁 30일 연속 출석! 🏆 개근상 달성!"

                check_special_titles(ws, user, nick)
                lv_msg = process_levelup(user)
                save_data(user_data)

                if bonus_msg:
                    send_chat(ws, f"✅ {nick}님 출석 완료! ({consecutive}일 연속){bonus_msg}")
                if lv_msg:
                    send_chat(ws, f"🎊 {nick}님{lv_msg}")
            else:
                save_data(user_data)

            # 입장 메시지
            special = load_special()
            if nick in special:
                send_chat(ws, special[nick])
            else:
                join_count = user.get("join_count", 0)
                user["join_count"] = join_count + 1
                save_data(user_data)

                if nick == CHAIRMAN_NICK:
                    send_chat(ws, f"👑 회장님 {nick}님 납시오~!! 모두 환영해주세요!! 💕")
                elif is_blidungi(nick):
                    send_chat(ws, f"🌟 블리둥이 {nick}님 왔다~!! ✨\n내 사람이 왔잖아💖\n얼른 와 앉아😳")
                elif join_count == 0:
                    send_chat(ws, f"💌 어서와 {nick}…\n왜 이제 왔어\n기다렸잖아💖\n자리 비워놨으니까 얼른 와 앉아😳")
                elif user.get("attendance", 0) >= 10:
                    send_chat(ws, f"👀 또 왔네?\n이쯤 되면…\n그냥 내 사람이야 인정하지?💖")
                else:
                    welcome = cfg.get("WELCOME_MSG", "어서오세요! 💕 {nickname}님!")
                    send_chat(ws, welcome.replace("{nickname}", nick))

        # 좋아요 / 하트
        elif cmd in ("LIKE", "HEART"):
            p     = data.get("payload", {})
            u_id  = str(p.get("userId", ""))
            nick  = p.get("nickname", "")
            count = int(p.get("count", 1))

            user_data = load_data()
            if u_id in user_data:
                prev_like = user_data[u_id].get("like_count", 0)
                user_data[u_id]["like_count"]       = prev_like + count
                user_data[u_id]["like_count_today"]  = user_data[u_id].get("like_count_today", 0) + count
                like_exp = int(cfg.get("LIKE_EXP", 5)) * count
                user_data[u_id]["exp"] = user_data[u_id].get("exp", 0) + like_exp

                # 좋아요 5개마다 복권 1장
                earned = (user_data[u_id]["like_count"] // 5) - (prev_like // 5)
                if earned > 0:
                    user_data[u_id]["lottery"] = user_data[u_id].get("lottery", 0) + earned
                    send_chat(ws, f"💖 {nick}님 좋아요 보너스! 복권 {earned}장 지급됐어요! 🎟️")

                check_special_titles(ws, user_data[u_id], nick)
                save_data(user_data)

        elif cmd == "GIFT" or cmd == "SPOON":
            p = data.get("payload", {})
            u_id        = str(p.get("userId", ""))
            nick        = p.get("nickname", "")
            spoon_count = int(p.get("count", p.get("spoonCount", 0)))
            gift_type   = p.get("giftType", p.get("type", ""))

            if gift_type:
                play_bgm(gift_type)

            roulette_count = 0
            for threshold, count in SPOON_ROULETTE_TIERS:
                if spoon_count >= threshold:
                    roulette_count = count
                    break

            if roulette_count > 0:
                do_roulette(ws, u_id, nick, roulette_count)
            else:
                roulette_spoon = int(cfg.get("ROULETTE_SPOON", 30))
                roulette_type  = cfg.get("ROULETTE_SPOON_TYPE", "").strip()
                type_match = (not roulette_type) or (gift_type == roulette_type)
                if spoon_count == roulette_spoon and type_match:
                    do_roulette(ws, u_id, nick, 1)

            if spoon_count >= int(cfg.get("DONATION_MIN", 100)):
                chat_text = p.get("text", "")
                reactions = cfg.get("SPOON_REACTIONS", "💕 감사해요!!").split(",")
                reaction  = random.choice(reactions).strip()
                send_chat(ws, f"🎉 {nick}님이 {spoon_count:,}스푼 쏴줬어요! {reaction}")
                if chat_text:
                    play_tts(f"{nick}님, {chat_text}")

            user_data = load_data()
            user, _ = get_or_create_user(u_id, nick, user_data)
            prev_total          = user.get("spoon_total", 0)
            user["spoon_total"] = prev_total + spoon_count
            user["spoon_today"] = user.get("spoon_today", 0) + spoon_count

            check_special_titles(ws, user, nick)

            prev_tickets = prev_total // 100
            new_tickets  = user["spoon_total"] // 100
            earned = new_tickets - prev_tickets
            if earned > 0:
                user["lottery"] = user.get("lottery", 0) + earned
                send_chat(ws, f"🎁 {nick}님 복권 {earned}장 지급됐어요! 🎟️")

            save_data(user_data)

    except Exception as e:
        print(f"⚠️ 데이터 처리 오류: {e}")

def on_open(ws):
    global broadcast_start_time
    broadcast_start_time = datetime.now()
    print("✅ 스푼 서버 연결 성공! 블리봇 가동 시작 💕")
    threading.Thread(target=backup_data, daemon=True).start()
    start_timer(ws)
    try:
        channel_id = cfg.get("CHANNEL_ID", CHANNEL_ID)
        join_msg = json.dumps({"command": "JOIN", "payload": {"castId": int(channel_id)}})
        ws.send(join_msg)
        print(f"📡 채널 입장 패킷 전송! (채널: {channel_id})")
    except Exception as e:
        print(f"⚠️ 입장 패킷 오류: {e}")

def on_error(ws, error):
    print(f"❌ 에러 발생: {error}")

def on_close(ws, code, msg):
    print(f"🔌 연결 종료됨 (code={code}, msg={msg})")

WS_HEADERS = {
    "Origin": "https://www.spooncast.net",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}

def start_bot(ws_url, log_func):
    def _run():
        while True:
            try:
                log_func("🔗 서버에 연결 중...")
                ws_app = websocket.WebSocketApp(
                    ws_url,
                    header=WS_HEADERS,
                    on_open=lambda ws: (on_open(ws), log_func("✅ 블리봇 연결 성공! 💕")),
                    on_message=on_message,
                    on_error=lambda ws, e: (on_error(ws, e), log_func(f"❌ 에러: {e}")),
                    on_close=lambda ws, c, m: (on_close(ws, c, m), log_func(f"🔌 연결 종료! code={c}, msg={m}")),
                )
                ws_app.run_forever(ping_interval=20, ping_timeout=10, skip_utf8_validation=True)
            except Exception as e:
                log_func(f"⚠️ 연결 오류: {e}")
            log_func("🔄 5초 후 재연결 시도...")
            time.sleep(5)
    threading.Thread(target=_run, daemon=True).start()

def launch_gui():
    os.makedirs("songs/bgm", exist_ok=True)
    os.makedirs("backup", exist_ok=True)

    if not os.path.exists(CONFIG_FILE):
        create_default_config()
    loaded = load_config()
    if loaded:
        cfg.update(loaded)

    root = tk.Tk()
    root.title("♡ 블리봇 ♡")
    root.geometry("420x560")
    root.resizable(False, False)
    root.configure(bg="#fff0f5")

    tk.Label(root, text="♡ 블 리 봇 ♡", font=("맑은 고딕", 18, "bold"), bg="#fff0f5", fg="#e75480").pack(pady=(18, 2))
    tk.Label(root, text="정블리 방송 전용 스마트 봇 💕", font=("맑은 고딕", 9), bg="#fff0f5", fg="#999").pack(pady=(0, 12))

    frame = tk.LabelFrame(root, text="  스푼 로그인  ", font=("맑은 고딕", 9), bg="#fff0f5", fg="#e75480", padx=15, pady=10)
    frame.pack(padx=20, fill="x")
    tk.Label(frame, text="시작하기를 누르면 크롬이 자동으로 열려요!", bg="#fff0f5", font=("맑은 고딕", 9), fg="#555").pack(anchor="w", pady=(4, 0))
    tk.Label(frame, text="크롬에서 애플/카카오/구글로 로그인해주세요 💕", bg="#fff0f5", font=("맑은 고딕", 9), fg="#e75480").pack(anchor="w", pady=(0, 4))

    frame_ch = tk.LabelFrame(root, text="  DJ 설정  ", font=("맑은 고딕", 9), bg="#fff0f5", fg="#e75480", padx=15, pady=8)
    frame_ch.pack(padx=20, fill="x", pady=(8, 0))
    tk.Label(frame_ch, text="고유닉", bg="#fff0f5", font=("맑은 고딕", 9)).grid(row=0, column=0, sticky="w", pady=4)
    entry_nick = tk.Entry(frame_ch, width=20, font=("맑은 고딕", 10))
    entry_nick.grid(row=0, column=1, padx=8, pady=4)
    entry_nick.insert(0, cfg.get("DJ_NICK", "").lstrip("@"))
    tk.Label(frame_ch, text="(@ 없이 입력)", bg="#fff0f5", font=("맑은 고딕", 8), fg="#999").grid(row=0, column=2, sticky="w")

    log_box = scrolledtext.ScrolledText(root, height=6, font=("맑은 고딕", 8), bg="#fff8fb", fg="#555", state="disabled", bd=1)
    log_box.pack(padx=20, pady=(10, 0), fill="x")

    def log(msg):
        log_box.configure(state="normal")
        log_box.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        log_box.see("end")
        log_box.configure(state="disabled")

    status_var = tk.StringVar(value="⏸ 대기 중")
    btn_start = tk.Button(root, text="💕 저장하고 시작하기", font=("맑은 고딕", 11, "bold"),
                          bg="#e75480", fg="white", activebackground="#c0395e", relief="flat", padx=10, pady=8)
    btn_start.pack(pady=12, ipadx=10)
    tk.Label(root, textvariable=status_var, font=("맑은 고딕", 9), bg="#fff0f5", fg="#e75480").pack()

    def on_start():
        dj_nick = entry_nick.get().strip().lstrip("@")
        if not dj_nick:
            messagebox.showwarning("입력 오류", "고유닉을 입력해주세요!")
            return
        save_config_value("DJ_NICK", dj_nick)
        cfg["DJ_NICK"] = dj_nick
        btn_start.configure(state="disabled", text="연결 중...")
        status_var.set("🌐 크롬 실행 중...")

        def _connect():
            log("🌐 크롬 실행 중... 로그인해주세요!")
            ws_url = spoon_auto_login("", "", log)
            if not ws_url:
                root.after(0, lambda: status_var.set("❌ 로그인 실패! 다시 시도해주세요"))
                root.after(0, lambda: btn_start.configure(state="normal", text="💕 저장하고 시작하기"))
                return
            root.after(0, lambda: status_var.set("✅ 블리봇 가동 중 💕"))
            root.after(0, lambda: btn_start.configure(state="normal", text="🔄 재연결"))
            start_bot(ws_url, log)

        threading.Thread(target=_connect, daemon=True).start()

    btn_start.configure(command=on_start)
    root.mainloop()

if __name__ == "__main__":
    launch_gui()