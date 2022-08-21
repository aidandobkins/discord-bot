import discord
import asyncio
import datetime
from discord.ext.commands import Bot
from discord.utils import *
from discord.ext import commands
from discord import FFmpegPCMAudio
from discord import Embed
from youtube_dl import YoutubeDL
import youtube_dl
import random
import praw
import os
import urllib.request, urllib.parse, re
from datetime import date
import time
from discord.ext import tasks
from discord.utils import get
from discord.ext import commands
from discord import NotFound
from discord.utils import get
import json
import sqlite3
from riotwatcher import LolWatcher, ApiError

f = open("api.txt", 'r')
apidata = f.read().splitlines()
f.close()

#SQL STUFF
con = sqlite3.connect("owes.db")

#NOMICS API STUFF
url = apidata[0]

#REDDIT API
reddit = praw.Reddit(
     client_id = apidata[1],
     client_secret = apidata[2],
     user_agent = apidata[3]
)

#RIOT API STUFF
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
tokenf = open('token.txt', 'r')
TOKEN = tokenf.readline()
tokenf.close()

client = discord.Client()

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
queue = []
namequeue = []
voice = ""

def playSong(err):
    if not voice.is_playing() and len(queue) > 0:
        namequeue.pop(0)
        voice.play(discord.FFmpegPCMAudio(source=queue.pop(0), **FFMPEG_OPTIONS), after=playSong)
    #elif len(queue) == 0 and not voice.is_playing():
        #await leave()
        
