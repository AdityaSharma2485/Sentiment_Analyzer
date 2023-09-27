import pyaudio
import wave
import os
import numpy as np
import librosa
import pandas as pd
import pickle
from keras.models import model_from_json
from sklearn.preprocessing import LabelEncoder
from threading import Thread
import time

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1  # Mono audio recording
RATE = 44100
WAVE_OUTPUT_FILENAME = "output01.wav"

RECORDING_BATCH_DURATION = 5  # Duration of each audio batch in seconds

# Load the LabelEncoder and its mapping
with open('E:\My_Projects\SIH\Call_Analyzer\label_encoder.pkl', 'rb') as label_encoder_file:
    label_encoder = pickle.load(label_encoder_file)

# Load the one-hot encoded labels
with open('E:\My_Projects\SIH\Call_Analyzer\y_train_onehot.pkl', 'rb') as onehot_file:
    y_train_onehot = pickle.load(onehot_file)

# Load the model architecture from a JSON file
json_file = open('E:\My_Projects\SIH\Call_Analyzer\model.json', 'r')
loaded_model_json = json_file.read()
json_file.close()

# Create the model from the JSON architecture
loaded_model = model_from_json(loaded_model_json)

# Load the model weights
loaded_model.load_weights("E:\My_Projects\SIH\Call_Analyzer\saved_models\Emotion_Voice_Detection_Model.h5")

class AudioRecorder:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.frames = []
        self.recording = False

    def start_recording(self):
        self.stream = self.p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        self.frames = []
        self.recording = True

    def stop_recording(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        self.recording = False

    def record_audio(self):
        while self.recording:
            data = self.stream.read(CHUNK)
            self.frames.append(data)

    def save_audio(self, filename):
        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()

def predict_emotion_from_audio_batch(audio_batch):
    # Load and process the audio file
    X, sample_rate = librosa.load(audio_file_path, res_type='kaiser_fast', duration=2.5, sr=22050*2, offset=0.5)
    sample_rate = np.array(sample_rate)

    # Extract MFCC features from the audio
    mfccs = np.mean(librosa.feature.mfcc(y=X, sr=sample_rate, n_mfcc=13), axis=0)
    featurelive = mfccs
    livedf2 = featurelive

    # Convert features to a DataFrame
    livedf2 = pd.DataFrame(data=livedf2)
    livedf2 = livedf2.stack().to_frame().T

    # Reshape the feature
    twodim = np.expand_dims(livedf2, axis=2)

    # Make predictions using the loaded model
    livepreds = loaded_model.predict(twodim, batch_size=32, verbose=1)

    # Convert predictions to labels
    livepreds1 = livepreds.argmax(axis=1)

    # Define a mapping from specific labels to generic emotion labels
    emotion_mapping = {
        'female_angry': 'Angry',
        'female_calm': 'Calm',
        'female_fearful': 'Fearful',
        'female_happy': 'Happy',
        'female_sad': 'Sad',
        'male_angry': 'Angry',
        'male_calm': 'Calm',
        'male_fearful': 'Fearful',
        'male_happy': 'Happy',
        'male_sad': 'Sad'
    }

    # Get the predicted class index
    predicted_class_index = livepreds1[0]

    # Map the class index to the predicted label
    predicted_label = label_encoder.inverse_transform([predicted_class_index])[0]

    cleaned_label = predicted_label.strip("[]'")
    # Get the generic emotion label from the mapping
    generic_emotion_label = emotion_mapping[cleaned_label]

    return generic_emotion_label

if __name__ == "__main__":
    recorder = AudioRecorder()
    recording_thread = Thread(target=recorder.record_audio)

    try:
        print("Press 'q' to stop recording.")
        recorder.start_recording()
        recording_thread.start()

        while True:
            # Record audio in batches of 2 seconds
            time.sleep(RECORDING_BATCH_DURATION)
            
            # Process and predict emotions for the last recorded batch
            predicted_emotion = predict_emotion_from_audio_batch(recorder.frames)
            print("Predicted emotion for the batch:", predicted_emotion)
            
            # Clear the recorded frames for the next batch
            recorder.frames = []
            
            # Stop recording when 'q' is pressed
            if input() == 'q':
                break

        recorder.stop_recording()
        recording_thread.join()

        # Save the overall audio in .wav format
        recorder.save_audio(WAVE_OUTPUT_FILENAME)

        # Process and predict emotions from the saved audio file
        predicted_emotion = predict_emotion_from_audio_batch(WAVE_OUTPUT_FILENAME)
        print("Predicted emotion for the overall audio:", predicted_emotion)

    except KeyboardInterrupt:
        pass
