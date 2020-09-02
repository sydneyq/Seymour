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

class Currency(commands.Cog):

    def __init__(self, client, database, meta):
        self.client = client
        self.dbConnection = database
        self.meta = meta
        '''
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, 'docs/store.json')
        filename2 = os.path.join(dirname, 'docs/emojis.json')
        filename3 = os.path.join(dirname, 'docs/ids.json')

        with open(filename) as json_file:
            self.store = json.load(json_file)

        with open(filename2) as json_file:
            self.emojis = json.load(json_file)

        with open(filename3) as json_file:
            self.ids = json.load(json_file)
        '''

    @commands.command(aliases=['i', 'coins'])
    async def inventory(self, ctx, other: discord.Member = None):
        if other == None:
            member = ctx.author
            id = ctx.author.id
        else:
            member = other
            id = other.id

        user = self.meta.getProfile(member)
        name = self.client.get_user(id).name

        pic = member.avatar_url

        embed = discord.Embed(
            title = name + '\'s Inventory',
            color = discord.Color.teal()
        )

        #Achievements
        #   helped
        helped = user['helped']
        embed.add_field(name=self.emojis['HelpPoint'] + " Help Points", value='`' + str(helped) + '`', inline=True)

        #   coins
        coins = user['coins']
        embed.add_field(name=self.emojis['Coin'] + " Coins", value='`' + str(coins) + '`', inline=True)

        #   coins
        gifts = user['gifts']
        embed.add_field(name=self.emojis['Gift'] + " Gifts", value='`' + str(gifts) + '`', inline=True)

        cakes = user['cakes']
        embed.add_field(name=self.emojis['Cake'] + " Cakes", value='`' + str(cakes) + '`', inline=True)

        gems = user['gems']
        embed.add_field(name=self.emojis['Gem'] + " Gems", value='`' + str(gems) + '`', inline=True)

        embed.set_thumbnail(url = pic)
        await ctx.send(embed = embed)

    @commands.command(aliases=['givecoins', 'agive', 'admgive', 'admingive', 'take'])
    async def give(self, ctx, member: discord.Member, amt: int, *, reason = ''):
        if not self.meta.isAdmin(ctx.author):
            return

        id = member.id
        user = self.dbConnection.findProfile({"id": id})

        if user is None:
            embed = discord.Embed(
                title = 'Sorry, ' + member.name + ' doesn\'t have a profile yet! They can make one by using +profile.',
                color = discord.Color.teal()
            )
            await ctx.send(embed = embed)
            return

        coins = user['coins']
        coins = coins + int(amt)
        self.dbConnection.updateProfile({"id": id}, {"$set": {"coins": coins}})

        userDiscord = discord.utils.get(self.client.get_all_members(), id=id)

        embed = discord.Embed(
            title = 'You\'ve been given `' + str(amt) + '` coins!',
            description = 'Your total: `' + str(coins) + '` coins',
            color = discord.Color.teal()
        )
        if reason != '':
            embed.add_field(name='Reason: ', value=reason)
        embed.set_thumbnail(url = 'https://www.mariowiki.com/images/thumb/1/17/CoinMK8.png/1200px-CoinMK8.png')

        try:
            await userDiscord.send(embed = embed)
        except:
            print('Could not send private message.')

        embed = discord.Embed(
            title = 'Gave ' + member.name + ' ' + str(amt) + ' coins!',
            description = member.name + '\'s coin count: ' + str(coins),
            color = discord.Color.teal()
        )
        await ctx.send(embed = embed)

        #finding log channel
        guild = ctx.guild
        for ch in guild.text_channels:
            if ch.name.lower() == 'log':
                log = guild.get_channel(ch.id)
                break

        msg = '**<@' + str(member.id) + '>** was given ' + str(amt) + ' coins by **' + ctx.author.name + '**.'
        if (reason != ''):
            msg += '\n```' + reason + '```'

        await log.send(msg)


    @commands.command(aliases=['helpedby', 'thanks'])
    async def rep(self, ctx):
        members = ctx.message.mentions
        log = ctx.guild.get_channel(self.ids['REP_CHANNEL'])

        for member in members:
            if ctx.author.id == member.id and not self.meta.isBotOwner(ctx.author):
                embed = discord.Embed(
                    title = 'You can\'t rep yourself!',
                    color = discord.Color.teal()
                )
                await ctx.send(embed = embed)
                return
            else:
                id = member.id
                user = self.meta.getProfile(member)

                helped = user['helped']
                helped = helped + 1
                self.dbConnection.updateProfile({"id": id}, {"$set": {"helped": helped}})
                embed = discord.Embed(
                    title = 'Repped ' + member.name + '!',
                    description = member.name + '\'s rep count: ' + str(helped) + ' ' + self.emojis['HelpPoint'],
                    color = discord.Color.teal()
                )
                await ctx.send(embed = embed)

                msg = self.emojis['Helped2'] + ' **<@' + str(member.id) + '>** was repped by <@' + str(ctx.author.id) + '>. `['+str(helped-1)+'->'+str(helped)+']` <@&'+str(self.ids['MOD_ROLE'])+'>'
                await log.send(msg)

    @commands.command(aliases=['removehelped'])
    async def derep(self, ctx):
        if not self.meta.isMod(ctx.author):
            return

        members = ctx.message.mentions
        log = ctx.guild.get_channel(self.ids['REP_CHANNEL'])

        for member in members:
            id = member.id
            user = self.meta.getProfile(member)

            helped = user['helped']
            helped -= 1
            self.dbConnection.updateProfile({"id": id}, {"$set": {"helped": helped}})

            embed = discord.Embed(
                title = 'Derepped ' + member.name + '!',
                description = member.name + '\'s rep count: ' + str(helped),
                color = discord.Color.teal()
            )
            await ctx.send(embed = embed)

            msg = '**<@' + str(member.id) + '>** was derepped by <@' + str(ctx.author.id) + '>. `['+str(helped+1)+'->'+str(helped)+']`'

            await log.send(msg)


def setup(client):
    database_connection = Database()
    meta_class = Meta(database_connection)
    client.add_cog(Currency(client, database_connection, meta_class))
