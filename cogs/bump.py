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
                    if member is None:
                        #await message.channel.send(embed=self.meta.embedOops(f"Something went wrong. Please tag the "
                        #                                               f"Dev.\nMention: {mention}\nID: `{id}`"))
                        #return
                        member = message.guild.get_member(mention[2:-1])
                        if member is None:
                            return

                    profile = self.meta.getProfile(member)
                    bumps = profile['bumps']
                    coins = profile['coins']

                    self.meta.addBumps(member, 1)
                    self.meta.addCoins(member, 50)

                    title = 'Thanks for Bumping!'
                    desc = mention + f", you\'ve gained: "
                    desc += f"\n`+1` Bump! [`{bumps}` -> `{bumps+1}`]"
                    desc += f"\n`+50` Coins! [`{coins}` -> `{coins+50}`]"

                    await message.channel.send(embed=self.meta.embed(title, desc, 'gold'))


def setup(client):
    database_connection = Database()
    meta_class = Meta(database_connection)
    client.add_cog(Bump(client, database_connection, meta_class))
