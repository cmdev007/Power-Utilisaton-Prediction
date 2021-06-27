from django.http.response import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from django.core.exceptions import *
import pandas as pd
import os
import time
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
    if "SENT.lock" in os.listdir("./backend"):
        LOCK = "Processing Video..."
    else:
        LOCK = "Processing Finished!"
        
    try:
        df = pd.read_csv(f"./backend/{session}/sentData.csv", header=0, index_col=0)

        context = {
                    "xlabels" : [i for i in df.index],
                    "anger" : [i for i in df["anger"]],
                    "disgust" : [i for i in df["disgust"]],
                    "fear" : [i for i in df["fear"]],
                    "joy" : [i for i in df["joy"]],
                    "sadness" : [i for i in df["sadness"]],
                    "sentdata" : LOCK
                }
    except:
        context = {
                    "xlabels" : [],
                    "anger" : [],
                    "disgust" : [],
                    "fear" : [],
                    "joy" : [],
                    "sadness" : [],
                    "sentdata" : LOCK
                }

    return JsonResponse(context)

def PidOpener(request):
    global session
    session = int(time.time())
    os.mkdir(f"./backend/{session}")
    link = request.POST.get('link', None)
    buff = {'anger' : 0,
            'disgust' : 0,
            'fear' : 0,
            'joy' : 0,
            'sadness' : 0}
    
    file1 = open(f"./backend/{session}/sentData.csv","w")#write mode
    file1.write("emotion,degree\n")
    for i in buff:
        file1.write(f"{i.capitalize()},{buff[i]}\n")
    file1.close()

    os.system(f"./backend/start-vsm-ensemble.sh '{link}' '{session}'&")
    return render(request, 'sentiment.html')
