import time, os

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

while(1):
    if "LKEY.txt" in os.listdir():
        try:
            f = open("LKEY.txt")
            LKEY = f.read()
            LKEY = int(LKEY.strip())
            f.close()

            NKEY = latestID("https://posoco.in/reports/daily-reports/daily-reports-2021-22/")
            
            if NKEY>LKEY:
                os.system("python3.8 linearRegression/runner.py")
                os.system("python3.8 prototype_1/runner.py")
                os.system("python3.8 prototype_2/runner.py")
            time.sleep(7200)
        except:
            time.sleep(15)
    else:
        time.sleep(10)
