import discord
from discord.ext import commands
from database import Database
from .meta import Meta
import json
import os
import asyncio
import random
import secret
from .soulmates import Soulmates

class Profile(commands.Cog):

    def __init__(self, client, database, meta, soulmates):
        self.client = client
        self.dbConnection = database
        self.meta = meta
        self.soulmates = soulmates

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

    def getBadges(self, member: discord.Member):
        str = ''

        if self.meta.isStaff(member):
            if self.meta.isBotOwner(member):
                str = str + self.emojis['BotDeveloper'] + ' '

            if self.meta.isAdmin(member):
                str = str + self.emojis['Administrator'] + ' '
            else:
                if self.meta.isMod(member):
                    str = str + self.emojis['Moderator'] + ' '
                if self.meta.isEventCoordinator(member):
                    str = str + self.emojis['EventCoordinator'] + ' '
                if self.meta.isMarketingOfficer(member):
                    str = str + self.emojis['MarketingOfficer'] + ' '

        if self.meta.hasRole(member, 'Certifying Team'):
            str = str + self.emojis['CertifyingTeam'] + ' '

        if self.meta.isCertified(member):
            str = str + self.emojis['Certified'] + ' '

        if self.meta.hasRole(member, 'Listeners'):
            str = str + self.emojis['Listener'] + ' '

        if self.meta.hasRole(member, 'Corgi Call Responders'):
            str = str + self.emojis['CorgiCallResponder'] + ' '

        user = self.meta.getProfile(member)

        if user['helped'] >= 10:
            str = str + self.emojis['HelpPts10'] + ' '
            if user['helped'] >= 20:
                str = str + self.emojis['HelpPts20'] + ' '
                if user['helped'] >= 30:
                    str = str + self.emojis['HelpPts30'] + ' '

        if self.meta.hasRole(member, '○° bubble tea °○'):
            str = str + self.emojis['Recruited10'] + ' '

        badges = user['badges']
        for badge in badges:
            str = str + self.dbConnection.findBadge({"id":badge})['literal'] + ' '

        return str

    @commands.command(aliases=['element'])
    async def affinity(self, ctx, *, affinity = None):
        if affinity is None or (affinity.lower() != 'water' and affinity.lower() != 'fire' and affinity.lower() != 'air' and affinity.lower() != 'earth'):
            embed = discord.Embed(
                title = 'Correct Usage: `+affinity water/air/fire/earth`.',
                color = discord.Color.teal()
            )
            await ctx.send(embed = embed)
            return

        affinity = affinity.lower().capitalize()

        id = ctx.author.id
        user = self.meta.getProfile(ctx.author)

        if user['affinity'] is None or user['affinity'] == '':
            self.meta.changeAffinity(ctx.author, affinity)
            await ctx.send(embed = self.meta.embedDone())
            return
        else:
            embed = discord.Embed(
                title = 'You already have an affinity!',
                color = discord.Color.teal()
            )
            await ctx.send(embed = embed)
            return

    @commands.command()
    async def givebadge(self, ctx, member: discord.Member, *, badge):
        if not self.meta.isAdmin(ctx.author):
            return
        else:
            self.meta.addBadgeToProfile(member, badge)
            await ctx.send(embed = self.meta.embedDone())

    #   Goes through certain elements of a users data in the database
    #   and puts them into an embed to send to the user through the bot
    @commands.command(aliases=['p'])
    async def profile(self, ctx, other: discord.Member = None):
        if other == None:
            id = ctx.author.id
            member = ctx.author
        else:
            id = other.id
            member = other

        user = self.meta.getProfile(member)
        pic = member.avatar_url
        name = member.name

        #Basics
        squad = user['squad']
        if (squad == "Tea"):
            embed = discord.Embed(color=0xe99c3e)
            embed.add_field(name="Squad", value=self.emojis['Tea'] + ' ' + user['squad'], inline=True)
            embed.set_author(name = name, icon_url = 'https://cdn2.stylecraze.com/wp-content/uploads/2015/04/2072_11-Surprising-Benefits-And-Uses-Of-Marijuana-Tea_shutterstock_231770824.jpg')
        elif (squad == "Coffee"):
            embed = discord.Embed(color=0xace605)
            embed.add_field(name="Squad", value=self.emojis['Coffee'] + ' ' + user['squad'], inline=True)
            embed.set_author(name = name, icon_url = 'https://www.caffesociety.co.uk/assets/recipe-images/latte-small.jpg')
        else:
            v = 'No Squad yet. Use `+squad tea/coffee` to join one!'
            if (squad != '' or squad == 'Squadless'):
                v = squad

            embed = discord.Embed(color = discord.Color.teal())
            embed.add_field(name="Squad", value=v, inline=True)
            embed.set_author(name = name)

        if user['affinity'] == '':
            msg2 = 'No affinity yet. Set one with `+affinity`!'
        else:
            msg2 = user['affinity']
            emoji = ''
            if msg2 == 'Fire':
                emoji = self.emojis['Fire']
            elif msg2 == 'Earth':
                emoji = self.emojis['Earth']
            elif msg2 == 'Air':
                emoji = self.emojis['Air']
            elif msg2 == 'Water':
                emoji = self.emojis['Water']
            msg2 = emoji + ' ' + msg2
        embed.add_field(name='Affinity', value=msg2, inline=True)

        embed.set_footer(text = 'Mind Café', icon_url = 'https://media.discordapp.net/attachments/591611902459641856/593267453363224588/Bean_Icon.png')

        #Marriage
        soulmates_print = self.soulmates.printSoulmates(member)
        embed.add_field(name="Soulmate(s)", value=soulmates_print, inline=True)

        #Companion
        companion = user['companion']
        msg = ''

        if companion is not '':
            isSpecial = False
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
                        isSpecial = True
                        break

            msg = companion
            if isSpecial:
                msg = self.emojis['Special'] + ' ' + companion
        else:
            msg = 'No companion yet. Get one at `+store`!'

        embed.add_field(name="Companion", value=msg, inline=True)

        #Acknowledgements
        badges = self.getBadges(member)
        numBadges = 0
        if badges == '':
            badges = 'No badges yet.'
        else:
            numBadges = badges.count('<')
        embed.add_field(name="Badges (`" + str(numBadges) + "`)", value=badges, inline=True)

        embed.set_thumbnail(url = pic)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        id = member.id
        user = self.meta.getProfile(member)
        self.dbConnection.removeProfile({"id": id})

        soulmates = user['soulmates']
        if not (soulmates is None):
            for soulmate in soulmates:
                try:
                    s = guild.get_user(soulmate)
                    self.meta.removeSoulmate(s, member)
                except:
                    continue

def setup(client):
    database_connection = Database()
    meta_class = Meta(database_connection)
    soulmates_class = Soulmates(client, database_connection, meta_class)
    client.add_cog(Profile(client, database_connection, meta_class, soulmates_class))
