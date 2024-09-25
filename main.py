from fastapi import FastAPI, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import Table , select , insert
from typing import Optional
import asyncio
import os
import platform
import subprocess
from db import database, insert_data, get_all_data, delete_data, metadata , insert_remark_data , get_remarks , remarks_table
from db import replacement_schedule
from datetime import datetime
from db_init import check_and_initialize_schedule
from contextlib import asynccontextmanager



processes = [
    {"id": 1, "name": "FQA", "url": "/fqa"},
    {"id": 2, "name": "N2Baking", "url": "/n2baking"},
    {"id": 3, "name": "반출입", "url": "/banexport"},
    {"id": 4, "name": "Packing", "url": "/packing"},
    {"id": 5, "name": "VRS", "url": "/vrs"},
    {"id": 6, "name": "FVI", "url": "/fvi"},
    {"id": 7, "name": "LM", "url": "/lm"},
    {"id": 8, "name": "AFVI", "url": "/afvi"},
    {"id": 9, "name": "Scale", "url": "/scale"},
    {"id": 10, "name": "Rinse", "url": "/rinse"},
    {"id": 11, "name": "Warpage", "url": "/warpage"},
    {"id": 12, "name": "RM", "url": "/rm"},
]

# 공정별 데이터 분기
async def insert_fqa_data(sheet_name: str, data):
    table = metadata.tables[sheet_name]
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

async def insert_vrs_data(sheet_name: str, data):
    table = metadata.tables[sheet_name]
    
    query = table.insert().values(
        [
            {
                "item_id": check["id"],
                "checked": check["checked"],
                "team": data["team"],
                "worker": data["worker"],
                "manager": data["manager"],
                "equipment_id": data["equipment_id"],
                "date": data["date"]
            }
            for check in data["checks"]
        ]
    )

    await database.execute(query)
async def insert_fvi_data(sheet_name: str, data):
    table = metadata.tables[sheet_name]
    
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

# 데이터베이스 연결 함수
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 애플리케이션 시작 시 실행할 코드
    await database.connect()
    yield
    # 애플리케이션 종료 시 실행할 코드
    await database.disconnect()
app = FastAPI(lifespan=lifespan)

# 정적 파일(예: CSS 파일)을 서빙하기 위한 설정
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    selected_process_id = request.cookies.get("selected_process", None)
    if selected_process_id:
        selected_process_id = int(selected_process_id)
        selected_process = next((p for p in processes if p["id"] == selected_process_id), processes[0])
    else:
        selected_process = processes[0]
    return templates.TemplateResponse("index.html", {"request": request, "processes": processes, "selected_process": selected_process})

@app.post("/select", response_class=HTMLResponse)
async def select_process(request: Request, response: Response, process_id: int = Form(...)):
    response.set_cookie(key="selected_process", value=str(process_id), max_age=900000)
    selected_process = next((p for p in processes if p["id"] == process_id), processes[0])
    return RedirectResponse(url=selected_process["url"], status_code=303)

@app.get("/fqa", response_class=HTMLResponse)
async def fqa_page(request: Request):
    return templates.TemplateResponse("fqa.html", {"request": request})

@app.get("/fvi", response_class=HTMLResponse)
async def fvi_page(request: Request):
    return templates.TemplateResponse("fvi.html", {"request": request})

@app.get("/vrs", response_class=HTMLResponse)
async def vrs_page(request: Request):
    return templates.TemplateResponse("vrs.html", {"request": request})

@app.get("/afvi", response_class=HTMLResponse)
async def afvi_page(request: Request):
    return templates.TemplateResponse("afvi.html", {"request": request})
# 공정별 시트 
# FQA
@app.get("/fqa/sheet1", response_class=HTMLResponse)
async def fqa_sheet1(request: Request, year: str, month: str, team: str, worker: str, manager: str):
    return templates.TemplateResponse("fqa_sheet1.html", {
        "request": request, 
        "year": year, 
        "month": month, 
        "team": team, 
        "worker": worker, 
        "manager": manager,
        "sheet_name": "fqa_sheet1" 
    })

