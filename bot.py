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

client = commands.Bot(commands.when_mentioned_or(';'), case_insensitive=True)

@client.event
async def on_ready():
    print('Online!\n---')
    await client.change_presence(status=discord.Status.online)#, activity=discord.Game('DM me for ModMail!'))

@client.command()
async def reload(ctx, extension):
    if Meta.isBotOwner(None, ctx.author):
        client.unload_extension(f'cogs.{extension}')
        client.load_extension(f'cogs.{extension}')
        await ctx.send('Cog reloaded!')
    else:
        await ctx.send('You don\'t have the permissions to do that!')

@client.command()
async def load(ctx, extension):
    if Meta.isBotOwner(ctx.author):
        client.load_extension(f'cogs.{extension}')
        await ctx.send('Cog loaded!')
    else:
        await ctx.send('You don\'t have the permissions to do that!')

@client.command()
async def unload(ctx, extension):
    if Meta.isBotOwner(ctx.author):
        client.unload_extension(f'cogs.{extension}')
        await ctx.send('Cog unloaded!')
    else:
        await ctx.send('You don\'t have the permissions to do that!')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

client.run(secret.BOT_TOKEN)
