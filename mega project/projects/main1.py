import speech_recognition as sr
import webbrowser # direct from web
import pyttsx3 # text to speech
import time
import Musiclib
import requests
from openai import OpenAI
from gtts import gTTS
import pygame
import os


# pip install pocket sphinx
recognizer = sr.Recognizer() 
newsapi = "8ef9173616bf4588bec40cf84c4413d2"

# Use pyttsx3 (offline) for TTS by default; fall back to gTTS+pygame if pyttsx3 fails
try:
    _tts_engine = pyttsx3.init()
except Exception:
    _tts_engine = None

def speak(text):
    """Speak text: prefer pyttsx3 (offline). If that fails, use gTTS + pygame as a fallback."""
    global _tts_engine
    if _tts_engine:
        try:
            _tts_engine.say(text)
            _tts_engine.runAndWait()
            return
        except Exception as e:
            print("pyttsx3 failed, falling back to gTTS/pygame:", e)

    # Fallback to gTTS + pygame
    try:
        tts = gTTS(text=text, lang='en')
        tmp = "temp_tts.mp3"
        tts.save(tmp)
        try:
            pygame.mixer.init()
        except Exception:
            # if mixer init fails, try quitting and reinitializing
            try:
                pygame.mixer.quit()
                pygame.mixer.init()
            except Exception as e:
                print("pygame mixer init failed:", e)
        pygame.mixer.music.load(tmp)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        try:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except Exception:
            pass
        try:
            os.remove(tmp)
        except Exception:
            pass
    except Exception as e:
        print("Fallback TTS (gTTS/pygame) failed:", e)

def speak_old(text):
    # Reinitialize each time to avoid audio lock
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    engine.stop()

def aiProcess(command):
    client = OpenAI(api_key="<sk-1234uvwxabcd5678uvwxabcd1234uvwxabcd5678>",
    )

    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a virtual assistant named jarvis skilled in general tasks like Alexa and Google Cloud. Give short responses please"},
        {"role": "user", "content": command}
    ]
    )

    return completion.choices[0].message.content
def processCommand(c):
    c = c.lower()
    if "open google" in c:
        webbrowser.open("https://google.com")
        speak("Opening Google")
    elif "open facebook" in c:
        webbrowser.open("https://facebook.com")
        speak("Opening Facebook")
    elif "open netflix" in c:
        webbrowser.open("https://netflix.com")
        speak("Opening Netflix")
    elif "open youtube" in c:
        webbrowser.open("https://youtube.com")
        speak("Opening YouTube")
    elif "open linkedin" in c:
        webbrowser.open("https://linkedin.com")
        speak("Opening LinkedIn")
    elif "open hotstar" in c:
        webbrowser.open("https://hotstar.com")
        speak("Opening Hotstar")
    elif "open chatgpt" in c:
        webbrowser.open("https://chatgpt.com/")
        speak("Opening ChatGPT")
    elif "open gemini" in c:
        webbrowser.open("https://gemini.google.com/")
        speak("Opening Gemini")
    elif c.startswith("play "):
        # support multi-word song names: everything after 'play '
        song = c[5:].strip()
        link = Musiclib.music.get(song)
        if link:
            speak(f"Playing {song}")
            webbrowser.open(link)
        
    elif "news" in c:
        try:
            r = requests.get(f"https://newsapi.org/v2/everything?q=keyword&apiKey={newsapi}")
            if r.status_code == 200:
                data = r.json()
                articles = data.get('articles', [])
                for article in articles[:5]:
                    speak(article.get('title', 'No title'))
            else:
                speak("Could not fetch news")
        except Exception as e:
            print("News fetch failed:", e)
            speak("Failed to fetch news")
    else:
        output = aiProcess(c)
        speak(output)
        # speak("Sorry Nilesh, I didn't understand that command.")
        

if __name__ == "__main__":
    speak("Initializing Jarvis....")
    time.sleep(1)
    while True:
        # Listen for the wake word "Jarvis"
        # obtain audio from the microphone
        r = sr.Recognizer()
         
        print("recognizing...")
        try:
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source, duration=0.5)
                print("Listening for wake word...")
                try:
                    audio = r.listen(source, timeout=3, phrase_time_limit=4)
                except sr.WaitTimeoutError:
                    print("No input detected (wake) - timeout")
                    continue

            try:
                word = r.recognize_google(audio)
                print("you said:", word)
            except sr.UnknownValueError:
                print("Could not understand wake word")
                continue
            except sr.RequestError as e:
                print("Google API RequestError:", e)
                time.sleep(1)
                continue

            if "jarvis" in word.lower():
                speak("Yes")
                print("Jarvis Active...")
                # Listen for command
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    print("Listening for command...")
                    try:
                        audio_cmd = r.listen(source, timeout=5, phrase_time_limit=8)
                    except sr.WaitTimeoutError:
                        print("No command detected - timeout")
                        continue

                try:
                    command = r.recognize_google(audio_cmd)
                    print("command:", command)
                    processCommand(command)
                except sr.UnknownValueError:
                    print("Could not understand command")
                    speak("Sorry, I didn't get that.")
                except sr.RequestError as e:
                    print("Google API RequestError (command):", e)
                    speak("Speech service error, check internet.")

        except OSError as e:
            print("Microphone/device error:", e)
            break
        except Exception as e:
            print("Unexpected error:", e)
            time.sleep(1)
