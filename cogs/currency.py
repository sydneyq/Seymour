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

    @commands.command(aliases=['pokedex', 'd'])
    async def dex(self, ctx, other: discord.Member = None):
        if other == None:
            member = ctx.author
            id = ctx.author.id
        else:
            member = other
            id = other.id

        user = self.meta.getProfile(member)

        embed = discord.Embed(
            title = member.name + '\'s Dex',
            color = discord.Color.teal()
        )

        companions = user['dex']
        eeveelutions = self.meta.getEeveelutions()
        val = ''
        for e in eeveelutions:
            if e in companions:
                val += self.emojis['Check']
            else:
                val += self.emojis['Cancel']
            val += ' ' + e + '\n'
        embed.add_field(name="Eeveelutions", value=val, inline=True)

        val2 = ''
        if 'Ditto' in companions:
            val2 += self.emojis['Check']
        else:
            val2 += self.emojis['Cancel']
        val2 += ' Ditto\n'
        embed.add_field(name = 'In The Wild', value=val2, inline=True)
        embed.set_thumbnail(url = member.avatar_url)
        await ctx.send(embed = embed)

    @commands.command()
    async def setCompanion(self, ctx, member: discord.Member, *, companion):
        if ctx.author.id != secret.BOT_OWNER_ID:
            return
        else:
            id = member.id
            self.dbConnection.updateProfile({"id": id}, {"$set": {"companion": companion}})
            embed = discord.Embed(
                title = 'Consider it done! ✅',
                color = discord.Color.teal()
            )
            await ctx.send(embed = embed)

    @commands.command(aliases=['removeCompanion', 'release'])
    async def releaseCompanion(self, ctx):
        id = ctx.author.id
        user = self.meta.getProfile(ctx.author)

        if user['companion'] == '':
            embed = discord.Embed(
                title = 'You don\'t have a companion to release!',
                color = discord.Color.teal()
            )
            await ctx.send(embed = embed)
            return

        embed = discord.Embed(
            title = 'Release your Companion?',
            description = 'React to this message with a ✅ for yes, ⛔ for no.\nYou have 60 seconds to decide!',
            color = discord.Color.teal()
        )
        await ctx.send(embed = embed)

        msgs = []
        async for msg in ctx.channel.history(limit=1):
            if (msg.author.id == 592436047175221259 or msg.author.id == 432038389663924225):
                msgs.append(msg)
                break

        msg = msgs[0]
        await msg.add_reaction('✅')
        await msg.add_reaction('⛔')

        emoji = ''

        def check(reaction, user):
            #print('str: ' + str(reaction.emoji))
            nonlocal emoji
            emoji = str(reaction.emoji)
            return user == ctx.author and (str(reaction.emoji) == '✅' or str(reaction.emoji) == '⛔')

        try:
            reaction, user = await self.client.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await channel.send('Timed out.')
        else:
            if emoji == '⛔':
                embed = discord.Embed(
                    title = 'Release canceled.',
                    color = discord.Color.teal()
                )
                await ctx.send(embed = embed)
                return
            print('emoji: ' + emoji)

            self.dbConnection.updateProfile({"id": id}, {"$set": {"companion": ''}})

            embed = discord.Embed(
                title = 'You released your companion!',
                color = discord.Color.teal()
            )
            await ctx.send(embed = embed)
            return

    @commands.command(aliases=['givecoins', 'agive', 'admgive'])
    async def admingive(self, ctx, member: discord.Member, amt, *, reason = ''):
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


    @commands.command()
    async def giveSquad(self, ctx, squad, amt: int, *, reason = ''):
        if not self.meta.isAdmin(ctx.author):
            return

        squad = squad.lower()
        squad = squad.capitalize()
        squadDocs = self.dbConnection.findProfiles({'squad' : squad})

        for doc in squadDocs:
            self.dbConnection.updateProfile({'id': doc['id']}, {"$set": {"coins": (doc['coins']+amt)}})

        squads = self.dbConnection.findMeta({'id':'temp_squads'})
        for staff in squads[squad]:
            user = self.meta.getProfile(self.meta.getMemberByID(ctx, staff))
            coins = user['coins']
            self.dbConnection.updateProfile({'id': staff}, {"$set": {"coins": coins+amt}})

        await ctx.send(embed = self.meta.embedDone())

        #finding log channel
        guild = ctx.guild
        for ch in guild.text_channels:
            if ch.name.lower() == 'log':
                log = guild.get_channel(ch.id)
                break

        msg = 'The **' + squad + ' Squad** was given ' + str(amt) + ' coins by **' + ctx.author.name + '**.'
        if (reason != ''):
            msg += '\n```' + reason + '```'

        await log.send(msg)

    @commands.command(aliases=['atake', 'admtake', 'takecoins'])
    async def admintake(self, ctx, member: discord.Member, amt, *, reason = ''):
        if not self.meta.isAdmin(ctx.author):
            return

        id = member.id
        user = self.meta.getProfile(member)
        amt = amt * -1
        self.meta.changeCoins(member, amt)

        embed = discord.Embed(
            title = 'Took ' + str(amt) + ' coins from ' + member.name + '!',
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

        msg = '**<@' + str(member.id) + '>** lost ' + str(amt) + ' coins by **' + ctx.author.name + '**.'
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
