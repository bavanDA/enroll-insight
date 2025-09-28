from fastapi import APIRouter, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from app.config import Config
from app.helpers.audio import save_temp_file, delete_temp_file, convert_to_pcm_wav

import azure.cognitiveservices.speech as speechsdk
import uuid
import os

router = APIRouter()

@router.post("/speech/text-to-speech")
async def synthesize_speech(text: str = Form(...)):
    if not Config.AZURE_SPEECH_KEY or not Config.AZURE_SPEECH_ENDPOINT:
        raise HTTPException(status_code=503, detail="Azure Speech credentials not configured.")

    speech_config = speechsdk.SpeechConfig(
        subscription=Config.AZURE_SPEECH_KEY,
        endpoint=Config.AZURE_SPEECH_ENDPOINT
    )


    os.makedirs("files", exist_ok=True)

    output_filename = f"files/{uuid.uuid4()}.wav"
    audio_config = speechsdk.audio.AudioOutputConfig(filename=output_filename)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    result = synthesizer.speak_text_async(text).get()
    if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
        raise HTTPException(status_code=500, detail="Speech synthesis failed.")

    return FileResponse(output_filename, media_type="audio/wav", filename="speech.wav")


@router.post("/speech/speech-to-text")
async def transcribe_speech(file: UploadFile):
    if not Config.AZURE_SPEECH_KEY or not Config.AZURE_SPEECH_ENDPOINT:
        raise HTTPException(status_code=503, detail="Azure Speech credentials not configured.")

    original_path = save_temp_file(file)
    converted_path = f"{original_path}.converted.wav"
    try:
        convert_to_pcm_wav(original_path, converted_path)

        speech_config = speechsdk.SpeechConfig(
            subscription=Config.AZURE_SPEECH_KEY,
            endpoint=Config.AZURE_SPEECH_ENDPOINT
        )
        audio_input = speechsdk.audio.AudioConfig(filename=converted_path)
        recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)

        result = recognizer.recognize_once_async().get()

        if result.reason != speechsdk.ResultReason.RecognizedSpeech:
            raise HTTPException(status_code=500, detail="Speech recognition failed.")

        return {"transcript": result.text}
    finally:
        delete_temp_file(original_path)
        delete_temp_file(converted_path)
