import os
from dotenv import load_dotenv
import speech_recognition as sr
from transformers import pipeline
import openai

# Loading the SENTIMENT ANALYSIS MODEL
sent_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

# Loading the OPENAI API
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

class AudioAnalyzer:
    def __init__(self):
        pass

    @staticmethod
    def audio_to_text(audio_file_path):
        recognizer = sr.Recognizer()

        # Load the audio file
        with sr.AudioFile(audio_file_path) as source:
            audio_data = recognizer.record(source)

        try:
            # Use Google Web Speech API for speech recognition
            text = recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError as e:
            raise ValueError("Google Web Speech API could not understand the audio") from e
        except sr.RequestError as e:
            raise ConnectionError(f"Could not request results from Google Web Speech API: {e}") from e

    @staticmethod
    def sent_on_text(sample_sentence):
        result = sent_pipeline(sample_sentence)
        return result

    @staticmethod
    def text_summarizer(prompt):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "you are a text summarizer (short and simple)"},
                {"role": "user", "content": prompt}
            ]
        )
        return response['choices'][0]['message']['content']

    @staticmethod
    def insights_from_gpt(prompt):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "analyse the given text and do 3 things for me, first answer yes or no is the customer is satisfied or not, second identify potential issues, third highlight areas for improvement. Now answer second, third with just some pointers and make it to the point (short and simple)."},
                {"role": "user", "content": prompt}
            ]
        )
        return response['choices'][0]['message']['content']

def main():
    audio_file_path = "C:\\Users\\adity\\Downloads\\input.wav"
    analyzer = AudioAnalyzer()
    speech_to_text = analyzer.audio_to_text(audio_file_path)
    print(f"Text from audio file:\n{speech_to_text}")
    sentiment_on_text = analyzer.sent_on_text(speech_to_text)
    print(f"Sentiment of the text:\n{sentiment_on_text}")
    summarized_text = analyzer.text_summarizer(speech_to_text)
    print(f"Text in summarized format:\n{summarized_text}")
    insights_from_text = analyzer.insights_from_gpt(speech_to_text)
    print(f"Valuable insights:\n{insights_from_text}")
    
if __name__ == "__main__":
    main()
