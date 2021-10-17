#!/usr/bin/env python
import discord
from dotenv import load_dotenv
from os import getenv

load_dotenv()

client = discord.client.Client()

@client.event
async def on_ready():
    print("Logged in as {0.user}".format(client))

@client.event
async def on_message(message):
    """
    listens to a message in any channel, and responds
    accordingly
    """
    # We don't want the bot to endlessly reply to itself
    if message.author == client.user:
        return
    if message.content.startswith("!test"):
        await message.channel.send("This is a test message to see if everything is working.")

client.run(getenv("APP_TOKEN"))
