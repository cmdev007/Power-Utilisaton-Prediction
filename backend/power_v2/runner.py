from bs4 import BeautifulSoup
from urllib.request import urlopen, urlretrieve, Request, urlopen
import cgi, os, time, datetime
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
from sklearn.metrics import mean_absolute_error, mean_squared_error

def smartDownloader(contains, key):
    url = f"https://posoco.in/download/20-05-21_nldc_psp/?wpdmdl={key}"
    remotefile = urlopen(url)
    blah = remotefile.info()['Content-Disposition']
    value, params = cgi.parse_header(blah)
    filename = params["filename"]
    
    if contains in filename:
        urlretrieve(url, f"currentData/{filename}")
    else:
        print(f"{key} : {filename}")
        return None

def link2id(link):
    for i in range(len(link)-1,0,-1):
        try:
            ans = int(link[i:])
        except:
            return(ans)

def pageResp(url):
    import urllib.request
    from bs4 import BeautifulSoup
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers={'User-Agent':user_agent,} 
    request=urllib.request.Request(url,None,headers)
    response = urllib.request.urlopen(request)
    data = response.read()
    hdata = BeautifulSoup(data,'html.parser')
    return hdata

def latestID(url):
    hdata = pageResp(url)
    for i in hdata.find_all("a", href=True):
        if "nldc_psp" in i["href"]:
            return link2id(str(i["href"]))

def weatherFetch():
    url = "https://www.worldweatheronline.com/ahmedabad-weather-history/gujarat/in.aspx"
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'

    headers={'User-Agent':user_agent,} 

    request= Request(url,None,headers) #The assembled request
    response = urlopen(request)
    data = response.read() # The data u need

    soup = BeautifulSoup(data,'html.parser')

    soup = BeautifulSoup(data,'html.parser')
    soupD = soup.find_all("input", attrs={"class" : ["form-control"], "id" : ["ctl00_MainContentHolder_txtPastDate"]})[0]
    soupD = soupD.attrs['value']
    soupD = int(time.mktime(datetime.datetime.strptime(soupD,"%Y-%m-%d").timetuple()))


    soup = BeautifulSoup(str(soup).split("Historical Weather on")[-1],'html.parser')

    buff = ""
    for link in soup.find_all("div",{"class":["col mr-1", "col mr-1 d-none d-sm-block","col mr-1 d-none d-md-block"]}):
        buff+=link.text+"\n"
    extFeat = []
    for i in buff.split("\n\n")[-1].split("\n")[:-1]:
        buffC = ""
        for j in i:
            try:
                float(buffC+j)
                buffC+=j
            except:
                break
        extFeat.append(float(buffC))
    return extFeat

# if "histData" not in os.listdir():
#     os.mkdir("histData")
# if len(os.listdir("histData"))>=60:
#     pass
# else:
#     os.system("python3.8 starter.py")

DATADIR = "currentData"
os.system(f"rm -rf {DATADIR}")
os.system(f"mkdir {DATADIR}")

LKEY = latestID("https://posoco.in/reports/daily-reports/daily-reports-2021-22/")
smartDownloader("NLDC_PSP", LKEY)

f = open("LKEY.txt", "w")
f.write(str(LKEY))
f.close()

allPDF = os.listdir(DATADIR)
allPDF.sort()

for i in allPDF:
    yr = i[6:8]
    mn = i[3:5]
    dt = i[0:2]
    res = i[8:]
    os.rename(f"{DATADIR}/{i}", f"{DATADIR}/{yr}.{mn}.{dt}{res}")

allPDF = os.listdir(DATADIR)
allPDF.sort()

for i in allPDF:
    os.system(f"pdftotext -layout '{DATADIR}/{i}'")

TXTDIR = "currentTXT"
os.system(f"rm -rf {TXTDIR}")
os.system(f"mkdir {TXTDIR}")
os.system(f"cp -rv {DATADIR}/*.txt {TXTDIR}/")

allTXT = os.listdir(TXTDIR)
allTXT.sort()

cData = pd.read_csv("ALL_Data.csv", index_col=0)

yrf = "20"+yr
sDate = f"{dt}/{mn}/{yrf}"
cTimestamp = int(time.mktime(datetime.datetime.strptime(sDate,"%d/%m/%Y").timetuple()))

MU = {}
for i in range(cData.shape[0]):
    MU[cData.index[i]] = cData["Consumption in Mega Units"][i]

for i in allTXT:
    f = open(f"{TXTDIR}/{i}")
    buff = f.readlines()
    f.close()
    for j in buff:
        if "gujarat" in j.strip().lower() or "गुजरात" in j.strip().lower():
            cData.loc[cTimestamp,"Consumption in Mega Units"] = float(j.split()[3])
            break

cData.loc[cTimestamp,list(cData.columns)[1:]] = weatherFetch()
cData.to_csv("ALL_Data.csv")

print("Loading model...")
model = load_model("model_bd_v2")
pData7 = model.predict(cData.iloc[-60:,:].to_numpy().reshape(1,60,8))
pData = round(float(pData7[0]),2)

cDate = finalMU["Date (YY-MM-DD)"].to_numpy()[-1].split(".")
cDate = f"{cDate[2]}/{cDate[1]}/20{cDate[0]}"
print(f"Prediction for tomorrow of {cDate} : {pData} MU")

oData = float(cData["Consumption in Mega Units"].to_numpy()[-1])

# cTimestamp = int(time.mktime(datetime.datetime.strptime(cDate,"%d/%m/%Y").timetuple()))

power_metrics = pd.read_csv("power_metrics.csv", index_col=0)
power_metrics.loc[cTimestamp,"actual"] = oData
power_metrics.loc[cTimestamp+86400,"prediction"] = pData
power_metrics.to_csv("power_metrics.csv")
power_metrics = power_metrics.dropna()
try:
    MAE = round(mean_absolute_error(power_metrics["actual"], power_metrics["prediction"]),2)
    RMSE = round(mean_squared_error(power_metrics["actual"], power_metrics["prediction"], squared=False),2)
except:
    MAE = "NA"
    RMSE = "NA"

f = open("prediction.csv", "w")
f.write(f"{oData},{pData},{cTimestamp},{MAE},{RMSE}")
f.close()

f = open("week_prediction.csv", "w")
f.write("predictions\n")
for i in pData7:
    f.write(f"{i}\n")
f.close()