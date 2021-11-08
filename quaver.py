#!/usr/bin/env python
import discord
from dotenv import load_dotenv
from os import getenv
from discord.ext import commands
from urllib.parse import urlparse
import pafy
from discord import FFmpegPCMAudio, PCMVolumeTransformer
import logging
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename="quaver.log", encoding="utf-8", mode="w")
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger.addHandler(handler)

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'}


def bot_in_voice_channel(voice_client):
    """
    Returns a True or False value depending on whether or
    not the bot is in voice channel
    """
    return voice_client and voice_client.is_connected()

def not_valid_url(url):
    parsed_url = urlparse(url);
    return (parsed_url.scheme == "" or parsed_url.scheme != "http"
            and parsed_url.scheme != "https")

def get_audio(url):
    video = pafy.new(url, gdata=False)
    audio_track = video.getbestaudio()
    converted_track = PCMVolumeTransformer(FFmpegPCMAudio(audio_track.url, **FFMPEG_OPTIONS))
    return converted_track

def user_not_in_voice_channel(user):
    user_voice = user.voice
    return (user_voice is None)

def playSong(ctx, audio):
    ctx.voice_client.play(audio)

def create_embed(title, message, type):
    color=discord.Color.green()
    if type == "Error" or type == "error":
        color=discord.Color.red()
    elif type == "Informative" or type == "informative":
        color=discord.Color.blue()

    embed = discord.Embed(
        title=title,
        description=message,
        color=color)

    return embed

async def set_volume(ctx, volume):
    if 0 <= volume <= 100:
        new_volume = float(volume / 100)
        ctx.voice_client.source.volume = new_volume
    else:
        embed = create_embed("Error!", "Only enter numbers between 0 and 100", "Error")
        return await ctx.send(embed=embed)

load_dotenv()

bot = commands.Bot(command_prefix="!q")
# I want a custom help message,
# So I have to remve Discords existing help command
bot.remove_command("help")

@bot.listen()
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="!qhelp"))

@bot.command()
async def help(ctx):
    """
    Prints a lovely little help message
    """
    embed = create_embed("Help", "Here are the commands you can run", "Informative")
    embed.add_field (
        name="!qhelp",
        value="Displays this help message",
        inline=True
    )
    embed.add_field (
        name="!qplay",
        value="Plays a song given a url",
        inline=True
    )
    embed.add_field (
        name="!qstop",
        value="Stops playing the currently playing song and clears the song queue",
        inline=True
    )
    embed.add_field (
        name="!qpause",
        value="Pauses the currently playing song",
        inline=True
    )
    embed.add_field (
        name="!qresume",
        value="Resumes a paused song. Pausing is different from stopping",
        inline=True
    )

    await ctx.send(embed=embed)

@commands.command()
async def play(ctx, url=None):
    """
    The play command joins a voice channel and plays audio if the command issuer is in
    a voice channel. If the command issuer is not in a voice channel,
    an error message is displayed. If the command issuer is in a different
    voice channel than the bot, the bot moves to join that voice channel.
    If the command is missing a url, an error is displayed.
    """
    if url is None:
        embed = create_embed("Error!", "The url is missing, try again!", "Error")

        return await ctx.send(embed=embed)

    if not_valid_url(url):
        embed = create_embed("Error!", "Only http and https protocols work for now.", "Error")

        return await ctx.send(embed=embed)

    if user_not_in_voice_channel(ctx.author):
        embed = create_embed("Error!", "You need to be in a voice channel", "Error")

        return await ctx.send(embed=embed)

    user_voice = ctx.author.voice
    voice_client = discord.utils.get(ctx.bot.voice_clients,
                                     guild=ctx.guild)

    if bot_in_voice_channel(voice_client):
        # If the bot is already in a voice channel
        # move to the voice channel the user
        # is in
        await voice_client.move_to(user_voice.channel)
    else:
        await user_voice.channel.connect()


    audio = get_audio(url)
    playSong(ctx, audio)

@commands.command(aliases=["v"])
async def vol(ctx, vol=None):
    if vol is None:
        embed = create_embed("Error!", "A value is missing, try again!", "Error")

        return await ctx.send(embed=embed)

    if user_not_in_voice_channel(ctx.author):
        embed = create_embed("Error!", "You need to be in a voice channel", "Error")

        return await ctx.send(embed=embed)

    if not bot_in_voice_channel(ctx.voice_client):
        embed = create_embed("Error!", "I'm not in a voice channel, nothing is playing.", "Error")

        return await ctx.send(embed=embed)

    try:
        volume = int(vol)

        await set_volume(ctx, volume)

    except:
        embed = create_embed("Error!", "invalid value. Only use whole numbers between 0 and 100.", "Error")

        return await ctx.send(embed=embed)


@commands.command()
async def stop(ctx):
    if user_not_in_voice_channel(ctx.author):
        embed = create_embed("Error!", "You need to be in a voice channel.", "Error")

        return await ctx.send(embed=embed)

    if not bot_in_voice_channel(ctx.voice_client):
        embed = create_embed("Error!", "I'm not in a voice channel, nothing is playing.", "Error")

        return await ctx.send(embed=embed)

    ctx.voice_client.stop()


@commands.command()
async def pause(ctx):
    if user_not_in_voice_channel(ctx.author):
        embed = create_embed("Error!", "You need to be in a voice channel", "Error")

        return await ctx.send(embed=embed)

    try:
        ctx.voice_client.pause()
    except AttributeError:
        embed = create_embed("Error!", "Nothing is playing!", "Error")

        return await ctx.send(embed=embed)

@commands.command()
async def resume(ctx):
    if user_not_in_voice_channel(ctx.author):
        embed = create_embed("Error!", "You need to be in a voice channel", "Error")

        return await ctx.send(embed=embed)

    try:
        ctx.voice_client.resume()
    except AttributeError:
        embed = create_embed("Error!", "Nothing is playing!", "Error")

        return await ctx.send(embed=embed)


@commands.command(aliases=["dis", "disc"])
async def disconnect(ctx):
    if user_not_in_voice_channel(ctx.author):
        embed = create_embed("Error!", "You need to be in a voice channel", "Error")

    if bot_in_voice_channel(ctx.voice_client):
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()
    else:
        embed = create_embed("Error!", "I'm not in a voice channel", "Error")

        return await ctx.send(embed=embed)


bot.add_command(play)
bot.add_command(vol)
bot.add_command(stop)
bot.add_command(pause)
bot.add_command(resume)
bot.add_command(disconnect)

bot.run(getenv("APP_TOKEN"))
