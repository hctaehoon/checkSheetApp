import sqlite3
from datetime import datetime
import pytz
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Slack Webhook URL
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

# Database file path
DATABASE_PATH = "./test.db"

# 공정별 Slack 메시지를 전송하는 함수
def send_slack_message(message):
    payload = {"text": message}
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    if response.status_code == 200:
        print(f"Slack 메시지 전송 완료: {message}")
    else:
        print(f"Slack 메시지 전송 실패: {response.status_code}")

# 한국 시간(KST) 기준 현재 날짜 구하기 (yymmdd 형식)
def get_today_date():
    tz = pytz.timezone('Asia/Seoul')
    today = datetime.now(tz).strftime("%y%m%d")
    return today

# FQA, FVI 체크 함수
def check_fqa_fvi(conn, table_name):
    today = get_today_date()
    query = f"SELECT COUNT(*) FROM {table_name} WHERE date = ?"
    cursor = conn.execute(query, (today,))
    result = cursor.fetchone()
    return result[0] > 0  # 데이터가 있으면 True

# VRS 체크 함수
def check_vrs(conn):
    today = get_today_date()
    vrs_checks = {}

    # 1~17호기, 19~23호기만 검사
    for equipment_id in range(1, 24):
        if equipment_id == 18:
            continue  # 18호기 제외
        query = f"SELECT COUNT(*) FROM vrs_sheet1 WHERE date = ? AND equipment_id = ?"
        cursor = conn.execute(query, (today, equipment_id))
        result = cursor.fetchone()
        vrs_checks[equipment_id] = result[0] > 0  # 데이터가 있으면 True

    return vrs_checks

# 조별 체크 여부 확인 (오후 전용)
def check_team_data(conn, table_name, team):
    today = get_today_date()
    query = f"SELECT COUNT(*) FROM {table_name} WHERE date = ? AND team = ?"
    cursor = conn.execute(query, (today, team))
    result = cursor.fetchone()
    return result[0] > 0  # 해당 조의 데이터가 있으면 True

# 전체 체크 로직
def check_all_processes(is_morning):
    conn = sqlite3.connect(DATABASE_PATH)

    # FQA 체크
    fqa_check = check_fqa_fvi(conn, "fqa_sheet1")

    # FVI 체크
    fvi_check = check_fqa_fvi(conn, "fvi_sheet1")

    # VRS 체크
    vrs_checks = check_vrs(conn)

    # 메세지 준비
    slack_messages = []

    # FQA 메시지
    if fqa_check:
        slack_messages.append("FQA 체크시트 - 작성 완료")
    else:
        slack_messages.append("FQA 체크시트 - 작성 요청 드립니다.")

    # FVI 메시지
    if fvi_check:
        slack_messages.append("FVI 체크시트 - 작성 완료")
    else:
        slack_messages.append("FVI 체크시트 - 작성 요청 드립니다.")

    # VRS 메시지
    incomplete_vrs_a = []  # A조 미작성 호기
    incomplete_vrs_b = []  # B조 미작성 호기

    # 오후일 경우 조별로 확인
    if not is_morning:
        teams = ["A", "B"]
        for process, table_name in [("FQA", "fqa_sheet1"), ("FVI", "fvi_sheet1")]:
            for team in teams:
                if not check_team_data(conn, table_name, team):
                    slack_messages.append(f"{process} 체크시트 - {team}조 미작성")

        for equipment_id in range(1, 24):
            if equipment_id == 18:
                continue
            for team in teams:
                query = f"SELECT COUNT(*) FROM vrs_sheet1 WHERE date = ? AND team = ? AND equipment_id = ?"
                cursor = conn.execute(query, (get_today_date(), team, equipment_id))
                result = cursor.fetchone()
                if result[0] == 0:
                    if team == "A":
                        incomplete_vrs_a.append(str(equipment_id))
                    elif team == "B":
                        incomplete_vrs_b.append(str(equipment_id))

    # VRS 미작성 호기 메시지 추가
    if incomplete_vrs_a:
        slack_messages.append(f"VRS A조 미작성 호기: {', '.join(incomplete_vrs_a)}")
    if incomplete_vrs_b:
        slack_messages.append(f"VRS B조 미작성 호기: {', '.join(incomplete_vrs_b)}")
    
    # 오전의 경우에는 조별 체크 제외하고 일반 VRS 체크 메시지
    elif is_morning:
        incomplete_vrs = [str(equip) for equip, check in vrs_checks.items() if not check]
        if incomplete_vrs:
            slack_messages.append(f"VRS 체크시트 미작성 호기: {', '.join(incomplete_vrs)}")
        else:
            slack_messages.append("VRS 체크시트 - 작성 완료")

    # Slack 메시지 전송
    for message in slack_messages:
        send_slack_message(message)

    conn.close()

# 테스트용으로 오전/오후 체크를 즉시 실행
def test_check():
    print("=== 오전 체크 테스트 ===")
    check_all_processes(is_morning=True)

    print("\n=== 오후 체크 테스트 ===")
    check_all_processes(is_morning=False)

# 테스트 실행
if __name__ == "__main__":
    test_check()
