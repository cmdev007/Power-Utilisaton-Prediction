from django.http.response import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from django.core.exceptions import *
import pandas as pd
import os
import time
import random
from datetime import datetime

# Create your views here.

def index(request):
    return render(request, 'index.html');

def home(request):
    return render(request, 'home.html');

def power(request):
    return render (request, 'power.html');

def about(request):
    return render (request, 'about.html');

def electricitylr(request):
    return render (request, 'electricitylr.html');

def electricity(request):
    return render (request, 'electricity.html');

def electricityV2(request):
    return render (request, 'electricityV2.html');

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
            emogi = ['๐', '๐', '๐', '๐', '๐', '๐', '๐', '๐คฃ', '๐ฅฒ', '๐', '๐', '๐', '๐', '๐', '๐', '๐', '๐ฅฐ', '๐', '๐', '๐', '๐', '๐', '๐', '๐', '๐', '๐คช', '๐คจ', '๐ง', '๐ค', '๐', '๐ฅธ', '๐คฉ', '๐ฅณ', '๐', '๐', '๐', '๐', '๐', '๐', '๐', 'โน๏ธ', '๐ฃ', '๐', '๐ซ', '๐ฉ', '๐ฅบ', '๐ข', '๐ญ', '๐ค', '๐ ', '๐ก', '๐คฌ', '๐คฏ', '๐ณ', '๐ฅต', '๐ฅถ', '๐ฑ', '๐จ', '๐ฐ', '๐ฅ', '๐', '๐ค', '๐ค', '๐คญ', '๐คซ', '๐คฅ', '๐ถ', '๐', '๐', '๐ฌ', '๐', '๐ฏ', '๐ฆ', '๐ง', '๐ฎ', '๐ฒ', '๐ฅฑ', '๐ด', '๐คค', '๐ช', '๐ต', '๐ค', '๐ฅด', '๐คข', '๐คฎ', '๐คง', '๐ท', '๐ค', '๐ค', '๐ค', '๐ค ']
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
    if "oldSessions" not in os.listdir("./backend/emowave/"):
        os.mkdir("./backend/emowave/oldSessions/")
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

def powerUpdater(request):
    current = "NA"
    future = "NA"
    cts = ""
    timeseries = []
    xlabels = []
    MAE = "NA"
    RMSE = "NA"
    week_data = []
    week_labels = []
    past_pred = []
    MAE_all = []
    try:
        power_metrics = pd.read_csv("./backend/power/prototype_1/power_metrics.csv", index_col = 0)
        power_metrics = power_metrics.dropna()
        timeseries = [i for i in power_metrics["actual"]][-60:]

        f = open("./backend/power/prototype_1/prediction.csv")
        mainData = f.read()
        f.close()
        week_data = [i for i in pd.read_csv("./backend/power/prototype_1/week_prediction.csv")["predictions"]]
        mainData = mainData.split(",")
        current = mainData[0]
        future = mainData[1]
        cts = mainData[2]
        MAE = mainData[3]
        RMSE = mainData[4]
        # xlabels = [f"{i.split('.')[2]}/{i.split('.')[1]}" for i in pSeries.index]
        for i in power_metrics.index[-60:]:
            dateObj = datetime.fromtimestamp(int(i))
            xlabels.append(f"{str(dateObj.day).zfill(2)}/{str(dateObj.month).zfill(2)}")
        for i in range(7):
            dateObj = datetime.fromtimestamp(int(cts)+((i+2)*86400))
            week_labels.append(f"{str(dateObj.day).zfill(2)}/{str(dateObj.month).zfill(2)}")

        past_pred = [i for i in power_metrics["prediction"]][-60:]
        MAE_all = [i for i in pd.read_csv("./backend/power/prototype_1/MAE.csv")["MAE"]]
    except:
        pass
    
    context = {
        "current" : current,
        "future" : future,
        "timeseries" : timeseries,
        "xlabels" : xlabels,
        "cts" : cts,
        "MAE" : MAE,
        "RMSE" : RMSE,
        "week_data" : week_data,
        "week_labels" : week_labels,
        "past_pred" : past_pred,
        "MAE_all" : MAE_all
    }
    return JsonResponse(context)

