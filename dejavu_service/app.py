from flask import Flask, request, jsonify, make_response
from dejavu_config import djv
from dejavu.logic.recognizer.file_recognizer import FileRecognizer
import requests
import os

app = Flask(__name__)

os.makedirs('audio', exist_ok=True)

@app.route("/feed-audio-to-dejavu/", methods=['GET'])
def feed_audio_to_dejavu():
    songs_folder = os.path.join(app.root_path, "media", "songs")
    djv.fingerprint_directory(songs_folder, [".wav", ".mp3"])
    return make_response(jsonify({'message': 'Audio Fingerprint created in database'}))

@app.route("/check-song/", methods=['POST'])
def identify_song():
    try:
        data = request.get_json()
        audio_file_path = data['audio_file_path']
        media_url = f"http://django:8000{audio_file_path}"
        file_name = audio_file_path.split('/')[-1]  
        response = requests.get(media_url)
        
        if response.status_code == 200:
            file_to_recognize = f"audio/{file_name}"
            with open(file_to_recognize, "wb") as f:
                f.write(response.content)

            recognizer = FileRecognizer(djv)
            results = recognizer.recognize_file(file_to_recognize)

            max_hashes_matched = 0
            max_hashes_mateched_song_name = ""
            for result in results['results']:
                print(result, '----------------------')
                if result['hashes_matched_in_input'] > max_hashes_matched:
                    max_hashes_matched = result['hashes_matched_in_input']
                    max_hashes_mateched_song_name = result['song_name']
            if os.path.exists(file_to_recognize):
                os.remove(file_to_recognize)
            return make_response(jsonify({
                'status': True,
                'message': '',
                'payload': {
                    'song_name': max_hashes_mateched_song_name.decode('utf-8') 
                }
            }))
        else:
            return make_response(jsonify({
                'status': False,
                'message': 'Audio file not found'
            }))
    except Exception as e:
        print(">>>>>>>>>>>flask error", e)
        return make_response(jsonify({
            'status': False,
            'message': 'flask error >>>> ' + str(e)
        }))