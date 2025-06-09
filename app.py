from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import shutil, os, subprocess
from uuid import uuid4
from pathlib import Path
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
from azure_eval import assess_pronunciation
from voice_model import evaluate_wav

REFERENCE_TEXTS = {
    "1": "He was pressing beyond the limits of his vocabulary.",
    "2": "But he reconciled himself to it by an act of faith.",
    "3": "Each insult added to the value of the claim.",
    "4": "There is more behind this than a mere university ideal.",
    "5": "You're a devil for fighting and will surely win."
}

def convert_to_wav(input_path: str, output_path: str):
    subprocess.run(["ffmpeg", "-y", "-i", input_path, output_path], check=True)

app = FastAPI()
UPLOAD_DIR = "uploads"
IMAGE_DIR = "static/image"
PDF_DIR = "output"
AUDIO_DIR = os.path.join(PDF_DIR, "audio")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/download_pdf/{filename}", response_class=FileResponse)
def download_pdf(filename: str):
    pdf_path = os.path.join(PDF_DIR, filename)
    return FileResponse(path=pdf_path, filename=filename, media_type="application/pdf")

@app.get("/download_audio/{filename}", response_class=FileResponse)
def download_audio(filename: str):
    audio_path = os.path.join(AUDIO_DIR, filename)
    return FileResponse(path=audio_path, filename=filename, media_type="audio/wav")

@app.post("/analyze/", response_class=HTMLResponse)
async def analyze(
    request: Request,
    file: UploadFile = File(...),
    reference: str = Form(...),
    mel_path: str = Form(...),
    speaker_name: str = Form(...),
    mode: str = Form(...)
):
    session_id = str(uuid4())[:8]
    original_path = os.path.join(UPLOAD_DIR, f"{session_id}_{file.filename}")

    with open(original_path, "wb") as f_out:
        shutil.copyfileobj(file.file, f_out)

    ext = Path(file.filename).suffix.lower()
    if ext != ".wav":
        wav_path = os.path.join(UPLOAD_DIR, f"{session_id}.wav")
        convert_to_wav(original_path, wav_path)
    else:
        wav_path = original_path

    reference_text = REFERENCE_TEXTS.get(reference, "")
    azure_result = assess_pronunciation(wav_path, reference_text)

    similarity_score, feedback, plot_path, highlighted_sentence = evaluate_wav(
        wav_path=wav_path,
        session_id=session_id,
        pron_json=azure_result,
        sentence=reference_text,
        l1_mel_path=mel_path
    )

    # 📄 PDF 생성
    pdf_filename = f"{speaker_name}_{mode}_{session_id}_result.pdf"
    pdf_path = os.path.join(PDF_DIR, pdf_filename)

    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("result_for_pdf.html")
    rendered_html = template.render(
        score=f"{similarity_score:.2f}",
        feedback=feedback,
        plot_path=os.path.abspath(plot_path),
        speaker=speaker_name,
        mode=mode
    )
    HTML(string=rendered_html, base_url=".").write_pdf(pdf_path)

    # 🎧 사용자 음성도 저장 (다운로드용)
    audio_filename = f"{speaker_name}_{mode}_{session_id}.wav"
    audio_path = os.path.join(AUDIO_DIR, audio_filename)
    shutil.copy(wav_path, audio_path)

    return templates.TemplateResponse("result.html", {
        "request": request,
        "azure": azure_result,
        "junseo": {
            "similarity_score": similarity_score,
            "intonation_feedback": feedback
        },
        "highlighted_text": highlighted_sentence,
        "intonation_plot": plot_path,
        "pdf_path": f"/download_pdf/{pdf_filename}",
        "audio_path": f"/download_audio/{audio_filename}"
    })
