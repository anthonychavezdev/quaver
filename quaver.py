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

def already_in_voice_channel(voice_client):
    return voice_client and voice_client.is_connected()

def not_valid_url(url):
    parsed_url = urlparse(url);
    return (parsed_url.scheme == "" or parsed_url.scheme != "http"
            and parsed_url.scheme != "https")

def get_audio(url):
    video = pafy.new(url)
    audio_track = video.getbestaudio()
    converted_track = PCMVolumeTransformer(FFmpegPCMAudio(audio_track.url, **FFMPEG_OPTIONS))
    return converted_track

def user_not_in_voice_channel(user):
    voice_state = user.voice
    return (voice_state is None)

async def set_volume(ctx, volume):
    if 0 <= volume <= 100:
        new_volume = float(volume / 100)
        ctx.voice_client.source.volume = new_volume
    else:
        embed = discord.Embed(
                title="Error!",
                description="Only enter numbers between 0 and 100",
                color=discord.Color.red())
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
    embed = discord.Embed(
            title="Help",
            description="Under construction",
            color=discord.Color.blue())

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
        embed = discord.Embed(
                title="Error!",
                description="The url is missing, try again!",
                color=discord.Color.red())

        return await ctx.send(embed=embed)

    if not_valid_url(url):
        embed = discord.Embed(
                title="Error!",
                description="Only http and https protocols work for now.",
                color=discord.Color.red())

        return await ctx.send(embed=embed)

    voice_state = ctx.author.voice
    if user_not_in_voice_channel(ctx.author):
        embed = discord.Embed(
                title="Error!",
                description="You need to be in a voice channel",
                color=discord.Color.red())

        return await ctx.send(embed=embed)

    voice_client = discord.utils.get(ctx.bot.voice_clients,
                                     guild=ctx.guild)

    if already_in_voice_channel(voice_client):
        await voice_client.move_to(voice_state.channel)
    else:
        await voice_state.channel.connect()

    audio = get_audio(url)
    ctx.voice_client.play(audio)

@commands.command()
async def vol(ctx, vol=None):
    if vol is None:
        embed = discord.Embed(
                title="Error!",
                description="A value is missing, try again!",
                color=discord.Color.red())

        return await ctx.send(embed=embed)

    if user_not_in_voice_channel(ctx.author):
        embed = discord.Embed(
                title="Error!",
                description="You need to be in a voice channel",
                color=discord.Color.red())
        return await ctx.send(embed=embed)

    if not already_in_voice_channel(ctx.voice_client):
        embed = discord.Embed(
                title="Error!",
                description="I'm not in a voice channel, nothing is playing.",
                color=discord.Color.red())
        return await ctx.send(embed=embed)

    try:
        volume = int(vol)

        await set_volume(ctx, volume)

    except:
        embed = discord.Embed(
                title="Error!",
                description="invalid value. Only use whole numbers between 0 and 100.",
                color=discord.Color.red())

        return await ctx.send(embed=embed)


@commands.command()
async def stop(ctx):
    if user_not_in_voice_channel(ctx.author):
        embed = discord.Embed(
                title="Error!",
                description="You need to be in a voice channel.",
                color=discord.Color.red())
        return await ctx.send(embed=embed)

    if not already_in_voice_channel(ctx.voice_client):
        embed = discord.Embed(
                title="Error!",
                description="I'm not in a voice channel, nothing is playing.",
                color=discord.Color.red())
        return await ctx.send(embed=embed)

    ctx.voice_client.stop()


@commands.command()
async def pause(ctx):
    if user_not_in_voice_channel(ctx.author):
        embed = discord.Embed(
                title="Error!",
                description="You need to be in a voice channel",
                color=discord.Color.red())
        return await ctx.send(embed=embed)

    try:
        ctx.voice_client.pause()
    except AttributeError:
        embed = discord.Embed(
                title="Error!",
                description="Nothing is playing!",
                color=discord.Color.red())
        return await ctx.send(embed=embed)

@commands.command()
async def resume(ctx):
    if user_not_in_voice_channel(ctx.author):
        embed = discord.Embed(
                title="Error!",
                description="You need to be in a voice channel",
                color=discord.Color.red())
        return await ctx.send(embed=embed)

    try:
        ctx.voice_client.resume()
    except AttributeError:
        embed = discord.Embed(
                title="Error!",
                description="Nothing is playing!",
                color=discord.Color.red())
        return await ctx.send(embed=embed)


@commands.command()
async def disconnect(ctx):
    if user_not_in_voice_channel(ctx.author):
        embed = discord.Embed(
                title="Error!",
                description="You need to be in a voice channel",
                color=discord.Color.red())
        return await ctx.send(embed=embed)

    if already_in_voice_channel(ctx.voice_client):
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()
    else:
        embed = discord.Embed(
                title="Error!",
                description="I'm not in a voice channel",
                color=discord.Color.red())
        return await ctx.send(embed=embed)

bot.add_command(play)
bot.add_command(vol)
bot.add_command(stop)
bot.add_command(pause)
bot.add_command(resume)
bot.add_command(disconnect)

bot.run(getenv("APP_TOKEN"))
