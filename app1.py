from flask import Flask, request, render_template, redirect, url_for
import speech_recognition as sr
import os
import google.generativeai as genai

app = Flask(__name__)

# Configure GenAI with API key from environment variable
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', "YOUR_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

def create_recognizer():
    return sr.Recognizer()

def process_audio_file(file_path):
    recognizer = create_recognizer()

    try:
        with sr.AudioFile(file_path) as source:
            audio_data = recognizer.record(source)

        text = recognizer.recognize_google(audio_data)

        model = genai.GenerativeModel('gemini-1.5-flash')
        response1 = model.generate_content(f"Transcripted text: {text}. Now generate a response.")
        generated_text1 = response1.text

        prompt = f"Listen to this conversation: {text} and generate for me a response on the possible diagnosis of the illness in English"
        response2 = model.generate_content(prompt)
        generated_text2 = response2.text

        return generated_text1, generated_text2

    except sr.UnknownValueError:
        return "Speech Recognition could not understand the audio", None
    except sr.RequestError as e:
        return f"Could not request results; {e}", None
    except Exception as e:
        return f"Error: {e}", None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    if file:
        file_path = os.path.join("uploads", file.filename)
        file.save(file_path)

        generated_text1, generated_text2 = process_audio_file(file_path)

        return render_template('result.html', transcript=generated_text1, response=generated_text2)

# Ensure this is the exact line:
if __name__ == '__main__':
    app.run(debug=True)

