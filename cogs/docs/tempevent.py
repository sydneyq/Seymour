import discord
from discord.ext import commands
from database import Database
from .meta import Meta
import json
import os
import asyncio
import secret
import random
from numpy.random import choice

class TempEvent(commands.Cog):

    def __init__(self, client, database, meta):
        self.client = client
        self.dbConnection = database
        self.meta = meta
        self.tea_score = 0
        self.coffee_score = 0

        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, 'docs/rules.json')
        filename2 = os.path.join(dirname, 'docs/emojis.json')
        filename3 = os.path.join(dirname, 'docs/ids.json')

        with open(filename) as json_file:
            self.rules = json.load(json_file)

        with open(filename2) as json_file:
            self.emojis = json.load(json_file)

        with open(filename3) as json_file:
            self.ids = json.load(json_file)

    @commands.command(aliases=['changepts', 'changept', 'chpts', 'chpt'])
    async def changePoints(self, ctx, squad, pts:int):
        if not self.meta.isBotOwner(ctx.author):
            return
        else:
            if squad == 'Coffee':
                self.coffee_score = pts
            elif squad == 'Tea':
                self.tea_score = pts
            await ctx.send(embed = self.meta.embedDone())

    @commands.command(aliases=['pts'])
    async def points(self, ctx):
        embed2 = discord.Embed(
            title = 'Squad Points',
            description = self.emojis['Tea'] + ' **Tea Squad:** `' + str(self.tea_score) + '`\n' + self.emojis['Coffee'] + ' **Coffee Squad:** `' + str(self.coffee_score) + '`',
            color = discord.Color.teal()
        )

        if self.tea_score > self.coffee_score:
            embed2.set_thumbnail(url = 'https://cdn.discordapp.com/attachments/591611902459641856/613918428293627914/teamteaBean.png')
        elif self.coffee_score > self.tea_score:
            embed2.set_thumbnail(url = 'https://cdn.discordapp.com/attachments/591611902459641856/613918442034298890/teamcoffeeBean.png')

        await ctx.send(embed = embed2)

def setup(client):
    database_connection = Database()
    meta_class = Meta(database_connection)
    client.add_cog(TempEvent(client, database_connection, meta_class))
