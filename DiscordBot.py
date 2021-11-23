import discord
import requests
import json
import time
import youtube_dl
import os
import random
from discord import client
from discord.ext import commands
from discord import Intents
from discord import FFmpegPCMAudio

dababyImages = ["dababy1.jpg", "dababy2.jpg", "dababy3.jpg", "dababy4.jpg"] #Array met een aantal images waaruit geselecteerd kan worden.
keys = ["REDACTED"] #Dit is de sleutel waarmee de bot gemanipuleerd word, deze is identical.
prefix = "?"

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix = prefix ,help_command=None, intents=intents)

#Functions
def jokeApi(): #Deze functie krijgt een random joke van een api, bij deze api is geen key nodig.
    jokeUrl = "https://official-joke-api.appspot.com/random_joke"
    response = requests.request("GET", jokeUrl)
    jokeApiResponse = str((json.loads(response.text)['setup']) + " " + (json.loads(response.text)['punchline']))
    return jokeApiResponse    

#Commands
@client.event #Dit is een commando dat een reactie geeft wanneer de bot klaar is voor gebruik
async def on_ready():
    await client.change_presence()
    print('Status: Online')
    
@client.command(pass_context=True) #Met dit commando word er een bericht gestuurd waarbij alle bruikbare commando's weergeven worden
async def help(ctx):
    embed = discord.Embed(
        title = 'Helping you!',
        description = 'Available commands:',
        colour = discord.Colour.blue()
    )

    embed.set_footer(text=('Requested by: ' + ctx.message.author.name))
    embed.set_thumbnail(url='https://cdn.discordapp.com/avatars/852510059874877441/9ca138c0a16d7f3de8bd2c0833136b0c.webp?size=1024')
    embed.add_field(name=(prefix + 'introduce'), value='Displays a short introduction of the bot.')
    embed.add_field(name=(prefix + 'ping'), value='Displays response time of the bot.')
    embed.add_field(name=(prefix + 'clear'), value='Removes certain amount of messages from a channel.')
    embed.add_field(name=(prefix + 'joke'), value='Displays a random joke each time.')
    embed.add_field(name=(prefix + 'join'), value='Joins the channel you are in.')
    embed.add_field(name=(prefix + 'leave'), value='Leaves the channel the bot is in.')
    embed.add_field(name=(prefix + 'play + [Youtube URL]'), value='Plays the Youtube url you requested.')
    embed.add_field(name=(prefix + 'pause'), value='Pauses the audio currently playing.')
    embed.add_field(name=(prefix + 'resume'), value='Resumes the audio currently playing.')
    embed.add_field(name=(prefix + 'stop'), value='Stops playing audio.')
    embed.add_field(name=(prefix + 'finn'), value='Random easter egg.')
    embed.add_field(name=(prefix + 'dababy'), value='Random easter egg.')

    await ctx.send(embed=embed)

@client.command(aliases=['Introduce']) #Dit commando zorgt ervoor dat de bot zichzelf voorsteld
async def introduce(ctx):
    await ctx.send("Hello, I am RedAlp! I am here to help.")

@client.command(aliases=['Ping']) #Met dit command krijg je de response tijd van de bot, hoe lang het duurt voor de bot om te reageren
async def ping(ctx):
    await ctx.send("Pong! " + str(round(client.latency * 1000))+ "ms")

@client.command(aliases=['Clear']) #Verwijderd een geselecteerd aantal berichten uit het kanaal, als er geen getal is opgegeven word het default 10 gedaan.
async def clear(ctx, amount=10):
    await ctx.channel.purge(limit = amount)

@client.command(aliases=['Joke']) #Geeft een random joke, met gebruik van de voorgenoemde API
async def joke(ctx):
    jokeApiResponse = jokeApi()
    await ctx.send(jokeApiResponse)

@client.command(aliases=['Join']) #Met die commando zal de bot checken of jij in een voice channel zit en zo ja, hetzelfde channel joinen.
async def join(ctx):
    if (ctx.author.voice):
        channel = ctx.message.author.voice.channel
        await channel.connect()
        await ctx.message.add_reaction('✅')
    else:
        await ctx.send("You are not in a voice channel, you must be in one for me to join!")

