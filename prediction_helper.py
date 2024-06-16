import pickle
import clean_helper as c
import numpy as np
import tensorflow as tf
from keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer

kamus_alay = c.kamus_alay()

# Load tfidf vectorizer
file_tfidf = open("modeling/tfidf_vectorizer.p", 'rb')
tfidf_vectorizer = pickle.load(file_tfidf)
file_tfidf.close()

# Load MLP Classifier Model
file_mlp = open('modeling/model_mlp.p','rb')
model_mlp = pickle.load(file_mlp)
file_mlp.close()

# Load tokenizer
sentiment = ['neutral', 'positive', 'negative']
file_lstm = open("modeling/tokenizer.pickle", 'rb')
tokenizer_lstm = pickle.load(file_lstm)
file_lstm.close()

# Load LSTM Model
model_lstm = load_model('modeling/model_lstm.h5')

# Function for predict by Neural Network MLP Classifier
def prediction_by_mlp(str):
    # data cleansing
    str = c.clean(str)
    str = c.word_substitute(str, kamus_alay)
    # feature extraction
    text = tfidf_vectorizer.transform([str])
    #predict
    result = model_mlp.predict(text)[0]
    print(result)
    if result == 0:
        return 'neutral'
    elif result == 1:
        return 'positive'
    elif result == 2:
        return 'negative'
    else:
        return 'neutral'
    
def prediction_by_lstm(str):
    # data cleansing
    str = c.clean(str)
    str = c.word_substitute(str, kamus_alay)
    
    predicted = tokenizer_lstm.texts_to_sequences([str])
    guess = pad_sequences(predicted, maxlen=91)

    prediction = model_lstm.predict(guess)
    print(type([str]))
    print("raw", prediction)
    print("prediction", np.argmax(prediction[0]))
    hasil = sentiment[np.argmax(prediction[0])]
    return hasil