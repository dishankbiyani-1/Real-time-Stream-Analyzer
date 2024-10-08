from stream_app.models import StreamChunk, Stream, Song
from stream_app.dejavu_flask_api_url import API_URL_FOR_IDENTIFY_SONG_IN_AUDIO_FILE

from django.conf import settings

import torch
from transformers import pipeline, AutoModelForSpeechSeq2Seq, AutoProcessor

from datetime import datetime
import threading
import queue
import time
import subprocess
import os
import requests
import json

STREAM_DATA = {}
os.makedirs(os.path.join(settings.MEDIA_ROOT, 'stream_chunks'), exist_ok=True)


class ModelInitializer:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        model_id = "distil-whisper/distil-large-v3"

        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
        )
        self.model.to(device)

        self.processor = AutoProcessor.from_pretrained(model_id)

        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=self.model,
            tokenizer=self.processor.tokenizer,
            feature_extractor=self.processor.feature_extractor,
            max_new_tokens=128,
            chunk_length_s=15,
            batch_size=16,
            torch_dtype=torch_dtype,
            device=device,
        )


def get_model_initializer():
    return ModelInitializer()


def audio_to_text(queue, control):
    try:
        model_initializer = get_model_initializer()
        pipe = model_initializer.pipe
        while True:
            if queue.empty() or control.get("stop", False):
                break
            else:
                output_file_mp3, stream_chunk_id = queue.get_nowait()
                
            result = pipe(output_file_mp3)
            stream_chunk = StreamChunk.objects.get(pk=stream_chunk_id)
            stream_chunk.audio_text=result["text"]
            stream_chunk.audio_file_path = None
            stream_chunk.save()

            if os.path.exists(output_file_mp3):
                os.remove(output_file_mp3)
            queue.task_done()
    except Exception as e:
        print(f"Error in audio_to_text: {e}")

def identify_song_in_audio(audio_file_path):
    data = {"audio_file_path": audio_file_path}
    response = requests.post(
        API_URL_FOR_IDENTIFY_SONG_IN_AUDIO_FILE, 
        data=json.dumps(data), 
        headers={'Content-Type': 'application/json'}
    )
    response_json = response.json()
    if response_json['status'] is True:
        song_name = response_json['payload']['song_name']
        song = Song.objects.filter(file__contains=song_name).first()
        if song:
            return song.pk
    return None

# Function to capture and record stream
def capture_stream(stream, queue, control, duration=120, prefix="stream"):
    try:
        while control.get("stop", False) is False:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            media_folder_path = os.path.join('media', 'stream_chunks', f"{prefix}_{timestamp}.mp3")
            output_file = os.path.join(settings.BASE_DIR, media_folder_path)

            cmd = [
                'ffmpeg',
                '-i', stream.get('url'),
                '-acodec', 'libmp3lame',
                '-ab', '128k',
                '-t', str(duration),
                output_file
            ]
            kwargs = dict(
                check=True, 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.STDOUT
            )
            subprocess.run(cmd, **kwargs)

            id = stream.get("id")
            audio_file_path = f"/{media_folder_path}"
            stream_chunk = StreamChunk.objects.create(stream_id=id, audio_file_path=audio_file_path)
            song_pk = identify_song_in_audio(audio_file_path)
            if song_pk is not None:
                stream_chunk.song_id = song_pk
                stream_chunk.save()
            queue.put((output_file, stream_chunk.id))
        print("Stream stopped successfully")
    except Exception as e:
        print(f"Error capturing stream: {e}")


def start_capture_stream_in_chunks(stream_data, duration=settings.AUDIO_FILE_DURATION, max_workers=2):
    """
        stream_data = {
            "id": 1,
            "url": 'http://example.com',
            "slug": "asdad76ahskjadsjah8787"
        }
    """
    q = queue.Queue()
    audio_process_control = {"stop": False}
    audio_process_thread = threading.Thread(target=audio_to_text, args=(q, audio_process_control))
    audio_process_thread.start()
    stream_control = {"stop": False}
    stream_thread = threading.Thread(target=capture_stream, args=(stream_data, q, stream_control, duration))
    stream_thread.start()
    STREAM_DATA[stream_data["id"]] = {
        "q": q,
        "audio_process_control": audio_process_control,
        "stream_control": stream_control
    }

def stop_stream(id):
    stream_obj = STREAM_DATA[id]
    q = stream_obj["q"]
    audio_process_control = stream_obj["audio_process_control"]
    stream_control = stream_obj["stream_control"]
    stream_control["stop"]=True
    q.join()
    audio_process_control["stop"]=True

def stop_stream_async(id):
    threading.Thread(target=stop_stream, args=(id,)).start()
