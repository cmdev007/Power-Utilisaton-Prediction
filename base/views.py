from django.http.response import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from django.core.exceptions import *
import pandas as pd
import os
import time
import random

# Create your views here.

def index(request):
    return render(request, 'index.html');

def home(request):
    return render(request, 'home.html');

def about(request):
    return render (request, 'about.html');

def electricity(request):
    return render (request, 'electricity.html');

def sentiment(request):
    return render (request, 'sentiment.html');
    
def stock(request):
    return render (request, 'stock.html');

def login(request):
    return render (request, 'login.html');

def register(request):
    return render (request, 'register.html');

def forgot(request):
    return render (request, 'forgot.html');

def charts(request):
    return render (request, 'charts.html');

def get_data(request,*args,**kwargs):
    data={ 
        "sales":100,
        "customers":20,
    }
    return JsonResponse(data)

def AutoUpdate(request):
    TITLE = ""
    try:
        if "SENT.lock" in os.listdir(f"./backend/emowave/oldSessions/{session}"):
            emogi = ['😀', '😃', '😄', '😁', '😆', '😅', '😂', '🤣', '🥲', '😊', '😇', '🙂', '🙃', '😉', '😌', '😍', '🥰', '😘', '😗', '😙', '😚', '😋', '😛', '😝', '😜', '🤪', '🤨', '🧐', '🤓', '😎', '🥸', '🤩', '🥳', '😏', '😒', '😞', '😔', '😟', '😕', '🙁', '☹️', '😣', '😖', '😫', '😩', '🥺', '😢', '😭', '😤', '😠', '😡', '🤬', '🤯', '😳', '🥵', '🥶', '😱', '😨', '😰', '😥', '😓', '🤗', '🤔', '🤭', '🤫', '🤥', '😶', '😐', '😑', '😬', '🙄', '😯', '😦', '😧', '😮', '😲', '🥱', '😴', '🤤', '😪', '😵', '🤐', '🥴', '🤢', '🤮', '🤧', '😷', '🤒', '🤕', '🤑', '🤠']
            LOCK = "Processing Video"
            sEmogi = random.choices(emogi,k=int((time.time()-session)%4)*2)
            sEmogi = "".join(sEmogi)
            LOCK = f"{sEmogi[0:int(len(sEmogi)/2)]}{LOCK}{sEmogi[int(len(sEmogi)/2):len(sEmogi)]}"
        else:
            LOCK = "Processing Finished!"
    except:
        LOCK = "Ready to Process"
    
    try:
        f = open(f"./backend/emowave/oldSessions/{session}/TITLE.txt")
        TITLE = f.read()
        tlist = TITLE.strip().split("-")
        tlist.pop()
        TITLE = "-".join(tlist)
        f.close()
    except:
        pass

    try:
        df = pd.read_csv(f"./backend/emowave/oldSessions/{session}/sentData.csv", header=0, index_col=0)

        context = {
                    "xlabels" : [i for i in df.index],
                    "anger" : [i for i in df["anger"]],
                    "disgust" : [i for i in df["disgust"]],
                    "fear" : [i for i in df["fear"]],
                    "joy" : [i for i in df["joy"]],
                    "sadness" : [i for i in df["sadness"]],
                    "sentdata" : LOCK,
                    "title" : TITLE
                }
    except:
        context = {
                    "xlabels" : [],
                    "anger" : [],
                    "disgust" : [],
                    "fear" : [],
                    "joy" : [],
                    "sadness" : [],
                    "sentdata" : LOCK,
                    "title" : TITLE
                }

    return JsonResponse(context)

def PidOpener(request):
    global session
    session = int(time.time())
    os.system("rm -rf ./backend/emowave/oldSessions/*")
    os.mkdir(f"./backend/emowave/oldSessions/{session}")
    os.system(f"touch ./backend/emowave/oldSessions/{session}/SENT.lock")
    link = request.POST.get('link', None)
    buff = {'anger' : 0,
            'disgust' : 0,
            'fear' : 0,
            'joy' : 0,
            'sadness' : 0}
    
    file1 = open(f"./backend/emowave/oldSessions/{session}/sentData.csv","w")#write mode
    file1.write("emotion,degree\n")
    for i in buff:
        file1.write(f"{i.capitalize()},{buff[i]}\n")
    file1.close()

    os.system(f"./backend/emowave/start-vsm-ensemble.sh '{link}' 'oldSessions/{session}'&")
    return render(request, 'sentiment.html')

def PidCloser(request):
    f = os.popen("ps -ef | awk '$NF~'"+str(session)+"' {print $2}'")
    PIDs = f.read()
    for i in PIDs.split():
        os.system(f"kill {i}")
    os.system(f"rm  ./backend/emowave/oldSessions/{session}/SENT.lock")
    return render(request, 'sentiment.html')