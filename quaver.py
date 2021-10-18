#!/usr/bin/env python
import discord
from dotenv import load_dotenv
from os import getenv
from discord.ext import commands

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


bot.run(getenv("APP_TOKEN"))
