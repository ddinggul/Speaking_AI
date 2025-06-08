from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import shutil, os, subprocess
from uuid import uuid4
from pathlib import Path

from azure_eval import assess_pronunciation
from voice_model import evaluate_wav

# 📌 문장 번호 → 실제 문장 텍스트 매핑
REFERENCE_TEXTS = {
    "1": "He was pressing beyond the limits of his vocabulary.",
    "2": "But he reconciled himself to it by an act of faith.",
    "3": "Each insult added to the value of the claim.",
    "4": "There is more behind this than a mere university ideal.",
    "5": "You're a devil for fighting and will surely win."
}

# ✅ m4a → wav 변환 함수
def convert_to_wav(input_path: str, output_path: str):
    subprocess.run(["ffmpeg", "-y", "-i", input_path, output_path], check=True)

# 기본 설정
app = FastAPI()
UPLOAD_DIR = "uploads"
IMAGE_DIR = "static/image"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)

# Static mount
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/analyze/", response_class=HTMLResponse)
async def analyze(
    request: Request,
    file: UploadFile = File(...),
    reference: str = Form(...),   # 👉 "1" ~ "5" 형태
    mel_path: str = Form(...)     # 👉 "spectrogram/L1/1_L1_mels.npy"
):
    session_id = str(uuid4())[:8]
    original_path = os.path.join(UPLOAD_DIR, f"{session_id}_{file.filename}")

    # 🔹 1. 파일 저장
    with open(original_path, "wb") as f_out:
        shutil.copyfileobj(file.file, f_out)

    # 🔹 2. 확장자 검사 후 wav로 변환
    ext = Path(file.filename).suffix.lower()
    if ext != ".wav":
        wav_path = os.path.join(UPLOAD_DIR, f"{session_id}.wav")
        convert_to_wav(original_path, wav_path)
    else:
        wav_path = original_path

    # 🔹 3. 기준 문장 텍스트 매핑
    reference_text = REFERENCE_TEXTS.get(reference, "")

    # 🔹 4. Azure 평가
    azure_result = assess_pronunciation(wav_path, reference_text)

    # 🔹 5. 준서 모델 평가
    similarity_score, feedback, plot_path, highlighted_sentence = evaluate_wav(
        wav_path=wav_path,
        session_id=session_id,
        pron_json=azure_result,
        sentence=reference_text,
        l1_mel_path=mel_path
    )

    # 🔹 6. 결과 렌더링
    return templates.TemplateResponse("result.html", {
        "request": request,
        "azure": azure_result,
        "junseo": {
            "similarity_score": similarity_score,
            "intonation_feedback": feedback
        },
        "highlighted_text": highlighted_sentence,
        "intonation_plot": plot_path
    })
