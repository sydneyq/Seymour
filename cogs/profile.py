import discord
from discord.ext import commands
from database import Database
from .meta import Meta
import json
import os
import asyncio
import random
import secret

class Profile(commands.Cog):

    def __init__(self, client, database, meta):
        self.client = client
        self.dbConnection = database
        self.meta = meta


        dirname = os.path.dirname(__file__)
        #filename = os.path.join(dirname, 'docs/store.json')
        filename2 = os.path.join(dirname, 'docs/emojis.json')
        #filename3 = os.path.join(dirname, 'docs/ids.json')

        #with open(filename) as json_file:
        #    self.store = json.load(json_file)

        with open(filename2) as json_file:
            self.emojis = json.load(json_file)

        #with open(filename3) as json_file:
        #    self.ids = json.load(json_file)


    def getBadges(self, member: discord.Member):
        str = ''

        if self.meta.isMod(member):
            if self.meta.isBotOwner(member):
                str = str + self.emojis['BotDeveloper'] + ' '
            else:
                if self.meta.isMod(member):
                    str = str + self.emojis['Moderator'] + ' '
        return str

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
        embed = discord.Embed(color=discord.Color.orange())
        embed.add_field(name="Coins", value=user['coins'], inline=True)
        embed.add_field(name="Points", value=user['pts'], inline=True)
        embed.add_field(name="Bumps", value=user['pts'], inline=True)
        embed.add_field(name="Gifts", value=user['gifts'], inline=True)
        embed.add_field(name="Pies", value=user['pies'], inline=True)

        #Acknowledgements
        badges = self.getBadges(member)
        numBadges = 0
        if badges == '':
            badges = 'No badges yet.'
        else:
            numBadges = badges.count('<')
        embed.add_field(name="Badges (`" + str(numBadges) + "`)", value=badges, inline=False)

        embed.set_thumbnail(url = pic)
        embed.set_author(name=name)
        embed.set_footer(text='Seymour, Your Bear Bot Friend')
        await ctx.send(embed=embed)


def setup(client):
    database_connection = Database()
    meta_class = Meta(database_connection)
    client.add_cog(Profile(client, database_connection, meta_class))
