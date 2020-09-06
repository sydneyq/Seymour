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

    @commands.command(aliases=['take'])
    async def give(self, ctx, member: discord.Member, amt: int, currency: str):
        """
        as in 'give @member 50 coins'
        take into account plural/single
        :param ctx:
        :param member:
        :param amt:
        :param currency:
        :return:
        """

        if not self.meta.isMod(ctx.author):
            return

        total = 0
        profile = self.meta.getProfile(member)
        if currency in ['coin', 'coins', 'c', 'cs']:
            currency = 'coins'
        elif currency in ['point', 'points', 'pts', 'pt']:
            currency = 'points'
        elif currency in ['pie', 'pies']:
            currency = 'pies'
        elif currency in ['bumps', 'bump']:
            currency = 'bumps'
        else:
            await ctx.send(embed=self.meta.embedOops('Invalid currency type.'))
            return

        total = self.meta.changeCurrency(member, amt, currency)

        if not total:
            await ctx.send(embed=self.meta.embedOops())
            return

        embed = discord.Embed(
            title=f"{member.name} been given `{amt}` {currency}!",
            description=f"Total: `{total}` {currency}",
            color=discord.Color.gold()
        )

        if amt > 0:
            try:
                await member.send(embed=embed)
            finally:
                print('Could not send private message.')

        await ctx.send(embed=embed)


def setup(client):
    database_connection = Database()
    meta_class = Meta(database_connection)
    client.add_cog(Currency(client, database_connection, meta_class))
