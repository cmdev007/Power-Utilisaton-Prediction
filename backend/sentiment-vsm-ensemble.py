#!/bin/python

import sys
import os
import speech_recognition as sr
import numpy as np
import pandas as pd
import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import subprocess
import tensorflow as tf
import sys

argv = sys.argv
session = argv[-1]

stopwords=['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]

punkts='''"#$%&\'()*+,-./:;<=>@[\\]^_`{|}~'''

EmoCount = {'anger' : 0,
            'disgust' : 0,
            'fear' : 0,
            'joy' : 0,
            'sadness' : 0}

df = pd.DataFrame(data = {'anger': [], 'disgust': [], 'fear': [], 'joy': [], 'sadness': []}, dtype=int)

dfCounter = 0

df.loc[dfCounter] = [EmoCount[i] for i in EmoCount]

dfCounter+=1

def CorFilt(i):
    ps = PorterStemmer()

    buff = word_tokenize(i.lower().replace("\n", "").replace("  ", " ").replace("n't", " not"))
    buff2 = ""
    for j in pos_tag(buff):
        if j[-1] == 'RB' and j[0] != "not":
            pass
        else:
            buff2 += j[0] + " "
    buff2 = buff2.replace("not ", "NOT")
    buff = word_tokenize(buff2.strip())
    ans = ""
    for j in buff:
        if (j not in punkts) and (j not in stopwords):
            if j == "!":
                ans += " XXEXCLMARK"
            elif j == "?":
                ans += " XXQUESMARK"
            else:
                if j != "'s" and j != "``":
                    ans += " " + ps.stem(j)
    return ans.strip()

import pickle
f=open("./backend/EmoVec","rb")
EmoVec=pickle.load(f)
f.close()

f=open("./backend/vectorizer","rb")
vectorizer=pickle.load(f)
f.close()

model=tf.keras.models.load_model("./backend/models/")


def EmowavE(sent, vectorizer=vectorizer, EmoVec=EmoVec, trans=True):
    transDict = {'gu': 'Gujarati',
                 'hi': 'Hindi'}
    # Translate from any language to english
    if trans:
        analysis = TextBlob(sent)
        if analysis.detect_language() != 'en':
            try:
                print(f"\nInput text was in {transDict[analysis.detect_language()]}")
            except:
                print(f"\nInput text was not in English")
            print("\nTranslating...")
            output = subprocess.check_output(['trans', '-b', sent])
            sent = output.decode('utf-8').strip()
            print(f"\nTranslation in English: {sent}")

    EmoBuff = vectorizer.transform([CorFilt(sent)])
    EmoDict = {0: 'anger',
               1: 'disgust',
               2: 'fear',
               3: 'joy',
               4: 'sadness'}

    weights = [float(cosine_similarity(EmoBuff.reshape(-1, 1).T, EmoVec[i].reshape(-1, 1).T)) for i in
               range(EmoVec.shape[0])]
    if sum(weights) == 0:
        weights = [0 for i in range(5)]
    else:
        weights = [i / sum(weights) for i in weights]

    return EmoDict[np.argmax(weights)], weights


def EmopreD(sent, model=model, vectorizer=vectorizer):
    EmoDict = {0: 'anger',
               1: 'disgust',
               2: 'fear',
               3: 'joy',
               4: 'sadness'}

    buff = vectorizer.transform([CorFilt(sent)]).toarray()
    weights = model.predict(buff.reshape(1, 1, buff.shape[1]))

    return EmoDict[np.argmax(weights)], weights


def EnsemblE(sent):
    EmoV, weightV = EmowavE(sent)
    EmoL, weightL = EmopreD(sent)

    if np.argmax(weightV) == np.argmax(weightL):
        sureFLAG = True
    else:
        sureFLAG = False

    if np.max(weightV) >= np.max(weightL):
        method = "VSM"
        Emo = EmoV
        print(f"\n\t>>> Emotion from {method}: {EmoV}")
    else:
        method = "LSTM"
        Emo = EmoL
        print(f"\n\t>>> Emotion from {method}: {EmoL}")

    if not sureFLAG:
        print("EmowavE is not sure this time though!")
    return sureFLAG, method, Emo


header = sys.stdin.buffer.read(78)
while(1):
    # data = sys.stdin.buffer.read(882000) #5 sec
    # data = sys.stdin.buffer.read(5292000) #30 sec
    data = sys.stdin.buffer.read(2646000)
    if data == b'':
        os.system("rm -rf /tmp/inter.wav")
        os.system("rm -rf /tmp/inter_f.wav")
        os.system(f"rm ./backend/{session}/SENT.lock")
        break
    f = open("/tmp/inter.wav", "wb")
    f.write(header)
    f.write(data)
    f.close()
    os.system("ffmpeg -y -i /tmp/inter.wav -f wav /tmp/inter_f.wav 2> /dev/null")

    File="/tmp/inter_f.wav"
    AUDIO_FILE = File
    r = sr.Recognizer()

    with sr.AudioFile(AUDIO_FILE) as source:
        audio = r.record(source)

    try:
        print("#######################################################################################")
        print("Recognizing Text...")
        Data=r.recognize_google(audio)
        sureFLAG, Method, Emo = EnsemblE(Data)
        EmoCount[Emo] += 1
        df.loc[dfCounter] = [EmoCount[i] for i in EmoCount]
        dfCounter+=1
        df.to_csv(f"./backend/{session}/sentData.csv")
        print("#######################################################################################")
        print("The audio file contains: " + Data)

    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")

    except sr.RequestError as e:
        print("Could not request results from Google Speech  Recognition service; {0}".format(e))
