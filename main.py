from pushsafer import Client
import config.config as config
import time
import requests
import json
from datetime import date
import discord
from discord import Webhook, RequestsWebhookAdapter
from threading import Thread
import asyncio

updates = 0
id = 0

wclient = Webhook.from_url(config.webhookurl, adapter=RequestsWebhookAdapter())

client = discord.Client()

session = requests.Session()
today = date.today()
privatekey = config.pskey
discordtoken = config.discordtoken
#client = Client(privatekey)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

latitude = "34.026291"
longitude = "-117.981627"
maxradius = "140.25834"
orderby = "time"
date = today.strftime("%y-%m-%d")
url = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&latitude=" + latitude + "&longitude=" + longitude + "&maxradiuskm=" + maxradius + "&orderby=" + orderby + "&limit=1" + "&starttime=" + date

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
        #neweq(round(mag, 1), title, urll)
        #client.get_channel(config.channelid).send("Earthquake! " + title)
        wclient.send("Earthquake! " + title + "\n" + urll)
        print(str(mag) + ": " + title + ", ")
    time.sleep(5)



def neweq(mag, msg, URL):
    title = "Earthquake Alert!"
    deviceid = "47512"
    icon = "2"
    sound = ""
    vibration = "2"
    URLTitle = "Open USGS report"
    Time2Live = "0"
    if mag >= 3.5:
        Priority = "2"
    else:
        Priority = "0"
    retry = "60"
    expire = "600"
    answer = "1"
    image1 = ""
    image2 = ""
    image3 = ""
    client.send_message(msg, title, deviceid, icon, sound, vibration, URL, URLTitle, Time2Live, Priority, retry, expire, answer, image1, image2, image3)
