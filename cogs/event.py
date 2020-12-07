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


class Event(commands.Cog):

    def __init__(self, client, database, meta):
        self.client = client
        self.dbConnection = database
        self.meta = meta


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if isinstance(message.channel, discord.DMChannel):
            return
        if message.channel.id != 728736226709864549:
            return

        server = self.dbConnection.findServer({'id': str(message.guild.id)})
        if server is None:
            print(f"SERVER: {server}")
            return
        channel = message.guild.get_channel(int(server['general_channel']))
        if channel is None:
            print(f"SERVER: [{server}] | CHANNEL: [{server['general_channel']}]")
            return

        # auto-highfive
        if random.random() < .05:
            past_timestamp = server['highfive']
            if past_timestamp == '' or self.meta.hasBeenMinutes(15, past_timestamp, self.meta.getDateTime()):
                self.dbConnection.updateServer({'id': str(message.guild.id)},
                                               {'$set': {'highfive': self.meta.getDateTime()}})
                amt = 25

                embed = discord.Embed(
                    title='Game On: Highfive! | Win ' + str(amt) + ' Coins!',
                    color=discord.Color.teal()
                )

                embed.add_field(name='Seymour says: o/',
                                value='Seymour would like a highfive! Be the first to say `\o` to highfive him back!')
                embed.set_footer(text='This expires in 10 seconds, don\'t leave him hanging!')
                await channel.send(embed=embed, delete_after=10)

                def check(m):
                    return '\o' in m.content.lower() and m.channel == channel

                try:
                    reply = await self.client.wait_for('message', timeout=10.0, check=check)
                except asyncio.TimeoutError:
                    embed_d = discord.Embed(
                        title='Seymour received no highfive. :(',
                        color=discord.Color.teal()
                    )
                    await channel.send(embed=embed_d, delete_after=3)
                    return
                else:
                    coins = self.meta.changeCurrency(reply.author, amt, 'coins')
                    title = f"{reply.author.name}, you've just earned {str(amt)} coins!"
                    desc = f"Total: `{str(coins)}` coins"

                    await channel.send(embed=self.meta.embed(title, desc))
                return



def setup(client):
    database_connection = Database()
    meta_class = Meta(database_connection)
    client.add_cog(Event(client, database_connection, meta_class))
