from fastapi import FastAPI, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import Table
from typing import Optional
import asyncio
import os
import platform
import subprocess
from db import database, insert_data, get_all_data, delete_data, metadata , insert_remark_data , get_remarks , remarks_table



app = FastAPI()

# 정적 파일(예: CSS 파일)을 서빙하기 위한 설정
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

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

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

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
        "manager": manager
    })

@app.get("/fqa/sheet2", response_class=HTMLResponse)
async def fqa_sheet2(request: Request, year: str, month: str, team: str, worker: str, manager: str):
    return templates.TemplateResponse("fqa_sheet2.html", {
        "request": request, 
        "year": year, 
        "month": month, 
        "team": team, 
        "worker": worker, 
        "manager": manager
    })

# VRS 시트 3개
@app.get("/vrs/sheet1", response_class=HTMLResponse)
async def vrs_sheet1(request: Request, year: str, month: str, team: str, worker: str, manager: str, equipment_id: int):
    print(f"Received equipment_id: {equipment_id}")
    return templates.TemplateResponse("vrs_sheet1.html", {
        "request": request, 
        "year": year, 
        "month": month, 
        "team": team, 
        "worker": worker, 
        "manager": manager,
        "equipment_id": equipment_id
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
        "equipment_id": equipment_id
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
        "equipment_id": equipment_id
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
        "manager": manager
    })

@app.get("/fvi/sheet2", response_class=HTMLResponse)
async def fvi_sheet2(request: Request, year: str, month: str, team: str, worker: str, manager: str):
    return templates.TemplateResponse("fvi_sheet2.html", {
        "request": request, 
        "year": year, 
        "month": month, 
        "team": team, 
        "worker": worker, 
        "manager": manager
    })
# 공정 별 저장 로직
@app.post("/save/{sheet_name}")
async def save_check_sheet(sheet_name: str, request: Request):
    data = await request.json()
    
    # 시트 이름을 로그로 출력하여 확인
    print(f"Received sheet name: {sheet_name}")
    
    # 체크리스트 데이터 처리
    if sheet_name.startswith("fqa"):
        await insert_fqa_data(sheet_name, data)
    elif sheet_name.startswith("vrs"):
        await insert_vrs_data(sheet_name, data)
    elif sheet_name.startswith("fvi"):
        await insert_fqa_data(sheet_name, data)
    elif sheet_name == "remark":
        print("remark전송")
    else:
        raise ValueError("Invalid sheet name")

    # 비고 데이터가 있으면 비고 테이블에 저장
    if data.get("remark"):
        await insert_remark_data({
            "process": sheet_name,  # 공정명을 sheet_name으로 저장
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

# # FQA 온도 체크
# @app.get("/fqa/temp", response_class=HTMLResponse)
# async def temp_page(request: Request, year: str, month: str, team: str, worker: str, manager: str):
#     process = "FQA"
#     return templates.TemplateResponse("temp.html", {
#         "request": request, 
#         "year": year, 
#         "month": month, 
#         "team": team, 
#         "worker": worker, 
#         "manager": manager,
#         "process": process
#     })

# 병합 작업을 비동기로 처리하는 함수
# async def run_merge_script(process):
#     # 예시: FQA 공정 병합
#     if process == "FQA":
#         if platform.system() == "Windows":
#             subprocess.run(["python", "fqa_merge.py"])
#         else:
#             await asyncio.create_subprocess_exec("python3", "fqa_merge.py")

# @app.get("/download")
# async def download_page(request: Request):
#     return templates.TemplateResponse("download.html", {"request": request})

# @app.post("/download")
# async def download_file(request: Request, month: int = Form(...)):
#     filename = f"FQA_{month}월.xlsx"
#     filepath = f"./excel/fqa/{filename}"

#     if not os.path.exists(filepath):
#         return JSONResponse(content={"message": "파일이 존재하지 않습니다."})

#     return FileResponse(filepath, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename=filename)

# @app.get("/merge/{process}")
# async def merge_process_data(process: str):
#     await run_merge_script(process)
#     return JSONResponse(content={"message": f"{process} 데이터 병합이 완료되었습니다."})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)