from django.http.response import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
import pandas as pd
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

def charts(request):
    return render (request, 'charts.html');

def get_data(request,*args,**kwargs):
    data={ 
        "sales":100,
        "customers":20,
    }
    return JsonResponse(data)

def AutoUpdate(request):
    df = pd.read_csv("static/csv/two.csv", header=0)

    context = {
                "xlabels" : [i for i in df["emotion"]],
                "ydegree" : [i for i in df["degree"]]

    }
    return JsonResponse(context)