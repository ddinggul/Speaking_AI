# 🗣️ Speaking AI: 영어 발음 및 억양 평가 웹앱

AI 기반으로 영어 학습자의 음성을 분석하여 **발음 정확도와 억양 유사도**를 시각적으로 제공하는 웹 애플리케이션입니다.


---

## 📌 주요 기능

- ✅ Azure 기반 **발음 평가 API** 활용 (정확도, 유창성, 완전성 등 점수 제공)
- ✅ 사용자 음성의 **Mel-spectrogram 곡선**을 생성하고 원어민 평균 곡선과 비교
- ✅ 문제가 감지된 단어 및 음소를 **하이라이트 처리**
- ✅ 5개 L1 기준 문장 선택 → 각각의 L1 Mel 평균 곡선 비교 가능
- ✅ 전체 다크 모드 + 프리미엄 서체 UI 디자인

---

## 🧪 데모 사용법

1. `.wav` 포맷의 영어 발음 파일을 업로드
2. 기준 문장을 선택 (예: `You're a devil for fighting and will surely win.`)
3. ▶️ 분석 시작 → 결과 페이지 자동 생성

---

## 🖼️ 예시 결과 화면

> 인식된 문장과 문제 음소 하이라이트  
> 억양 곡선 시각화 등 시멘틱 피드백 제공

![Demo](https://github.com/ddinggul/Speaking_AI/blob/main/demo.png?raw=true)

---

## ⚙️ 설치 및 실행 방법

```bash
# 1. 클론 후 진입
git clone https://github.com/ddinggul/Speaking_AI.git
cd Speaking_AI

# 2. 가상환경 & 패키지 설치
python -m venv venv
source venv/bin/activate  # Windows는 venv\Scripts\activate
pip install -r requirements.txt

# 3. 환경변수 설정 (.env)
AZURE_SPEECH_KEY=YOUR_KEY
AZURE_REGION=YOUR_REGION

# 4. 서버 실행
uvicorn app:app --reload
```
---

## 🧩 프로젝트 구조

```bash
.
├── app.py # FastAPI 서버
├── azure_eval.py # Azure 평가 로직
├── voice_model.py # Mel 곡선 비교 및 시각화
├── templates/result.html # 결과 템플릿
├── static/
│ ├── index.html # 첫 화면
│ ├── css/style.css # 스타일
│ └── image/ # 생성된 시각화 이미지
├── spectrogram/L1/ # 기준 Mel 곡선 (1~5)
├── uploads/ # 사용자 음성 업로드
└── requirements.txt
```
---

---

## 🔐 보안 주의
- `.env`, `config.py`는 반드시 `.gitignore`에 포함해야 합니다.
- `AZURE_SPEECH_KEY` 등 민감정보는 절대 GitHub에 업로드하지 마세요.

---

## 📚 사용 기술

- **FastAPI + Jinja2** – 웹 프레임워크
- **Azure Speech SDK** – 발음 평가 API
- **Librosa / Matplotlib / Numpy** – 음향 분석 및 시각화
- **HTML / CSS** – 사용자 인터페이스 (다크 테마)

---

## 📬 개발자

- **최준서** (한성대학교 영미언어정보트랙 / AI응용학과 / 한국어교육트랙)  
- 📫 Instagram: [@2dinggul_myroom](https://instagram.com/2dinggul_myroom)
- 📧 Email: [litterrariuschwy@gmail.com](mailto:litterrariuschwy@gmail.com)
