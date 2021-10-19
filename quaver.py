#!/usr/bin/env python
import discord
from dotenv import load_dotenv
from os import getenv
from discord.ext import commands

def already_in_voice_channel(voice_client):
    return voice_client and voice_client.is_connected()

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
            color=discord.Color.blue()
            )
    await ctx.send(embed=embed)

@commands.command()
async def play(ctx, url=None):
    """
    The play command joins a voice channel if the command issuer is in
    a voice channel. If the command issuer is not in a voice channel,
    an error message is displayed. If the command issuer is in a different
    voice channel than the bot, the bot moves to join that voice channel.
    If the command is missing a url, an error is displayed.
    """
    if url is None:
        return await ctx.send("The url is missing, try again!")
    voice_state = ctx.author.voice
    if voice_state is None:
        return await ctx.send("You need to be in a voice channel")
    else:
        voice_client = discord.utils.get(ctx.bot.voice_clients,
                                         guild=ctx.guild)
        if already_in_voice_channel(voice_client):
            await voice_client.move_to(voice_state.channel)
        else:
            await voice_state.channel.connect()

bot.add_command(play)

bot.run(getenv("APP_TOKEN"))
