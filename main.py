from flask import Flask, render_template, request, send_file
import os
from tts_with_rvc import TTS_RVC
import asyncio

app = Flask(__name__, static_folder='static')

# Функция для получения списка доступных моделей
def get_available_models():
    models_dir = "models"
    models = []
    for file in os.listdir(models_dir):
        if file.endswith('.pth'):
            models.append(file)
    return models

# Инициализация TTS_RVC
tts = TTS_RVC(rvc_path="src\\rvclib", 
              model_path="models\\DenVot13800.pth",  # дефолтная модель
              input_directory="input\\")
tts.set_voice("ru-RU-DmitryNeural")

# Создаем папки для временных файлов, если их нет
os.makedirs("temp", exist_ok=True)
os.makedirs("uploads", exist_ok=True)
os.makedirs("models", exist_ok=True)
os.makedirs("input", exist_ok=True)
os.makedirs("logs", exist_ok=True)


def get_available_indices():
    indices_dir = "logs"  # или другая папка где хранятся индексы
    indices = []
    for file in os.listdir(indices_dir):
        if file.endswith('.index'):
            indices.append(file)
    return indices

@app.route('/')
def index():
    models = get_available_models()
    indices = get_available_indices()
    return render_template('index.html', models=models, indices=indices)


@app.route('/process_tts', methods=['POST'])
def process_tts():
    try:
        text = request.form['text']
        pitch = int(request.form['pitch'])
        selected_model = request.form['model']
        index_path = request.form['index_path']
        index_rate = float(request.form['index_rate'])

        tts.current_model = os.path.join("models", selected_model)
        if index_path:
            tts.index_path = os.path.abspath(os.path.join("logs", index_path))
            print("Index path:", tts.index_path)
        
        path = tts(
            text=text,
            pitch=pitch,
            index_rate=index_rate
        )
        return send_file(path, as_attachment=True)
    except Exception as e:
        return str(e), 500

@app.route('/process_audio', methods=['POST'])
def process_audio():
    if 'audio' not in request.files:
        return 'No file uploaded', 400
        
    file = request.files['audio']
    pitch = int(request.form['pitch'])
    selected_model = request.form['model']
    index_path = request.form['index_path']
    index_rate = float(request.form['index_rate'])
    
    if file.filename == '':
        return 'No selected file', 400
        
    tts.current_model = os.path.join("models", selected_model)
    if index_path:
        tts.index_path = os.path.abspath(os.path.join("logs", index_path))
        print("Index path:", tts.index_path)
    
    input_path = os.path.join('uploads', file.filename)
    file.save(input_path)
    
    output_path = tts.speech(
        input_path=input_path,
        pitch=pitch,
        index_rate=index_rate
    )
    
    os.remove(input_path)
    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)