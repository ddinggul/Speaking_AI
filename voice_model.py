import os
import re
import numpy as np
import librosa
import matplotlib.pyplot as plt
from matplotlib import font_manager
import json
from datetime import datetime


# 한글 폰트 설정
font_path = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
font_manager.fontManager.addfont(font_path)
plt.rcParams['font.family'] = 'AppleGothic'

# L1 평균 Mel 곡선
L1_MEL_PATH = "spectrogram/L1/5_L1_mels.npy"

def extract_mel_curve(wav_path, sr=16000):
    y, _ = librosa.load(wav_path, sr=sr)
    mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=80)
    mel_db = librosa.power_to_db(mel, ref=np.max)
    return mel_db.mean(axis=0)

def cosine_similarity(v1, v2):
    min_len = min(len(v1), len(v2))
    v1, v2 = v1[:min_len], v2[:min_len]
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8)

def plot_pitch_contours(l2_curve, l1_curve, save_path):
    min_len = min(len(l2_curve), len(l1_curve))
    l2_curve, l1_curve = l2_curve[:min_len], l1_curve[:min_len]

    plt.figure(figsize=(10, 4))
    plt.plot(l1_curve, label="L1 평균 억양 곡선", linewidth=2)
    plt.plot(l2_curve, label="당신의 억양 곡선", linewidth=2)
    plt.title("억양 곡선 비교")
    plt.xlabel("시간 프레임")
    plt.ylabel("Mel dB")
    plt.legend(loc="upper right")
    plt.tight_layout()

    plt.savefig(save_path)
    plt.close()


def evaluate_wav(wav_path, session_id, pron_json, sentence, l1_mel_path):
    import html

    # Pitch curve
    user_curve = extract_mel_curve(wav_path)
    L1_curve = np.load(l1_mel_path).mean(axis=0)  # ✅ 동적으로 전달받은 Mel 경로 사용
    sim = cosine_similarity(user_curve, L1_curve)

    feedback = (
        "대단해요! 원어민과 거의 동일한 억양이에요." if sim > 0.95 else
        "좋아요! 억양이 자연스러워요." if sim > 0.85 else
        "조금 더 억양에 신경 써보세요." if sim > 0.7 else
        "억양 차이가 커요. 원어민 억양을 더 따라해보세요."
    )

    # 시각화 저장
    filename = f"{session_id}_intonation.png"
    save_path = os.path.join("static/image", filename)
    plot_path = f"/static/image/{filename}"
    plot_pitch_contours(user_curve, L1_curve, save_path)

    # 문장 및 문제 음소 기반 하이라이팅
    recognized_text = pron_json.get("text", "").strip()
    highlighted = ""

    # 🔴 문제 음소 목록 소문자화
    problematic_phones = set(
        p["phoneme"].lower()
        for p in pron_json.get("problematic_phonemes", [])
        if p["score"] < 60
    )

    if recognized_text and problematic_phones:
        words = recognized_text.split()
        highlighted_words = []

        for word in words:
            lowered = word.lower()
            if any(p in lowered for p in problematic_phones):
                highlighted_words.append(f"<span style='color:red;font-weight:bold'>{html.escape(word)}</span>")
            else:
                highlighted_words.append(html.escape(word))

        highlighted = " ".join(highlighted_words)

        phoneme_list = ", ".join(
            f"<span style='color:red'>{html.escape(p['phoneme'])}</span>({int(p['score'])}점)"
            for p in pron_json["problematic_phonemes"] if p["score"] < 60
        )
        highlighted += f"<br><span style='color:gray;'>※ 문제 음소: {phoneme_list}</span>"

    elif recognized_text:
        highlighted = html.escape(recognized_text)

    else:
        highlighted = "<i style='color:gray;'>발화 인식 실패 – 음성이 제대로 인식되지 않았습니다.</i>"

    return round(sim * 100, 2), feedback, plot_path, highlighted





