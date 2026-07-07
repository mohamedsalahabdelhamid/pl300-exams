"""
PL-300 Exam Center — FastAPI Server
Serves individual exam files from data/ directory.
"""

import json
import os
import sys
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

if getattr(sys, 'frozen', False):
    DATA_DIR = Path(sys.executable).parent
else:
    DATA_DIR = Path(__file__).parent
DATA_PATH = DATA_DIR / "data"

app = FastAPI(title="PL-300 Exam Center")

app.mount("/static", StaticFiles(directory=str(DATA_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(DATA_DIR / "templates"))

exam_cache = [None] * 7  # index 1-6

def load_exam(exam_id):
    if not exam_cache[exam_id]:
        path = DATA_PATH / f"exam_{exam_id}.json"
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    exam_cache[exam_id] = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"[WARN] Failed to load exam_{exam_id}.json: {e}")
    return exam_cache[exam_id]

def get_all_exam_info():
    sizes = []
    for i in range(1, 7):
        exam = load_exam(i)
        sizes.append(len(exam["questions"]) if exam else 0)
    total = sum(sizes)
    return {"exams": 6, "exam_sizes": sizes, "total": total}

@app.on_event("startup")
def startup():
    if not DATA_PATH.exists():
        print(f"[WARN] Data directory not found: {DATA_PATH}")
        return
    for i in range(1, 7):
        load_exam(i)

@app.get("/api/questions")
def api_questions(exam: int = None):
    if exam is not None:
        data = load_exam(exam)
        if data:
            return {"exam": exam, "total": len(data["questions"]), "questions": data["questions"]}
        return {"exam": exam, "total": 0, "questions": []}
    return get_all_exam_info()

@app.get("/api/exams")
def api_exams():
    return get_all_exam_info()

@app.get("/exam/{exam_id}", response_class=HTMLResponse)
def exam_page(exam_id: int, request: Request):
    if exam_id < 1 or exam_id > 6:
        return HTMLResponse("Exam not found", status_code=404)
    return templates.TemplateResponse(request, "exam.html", {"exam_id": exam_id})

@app.get("/data/corrections.json")
def get_corrections():
    path = DATA_PATH / "corrections.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return JSONResponse(json.load(f))
    return JSONResponse({})

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(request, "dashboard.html")
