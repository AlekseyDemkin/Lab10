import pyttsx3
import pyaudio
import vosk
import requests
import json
from translate import Translator


def speak(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.say(text)
    engine.runAndWait()


def listen():
    model = vosk.Model('vosk-model-small-ru-0.4')
    rec = vosk.KaldiRecognizer(model, 8000)

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=8000, input=True, frames_per_buffer=8000)

    print("Говорите...")
    stream.start_stream()

    while True:
        data = stream.read(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data) and len(data) > 0:
            answer = json.loads(rec.Result())
            if answer['text']:
                return answer['text']


def get_random_activity():
    response = requests.get('https://www.boredapi.com/api/activity')
    data = response.json()
    activity = data['activity']
    return activity, data


def save_to_file(text):
    with open('assistant.txt', 'w') as file:
        file.write("Предлагаю вам заняться: " + str(activity) + ", вам потребуется " +
                   str(data['participants']) + " человек(а)" + " и " + str(data['price']) + " евро.")
    print("Файл сохранен.")


def translate_text(text):
    translator = Translator(from_lang='english', to_lang='russian')
    translation = translator.translate(text)
    return translation


r = pyttsx3.init('sapi5')
voices = r.getProperty('voices')
r.setProperty('voices', 'ru')

while True:
    result = listen()
    command = result

    if 'случайный' in command:
        activity, data = get_random_activity()
        activity = translate_text(activity)
        print("Предлагаю вам заняться: " + activity)
        speak("Предлагаю вам заняться: " + activity)
        print()

    elif 'цена' in command:
        price = data['price']
        print("Вам потребуется: " + str(price) + " евро")
        speak("Вам потребуется: " + str(price) + " евро")

    elif 'участники' in command:
        participants = data['participants']
        print("Для этого занятия потребуется " + str(participants) + " человек.")
        speak("Для этого занятия потребуется " + str(participants) + " человек.")

    elif 'далее' in command:
        next_activity, data = get_random_activity()
        next_activity = translate_text(next_activity)
        print("Следующее занятие: " + next_activity)
        speak("Следующее занятие: " + next_activity)

    elif 'сохранить' in command:
        save_to_file(command)
        print("Файл успешно сохранен.")
        speak("Файл успешно сохранен.")

    elif 'выход' in command or 'пока' in command:
        print('выход')
        break

    else:
        print("Команда не распознана. Повторите, пожалуйста.")
