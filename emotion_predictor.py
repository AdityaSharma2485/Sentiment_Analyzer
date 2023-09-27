from keras.models import model_from_json
import librosa
import numpy as np
from sklearn.preprocessing import LabelEncoder
import pickle
import pandas as pd

def predict_emotion(audio_file_path):
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
    # Example usage when running the script as the main program
    audio_file_path = 'E:\My_Projects\SIH\Call_Analyzer\Emotions\Angry_emotion.wav'
    predicted_emotion = predict_emotion(audio_file_path)
    print("Predicted emotion:", predicted_emotion)
