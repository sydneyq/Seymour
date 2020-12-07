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

        self.typeracer_strings = ['the quick brown fox jumps over the lazy dog',  # 1
                                  'seymour the bear bot friend',  # 2
                                  'tea and coffee make the world go round',  # 3
                                  'with great power comes great responsibility',  # 4
                                  'elementary my dear watson',  # 5
                                  'the snack that smiles back',  # 6
                                  'take a deep breath',  # 7
                                  'sorry earth is closed today',  # 8
                                  'i am right where i am supposed to be',  # 9
                                  'houston we have a problem',  # 10
                                  'you had me at hello world',  # 11
                                  'keep your friends close and your enemies closer',  # 12
                                  'today is going to be a good day',  # 13
                                  'adventure is out there',  # 14
                                  'there is no one i would rather be than me',  # 15
                                  'hakuna matata what a wonderful phrase',  # 16
                                  'no one deserves to be forgotten',  # 17
                                  'i could do this all day',  # 18
                                  'i have been falling for thirty minutes',  # 19
                                  'come with me where dreams are born and time is never planned',  # 20
                                  'i wanna be the very best like no one ever was',  # 21
                                  'we are a product of the stories we tell ourselves',  # 22
                                  'let us learn to show our friendship for a man when he is alive and not after he is dead',
                                  # 23
                                  'a man can learn more from defeat than success or victory',  # 24
                                  'when there are clouds in the sky you will get by',  # 25
                                  'if you do not like where you are move you are not a tree',  # 26
                                  'i think you are confused for it is you who will taste defeat',  # 27
                                  'we used google cloud platform to predict how clouds will behave',  # 28
                                  'it is bed o clock you best be sleeping',  # 29
                                  'when you cannot sleep at night it is because you are awake',  # 30
                                  'does the sun shine for man to tell it where to cast its rays',
                                  'the wilderness must be explored',
                                  'no one deserves to fade away',
                                  'a wilderness explorer is a friend to all be it plants or fish or tiny mole caw caw rawr']

    @commands.command(aliases=['typerace', 'squadrace', 'squadracer', 'race'])
    async def typeracer(self, ctx,
                        channel: discord.TextChannel = None):  # rounds: int = 1, channel: discord.TextChannel = None):
        message = ctx.message
        if not self.meta.isBotOwner(message.author):
            return

        if channel is None:
            channel = ctx.channel

        await ctx.message.delete()

        # for round in range(0, rounds):
        string = random.choice(self.typeracer_strings)
        amt = 25
        altered = ''

        punctuation = ['!', '@', '&', '.']
        for ch in string:
            altered += ch + random.choice(punctuation)

        altered = altered[:-1]

        embed = discord.Embed(
            title='Game On: Typeracer! | Win ' + str(amt) + ' Coins!',
            color=discord.Color.teal()
        )

        embed.add_field(name='Be the first to type the sentence without any punctuation or symbols!',
                        value='`' + altered + '`')
        # embed.set_footer(text = 'This expires in 3 minutes.')
        msg = await channel.send(embed=embed)

        def check(m):
            return m.content.lower() == string and m.channel == channel

        msg = await self.client.wait_for('message', check=check)
        coins = self.meta.changeCurrency(ctx.author, amt, 'coins')

        title = f"{msg.author.name}, you've just earned {str(amt)} coins!"
        desc = f"Total: `{str(coins)}` coins"

        await msg.edit(embed=self.meta.embedDone(title, desc))
        return

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
            return

        channel = server['general_channel']

        # auto-highfive
        if random.random() < .05:
            past_timestamp = server['highfive']
            if past_timestamp == '' or self.meta.hasBeenMinutes(20, past_timestamp, self.meta.getDateTime()):
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

                    await channel.send(embed=self.meta.embedDone(title, desc))
                return

        # auto-typeracer
        if random.random() < .1:
            # check timestamp
            past_timestamp = server['typeracer']
            if past_timestamp == '' or self.meta.hasBeenMinutes(40, past_timestamp, self.meta.getDateTime()):

                string = random.choice(self.typeracer_strings)
                amt = 50
                altered = ''

                punctuation = ['!', '@', '&', '.']
                for ch in string:
                    altered += ch + random.choice(punctuation)

                altered = altered[:-1]

                embed = discord.Embed(
                    title='Game On: Typeracer! | Win ' + str(amt) + ' Coins!',
                    # title = 'Game On: Squad Racers!',
                    color=discord.Color.teal()
                )

                embed.add_field(name='Be the first to type the sentence without any punctuation or symbols!',
                                value='`' + altered + '`')
                msg = await channel.send(embed=embed)

                def check(m):
                    return m.content.lower() == string and m.channel == channel

                reply = await self.client.wait_for('message', check=check)

                coins = self.meta.changeCurrency(reply.author, amt, 'coins')
                title = f"{reply.author.name}, you've just earned {str(amt)} coins!"
                desc = f"Total: `{str(coins)}` coins"

                await msg.edit(embed=self.meta.embedDone(title, desc))
                self.dbConnection.updateMeta({'id': str(message.guild.id)},
                                             {'$set': {'typeracer': self.meta.getDateTime()}})
                return
            else:
                return
        else:
            return


def setup(client):
    database_connection = Database()
    meta_class = Meta(database_connection)
    client.add_cog(Event(client, database_connection, meta_class))
