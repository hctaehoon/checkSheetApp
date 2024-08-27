from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from databases import Database
import aiosqlite

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


engine = create_engine(DATABASE_URL)
metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def insert_data(sheet_name: str, data):
    # 선택한 시트에 따라 다른 테이블에 저장
    if sheet_name == "sheet1":
        table = fqa_sheet1
    elif sheet_name == "sheet2":
        table = fqa_sheet2
    elif sheet_name == "temperature":
        table = temperature_table
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

async def get_all_data(table_name: str):
    query = f"SELECT * FROM {table_name}"
    return await database.fetch_all(query)