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

    def getBadges(self, member: discord.Member):
        """

        :param member:
        :return: list of badge literals
        """

        full = []

        # position badges
        if self.meta.isMod(member):
            if self.meta.isBotOwner(member):
                full.append(self.meta.getBadge('dev'))
            else:
                full.append(self.meta.getBadge('mod'))

        profile = self.meta.getProfile(member)

        # profile stat badges
        # pass

        # database profile badges
        badges = profile['badges']
        for badge in badges:
            full.append(self.meta.getBadge(badge))

        return full

    @commands.command(aliases=['badge'])
    async def showbadge(self, ctx, badge=None):
        literal = None if badge is None else self.meta.getBadge(badge)
        if literal is not None:
            await ctx.send(embed=self.meta.embed(badge, literal))
        else:
            await ctx.send(embed=self.meta.embedOops('Badge not found.'))
        return

    @commands.command()
    async def givebadge(self, ctx, member: discord.Member, *, badge):
        if not self.meta.isMod(ctx.author):
            return
        else:
            self.meta.addBadgeToProfile(member, badge)
            await ctx.send(embed=self.meta.embedDone())

    @commands.command(aliases=['takebadge'])
    async def removebadge(self, ctx, member: discord.Member, *, badge):
        if not self.meta.isMod(ctx.author):
            return
        else:
            self.meta.removeBadgeFromProfile(member, badge)
            await ctx.send(embed=self.meta.embedDone())

    @commands.command(aliases=['createbadge'])
    async def makebadge(self, ctx, badge_id: str, badge_literal: str):
        if not self.meta.isMod(ctx.author):
            return
        else:
            self.meta.makeBadge(badge_id, badge_literal)
            await ctx.send(embed=self.meta.embedDone())

    @commands.command(aliases=[])
    async def deletebadge(self, ctx, badge_id: str):
        if not self.meta.isMod(ctx.author):
            return
        else:
            self.meta.deleteBadge(badge_id)
            await ctx.send(embed=self.meta.embedDone())

    #   Goes through certain elements of a users data in the database
    #   and puts them into an embed to send to the user through the bot
    @commands.command(aliases=['p'])
    async def profile(self, ctx, other: discord.Member = None):
        if other is None:
            member = ctx.author
        else:
            member = other

        user = self.meta.getProfile(member)
        pic = member.avatar_url
        name = member.name

        # Basics
        embed = discord.Embed(color=member.color)
        embed.add_field(name="Coins", value=user['coins'], inline=True)
        embed.add_field(name="Points", value=user['pts'], inline=True)
        embed.add_field(name="Bumps", value=user['bumps'], inline=True)
        embed.add_field(name="Gifts", value=user['gifts'], inline=True)
        embed.add_field(name="Pies", value=user['pies'], inline=True)

        # Acknowledgements
        badges = self.getBadges(member)
        if badges is None or len(badges) == 0:
            v = 'No badges yet.'
        else:
            v = " ".join(badges)

        embed.add_field(name="Badges (`" + str(len(badges)) + "`)", value=v, inline=False)

        embed.set_thumbnail(url=pic)
        embed.set_author(name=name)
        embed.set_footer(text='Seymour, Your Bear Bot Friend')
        await ctx.send(embed=embed)


def setup(client):
    database_connection = Database()
    meta_class = Meta(database_connection)
    client.add_cog(Profile(client, database_connection, meta_class))
