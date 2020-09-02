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

class Corgi(commands.Cog):

    def __init__(self, client, database, meta):
        self.client = client
        self.dbConnection = database
        self.meta = meta

        dirname = os.path.dirname(__file__)
        filename2 = os.path.join(dirname, 'docs/emojis.json')
        filename3 = os.path.join(dirname, 'docs/ids.json')
        filename4 = os.path.join(dirname, 'docs/corgi.json')

        with open(filename2) as json_file:
            self.emojis = json.load(json_file)

        with open(filename3) as json_file:
            self.ids = json.load(json_file)

        with open(filename4) as json_file:
            self.corgi = json.load(json_file)

    @commands.command(aliases=['c'])
    async def corgi(self, ctx, corgi = None):
        isTea = True
        user = self.meta.getProfile(ctx.author)
        if corgi is None or not(corgi.lower().capitalize() == 'Mocha' or corgi.lower().capitalize() == 'Matcha'):
            if user['squad'] == '':
                if corgi == '':
                    await ctx.send(embed = self.meta.embedOops())
                    return
                else:
                    if corgi == 'mocha' or corgi.lower() == 'tea':
                        corgi = 'Mocha'
                    elif corgi == 'matcha' or corgi.lower() == 'coffee':
                        corgi = 'Matcha'
                    else:
                        await ctx.send(embed = self.meta.embedOops())
                        return
            else:
                if user['squad'] != 'Tea':
                    isTea = False
                    corgi = 'Mocha'
                else:
                    corgi = 'Matcha'
        await ctx.send(embed = self.embedCorgi(corgi))

    def getCorgi(self, corgi):
        corgi_profile = self.dbConnection.findMeta({"id": corgi})
        return corgi_profile

    def embedCorgi(self, corgi):
        corgi_profile = self.getCorgi(corgi)
        str = ''

        v = 'Keep your Squad Corgi happy by `+feed`ing them Biscuits when they\'re sad or hungry!'
        v += ' Biscuits cost 100 coins each.'

        mood = self.getMood(corgi)
        embed = discord.Embed(
            title = corgi + ' is feeling `' + mood + '`',
            description = v,
            color = discord.Color.teal()
        )
        embed.set_thumbnail(url = self.getMoodImage(mood))
        return embed

    def getMood(self, corgi):
        mood = self.getCorgi(corgi)['mood']
        if mood == 'hungry' or mood == 'sad':
            return mood
        elif mood == '' or random.random() < .05:
            moods = ['awake',
            'sleepy',
            'playful',
            'smiley',
            'hype',
            'a-okay',
            'happy',
            'excited',
            'done',
            'tired',
            'sneaky']
            mood = random.choice(moods)
            self.setMood(corgi, mood)
        return mood

    def isHungry(self, corgi):
        mood = self.getMood(corgi)
        if mood == 'hungry' or mood == 'sad':
            return True
        return False

    def getMoodImage(self, mood):
        return self.corgi[mood]

    @commands.command()
    async def feed(self, ctx):
        #get person's squad
        user = self.meta.getProfile(ctx.author)
        squad = user['squad']
        corgi = 'Matcha'
        if squad == '':
            await ctx.send(embed = self.meta.embedOops())
            return
        else:
            if squad == 'Coffee':
                corgi = 'Mocha'
        #check if corgi is sad or hungry
        mood = self.getMood(corgi)
        if not (mood == 'sad' or mood == 'hungry'):
            embed = discord.Embed(
                title = corgi + ' isn\'t hungry right now!',
                description = 'Feed your Squad Corgi biscuits when they\'re hungry or sad!',
                color = discord.Color.teal()
            )
            await ctx.send(embed = embed)
            return
        #check if they have 100 coins
        if user['coins'] < 100:
            embed = discord.Embed(
                title = 'You need 100 coins to buy a Biscuit!',
                description = self.meta.printCurrency(ctx.author),
                color = discord.Color.teal()
            )
            await ctx.send(embed = embed)
            return
        #subtract 100 from their total
        self.meta.subCoins(ctx.author, 100)
        #reset time on that corgi
        self.setNewTime(corgi)
        #show thankful corgi embed
        embed = discord.Embed(
            title = corgi + ' noms up '+ctx.author.name+'\'s Biscuit!',
            description = 'You\'ve gained `1` Cake for feeding ' + corgi + '!',
            color = discord.Color.teal()
        )
        embed.set_thumbnail(url = self.getMoodImage('thankful'))
        await ctx.send(embed = embed)
        #change corgi mood to ''
        self.setMood(corgi, '')
        #give person a cake "candy" on profile
        self.meta.addCake(ctx.author, 1)
        return

    def setNewTime(self, corgi):
        self.dbConnection.updateMeta({"id": corgi}, {"$set": {"fed": self.meta.getDateTime()}})
        return

    def setMood(self, corgi, mood):
        self.dbConnection.updateMeta({"id": corgi}, {"$set": {"mood": mood}})
        return

    async def makeCorgiHungry(self, guild, corgi):
        choices = ['hungry', 'sad']
        mood = random.choice(choices)
        self.setMood(corgi, mood)

        embed = discord.Embed(
            title = corgi + ' is feeling ' +mood+ '!',
            description = '`+feed` your Squad Corgi to keep them happy!\nBiscuits cost 100 coins each.',
            color = discord.Color.teal()
        )
        embed.set_thumbnail(url = self.getMoodImage(mood))

        squad = 'Coffee'
        if corgi == 'Matcha':
            squad = 'Tea'
        channel = self.meta.getSquadChannel(guild, squad)
        await channel.send(embed = embed)
        return

    def canMakeHungry(self, corgi):
        if self.isHungry(corgi):
            return False
        profile = self.getCorgi(corgi)
        fed = profile['fed']
        if fed == '':
            return True
        elif not self.meta.hasBeenMinutes(60, fed, self.meta.getDateTime()):
            return False
        return True

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if isinstance(message.channel, discord.DMChannel):
            return
        if random.random() < .3:
            if self.canMakeHungry('Mocha'):
                await self.makeCorgiHungry(message.guild, 'Mocha')
            if self.canMakeHungry('Matcha'):
                await self.makeCorgiHungry(message.guild, 'Matcha')
            else:
                return

def setup(client):
    database_connection = Database()
    meta_class = Meta(database_connection)
    client.add_cog(Corgi(client, database_connection, meta_class))
