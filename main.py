from pushsafer import Client
import config.config as config
import time
import requests
import json
from lxml import html
from kthread import KThread
from datetime import date

session = requests.Session()
today = date.today()
privatekey = config.pskey
client = Client(privatekey)

id = ""
updates = 0

latitude = "35.040554"
longitude = "-117.138306"
maxradius = "251.3414"
orderby = "time"
date = today.strftime("%y-%m-%d")
url = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&latitude=" + latitude + "&longitude=" + longitude + "&maxradiuskm=" + maxradius + "&orderby=" + orderby + "&limit=1" + "&starttime=" + date

def neweq(mag, msg, URL):
    title = "Earthquake Alert!"
    deviceid = "47512"
    icon = "2"
    sound = ""
    vibration = "2"
    URLTitle = "Open USGS report"
    Time2Live = "0"
    Priority = "2"
    retry = "60"
    expire = "600"
    answer = "1"
    image1 = ""
    image2 = ""
    image3 = ""
    client.send_message(msg, title, deviceid, icon, sound, vibration, URL, URLTitle, Time2Live, Priority, retry, expire, answer, image1, image2, image3)

while True:
    initdata = session.get(url)
    data = json.loads(initdata.text)
    data_ = data['features'][0]['properties']
    curtime = data['features'][0]['properties']['time']
    if curtime == id:
        updates = updates + 1
        if updates <= 1:
            print(str(updates) + " update since last quake")
        else:
            print(str(updates) + " updates since last quake")
    else:
        id = data_['time']
        mag = data_['mag']
        title = data_['title']
        urll = data_['url']
        neweq(round(mag, 1), title, urll)
        print(str(mag) + ": " + title + ", ")
        
    time.sleep(5)