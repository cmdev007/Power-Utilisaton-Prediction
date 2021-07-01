from urllib.request import urlopen
from urllib.request import urlretrieve
import cgi, os, time

def smartDownloader(contains, key):
    url = f"https://posoco.in/download/20-05-21_nldc_psp/?wpdmdl={key}"
    remotefile = urlopen(url)
    blah = remotefile.info()['Content-Disposition']
    value, params = cgi.parse_header(blah)
    filename = params["filename"]
    
    if contains in filename:
        urlretrieve(url, f"histData/{filename}")
    else:
        print(f"{key} : {filename}")
        return None

def threadRipper(contains, key):
    import threading
    NTHREADS = 10
    while(len(os.listdir("histData"))<60):
        threads = []

        for j in range(NTHREADS):
            t = threading.Thread(target=smartDownloader,args=(contains,key-j))
            t.daemon = True
            threads.append(t)

        for j in range(NTHREADS):
            threads[j].start()

        for j in range(NTHREADS):
            threads[j].join(timeout=20)

        key-=NTHREADS

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

if "histData" not in os.listdir():
    os.mkdir("histData")
if len(os.listdir("histData"))>=60:
    pass
else:
    LKEY = latestID("https://posoco.in/reports/daily-reports/daily-reports-2021-22/")
    threadRipper("NLDC_PSP", LKEY)