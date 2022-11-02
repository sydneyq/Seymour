import discord
import os
from discord.ext import commands

import sys
import signal
import asyncio
import pymongo
import math

import database
import secret

from cogs.meta import Meta

intents = discord.Intents.all()
intents.reactions = True
#client = discord.Client(intents=intents)
client = commands.Bot(commands.when_mentioned_or(';'), case_insensitive=True, intents=intents)

@client.event
async def on_ready():
    for f in os.listdir('./cogs'):
        if f.endswith('.py'):
            await client.load_extension(f'cogs.{filename[:-3]}')
    print('Online!\n---')
    await client.change_presence(status=discord.Status.online)#, activity=discord.Game('DM me for ModMail!'))

@client.command()
async def reload(ctx, extension):
    member = ctx.author
    if member.id == secret.OLIVE_ID or member.id == secret.SYD_ID:
        client.unload_extension(f'cogs.{extension}')
        client.load_extension(f'cogs.{extension}')
        await ctx.send('Cog reloaded!')
    else:
        await ctx.send('You don\'t have the permissions to do that!')

@client.command()
async def load(ctx, extension):
    member = ctx.author
    if member.id == secret.OLIVE_ID or member.id == secret.SYD_ID:
        client.load_extension(f'cogs.{extension}')
        await ctx.send('Cog loaded!')
    else:
        await ctx.send('You don\'t have the permissions to do that!')

@client.command()
async def unload(ctx, extension):
    member = ctx.author
    if member.id == secret.OLIVE_ID or member.id == secret.SYD_ID:
        client.unload_extension(f'cogs.{extension}')
        await ctx.send('Cog unloaded!')
    else:
        await ctx.send('You don\'t have the permissions to do that!')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

client.run(secret.BOT_TOKEN)