async def leave():
    time.sleep(300)
    if(not voice.is_playing()):
        #PRINT A STATEMENT SAYING ITS LEAVING AFTER 5 MINS
        await voice.disconnect()

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
    global voice
    if message.author == client.user:
        return

    #PINKCAP COMMAND
    if message.content == '!pinkcap':
        await message.channel.send('https://imgur.com/a/Dbt8sdq')
        
    #LEAGUE RANK COMMAND
    elif message.content.startswith('!rank '):
        rankstr = message.content.replace('!rank ', "")
        newmsg = rankLookUp(rankstr)
        await message.channel.send(newmsg)

    #BIRTHDAY COMMAND
    elif message.content == '!birthday':
        bday = checkBirthdays()

        if bday[0] == 0:
            await message.channel.send("It's " + bday[1] + "'s Birthday Today!!!")
        else:
            await message.channel.send("There are " + str(bday[0]) + " days until " + bday[1] + "'s birthday.")

    #DOGE COMMAND
    elif message.content == '!doge':
        reading = urllib.request.urlopen(url)
        for i in range(37):
            reading.read(5)
        price = reading.read(12)
        price1 = price.decode('utf-8')
        price1 = price1.strip('\"')
        printprice = "The price of Dogecoin is: \n> " + price1 + " USD"
        await message.channel.send(printprice)

    #LAFF COMMAND
    elif message.content == '!laff': #laughjokes reddit command
        num = random.randint(0,49)
        i = 0
        for submission in reddit.subreddit("LaughJokes").hot(limit=50):
            if num == i:   ##and submission.url == laffBlacklist.parse
                laff = submission.url
            i += 1
        await message.channel.send(laff)
    
    #DELETE COMMAND
    elif message.content.startswith('!delete '):
        deletenumstr = message.content.replace('!delete ', "")
        deletenum = int(deletenumstr)
        if deletenum > 10:
            await message.channel.send("Put in a lower number, max is 10")
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
    elif message.content == '!lance': #lance command
        lancef = open('lance.txt', 'r')
        templist = lancef.read()
        lances = templist.split(',')
        chosen_lance = random.choice(lances)
        await message.channel.send(chosen_lance)
        lancef.close()

    #LOSERSQUEUE COMMAND
    elif message.content == '!losersqueue': #losersqueue command
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
    elif message.content == '!help':
        await message.channel.send("**!losersqueue** - Tells Cameron's current rank and a cute little quip" +
                                   "\n**!rank (summoner name)** - Lance will respond with the Solo/Duo rank of that player" +
                                   "\n**!pinkcap** - Emoji of Dylan" +
                                   "\n**!lance** - Gives you a random lance photo to brighten your day" +
                                   "\n**!laff** - Provides a random hot submission from r/LaughJokes" + 
                                   "\n**!delete (1-10)** - Deletes the last () amount of Lance messages" +  
                                   "\n**!birthday** - Lance will tell you how long it is until the next person's birthday (he also reminds us every so often)" +
                                   "\n**!doge** - Lance will tell you the current trading price of dogecoin" +
                                   "\n\n**Adding reactions:**" +
                                   "\n🍆 - Lance will match your eggplant" +
                                   "\n👎 - Lance will delete this message if atleast 5 thumbs down emojis are reacted with" +
                                   "\n\n**BALANCE COMMANDS**" +
                                   "\n**!seebalance (person)** - View the amount that someone owes people (use no name to see yourself)" +
                                   "\n**!(PersonX) owes (PesonY) (amount)** - Sets the amount that somebody owes somebody else" +
                                   "\n**!(PersonX) paid (PesonY) (amount)** - Sets the amount that somebody paid somebody else" +
                                   "\nPossible syntax include any number and combination of people, and the use of '$', 'and', 'owe'/'owes'" +
                                   "\n\n**SONG COMMANDS**" +
                                   "\n**!play/!p (yt link/yt search)** - Plays the youtube link audio in the channel you are currently in" +
                                   "\n**!theme** - Plays Lance's epic theme in the channel you are currently in" + 
                                   "\n**!stop** - Stops Lance from playing whatever audio he is currently playing and clears queue" +
                                   "\n**!skip** - Skips to the next song in the queue" +
                                   "\n**!songdel (queue#)** - Removes the specified song from the queue" +
                                   "\n**!leave** - Disconnects Lance from your current channel" +
                                   "\n**!queue** - Shows what is in the queue currently")
    #OWES COMMANDS
    elif message.content.startswith('!seebalance ') or message.content == '!seebalance':
        if message.content == '!seebalance':
            userid = message.author.id
            #TODO: mark whose id is whose, and store those in a separate file for privacy
            if userid == 183383851735711744:
                name = 'aidan'
            else:
                name = 'unknown'
        else:
            name = message.content.replace('!seebalance ', "")

        #TODO: SQL query to find balance in db, according to name row
        cur = con.cursor()
        rows = cur.execute("SELECT * FROM " + name)

        await message.channel.send(str(rows.fetchall()))

    elif message.content.startswith('!') and (' owes ' in message.content or ' owe ' in message.content): 
        #syntax is "!Aidan owes Cody Dylan 20" || !Aidan Dylan owe Cody 30
        #it also can parse out ' and ' and '$' to allow for more natural language like:
        #!Aidan and Dylan owe Cody and Brandon $30
        mess = message.content.replace('!', "")
        mess = mess.replace(' and ', " ")
        mess = mess.replace('$', "")
        if ' owes ' in message.content:
            mess = mess.split(" owes ") #[Aidan, Cody Dylan 20]
        else:
            mess = mess.split(" owe ") #[Aidan Dylan, Cody 30]
        owers = mess[0].split() #[Aidan] || [Aidan, Dylan]
        mess = mess[1].split() #[Cody, Dylan, 20] || [Cody, 30]
        amount_owed = mess[-1] #20 || 30
        owees = mess[:-1] #[Cody, Dylan] || [Cody]

        for i in range(len(owers)):
            owers[i] = owers[i].lower()

        for i in range(len(owees)):
            owees[i] = owees[i].lower()

        #TODO: SQL Query to insert this info into the db
        cur = con.cursor()
        
        for i in owers:
            cur.execute("CREATE TABLE IF NOT EXISTS " + i + " (person_owed VARCHAR(20), amount_owed INT(10))")
            for j in owees:
                existing_owed = cur.execute("SELECT amount_owed FROM " + i + " WHERE person_owed = '" + j + "'")
                existing_owed = existing_owed.fetchone()
                if existing_owed == None:
                    cur.execute("INSERT INTO " + i + ' VALUES ("' + j + '", ' + str(amount_owed) + ')')
                else:
                    cur.execute("UPDATE " + i + " SET amount_owed = " + str(amount_owed + int(existing_owed[0])) + "WHERE person_owed = '" + j + "'")

        await message.channel.send("Owers: " + str(owers) + "\nOwees: " + str(owees) + "\nAmount Owed to the Owees (Individually, not split up evenly): " + str(amount_owed))

    elif message.content.startswith('!') and ' paid ' in message.content: 
         #syntax is "!Aidan paid Cody 20"
        #it also can parse out ' and ' and '$' to allow for more natural language like:
        #!Aidan and Dylan paid Cody and Brandon $30
        mess = message.content.replace('!', "")
        mess = mess.replace(' and ', " ")
        mess = mess.replace('$', "")
        mess = mess.split(" paid ") #[Aidan, Cody Dylan 20]

        payers = mess[0].split() #[Aidan] || [Aidan, Dylan]
        mess = mess[1].split() #[Cody, Dylan, 20] || [Cody, 30]
        amount_paid = mess[-1] #20 || 30
        payees = mess[:-1] #[Cody, Dylan] || [Cody]

        for i in range(len(payers)):
            payers[i] = payers[i].lower()

        for i in range(len(payees)):
            payees[i] = payees[i].lower()

        #TODO: SQL Query to insert this info into the db
        cur = con.cursor()

        for i in payers:
            for j in payees:
                existing_owed = cur.execute("SELECT amount_owed FROM " + i + " WHERE person_owed = '" + j + "'")
                existing_owed = existing_owed.fetchone()
                if existing_owed == None:
                    await message.channel.send(str(payers) + " didn't owe " + str(payees) + " anything.")
                else:
                    remaining_owed = int(existing_owed[0]) - int(amount_paid)
                    if remaining_owed < 0: 
                        remaining_owed = 0
                    cur.execute("UPDATE " + i + " SET amount_owed = " + str(remaining_owed) + " WHERE person_owed = '" + j + "'")

        await message.channel.send("Payers: " + str(payers) + "\nPayees: " + str(payees) + "\nAmount Paid to the Payees (Individually, not split up evenly): " + str(amount_paid))

    #SONG COMMANDS
    elif message.content.startswith('!play ') or message.content.startswith('!p '):
        if message.content.startswith('!play'):
            mess = message.content.replace('!play ', "")
        else:
            mess = message.content.replace('!p ', "")

        await message.add_reaction('✅')
        
        if not mess.startswith('http'):
            query_string = urllib.parse.urlencode({'search_query': mess})
            htm_content = urllib.request.urlopen('http://www.youtube.com/results?' + query_string)
            results = re.findall(r'/watch\?v=(.{11})', htm_content.read().decode())
            mess = 'http://www.youtube.com/watch?v=' + results[0]
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'highWaterMark': '1<<25',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
                }],
            }
        
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(mess, download=False)
            URL = info['formats'][0]['url']
            vidtitle = info['title']
            thumb = info['thumbnail']
        
        if len(client.voice_clients) == 0:
            voice = await message.author.voice.channel.connect()    
        else:
            voice = client.voice_clients[0]

        namequeue.append(vidtitle)
        queue.append(URL)
        
        if (len(queue) == 1 and voice.is_playing()) or (len(queue) > 1):
            titlemess = "**ADDED TO QUEUE**\n"
        elif len(queue) == 1:
            titlemess = "**NOW PLAYING**\n"
        
        duration = datetime.timedelta(seconds = int(info['duration']))
        
        embedvar = discord.Embed(title=titlemess)
        embedvar.set_thumbnail(url=thumb)
        embedvar.add_field(name="Song", value=str("[" + vidtitle + "](" + mess + ")"), inline=False)
        embedvar.add_field(name="Duration", value=duration)
        if titlemess != "**NOW PLAYING**\n":
            embedvar.add_field(name="Position in Queue", value=str(queue.index(URL)+1))
        await message.channel.send(embed=embedvar)
        
        if not voice.is_playing() and len(queue) > 0:
            namequeue.pop(0)
            voice.play(discord.FFmpegPCMAudio(source=queue.pop(0), **FFMPEG_OPTIONS), after=playSong)

    if message.content == "!theme":
        if len(client.voice_clients) == 0:
            voice = await message.author.voice.channel.connect()    
        else:
            voice = client.voice_clients[0]
            
        namequeue.append("Theme Song")
        queue.append("../Songs/theme.mp3")
        
        if not voice.is_playing() and len(queue) > 0:
            namequeue.pop(0)
            voice.play(discord.FFmpegPCMAudio(source=queue.pop(0), **FFMPEG_OPTIONS), after=playSong)

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
        namequeue.clear()
        voice.stop()

        #await playSong(err)
        
    if message.content == "!queue":
        if len(namequeue) == 0:
            await message.channel.send("The Song Queue is empty")
        else: 
            songs = "```"
            for i in range(len(namequeue)):
                songs += "Song " + str(i+1) + ": " + namequeue[i] + '\n'
            
            songs += "```"
            await message.channel.send(songs)
    
    if message.content == "!skip":
        if len(client.voice_clients) == 0:
            voice = await message.author.voice.channel.connect()    
        else:
            voice = client.voice_clients[0]

        voice.stop()
        
    if message.content.startswith("!songdel "):
        mess = message.content.replace('!songdel ', "")
        
        if len(queue) == 0:
            await message.channel.send("The queue is empty.")
        else:
            queue.pop(int(mess)-1)
            await message.channel.send("**Removed: **" + namequeue.pop(int(mess)-1))
            

            
    


@client.event
async def on_voice_state_update(member, before, after):
    if after.afk: 
        await member.move_to(None)  

client.run(TOKEN)