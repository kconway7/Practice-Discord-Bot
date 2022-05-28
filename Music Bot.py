import asyncio
from multiprocessing import context
import discord, youtube_dl, os, asyncio
from discord.ext import commands
bot = commands.Bot(command_prefix = "!")
queuelist = []
filesToDelete = []

@bot.command()
async def join(context):
    channel = context.author.voice.channel
    if context.voice_client is not None:
        await context.voice_client.move_to(channel)
    else:
        await channel.connect()

@bot.command()
async def leave(context, help = "leaves the Voice Channel"):
    await context.voice_client.disconnect()

@bot.command()
async def play(context, *, searchword):
    ydl_opts = {}
 
    voice = context.voice_client

    #Get the Title
    if searchword[0:4] == "http" or searchword[0:3] == "www":
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(searchword, download = False)
            title = info["title"]
            url = searchword
 
    if searchword[0:4] != "http" and searchword[0:3] != "www":
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{searchword}", download = False)["entries"][0]
            title = info["title"]
            url = info["webpage_url"]
 
    ydl_opts = {
        'format' : 'bestaudio/best',
        "outtmpl" : f"{title}.mp3",
        "postprocessors": 
        [{"key" : "FFmpegExtractAudio", "preferredcodec" : "mp3", "preferredquality" : "192"}],   
    }


    def download(url):
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, download, url)
    
    #playing and queueing audioo
    if voice.is_playing():
        queuelist.append(title)
        await context.send(f"Added to Queue: ** {title} ** :musical_note:")
    else:
        voice.play(discord.FFmpegPCMAudio(f"{title}.mp3"), after = lambda e : check_queue())
        await context.send(f"Playing ** {title} ** :musical_note:")
        filesToDelete.append(title)
        await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.listening, name = title))

    def check_queue():
        try:
            if queuelist[0] != None:
                voice.play(discord.FFmpegPCMAudio(f"{queuelist[0]}.mp3"), after = lambda e : check_queue())
                coro = bot.change_presence(activity = discord.Activity(type = discord.ActivityType.listening, name = title))
                future = asyncio.run_coroutine_threadsafe(coro, bot.loop)
                future.result()
                filesToDelete.append(queuelist[0])
                queuelist.pop(0)
        except IndexError:
            for file in filesToDelete:
                os.remove(f"{file}.mp3")
                filesToDelete.clear()

#list of pause, resume, skip and view queue list commands
@bot.command()
async def pause(context):
    if context.voice_client.is_playing() == True:
        context.voice_client.pause()
    else:
        await context.send("Audio is not playing.")

@bot.command()
async def resume(context):
    if not context.voice_client.is_playing():
        context.voice_client.resume()
    else:
        await context.send("Audio is not playing.")

@bot.command(aliases = ["skip"])
async def stop(context):
    if context.voice_client.is_playing() == True:
        context.voice_client.stop()
    else:
        await context.send("Audio is not playing.")

@bot.command()
async def viewqueue(context):
    await context.send(f"Queue ** {str(queuelist)} ** ")

bot.run("") #Bot token goes here