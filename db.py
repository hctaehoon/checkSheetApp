from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from databases import Database

DATABASE_URL = "sqlite:///./test.db"
database = Database(DATABASE_URL)
metadata = MetaData()

# Define tables
fqa_sheet1 = Table(
    "fqa_sheet1",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("item_id", Integer),
    Column("checked", Integer),
    Column("team", String),
    Column("worker", String),
    Column("manager", String),
    Column("date", String),
)

fqa_sheet2 = Table(
    "fqa_sheet2",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("item_id", Integer),
    Column("checked", Integer),
    Column("team", String),
    Column("worker", String),
    Column("manager", String),
    Column("date", String),
)

# VRS Sheet Tables with Equipment ID
vrs_sheet1 = Table(
    "vrs_sheet1",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("item_id", Integer),
    Column("checked", Integer),
    Column("team", String),
    Column("worker", String),
    Column("manager", String),
    Column("equipment_id", Integer),  # 장비 호기
    Column("date", String),
)

vrs_sheet2 = Table(
    "vrs_sheet2",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("item_id", Integer),
    Column("checked", Integer),
    Column("team", String),
    Column("worker", String),
    Column("manager", String),
    Column("equipment_id", Integer),  # 장비 호기
    Column("date", String),
)

vrs_sheet3 = Table(
    "vrs_sheet3",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("item_id", Integer),
    Column("checked", Integer),
    Column("team", String),
    Column("worker", String),
    Column("manager", String),
    Column("equipment_id", Integer),  # 장비 호기
    Column("date", String),
)

# FVI Sheet Tables
fvi_sheet1 = Table(
    "fvi_sheet1",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("item_id", Integer),
    Column("checked", Integer),
    Column("team", String),
    Column("worker", String),
    Column("manager", String),
    Column("date", String),
)

fvi_sheet2 = Table(
    "fvi_sheet2",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("item_id", Integer),
    Column("checked", Integer),
    Column("team", String),
    Column("worker", String),
    Column("manager", String),
    Column("date", String),
)

# 수정된 temp 테이블 정의
temperature_table = Table(
    "temperature_records",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("temperature", Integer),
    Column("humidity", Integer),  # 습도 컬럼 추가
    Column("manager", String),
    Column("team", String),
    Column("process", String),
    Column("date", String),
)


# 비고 테이블 추가
remarks_table = Table(
    "remarks",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("process", String),        # 공정 이름 (예: FQA, VRS 등)
    Column("equipment_type", String, nullable=True), # 장비 종류 (Optional)
    Column("equipment_id", Integer, nullable=True),  # 장비 호기 (Optional)
    Column("team", String),           # 조
    Column("manager", String),        # 관리자
    Column("remark", String),         # 비고 내용
    Column("date", String)            # 날짜
)


# 비고 데이터 삽입 함수 추가
async def insert_remark_data(data):
    query = remarks_table.insert().values(
        process=data.get("process"),
        equipment_type=data.get("equipment_type"),
        equipment_id=data.get("equipment_id"),
        team=data.get("team"),
        manager=data.get("manager"),
        remark=data.get("remark"),
        date=data.get("date")
    )
    await database.execute(query)
    
# 비고 데이터 조회 함수 추가
async def get_remarks():
    query = remarks_table.select()
    return await database.fetch_all(query)

engine = create_engine(DATABASE_URL)
metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def insert_data(sheet_name: str, data):
    # 선택한 시트에 따라 다른 테이블에 저장
    if sheet_name == "fqa_sheet1":
        table = fqa_sheet1
        include_equipment_id = False
    elif sheet_name == "fqa_sheet2":
        table = fqa_sheet2
        include_equipment_id = False
    elif sheet_name == "temperature":
        table = temperature_table
        include_equipment_id = False
    elif sheet_name == "vrs_sheet1":
        table = vrs_sheet1
        include_equipment_id = True
    elif sheet_name == "vrs_sheet2":
        table = vrs_sheet2
        include_equipment_id = True
    elif sheet_name == "vrs_sheet3":
        table = vrs_sheet3
        include_equipment_id = True
    elif sheet_name == "fvi_sheet1":
        table = fvi_sheet1
        include_equipment_id = False
    elif sheet_name == "fvi_sheet2":
        table = fvi_sheet2
        include_equipment_id = False
    else:
        raise ValueError("Invalid sheet name")

    if sheet_name == "temperature":
        query = table.insert().values(
            temperature=data["temperature"],
            humidity=data["humidity"],
            manager=data["manager"],
            team=data["team"],
            process="FQA",
            date=data["date"]
        )
    else:
        # equipment_id가 필요한 경우와 아닌 경우를 구분하여 데이터를 처리합니다.
        if include_equipment_id:
            query = table.insert().values(
                [
                    {
                        "item_id": check["id"],
                        "checked": check["checked"],
                        "team": data["team"],
                        "worker": data["worker"],
                        "manager": data["manager"],
                        "equipment_id": data["equipment_id"],  # 장비 호기 데이터 추가
                        "date": data["date"]
                    }
                    for check in data["checks"]
                ]
            )
        else:
            query = table.insert().values(
                [
                    {
                        "item_id": check["id"],
                        "checked": check["checked"],
                        "team": data["team"],
                        "worker": data["worker"],
                        "manager": data["manager"],
                        "date": data["date"]
                    }
                    for check in data["checks"]
                ]
            )

    await database.execute(query)

async def delete_data(table_name: str, item_id: int):
    query = f"DELETE FROM {table_name} WHERE id = :item_id"
    await database.execute(query, {"item_id": item_id})

VALID_TABLES = ["fqa_sheet1", "fqa_sheet2", "vrs_sheet1", "vrs_sheet2", "vrs_sheet3", "fvi_sheet1", "fvi_sheet2", "temperature_records"]

async def get_all_data(table_name: str):
    if table_name not in VALID_TABLES:
        raise ValueError("Invalid table name")
    query = f"SELECT * FROM {table_name}"
    return await database.fetch_all(query)