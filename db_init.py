from sqlalchemy import select
from datetime import datetime, timedelta
from db import replacement_schedule, database





# 시트별 기본 항목과 교체 주기 정의
default_items = {
    "fqa_sheet1": [
        {"item_id": 11, "replacement_interval_days": 90},  # Brush
        {"item_id": 12, "replacement_interval_days": 365},  # 검사 불소 Pad
    ],
    "fvi_sheet1": [
        {"item_id": 14, "replacement_interval_days": 90},  # Picker Pad
        {"item_id": 15, "replacement_interval_days": 90},  # Brush
        {"item_id": 16, "replacement_interval_days": 365},  # Jig Pad
    ],
    # "vrs_sheet1": [
    #     {"item_id": 7, "replacement_interval_days": 90},  # Regulator
    #     {"item_id": 8, "replacement_interval_days": 365},  # Boat Pad
    #     {"item_id": 9, "replacement_interval_days": 1825},  # 자바라 교체
    # ],
    # "vrs_sheet2": [
    #     {"item_id": 7, "replacement_interval_days": 90},  # Brush 교체
    # ],
}

# 비동기 교체 주기 데이터 초기화 함수
async def check_and_initialize_schedule(sheet_name: str):
    # 데이터베이스 연결
    await database.connect()

    # 해당 시트 이름으로 데이터가 있는지 확인
    query = select(replacement_schedule).where(replacement_schedule.c.sheet_name == sheet_name)
    existing_data = await database.fetch_all(query)

    # 데이터가 없으면 초기 데이터 삽입
    if not existing_data:
        print(f"No data found for {sheet_name}, inserting default values...")
        today = datetime.now().strftime("%Y-%m-%d")
        
        # 해당 시트의 기본 항목들을 가져옴
        if sheet_name in default_items:
            items = default_items[sheet_name]
            for item in items:
                next_replacement_date = (datetime.now() + timedelta(days=item["replacement_interval_days"])).strftime("%Y-%m-%d")
                new_record = {
                    "sheet_name": sheet_name,
                    "item_id": item["item_id"],
                    "last_replacement_date": today,
                    "next_replacement_date": next_replacement_date,
                    "replacement_interval_days": item["replacement_interval_days"],
                    "equipment_id": 0  # fqa와 fvi는 장비 호기가 없으므로 기본값 0으로 설정
                }
                # 새로운 데이터를 비동기 방식으로 테이블에 삽입
                await database.execute(replacement_schedule.insert().values(new_record))
            
            print(f"Default values inserted for {sheet_name}.")
        else:
            print(f"Sheet name {sheet_name} not found in default_items.")
    else:
        print(f"Data already exists for {sheet_name}.")

    # 데이터베이스 연결 종료
    await database.disconnect()
# 현재 테이블 데이터를 확인하고 출력하는 함수
async def fetch_replacement_schedule_data():
    query = select(replacement_schedule)
    data = await database.fetch_all(query)

    if not data:
        print("No data found in the replacement_schedule table.")
    else:
        print("Current data in the replacement_schedule table:")
        for row in data:
            print(f"ID: {row['id']}, Sheet Name: {row['sheet_name']}, Item ID: {row['item_id']}, Last Replacement Date: {row['last_replacement_date']}, Next Replacement Date: {row['next_replacement_date']}, Interval Days: {row['replacement_interval_days']}")

# 비동기 함수 실행을 위한 메인 루틴
async def main():
    await database.connect()
    await check_and_initialize_schedule("fqa_sheet1")
    await check_and_initialize_schedule("fvi_sheet1")
    await fetch_replacement_schedule_data()  # 테이블 데이터 조회 및 출력
    await database.disconnect()


# 비동기 함수 실행
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())


