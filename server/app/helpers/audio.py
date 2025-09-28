import uuid
import os
from fastapi import UploadFile


import subprocess

def convert_to_pcm_wav(input_path: str, output_path: str):
    # Use ffmpeg to convert audio to 16kHz, 16-bit, mono PCM WAV
    command = [
        "ffmpeg",
        "-i", input_path,
        "-ar", "16000",
        "-ac", "1",
        "-f", "wav",
        "-sample_fmt", "s16",
        output_path
    ]
    subprocess.run(command, check=True)


def save_temp_file(upload_file: UploadFile) -> str:
    """
    Saves an uploaded file to a temporary location and returns the file path.
    """
    temp_filename = f"{uuid.uuid4()}.wav"
    with open(temp_filename, "wb") as f:
        f.write(upload_file.file.read())
    return temp_filename

def delete_temp_file(filename: str) -> None:
    """
    Deletes the temporary file if it exists.
    """
    if os.path.exists(filename):
        os.remove(filename)
