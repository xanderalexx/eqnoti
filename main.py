import config.config as config
import os
import logging
import time
import requests
import json
from datetime import date
import discord
from discord import Webhook, RequestsWebhookAdapter
#import sevenseq.sevenseq as sevenseq
import sys
import epaper.epaper as epaper

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

logger.info(str(len(sys.argv)) + " " + str(sys.argv))
silentmode = 0
try:
    if sys.argv[1] == "silent":
        silentmode = 1
    else:
        silentmode = 0
except:
    print("")
updates = 0
id = 0
datalist = ['']
datalist2 = ['']

wclient = Webhook.from_url(config.webhookurl, adapter=RequestsWebhookAdapter())
errorclient = Webhook.from_url(config.errorwebhookurl, adapter=RequestsWebhookAdapter())
largeclient = Webhook.from_url(config.largewebhookurl, adapter=RequestsWebhookAdapter())

bruh = False
epochh = time.time()
while bruh == False:
    try:
        errorclient.send("Starting up... (" + time.strftime('%I:%M:%S %p %m/%d/%Y', time.localtime(epochh)) + ")")
    except Exception as e:
        print(str(e))
    else:
        bruh = True

session = requests.Session()
today = date.today()

latitude = "34.026291"
longitude = "-117.981627"
maxradius = "140.25834"
orderby = "time"
date = today.strftime("%y-%m-%d")
url = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&latitude=" + latitude + "&longitude=" + longitude + "&maxradiuskm=" + maxradius + "&orderby=" + orderby + "&limit=1"# + "&starttime=" + date

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
    epoch = data_['time']
    geourl = "https://www.google.com/maps/search/?api=1&query=" + str(lat) + "000" + "%2C" + str(long) + "000"
    
    timestamp = time.strftime('%m/%d/%Y %I:%M:%S %p', time.localtime(epoch / 1000))
    embeded=discord.Embed(title="Earthquake Detected @ " + timestamp, color=discord.Color.blue())
    embeded.set_author(name="eqnoti", icon_url="https://cdn.discordapp.com/avatars/919764620003135538/0cf2d9fbf4a1f3f51da64487c08be936.webp")
    embeded.set_thumbnail(url="https://www.wavy.com/wp-content/uploads/sites/3/2020/10/USGS_logo_green_SQUARE.png")
    embeded.add_field(name = "**What:** ", value = "A " + str(round(mag, 1)) + " magnitude earthquake occurred " + convertplace(place))
    embeded.add_field(name = "**Where:**", value = geourl)
    embeded.add_field(name = "**Details:**", value = urll)
    return embeded

def errorhandler(ex):
    logger.error("eqnoti is currently experiencing an error and is being handled. Here is the error message: \n" + str(ex))
    epoch = time.time()
    current_time = time.strftime('%I:%M:%S %p %m/%d/%Y', time.localtime(epoch))
    while True:
        try:
            errormessage = "eqnoti has encountered an error @ " + current_time + ". Here is the error message: '" + str(ex) + "'"
            errorclient.send(errormessage)
        except:
            pass
        else:
            break
        time.sleep(0.5)

while True:
    try:
        initdata = session.get(url)
    except Exception as e:
        errorhandler(e)
    else:
        try:
            data = json.loads(initdata.text)
            try:
                data_ = data['features'][0]['properties']
            except Exception as e:
                errorhandler(e)
            else:
                curtime = data['features'][0]['properties']['ids']
                if curtime == id:
                    updates = updates + 1
                    current_time = time.strftime('%I:%M:%S %p %m/%d/%Y', time.localtime(time.time()))
                    if updates <= 1:
                        logger.info(str(updates) + " update since last quake (" + current_time + ")")
                    else:
                        logger.info(str(updates) + " updates since last quake (" + current_time + ")")
                elif data_['ids'] in datalist and data_['ids'] not in datalist2:
                    logging.info("Earthquake already in datalist detected: \n" + str(mag) + ": " + "A " + str(round(mag, 1)) + " magnitude earthquake occurred " + convertplace(place))
                    datalist2.append(data_['ids'])
                else:
                    datalist.append(data_['ids'])
                    id = data_['ids']
                    mag = data_['mag']
                    title = data_['title']
                    urll = data_['url']
                    place = data_['place']
                    epoch = data_['time']
                    newplace = convertplace(place)
                    embeded = returnembed(data_, data['features'][0]['geometry'])
                    pings = "<@&921000883322511400>"
                    if round(mag, 1) >= 3.5:
                        pings = pings + ", <@&921002317766086656>"
                        largeclient.send(str(round(mag, 1)) + " Magnitute EQ " + newplace + " " + pings)
                        largeclient.send(embed=embeded)
                    wclient.send(str(round(mag, 1)) + " Magnitute EQ " + newplace + " " + pings)
                    wclient.send(embed=embeded)
                    msg = str(mag) + ": " + "A " + str(round(mag, 1)) + " magnitude earthquake occurred " + newplace
                    logger.info(msg)
                    if silentmode != 1:
                        epaper.displayy(str(round(mag, 1)), newplace, time.strftime('%m/%d/%Y %I:%M:%S %p', time.localtime(epoch / 1000)), data['features'][0]['geometry'])
                    updates = 0
        except Exception as e:
            errorhandler(e)
        time.sleep(5)