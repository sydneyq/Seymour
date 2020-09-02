import discord
from discord.ext import commands
from database import Database
from .meta import Meta
import random
import json
import os
import asyncio
from numpy.random import choice
import secret
import datetime

class Cooldown(commands.Cog):

    def __init__(self, client, database, meta):
        self.client = client
        self.dbConnection = database
        self.meta = meta

        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, 'docs/store.json')

        with open(filename) as json_file:
            self.store = json.load(json_file)

    #@commands.cooldown(1, 60*60*24, commands.BucketType.user)
    @commands.command(aliases=['treasurehunt', 'treasure'])
    async def daily(self, ctx):
        id = ctx.message.author.id

        user = self.meta.getProfile(ctx.author)

        #datetime check
        if not user['daily'] == '':
            if not self.meta.hasBeen24Hours(user['daily'], self.meta.getDateTime()):
                minutes = self.meta.getMinuteDifference(user['daily'], self.meta.getDateTime())
                hr = int(minutes / 60)
                min = minutes % 60
                embed = discord.Embed(
                    title = 'Sorry, you need to wait `'+str(hr)+'` hours and `' + str(min) + '` more minutes!' ,
                    color = discord.Color.teal()
                )
                await ctx.send(embed = embed)
                return

        #companion check
        companion = user['companion']
        if companion == '':
            embed = discord.Embed(
                title = 'Sorry, you need a companion for that!',
                color = discord.Color.teal()
            )
            await ctx.send(embed = embed)
            return

        #update datetime
        self.dbConnection.updateProfile({"id": id}, {"$set": {"daily": self.meta.getDateTime()}})

        elem = ['gift', 'coins']
        wei = [.1, .9]
        ref = choice(elem, p=wei)

        isEvolved = False

        if (ref == 'coins'):
            elements = [25, 50, 75]
            weights = [0.6, 0.3, 0.1]

            if companion in [item['name'] for item in self.store['Evolved Companions']]:
                isEvolved = True
                weights = [0.3, 0.5, 0.2]

            amt = choice(elements, p=weights)

            coins = user['coins']
            coins = coins + int(amt)
            self.dbConnection.updateProfile({"id": id}, {"$set": {"coins": coins}})

            embed = discord.Embed(
                title = ctx.author.name + ', your ' + companion + ' found `' + str(amt) + '` coins!',
                description = '<@' + str(id) + '>\'s coin count: `' + str(coins) + '`',
                color = discord.Color.teal()
            )
        elif (ref == 'gift'):
            gifts = user['gifts']
            gifts += 1
            self.dbConnection.updateProfile({"id": id}, {"$set": {"gifts": gifts}})

            embed = discord.Embed(
                title = ctx.author.name + ', your ' + companion + ' found a Coin Gift!',
                description = '<@' + str(id) + '>\'s gifts: `' + str(gifts) + '`',
                color = discord.Color.teal()
            )

        if companion != '':
            isFound = False
            for c in self.store['Coin Companions']:
                if c['name'].lower() == companion.lower():
                    embed.set_image(url = c['src'])
                    isFound = True
                    break

            if not isFound:
                for c in self.store['Helped Companions']:
                    if c['name'].lower() == companion.lower():
                        embed.set_image(url = c['src'])
                        isFound = True
                        break

            if not isFound:
                for c in self.store['Evolvable Companions']:
                    if c['name'].lower() == companion.lower():
                        embed.set_image(url = c['src'])
                        isFound = True
                        break

            if not isFound:
                for c in self.store['Evolved Companions']:
                    if c['name'].lower() == companion.lower():
                        embed.set_image(url = c['src'])
                        isFound = True
                        break

        if isEvolved:
            embed.set_footer(text = 'Evolved Companion detected! You have a higher chance of getting more coins.')
        await ctx.channel.send(embed = embed)

def setup(client):
    database_connection = Database()
    meta_class = Meta(database_connection)
    client.add_cog(Cooldown(client, database_connection, meta_class))
