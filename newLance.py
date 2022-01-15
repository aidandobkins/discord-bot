import discord
import asyncio
from discord.ext.commands import Bot
from discord.utils import *
from discord.ext import commands
from discord import FFmpegPCMAudio
from youtube_dl import YoutubeDL
import youtube_dl
import random
import praw
import os
import urllib.request
from datetime import date
import time
from discord.ext import tasks
from discord.utils import get
from discord.ext import commands
from discord import NotFound
from discord.utils import get
import json

f = open("api.txt", 'r')
apidata = f.read().splitlines()
f.close()

#NOMICS API STUFF
#---------------------------------------
#---------------------------------------
#---------------------------------------

url = apidata[0]

#REDDIT API STUFF
#---------------------------------------
#---------------------------------------
#---------------------------------------

reddit = praw.Reddit(
     client_id = apidata[1],
     client_secret = apidata[2],
     user_agent = apidata[3]
)

#RIOT API STUFF
#---------------------------------------
#---------------------------------------
#---------------------------------------
#---------------------------------------
#---------------------------------------
#---------------------------------------

from riotwatcher import LolWatcher, ApiError

api_key = apidata[4]
watcher = LolWatcher(api_key)
my_region = 'na1'

def rankLookUp(name):
    me = watcher.summoner.by_name(my_region, name)
    my_ranked_stats = watcher.league.by_summoner(my_region, me['id'])

    tier = ""
    division = ""
    lp = ""

    if not my_ranked_stats:
        return name + " is not ranked in Solo/Duo Queue."
    
    raw1 = my_ranked_stats[0]
    if len(my_ranked_stats) > 1:
        raw2 = my_ranked_stats[1]

    if raw1["queueType"] == 'RANKED_SOLO_5x5':
        tier = raw1["tier"]
        division = raw1["rank"]
        lp = raw1["leaguePoints"]
    else:
        tier = raw2["tier"]
        division = raw2["rank"]
        lp = raw2["leaguePoints"]

    return name + " is **" + str(tier) + "** **" + str(division) + "**\n*" + str(lp) + "* *LP*"

#DISCORD BOT STUFF
#---------------------------------------
#---------------------------------------
#---------------------------------------
tokenf = open('token.txt', 'r')
TOKEN = tokenf.readline()
tokenf.close()

client = discord.Client()

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
queue = []

#queue command (INPROGRESS)
#async def play_next():
#    voice = client.voice_clients[0]
#    if(len(queue) > 0):
#        if last_played == queue[0]:
#            queue.pop[0]
#        last_played = queue[0]
#        voice.play(discord.FFmpegPCMAudio(queue[0], **FFMPEG_OPTIONS), after = play_next())

def checkBirthdays():
    birthf = open('birthdays.json')
    tempb = json.load(birthf)
    birthf.close()
    birthdays = tempb['birthdays']
    today = date.today()
    mindiff = 365
    name = ""
    for i in birthdays:
        diff = date(today.year, i['month'], i['day']) - today
        days = diff.days
        if days < 0:
            days = days + 365
        if days < mindiff: 
            mindiff = days
            name = i['name']
    return [mindiff, name]

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)

@tasks.loop(minutes=1440)
async def sendBday():
    await client.wait_until_ready()
    chan = client.get_channel(746836143093579778)
    bday = checkBirthdays()
    if bday[0] == 0:
        await chan.send("It's " + bday[1] + "'s Birthday Today!!!")
    elif bday[0] == 5 or bday[0] == 4 or bday[0] == 3 or bday[0] == 2:
        await chan.send("There are " + str(bday[0]) + " days until " + bday[1] + "'s birthday.")
    elif bday[0] == 21:
        await chan.send("There are three weeks until " + bday[1] + "'s birthday.")
    elif bday[0] == 14:
        await chan.send("There are two weeks until " + bday[1] + "'s birthday.")
    elif bday[0] == 30:
        await chan.send("There are 30 days until " + bday[1] + "'s birthday.")
    elif bday[0] == 7:
        await chan.send("There is one week until " + bday[1] + "'s birthday.")
    elif bday[0] == 1:
        await chan.send (bday[1] + "'s birthday is tomorrow!")

sendBday.start()

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix=',', intents=intents)

@client.event 
async def on_member_join(member):
  role = get(member.guild.roles, id=746836638046486672)
  await member.add_roles(role)

@client.event
async def on_reaction_add(reaction, user):
    if reaction.emoji == '🍆':
        await reaction.message.add_reaction(reaction.emoji)

    if reaction.emoji == '👎' and reaction.count >= 5:
        await reaction.message.delete()