@app.get("/fqa/sheet2", response_class=HTMLResponse)
async def fqa_sheet2(request: Request, year: str, month: str, team: str, worker: str, manager: str):
    return templates.TemplateResponse("fqa_sheet2.html", {
        "request": request, 
        "year": year, 
        "month": month, 
        "team": team, 
        "worker": worker, 
        "manager": manager,
        "sheet_name": "fqa_sheet2" 
    })

# VRS 시트 3개
@app.get("/vrs/sheet1", response_class=HTMLResponse)
async def vrs_sheet1(request: Request, year: str, month: str, team: str, worker: str, manager: str, equipment_id: int):
    return templates.TemplateResponse("vrs_sheet1.html", {
        "request": request, 
        "year": year, 
        "month": month, 
        "team": team, 
        "worker": worker, 
        "manager": manager,
        "equipment_id": equipment_id,
        "sheet_name": "vrs_sheet1" 
    })


@app.get("/vrs/sheet2", response_class=HTMLResponse)
async def vrs_sheet2(request: Request, year: str, month: str, team: str, worker: str, manager: str, equipment_id: int):
    return templates.TemplateResponse("vrs_sheet2.html", {
        "request": request, 
        "year": year, 
        "month": month, 
        "team": team, 
        "worker": worker, 
        "manager": manager,
        "equipment_id": equipment_id,
        "sheet_name": "vrs_sheet2" 
    })

@app.get("/vrs/sheet3", response_class=HTMLResponse)
async def vrs_sheet3(request: Request, year: str, month: str, team: str, worker: str, manager: str, equipment_id: int):
    return templates.TemplateResponse("vrs_sheet3.html", {
        "request": request, 
        "year": year, 
        "month": month, 
        "team": team, 
        "worker": worker, 
        "manager": manager,
        "equipment_id": equipment_id,
        "sheet_name": "vrs_sheet3" 
    })
# FVI 시트 2개
@app.get("/fvi/sheet1", response_class=HTMLResponse)
async def fvi_sheet1(request: Request, year: str, month: str, team: str, worker: str, manager: str):
    return templates.TemplateResponse("fvi_sheet1.html", {
        "request": request, 
        "year": year, 
        "month": month, 
        "team": team, 
        "worker": worker, 
        "manager": manager,
        "sheet_name": "fqa_sheet1" 
    })

@app.get("/fvi/sheet2", response_class=HTMLResponse)
async def fvi_sheet2(request: Request, year: str, month: str, team: str, worker: str, manager: str):
    return templates.TemplateResponse("fvi_sheet2.html", {
        "request": request, 
        "year": year, 
        "month": month, 
        "team": team, 
        "worker": worker, 
        "manager": manager,
        "sheet_name": "fvi_sheet2" 
    })
# 공정 별 저장 로직
@app.post("/save/{sheet_name}")
async def save_check_sheet(sheet_name: str, request: Request):
    data = await request.json()
    
    # 시트 이름을 로그로 출력하여 확인
    
    # 체크리스트 데이터 처리
    if sheet_name.startswith("fqa"):
        await insert_fqa_data(sheet_name, data)
    elif sheet_name.startswith("vrs"):
        await insert_vrs_data(sheet_name, data)
    elif sheet_name.startswith("fvi"):
        await insert_fvi_data(sheet_name, data)
    elif sheet_name == "remark":
        print("remark전송")
    else:
        raise ValueError("Invalid sheet name")

    # 비고 데이터가 있으면 비고 테이블에 저장
    if data.get("remark"):
        await insert_remark_data({
            "process": data.get("process"),  # 공정명을 sheet_name으로 저장
            "equipment_type": data.get("equipment_type", None),  # 선택적 데이터
            "equipment_id": data.get("equipment_id", None),      # 선택적 데이터
            "team": data.get("team"),
            "manager": data.get("manager"),
            "remark": data.get("remark"),
            "date": data.get("date")
        })

    return JSONResponse(content={"message": f"Data successfully saved to {sheet_name}"})

# 비고 데이터 저장 라우터
@app.post("/save/remark")
async def save_remark(request: Request):
    data = await request.json()
    # 비고 데이터가 공백이 아니면 저장
    if data.get("remark"):
        print("저장할 데이터:", data)
        await insert_remark_data(data)
    return JSONResponse(content={"message": "Remark successfully saved"})



# 비고 데이터 조회 라우터
@app.get("/remarks", response_class=HTMLResponse)
async def get_remarks_page(request: Request):
    remarks = await get_remarks()
    return templates.TemplateResponse("remarks.html", {"request": request, "remarks": remarks})
