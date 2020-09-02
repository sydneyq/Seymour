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

class Bump(commands.Cog):

    def __init__(self, client, database, meta):
        self.client = client
        self.dbConnection = database
        self.meta = meta

    # bump listener
    @commands.Cog.listener()
    async def on_message(self, message):
        # the bot itself
        if self.meta.isSelf(message.author):
            return

        # is disboard
        if message.author.id == 302050872383242240:
            if message.embeds is not None:
                content = message.embeds[0].to_dict()
                if 'Bump done' in content['description']:
                    mention = content['description'].split(',')[0]
                    id = int(mention[2:-1])
                    member = message.guild.get_member(id)

                    profile = self.meta.getProfile(member)
                    bumps_1 = profile['bumps']
                    bumps_2 = bumps_1 + 1

                    self.meta.addBumps(member, 1)

                    embed = discord.Embed(
                        title='Thanks for Bumping!',
                        description= mention + f", you\'ve gained one Bump! [`{bumps_1}` -> `{bumps_2}`]",
                        color=discord.Color.teal()
                    )
                    await message.channel.send(embed=embed)


def setup(client):
    database_connection = Database()
    meta_class = Meta(database_connection)
    client.add_cog(Bump(client, database_connection, meta_class))