@client.event
async def on_message(message): #makes sure lance didnt say the command
    if message.author == client.user:
        return

    #PINKCAP COMMAND
    if message.content == '!pinkcap':
        await message.channel.send('https://imgur.com/a/Dbt8sdq')
        
    #LEAGUE RANK COMMAND
    if message.content.startswith('!rank '):
        rankstr = message.content.replace('!rank ', "")
        newmsg = rankLookUp(rankstr)
        await message.channel.send(newmsg)

    #BIRTHDAY COMMAND
    if message.content == '!birthday':
        bday = checkBirthdays()

        if bday[0] == 0:
            await message.channel.send("It's " + bday[1] + "'s Birthday Today!!!")
        else:
            await message.channel.send("There are " + str(bday[0]) + " days until " + bday[1] + "'s birthday.")

    #DOGE COMMAND
    if message.content == '!doge':
        reading = urllib.request.urlopen(url)
        for i in range(37):
            reading.read(5)
        price = reading.read(12)
        price1 = price.decode('utf-8')
        price1 = price1.strip('\"')
        printprice = "The price of Dogecoin is: \n> " + price1 + " USD"
        await message.channel.send(printprice)

    #LAFF COMMAND
    if message.content == '!laff': #laughjokes reddit command
        num = random.randint(0,49)
        i = 0
        for submission in reddit.subreddit("LaughJokes").hot(limit=50):
            if num == i:   ##and submission.url == laffBlacklist.parse
                laff = submission.url
            i += 1
        await message.channel.send(laff)
    
    #DELETE COMMAND
    if message.content.startswith('!delete '):
        deletenumstr = message.content.replace('!delete ', "")
        deletenum = int(deletenumstr)
        if deletenum > 10:
            await message.channel.send("Put in a lower number you fuck")
            return
        count = 0
        await message.delete()

        for i in range(deletenum):
            async for message in message.channel.history(limit=100):
                if count == 1:
                    await message.delete()
                    count = 0
                    break
                if message.author == client.user:
                    await message.delete()
                    count = 1

    #LANCE COMMAND
    if message.content == '!lance': #lance command
        lancef = open('lance.txt', 'r')
        templist = lancef.read()
        lances = templist.split(',')
        chosen_lance = random.choice(lances)
        await message.channel.send(chosen_lance)
        lancef.close()

    #LOSERSQUEUE COMMAND
    if message.content == '!losersqueue': #losersqueue command
        concat = rankLookUp("Bellow")
        shittalk = [
            ':heart::heart: **Cameron is doing all he can!** :heart::heart:\n\n' + concat,
            ":heart::heart: **You'll get em next time Cam!** :heart::heart:\n\n" + concat,
            ':heart::heart: **Cameron suk** :heart::heart:\n\n' + concat,
            ':heart::heart: **bEsT BaRD nA** :heart::heart:\n\n' + concat,
            ':heart::heart: **Solid effort Cam** :heart::heart:\n\n' + concat,
            ':heart::heart: **"got tyler1 rip"** :heart::heart:\n\n' + concat,
            ':heart::heart: **hashinshin is on my dodge list** :heart::heart:\n\n' + concat,
            ':heart::heart: **"but my team"** :heart::heart:\n\n' + concat
        ]
        chosenshittalk = random.choice(shittalk)
        await message.channel.send(chosenshittalk)

    #HELP COMMAND
    if message.content == '!help':
        await message.channel.send("**!losersqueue** - Tells Cameron's current rank and a cute little quip" +
                                   "\n**!rank (summoner name)** - Lance will respond with the Solo/Duo rank of that player" +
                                   "\n**!pinkcap** - Emoji of Dylan" +
                                   "\n**!lance** - Gives you a random lance photo to brighten your day" +
                                   "\n**!laff** - Provides a random hot submission from r/LaughJokes" + 
                                   "\n**!delete (1-10)** - Deletes the last () amount of Lance messages" +  
                                   "\n**!play/!p (youtube link)** - Plays the youtube link audio in the channel you are currently in" +
                                   "\n**!theme** - Plays Lance's epic theme in the channel you are currently in" + 
                                   "\n**!stop** - Stops Lance from playing whatever audio he is currently playing" +
                                   "\n**!leave** - Disconnects Lance from your current channel" +
                                   "\n**!birthday** - Lance will tell you how long it is until the next person's birthday (he also reminds us every so often)" +
                                   "\n**!doge** - Lance will tell you the current trading price of dogecoin" +
                                   "\n\n**Adding reactions:**" +
                                   "\n🍆 - Lance will match your eggplant" +
                                   "\n👎 - Lance will delete this message if atleast 5 thumbs down emojis are reacted with")

    if message.content.startswith('!play ') or message.content.startswith('!p '):
        if message.content.startswith('!play'):
            mess = message.content.replace('!play ', "")
        else:
            mess = message.content.replace('!p ', "")

        if len(client.voice_clients) == 0:
            voice = await message.author.voice.channel.connect()    
        else:
            voice = client.voice_clients[0]

        await message.add_reaction('✅')

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
                }],
            }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(mess, download=False)
            URL = info['formats'][0]['url']

        if not voice.is_playing():
            voice.play(discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
        else:
            await message.channel.send("**Theres a song playing, wait until it is finished, or until Aidan implements a queue system**")
            queue.append(URL)

    if message.content == "!theme":
        if len(client.voice_clients) == 0:
            voice = await message.author.voice.channel.connect()    
        else:
            voice = client.voice_clients[0]
            
        if not voice.is_playing():
            voice.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source="../songs/theme.mp3"))
        else:
            await message.channel.send("**Theres a song playing, wait until it is finished, or until Aidan implements a queue system**")

    if message.content == "!leave":
        if len(client.voice_clients) == 0:
            voice = await message.author.voice.channel.connect()    
        else:
            voice = client.voice_clients[0]

        queue.clear()
        await voice.disconnect()

    if message.content == "!stop":
        if len(client.voice_clients) == 0:
            voice = await message.author.voice.channel.connect()    
        else:
            voice = client.voice_clients[0]

        queue.clear()
        voice.stop()


@client.event
async def on_voice_state_update(member, before, after):
    if after.afk: 
        await member.move_to(None)  

client.run(TOKEN)