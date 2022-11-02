import discord
from discord.ext import commands

import json
import random
from random import randint

import aiohttp
import asyncio
import async_timeout

import requests

class Pics(commands.Cog):
    channelID = 593153723610693632

    def __init__(self, client):
        self.client = client

    @commands.command(alises=['breath', 'anxiety'])
    async def breathe(self, ctx):
        responses = ['https://3.bp.blogspot.com/-CPo9Wmvy3nk/WOor5x_RuvI/AAAAAAABIPU/TwjI_F_ltc8alkqgGOMC3gLv76n2mc5-ACLcB/s640/1ninetymileshD6nE1u3bq3no1_500.gif',
        'https://media0.giphy.com/media/zzwt3TRTaULv2/source.gif',
        'https://media.giphy.com/media/krP2NRkLqnKEg/giphy.gif']
        embed = discord.Embed(
            title = 'Take a minute to breathe.',
            color = discord.Color.teal()
        )
        embed.set_image(url = random.choice(responses))

        await ctx.send(embed = embed)

    @commands.command(pass_context=True)
    async def dog(self, ctx):
        response = requests.get('https://dog.ceo/api/breeds/image/random')
        data = response.json()
        await ctx.message.channel.send(data['message'])

    @commands.command(pass_context=True)
    async def corgipic(self, ctx):
        response = requests.get('https://dog.ceo/api/breed/corgi/images/random')
        data = response.json()
        await ctx.message.channel.send(data['message'])

    @commands.command(pass_context=True)
    async def cat(self, ctx):
        response = requests.get('https://aws.random.cat/meow')
        data = response.json()
        await ctx.message.channel.send(data['file'])

async def setup(client):
    await client.add_cog(Pics(client))
