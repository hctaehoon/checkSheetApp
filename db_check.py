from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from db import replacement_schedule, metadata  # db.py에서 정의된 테이블과 메타데이터 불러오기

# 데이터베이스 URL 설정 (예: SQLite 사용)
DATABASE_URL = "sqlite:///./test.db"

# SQLAlchemy 엔진 및 세션 설정
engine = create_engine(DATABASE_URL)
metadata.create_all(engine)  # 테이블이 없을 경우 생성

# 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

# 교체 주기 테이블 데이터 확인 및 출력 함수
def check_replacement_schedule():
    query = select(replacement_schedule)  # replacement_schedule 테이블에서 모든 데이터 선택
    result = session.execute(query).fetchall()

    if not result:
        print("No data found in the replacement_schedule table.")
    else:
        print("Data found in replacement_schedule table:")
        for row in result:
            print(f"ID: {row[0]}, Sheet Name: {row[1]}, Item ID: {row[2]}, Equipment ID: {row[3]}, Last Replacement Date: {row[4]}, Next Replacement Date: {row[5]}, Replacement Interval Days: {row[6]}")

# 함수 호출
check_replacement_schedule()

# 세션 종료
session.close()