def powerUpdaterLr(request):
    current = "NA"
    future = "NA"
    cts = ""
    timeseries = []
    xlabels = []
    MAE = "NA"
    RMSE = "NA"
    week_data = []
    week_labels = []
    past_pred = []
    MAE_all = []
    try:
        power_metrics = pd.read_csv("./backend/power/linearRegression/power_metrics.csv", index_col = 0)
        power_metrics = power_metrics.dropna()
        timeseries = [i for i in power_metrics["actual"]][-60:]

        f = open("./backend/power/linearRegression/prediction.csv")
        mainData = f.read()
        f.close()
        # f = open("./backend/power/linearRegression/prediction.csv")
        week_data = [i for i in pd.read_csv("./backend/power/linearRegression/week_prediction.csv")["predictions"]]
        mainData = mainData.split(",")
        current = mainData[0]
        future = mainData[1]
        cts = mainData[2]
        MAE = mainData[3]
        RMSE = mainData[4]
        # xlabels = [f"{i.split('.')[2]}/{i.split('.')[1]}" for i in pSeries.index]
        for i in power_metrics.index[-60:]:
            dateObj = datetime.fromtimestamp(int(i))
            xlabels.append(f"{str(dateObj.day).zfill(2)}/{str(dateObj.month).zfill(2)}")
        for i in range(7):
            dateObj = datetime.fromtimestamp(int(cts)+((i+2)*86400))
            week_labels.append(f"{str(dateObj.day).zfill(2)}/{str(dateObj.month).zfill(2)}")

        past_pred = [i for i in power_metrics["prediction"]][-60:]
        MAE_all = [i for i in pd.read_csv("./backend/power/linearRegression/MAE.csv")["MAE"]]
    except:
        pass
    
    context = {
        "current" : current,
        "future" : future,
        "timeseries" : timeseries,
        "xlabels" : xlabels,
        "cts" : cts,
        "MAE" : MAE,
        "RMSE" : RMSE,
        "week_data" : week_data,
        "week_labels" : week_labels,
        "past_pred" : past_pred,
        "MAE_all" : MAE_all
    }
    return JsonResponse(context)

def powerUpdaterV2(request):
    current = "NA"
    future = "NA"
    cts = ""
    timeseries = []
    xlabels = []
    MAE = "NA"
    RMSE = "NA"
    week_data = []
    week_labels = []
    past_pred = []
    MAE_all = []
    try:
        power_metrics = pd.read_csv("./backend/power/prototype_2/power_metrics.csv", index_col = 0)
        power_metrics = power_metrics.dropna()
        timeseries = [i for i in power_metrics["actual"]][-60:]

        f = open("./backend/power/prototype_2/prediction.csv")
        mainData = f.read()
        f.close()
        week_data = [i for i in pd.read_csv("./backend/power/prototype_2/week_prediction.csv")["predictions"]]
        mainData = mainData.split(",")
        current = mainData[0]
        future = mainData[1]
        cts = mainData[2]
        MAE = mainData[3]
        RMSE = mainData[4]
        # xlabels = [f"{i.split('.')[2]}/{i.split('.')[1]}" for i in pSeries.index]
        for i in power_metrics.index[-60:]:
            dateObj = datetime.fromtimestamp(int(i))
            xlabels.append(f"{str(dateObj.day).zfill(2)}/{str(dateObj.month).zfill(2)}")
        for i in range(7):
            dateObj = datetime.fromtimestamp(int(cts)+((i+2)*86400))
            week_labels.append(f"{str(dateObj.day).zfill(2)}/{str(dateObj.month).zfill(2)}")

        past_pred = [i for i in power_metrics["prediction"]][-60:]
        MAE_all = [i for i in pd.read_csv("./backend/power/prototype_2/MAE.csv")["MAE"]]
    except:
        pass
    
    context = {
        "current" : current,
        "future" : future,
        "timeseries" : timeseries,
        "xlabels" : xlabels,
        "cts" : cts,
        "MAE" : MAE,
        "RMSE" : RMSE,
        "week_data" : week_data,
        "week_labels" : week_labels,
        "past_pred" : past_pred,
        "MAE_all" : MAE_all
    }
    return JsonResponse(context)