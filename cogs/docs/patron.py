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

class Patron(commands.Cog):

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

    @commands.command(aliases=['donation', 'patron'])
    async def donate(self, ctx):
        embed = discord.Embed(
            title = 'Bean Patrons',
            description = 'When you donate, you help us pay for Bean\'s servers/services and other great things for the Mind Café server!',
            color = discord.Color.gold()
        )

        v = '**Venmo: @qrsydney**'
        v += '\n**Paypal: http://paypal.me/qsydney**'
        v += '\nUnless you\'d like to be anonymous, please add your Discord username and tag to the description so we can give you the perks you deserve!'
        embed.add_field(name='Donate', value=v)

        v = 'Everyone who donates at least a dollar gets the <@&'+str(self.ids['PATRON_ROLE'])+'> role and Patron badge ('+self.emojis['Gem']+')!'
        v += '\nFor every $1 donated, you get 150 Coins ('+self.emojis['Coin']+').'
        v += '\nFor every $5 donated, you get 1 Gem ('+self.emojis['Gem']+').'
        embed.add_field(name='Perks', value=v)
        embed.set_footer(text = 'After donating, please allow us at least 24h to get the perks to you manually!')
        embed.set_thumbnail(url = 'https://cdn.discordapp.com/attachments/388576512359530499/634359147814584350/mindcafe_animated.gif')
        await ctx.send(embed = embed)

    @commands.command(aliases=['givegem', 'givegems', 'ggems'])
    async def ggem(self, ctx, member: discord.Member, amt):
        if not self.meta.isBotOwner(ctx.author):
            return

        profile = self.meta.getProfile(member)
        id = member.id

        gems = user['gems']
        gems = gems + int(amt)
        self.dbConnection.updateProfile({"id": id}, {"$set": {"gems": gems}})

        userDiscord = discord.utils.get(self.client.get_all_members(), id=id)

        embed = discord.Embed(
            title = 'You\'ve been given `' + str(amt) + '` gems!',
            description = 'Your total: `' + str(gems) + '` gems ' + self.ids['Gem'],
            color = discord.Color.teal()
        )

        try:
            await userDiscord.send(embed = embed)
        except:
            print('Could not send private message.')

        embed = discord.Embed(
            title = 'Gave ' + member.name + ' ' + str(amt) + ' gems!',
            description = member.name + '\'s gem count: ' + str(gems),
            color = discord.Color.teal()
        )
        await ctx.send(embed = embed)

        #finding log channel
        guild = ctx.guild
        for ch in guild.text_channels:
            if ch.name.lower() == 'log':
                log = guild.get_channel(ch.id)
                break

        msg = '**<@' + str(member.id) + '>** was given ' + str(amt) + ' gems by **' + ctx.author.name + '**.'
        await log.send(msg)

    @commands.command(aliases=['takegem', 'takegems', 'tgem'])
    async def tgems(self, ctx, member: discord.Member, amt, *, reason = ''):
        if not self.meta.isAdmin(ctx.author):
            return

        id = member.id
        user = self.meta.getProfile(member)
        gems = user['gems'] - amt
        self.dbConnection.updateProfile({"id": id}, {"$set": {"gems": gems}})

        embed = discord.Embed(
            title = 'Took ' + str(amt) + ' gems from ' + member.name + '!',
            description = member.name + '\'s gem count: ' + str(gems),
            color = discord.Color.teal()
        )
        await ctx.send(embed = embed)

        #finding log channel
        guild = ctx.guild
        for ch in guild.text_channels:
            if ch.name.lower() == 'log':
                log = guild.get_channel(ch.id)
                break

        msg = '**<@' + str(member.id) + '>** lost ' + str(amt) + ' gems by **' + ctx.author.name + '**.'
        if (reason != ''):
            msg += '\n```' + reason + '```'

        await log.send(msg)

    @commands.command(aliases=['namepatron', 'createpatron', 'makepatron'])
    async def newpatron(self, ctx, member: discord.Member, amt: float):
        if not self.meta.isBotOwner(ctx.author):
            return

        role = ctx.guild.get_role(self.ids['PATRON_ROLE'])
        await member.add_roles(role)

        self.meta.addBadgeToProfile(member, 'BeanPatron')

        addgems = int(amt/5)
        if addgems > 0:
            self.meta.addGems(member, addgems)

        coins = int(int(amt) * 150)
        self.meta.addCoins(member, coins)

        await ctx.guild.get_channel(self.ids['ANNOUNCEMENTS_CHANNEL']).send(embed = self.meta.embed(member.name + ' just donated!', 'Thanks so much for helping us maintain and improve the server.', 'gold'))
        await ctx.send(embed = self.meta.embedDone())
        return

    @commands.command(aliases=['gem', 'redeem'])
    async def redeemgem(self, ctx, *, companion):
        getStoreItem = self.meta.getStoreItem(input)

        if getStoreItem == '':
            await ctx.send(embed = self.meta.embedOops())
            return

        category = getStoreItem['type']
        recipient = ctx.author

        if not ('Companions' in category):
            await ctx.send(embed = self.meta.embedOops())
            return

        #is this companion a gift?
        isGift = await self.meta.confirm(ctx, ctx.author, 'Is this Redeem a gift to someone else?')

        #if yes, ask who & confirm the other person wants it
        if isGift:
            embed = discord.Embed(
                title = 'Please tag the person you\'re gifting to.',
                color = discord.Color.gold()
            )
            await ctx.send(embed = embed)

            def check(m):
                return m.author == ctx.author
            msg = await self.client.wait_for('message', check=check)
            mention = msg.mentions[0]
            if mention.bot:
                await ctx.send(embed = self.meta.embedOops())
                return

            isWanted = await self.meta.confirm(ctx, mention, mention.mention + ', do you accept this gift?')
            if not isWanted:
                return

        #give companion
        self.meta.addToDex(recipient, companion)
        self.dbConnection.updateProfile({"id": recipient.id}, {"$set": {"companion": companion}})

        #-1 gem from profile
        self.meta.subGems(ctx.author, 1)

        await ctx.send(embed = self.meta.embedDone())
        return

    @commands.command(aliases=['unlocked', 'perm', 'permanent', 'rc'])
    async def redeemed(self, ctx, member: discord.Member = None):
        if member == None:
            member = ctx.author

        user = self.meta.getProfile(member)

        desc = ''
        for c in user['redeemed']:
            if desc == '':
                desc = c
            else:
                desc += ', ' + c
        if desc == '':
            desc = 'N/A'
        embed = discord.Embed(
            title = member.name + '\'s Unlocked Companions',
            description = desc,
            color = discord.Color.gold()
        )
        embed.set_footer(text = 'These companions are permanent and never have to be paid for by the owner again!')
        embed.set_thumbnail(url = member.avatar_url)
        await ctx.send(embed = embed)
        return

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if isinstance(message.channel, discord.DMChannel):
            return

        if self.meta.isPatron(message.author):
            msg = message.content
            if self.meta.hasWord('hi', msg) or self.meta.hasWord('hello', msg) or self.meta.hasWord('hey', msg):
                if random.random() < .05:
                    name = '**' + message.author.name + '**'
                    greetings = ['Hi there, Patron ' + name + '! I hope you\'re doing well.',
                    'Wow, Patron ' + name + ', it\'s you! Hi!',
                    'Good morning, Patron ' + name + '! I\'m sure it\'s morning somewhere...',
                    'Today is going to be a good day, Patron ' + name + '! Go out there and conquer!',
                    'Hi there Patron ' + name + ', have I ever told you how much I appreciate you?',
                    'Patron ' + name + '! How are you today? I hope you\'re doing swell.',
                    'Hey, Patron ' + name + '! *You* are absolutely *wonderful!*',
                    'Patron ' + name + '! Just in time. It\'s great to see you!',
                    'Hey there, Patron ' + name + '! Jarvis says hello too!',
                    'Hello! Just a reminder that no matter what anyone else tells you, Patron ' + name + ', you are worthwhile. Never forget it!']
                    await message.channel.send(random.choice(greetings))
                return
            return
        return

def setup(client):
    database_connection = Database()
    meta_class = Meta(database_connection)
    client.add_cog(Patron(client, database_connection, meta_class))
