import azure.cognitiveservices.speech as speechsdk
import json
from config import AZURE_KEY, REGION

def assess_pronunciation(wav_path: str, reference_text: str):
    speech_config = speechsdk.SpeechConfig(subscription=AZURE_KEY, region=REGION)
    audio_config = speechsdk.audio.AudioConfig(filename=wav_path)

    pronunciation_config = speechsdk.PronunciationAssessmentConfig(
        reference_text=reference_text,
        grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
        granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme,
        enable_miscue=True
    )

    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    pronunciation_config.apply_to(recognizer)

    result = recognizer.recognize_once()
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        pron_result = speechsdk.PronunciationAssessmentResult(result)

        # JSON 상세 응답 추출
        detail_json = result.properties.get(speechsdk.PropertyId.SpeechServiceResponse_JsonResult)
        detail = json.loads(detail_json)

        phoneme_scores = []
        try:
            words = detail["NBest"][0]["Words"]
            for word in words:
                for phoneme in word.get("Phonemes", []):
                    score = phoneme["PronunciationAssessment"]["AccuracyScore"]
                    symbol = phoneme["Phoneme"]
                    if score < 70:  # 기준 미달 음소만 추출
                        phoneme_scores.append({"phoneme": symbol, "score": round(score, 1)})
        except Exception as e:
            print(f"[⚠️ parsing error] {e}")

        return {
            "accuracy": pron_result.accuracy_score,
            "fluency": pron_result.fluency_score,
            "completeness": pron_result.completeness_score,
            "pronunciation": pron_result.pronunciation_score,
            "text": result.text,
            "problematic_phonemes": phoneme_scores
        }
    else:
        return {"error": "음성 인식 실패 또는 평가 불가"}