@client.command(pass_context = True, aliases=['dc', 'Leave']) #Met die commando zal de bot checken of hijzelf in een voice channel zit, zo ja zal hij dit channel leaven.
async def leave(ctx):
    if (ctx.voice_client):
        await ctx.guild.voice_client.disconnect()
        await ctx.message.add_reaction('✅')
    else:
        await ctx.send("I am not in a voice channel.")

#Play audio

@client.command(pass_content = True, aliases=['p', 'P', 'Play']) #Met dit command zal de bot eerst de link afgaan met het Youtube_DL package en zodra die een file vind met .mp3 zal hij deze downloaden en daarna door middel van FFmpeg afspelen.
async def play(ctx, url:str):

    if not (ctx.author.voice):
        channel = ctx.message.author.voice.channel
        await ctx.send("To request a song, you must be in a voice channel.")

    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
    except PermissionError:
        await ctx.send("Wait for the current playing music to end or use the 'stop' command")
        return

    Channel = ctx.message.author.voice.channel
    if not (ctx.voice_client):
        await Channel.connect()
    await ctx.message.add_reaction('✅')
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            nowPlaying = str(file)[0:-16]
            nowPlaying2 = nowPlaying
            os.rename(file, "song.mp3")
    voice.play(discord.FFmpegPCMAudio("song.mp3"))

    songEmbed = discord.Embed( #Embed voor het aangeven welk liedje aan het spelen is.
        title = 'Music Time!',
        description = 'Now playing: ' + nowPlaying,
        colour = discord.Colour.blue()
    )

    songEmbed.set_footer(text='Author: ' + ctx.message.author.name)
    songEmbed.set_thumbnail(url='https://cdn.discordapp.com/avatars/852510059874877441/9ca138c0a16d7f3de8bd2c0833136b0c.webp?size=1024')
    songEmbed.add_field(name='Url: ', value=url, inline=True)
    await ctx.send(embed=songEmbed)

@client.command(pass_context = True) #Pauseerd de media die op het moment aan het spelen is
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients,guild=ctx.guild)
    if voice.is_playing(): #Kijkt of er muziek aan het spelen is
        voice.pause()
        await ctx.message.add_reaction('✅')
    else:
        await ctx.send("There is no audio playing right now.")

@client.command(pass_context = True) #Vervolgd de media die op het moment aan het spelen is
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients,guild=ctx.guild)
    if voice.is_paused(): #Kijkt of er muziek gepauseerd is.
        voice.resume()
        await ctx.message.add_reaction('✅')
    else:
        await ctx.send("There is no audio paused right now.")

@client.command(pass_context = True) #Stopt compleet met het spelen van media.
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients,guild=ctx.guild)
    voice.stop() #Stopt met spelen van audio
    await ctx.message.add_reaction('✅')

#Easter eggs, Geen uitleg bij.
@client.command(pass_content = True, aliases=['Finn'])
async def finn(ctx):
    if (ctx.voice_client):
        await ctx.send("Nee, niet nu ik er al ben.")
    elif (ctx.author.voice):
        channel = ctx.message.author.voice.channel
        voice = await channel.connect()
        finnsource = FFmpegPCMAudio('wetfart.wav')
        player = voice.play(finnsource)
        while voice.is_playing():
            if not (voice.is_playing()):
                break
        await ctx.guild.voice_client.disconnect()
    else:
        await ctx.send("Deze zemmel is gewoon niet in een voice channel.")

@client.command(pass_content = True)
async def dababy(ctx):
    await ctx.send("Lezzz go, I'm dababy", file=discord.File(random.choice(dababyImages))) #Geeft een random image uit een lijst van png images

#Events
@client.event #Wanneer iemand de guild/server joined zal de bot dat zien en een welkombericht sturen
async def on_member_join(member):
    for channel in member.guild.channels: #kijkt bij elke channel of de channel met de string te vinden is.
        if str(channel) == "welcome":
            await channel.send("`Welcome `*" + str(member)[0:-5] + "*")

@client.event #Wanneer iemand de guild/server verlaat zal de bot dat zien en een vaarwelbericht sturen
async def on_member_remove(member):
    for channel in member.guild.channels: #kijkt bij elke channel of de channel met de string te vinden is.
        if str(channel) == "welcome":
            await channel.send("`Goodbye `*" + str(member)[0:-5] + "*")

client.run(keys[0]) #Hier is de key van de bot nodig, bovenin genoemd