# DB 관리 페이지
@app.get("/db_manage", response_class=HTMLResponse)
async def db_manage(request: Request):
    return templates.TemplateResponse("db_manage.html", {"request": request})

@app.get("/db_manage/{table_name}", response_class=HTMLResponse)
async def get_table_data(request: Request, table_name: str):
    if table_name not in ["fqa_sheet1", "fqa_sheet2", "vrs_sheet1", "vrs_sheet2", "vrs_sheet3", "fvi_sheet1", "fvi_sheet2", "temperature_records"]:
        raise HTTPException(status_code=404, detail="Table not found")
    data = await get_all_data(table_name)
    return templates.TemplateResponse("table_data.html", {"request": request, "data": data, "table_name": table_name})

@app.delete("/db_manage/{table_name}/delete/{item_id}")
async def delete_item(table_name: str, item_id: int):
    if table_name not in ["fqa_sheet1", "fqa_sheet2", "vrs_sheet1", "vrs_sheet2", "vrs_sheet3", "fvi_sheet1", "fvi_sheet2", "temperature_records"]:
        raise HTTPException(status_code=404, detail="Table not found")
    await delete_data(table_name, item_id)
    return {"message": "Item deleted successfully"}

@app.delete("/db_manage/{table_name}/delete_all")
async def delete_all_data(table_name: str):
    if table_name not in ["fqa_sheet1", "fqa_sheet2", "vrs_sheet1", "vrs_sheet2", "vrs_sheet3", "fvi_sheet1", "fvi_sheet2", "temperature_records"]:
        raise HTTPException(status_code=404, detail="Table not found")
    query = f"DELETE FROM {table_name}"
    await database.execute(query)
    return {"message": f"All data from {table_name} has been deleted"}

from fastapi import HTTPException

# 개별 비고 삭제 라우터
@app.delete("/delete/remark/{remark_id}")
async def delete_remark(remark_id: int):
    query = remarks_table.delete().where(remarks_table.c.id == remark_id)
    result = await database.execute(query)
    if result:
        return {"message": "비고가 성공적으로 삭제되었습니다."}
    else:
        raise HTTPException(status_code=404, detail="비고를 찾을 수 없습니다.")

# 전체 비고 삭제 라우터
@app.delete("/delete/remarks")
async def delete_all_remarks():
    query = remarks_table.delete()
    await database.execute(query)
    return {"message": "모든 비고가 성공적으로 삭제되었습니다."}

# 교체 주기 업데이트 API
@app.post("/update/replacement_schedule")
async def update_replacement_schedule(data: dict):
    # 장비 호기 값이 없는 경우 기본값 0으로 설정
    equipment_id = data.get('equipment_id', 0)

    
    if equipment_id:
        print(f"Equipment ID: {equipment_id}")
    else:
        print("장비가없음")
    query = replacement_schedule.update().where(
        (replacement_schedule.c.sheet_name == data['sheet_name']) &
        (replacement_schedule.c.item_id == data['item_id']) &
        (replacement_schedule.c.equipment_id == equipment_id)
    ).values(
        last_replacement_date=data['last_replacement_date'],
        next_replacement_date=data['next_replacement_date'],
        replacement_interval_days=data['replacement_interval_days']
    )

    await database.execute(query)
    return {"message": "Replacement date updated successfully"}

# 교체 주기 조회 API
@app.get("/get/replacement_schedule/{sheet_name}")
async def get_replacement_schedule(sheet_name: str, equipment_id: Optional[int] = None):
    query = select(replacement_schedule).where(
        replacement_schedule.c.sheet_name == sheet_name
    )
    
    if equipment_id is not None:
        query = query.where(replacement_schedule.c.equipment_id == equipment_id)
    
    replacement_data = await database.fetch_all(query)
    

    if not replacement_data:
        return {"message": "No replacement data found"}

    return {
        "replacement_data": [
            {
                "item_id": row["item_id"],
                "last_replacement_date": row["last_replacement_date"],
                "next_replacement_date": row["next_replacement_date"],
                "replacement_interval_days": row["replacement_interval_days"],
                "equipment_id": row["equipment_id"]
            }
            for row in replacement_data
        ]
    }


