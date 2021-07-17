from bs4 import BeautifulSoup
from urllib.request import urlopen, urlretrieve, Request
import cgi, os, time, datetime
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
from sklearn.metrics import mean_absolute_error, mean_squared_error
from mechanize import Browser

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

def weatherFetch(ts):
    city_frac = {'ahmedabad' : 0.43,
                'surat' : 0.32,
                'vadodara' : 0.12,
                'rajkot' : 0.09,
                'bhavnagar' : 0.04}
    dObj = datetime.datetime.fromtimestamp(int(ts))
    Date = f"{dObj.year}-{dObj.month}-{dObj.day}"
    datetime.datetime.fromtimestamp(ts)
    ans = np.zeros(7)
    for city in city_frac:
        url = f"https://www.worldweatheronline.com/{city}-weather-history/gujarat/in.aspx"
        
        brwsr = Browser()
        brwsr.open(url)
        brwsr.select_form(name = 'aspnetForm')
        brwsr['ctl00$MainContentHolder$txtPastDate'] = Date
        response = brwsr.submit()
        data = response.read()
        
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
        extFeat = np.array(extFeat)
        ans+=(extFeat*city_frac[city])
    return [i for i in ans], soupD

def this2that(data, test = False, SScaler = None, MMScaler = None, lmbda = None):
    from scipy.stats import boxcox
    if not test:
        pp1, lmbda = boxcox(data.to_numpy())
    else:
        pp1 = boxcox(data, lmbda)

    pp2 = [i for i in pp1]

    from sklearn.preprocessing import StandardScaler

    if not test:
        SScaler = StandardScaler()
        SScaler.fit(np.array(pp2).reshape(-1,1))
    pp3 = SScaler.transform(np.array(pp2).reshape(-1,1))

    # example of normalization
    from sklearn.preprocessing import MinMaxScaler
    if not test:
        MMScaler = MinMaxScaler()
        MMScaler.fit(pp3)
    # difference transform
    pp4 = MMScaler.transform(pp3)

    if not test:
        return pp4, lmbda, SScaler, MMScaler, pp1
    else:
        return pp4

def that2this(data, lmbda, SScaler, MMScaler, Dinv=None):
    pp3i = MMScaler.inverse_transform(data)

    pp2i = SScaler.inverse_transform(pp3i)
    pp2i = pp2i.reshape(pp2i.shape[0],)

    def invert_difference(orig_data, diff_data, interval):
        return [diff_data[i-interval] + orig_data[i-interval] for i in range(interval, len(orig_data))]
    # pp1i = invert_difference(Dinv, pp2i, 1)
    pp1i = [i for i in pp2i]

    from math import log
    from math import exp
    # invert a boxcox transform for one value
    def invert_boxcox(value, lam):
        # log case
        if lam == 0:
            return exp(value)
        # all other cases
        return exp(log(lam * value + 1) / lam)
    ans = [invert_boxcox(i, lmbda) for i in pp1i]

    return ans

def pastFiller():
    import pickle
    cData = pd.read_csv("../ALL_Data.csv", index_col=0)
    f = open("model_lr/linearmodel.pkl", "rb")
    lr = pickle.load(f)
    f.close()
    from sklearn.metrics import mean_absolute_error
    f = open("power_metrics.csv","w")
    f.write("timestamp,actual,prediction")
    f.close()
    MAE = []
    pDf = pd.read_csv("power_metrics.csv", index_col=0)
    for i in range(60):
        ts = int(cData.index[-(i+1)])
        pDf.loc[ts,"actual"] = cData.loc[ts,"Consumption in Mega Units"]
        
        pData7 = lr.predict(pd.DataFrame(cData["Consumption in Mega Units"]).iloc[-60-i:len(cData)-i,:].to_numpy().reshape(1,-1))
        pData = round(float(pData7[0]),2)
        pDf.loc[ts+86400, "prediction"] = pData
        buff = pDf.sort_index().dropna()
        try:
            MAE.append(mean_absolute_error(buff["actual"],buff["prediction"]))
        except:
            pass

    pDf = pDf.sort_index().dropna()

    pDf.to_csv("power_metrics.csv")

    f = open("MAE.csv","w")
    f.write("MAE\n")
    for i in MAE:
        f.write(f"{i}\n")
    f.close()

# if "histData" not in os.listdir():
#     os.mkdir("histData")
# if len(os.listdir("histData"))>=60:
#     pass
# else:
#     os.system("python3.8 starter.py")

if "power_metrics.csv" not in os.listdir():
    pastFiller()

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

cData = pd.read_csv("../ALL_Data.csv", index_col=0)

yrf = "20"+yr
sDate = f"{dt}/{mn}/{yrf}"
cTimestamp = int(time.mktime(datetime.datetime.strptime(sDate,"%d/%m/%Y").timetuple()))

# MU = {}
# for i in range(cData.shape[0]):
#     MU[cData.index[i]] = cData["Consumption in Mega Units"][i]

for i in allTXT:
    f = open(f"{TXTDIR}/{i}")
    buff = f.readlines()
    f.close()
    for j in buff:
        if "gujarat" in j.strip().lower() or "गुजरात" in j.strip().lower():
            cData.loc[cTimestamp,"Consumption in Mega Units"] = float(j.split()[3])
            break

WData, WDate = weatherFetch(cTimestamp)
cData.loc[WDate,list(cData.columns)[1:]] = WData
cData = cData.dropna()
cData.to_csv("../ALL_Data.csv")

print("Loading model...")
import pickle
f = open("model_lr/linearmodel.pkl", "rb")
lr = pickle.load(f)
f.close()
pData7 = lr.predict(pd.DataFrame(cData["Consumption in Mega Units"]).iloc[-60:,:].to_numpy().reshape(1,-1))
pData = round(float(pData7[0]),2)

# cDate = finalMU["Date (YY-MM-DD)"].to_numpy()[-1].split(".")
# cDate = f"{cDate[2]}/{cDate[1]}/20{cDate[0]}"
print(f"Prediction for tomorrow {pData} MU")

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
    f = open("MAE.csv","a")
    f.write(f"{MAE}\n")
    f.close()
except:
    MAE = "NA"
    RMSE = "NA"

f = open("prediction.csv", "w")
f.write(f"{oData},{pData},{cTimestamp},{MAE},{RMSE}")
f.close()

for i in range(7):
    pData7 = lr.predict(pd.DataFrame(cData["Consumption in Mega Units"]).iloc[-60:,:].to_numpy().reshape(1,-1))
    pData = round(float(pData7[0]),2)
    ts = int(cData.index[-1])
    cData.loc[ts+86400, "Consumption in Mega Units"] = pData

week_prediction = pd.DataFrame(cData["Consumption in Mega Units"]).iloc[-7:,:]
f = open("week_prediction.csv", "w")
f.write("predictions\n")
for i in week_prediction["Consumption in Mega Units"]:
    f.write(f"{i}\n")
f.close()