import config.config as config
import time
import requests
import json
from datetime import date
import discord
from discord import Webhook, RequestsWebhookAdapter
import sevenseq.sevenseq as sevenseq
import sys

updates = 0
id = 0

wclient = Webhook.from_url(config.webhookurl, adapter=RequestsWebhookAdapter())

session = requests.Session()
today = date.today()

latitude = "34.026291"
longitude = "-117.981627"
maxradius = "140.25834"
orderby = "time"
date = today.strftime("%y-%m-%d")
url = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&latitude=" + latitude + "&longitude=" + longitude + "&maxradiuskm=" + maxradius + "&orderby=" + orderby + "&limit=1" + "&starttime=" + date

def convertplace(x):
    hmm = "ab"
    hmm = list(hmm)
    hmm[0] = x[0]
    if x[1] == "k":
        hmm[1] = ""
        x = x[3:len(x)]
    else:
        hmm[1] = x[1]
        x = x[4:len(x)]
    km = int(str(hmm[0] + hmm[1]))
    return str(round((km / 1.609), 2)) + "mi" + x

def returnembed(data_, geo):
    mag = data_['mag']
    title = data_['title']
    urll = data_['url']
    place = data_['place']
    long = geo['coordinates'][0]
    lat = geo['coordinates'][1]
    geourl = "https://www.google.com/maps/search/?api=1&query=" + str(lat) + "000" + "%2C" + str(long) + "000"
    
    embeded=discord.Embed(title="Earthquake Detected", color=discord.Color.blue())
    embeded.set_author(name="eqnoti", icon_url="https://cdn.discordapp.com/avatars/919764620003135538/0cf2d9fbf4a1f3f51da64487c08be936.webp")
    embeded.set_thumbnail(url="https://www.wavy.com/wp-content/uploads/sites/3/2020/10/USGS_logo_green_SQUARE.png")
    embeded.add_field(name = "**What:** ", value = "A " + str(round(mag, 1)) + " magnitude earthquake occurred " + convertplace(place))
    embeded.add_field(name = "**Where:**", value = geourl)
    embeded.add_field(name = "**Details:**", value = urll)
    #pings = "<@&921000883322511400>"
    #if mag >= 3.5:
    #    pings = pings + ", <@&921002317766086656>"
    #embeded.add_field(name = "**Pings:**", value = pings)
    return embeded
    
while True:
    initdata = session.get(url)
    data = json.loads(initdata.text)
    data_ = data['features'][0]['properties']
    curtime = data['features'][0]['properties']['time']
    if curtime == id:
        updates = updates + 1
        #sevenseq.setnum(updates)
        if updates <= 1:
            print(str(updates) + " update since last quake")
        else:
            print(str(updates) + " updates since last quake")
    else:
        id = data_['time']
        mag = data_['mag']
        title = data_['title']
        urll = data_['url']
        place = data_['place']
        embeded = returnembed(data_, data['features'][0]['geometry'])
        wclient.send(embed=embeded)
        pings = "<@&921000883322511400>"
        if mag >= 3.5:
            pings = pings + ", <@&921002317766086656>"
        wclient.send(pings)
        #neweq(round(mag, 1), title, urll)
        #client.get_channel(config.channelid).send("Earthquake! " + title)
        sevenseq.setnum(round(mag, 1), 2)
        print(str(mag) + ": " + "A " + str(round(mag, 1)) + " magnitude earthquake occurred " + convertplace(place))
        updates = 0
    time.sleep(5)