# 교체 주기 체크 API
@app.get("/check/replacement_dates/{sheet_name}")
async def check_replacement_dates(sheet_name: str, equipment_id: Optional[int] = None):
    query = replacement_schedule.select().where(replacement_schedule.c.sheet_name == sheet_name)
    
    if equipment_id is not None:
        query = query.where(replacement_schedule.c.equipment_id == equipment_id)
    
    rows = await database.fetch_all(query)

    # 현재 날짜와 비교하여 교체 주기가 지난 항목이 있는지 확인
    all_valid = True
    for row in rows:
        if row['next_replacement_date'] < datetime.now().strftime("%Y-%m-%d"):
            all_valid = False
            break

    return {"allValid": all_valid}


async def insert_vrs_data_direct(sheet_name: str, data):
    """
    관리자 모드에서 VRS 시트에 데이터를 강제로 삽입하는 함수.
    """
    # 시트에 맞는 테이블 객체를 가져옴
    table = metadata.tables[sheet_name]

    # 삽입할 데이터를 구성
    query = table.insert().values(
        [
            {
                "item_id": item["item_id"],
                "checked": item["checked"],
                "team": data["team"],
                "worker": data["worker"],
                "manager": data["manager"],
                "equipment_id": data["equipment_id"],
                "date": data["date"]
            }
            for item in data["checks"]
        ]
    )
    
    # 데이터베이스에 삽입
    await database.execute(query)

# VRS 시트별 삽입 항목 리스트 정의
vrs_sheet1_items = [
    {"item_id": 1, "checked": 1}, {"item_id": 2, "checked": 1}, {"item_id": 3, "checked": 1},
    {"item_id": 4, "checked": 1}, {"item_id": 5, "checked": 1}, {"item_id": 6, "checked": 1},
    {"item_id": 7, "checked": 1}, {"item_id": 8, "checked": 0}, {"item_id": 9, "checked": 0}
]

vrs_sheet2_items = [
    {"item_id": 1, "checked": 1}, {"item_id": 2, "checked": 1}, {"item_id": 3, "checked": 1},
    {"item_id": 4, "checked": 1}, {"item_id": 5, "checked": 1}, {"item_id": 6, "checked": 1},
    {"item_id": 7, "checked": 0}
]

vrs_sheet3_items = [
    {"item_id": 1, "checked": 1}, {"item_id": 2, "checked": 1}, {"item_id": 3, "checked": 1},
    {"item_id": 4, "checked": 1}, {"item_id": 5, "checked": 1}, {"item_id": 6, "checked": 1}
]
@app.post("/submit-secret")
async def submit_secret(request: Request):
    try:
        data = await request.json()  # 클라이언트에서 받은 JSON 데이터
    except ValueError:
        return JSONResponse(content={"message": "잘못된 입력 형식입니다."}, status_code=400)
    
    # 기본 데이터 처리
    team = data['team']
    worker = data['worker']
    manager = data['manager']
    equipment_ids = [int(e_id) for e_id in data['equipment_ids'] if e_id]  # 장비 ID 변환
    today = datetime.now().strftime("%y%m%d")  # 오늘 날짜

    if not equipment_ids:
        return JSONResponse(content={"message": "장비 호기가 입력되지 않았습니다."}, status_code=400)

    # 강제 삽입을 위한 함수
    async def insert_into_table(sheet_name: str, equipment_id: int, items: list):
        table = metadata.tables[sheet_name]
        query = table.insert().values(
            [
                {
                    "item_id": item["item_id"],
                    "checked": item["checked"],
                    "team": team,
                    "worker": worker,
                    "manager": manager,
                    "equipment_id": equipment_id,
                    "date": today
                }
                for item in items
            ]
        )
        await database.execute(query)  # 데이터베이스에 쿼리 실행

    # 각 시트별로 데이터 강제 삽입
    for equipment_id in equipment_ids:
        await insert_into_table("vrs_sheet1", equipment_id, vrs_sheet1_items)
        await insert_into_table("vrs_sheet2", equipment_id, vrs_sheet2_items)
        await insert_into_table("vrs_sheet3", equipment_id, vrs_sheet3_items)

    return JSONResponse(content={"message": "데이터가 성공적으로 저장되었습니다."})



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)