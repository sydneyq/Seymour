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

        self.typeracer_strings = ['the quick brown fox jumps over the lazy dog', #1
        'bean the corgi is the goodest boy', #2
        'tea and coffee make the world go round', #3
        'with great power comes great responsibility', #4
        'elementary my dear watson', #5
        'the snack that smiles back', #6
        'take a deep breath', #7
        'sorry earth is closed today', #8
        'i am right where i am supposed to be', #9
        'houston we have a problem', #10
        'you had me at hello world', #11
        'keep your friends close and your enemies closer', #12
        'today is going to be a good day', #13
        'adventure is out there', #14
        'there is no one i would rather be than me', #15
        'hakuna matata what a wonderful phrase', #16
        'no one deserves to be forgotten', #17
        'i could do this all day', #18
        'i have been falling for thirty minutes', #19
        'come with me where dreams are born and time is never planned', #20
        'i wanna be the very best like no one ever was', #21
        'we are a product of the stories we tell ourselves', #22
        'let us learn to show our friendship for a man when he is alive and not after he is dead', #23
        'a man can learn more from defeat than success or victory', #24
        'when there are clouds in the sky you will get by', #25
        'if you do not like where you are move you are not a tree', #26
        'i think you are confused for it is you who will taste defeat', #27
        'we used google cloud platform to predict how clouds will behave', #28
        'it is bed o clock you best be sleeping', #29
        'when you cannot sleep at night it is because you are awake', #30
        'does the sun shine for man to tell it where to cast its rays',
        'the wilderness must be explored',
        'no one deserves to fade away',
        'a wilderness explorer is a friend to all be it plants or fish or tiny mole caw caw rawr']

        dirname = os.path.dirname(__file__)
        filename2 = os.path.join(dirname, 'docs/emojis.json')
        filename3 = os.path.join(dirname, 'docs/ids.json')

        with open(filename2) as json_file:
            self.emojis = json.load(json_file)

        with open(filename3) as json_file:
            self.ids = json.load(json_file)

    @commands.command(aliases=['givecake'])
    async def gcake(self, ctx, member: discord.Member):
        if not self.meta.isBotOwner(ctx.author):
            await ctx.send(embed = self.meta.embedOops())
            return
        else:
            self.meta.addCake(member, 1)
            await ctx.send(embed = self.meta.embedDone())
            return

    @commands.command(aliases=['takecake'])
    async def tcake(self, ctx, member: discord.Member):
        if not self.meta.isBotOwner(ctx.author):
            await ctx.send(embed = self.meta.embedOops())
            return
        else:
            self.meta.subCake(member, 1)
            await ctx.send(embed = self.meta.embedDone())
            return

    @commands.command(aliases=[])
    async def cake(self, ctx, member: discord.Member):
        #can't cake admins
        if self.meta.isAdmin(member):
            await ctx.send(embed = self.meta.embedOops())
            return
        #check has cake
        if not self.meta.subCake(ctx.author):
            await ctx.send(embed = self.meta.embedOops())
            return
        #can't cake bots
        if member.bot:
            await ctx.send(embed = self.meta.embedOops())
            return

        titles = ['Sir',
        'Knight',
        'Madame',
        'Prince',
        'Charming',
        'Flopping',
        'Fuzzy',
        'Colonel',
        'President',
        'Best',
        'McLovin\'',
        'Cakey',
        'Kooky',
        'Fabulous',
        'Spikey',
        'Zoomin\'',
        'Wild',
        'Fire-breathing',
        'Googly',
        'Spooky']
        prefixes = ['Sparkle',
        'Ice Cream',
        'Halloween',
        'Candle',
        'Noodle',
        'Scallop',
        'Pumpkin',
        'Pickle',
        'Dotted',
        'Cake',
        'Cupcake',
        'Bork',
        'Glitter',
        'Party']
        suffixes = ['Sparkles',
        'Pixie',
        'Unicorn',
        'Slayer',
        'Wizard',
        'Pants',
        'Wacky',
        'Face',
        'Doodle',
        'Foot',
        'Caked',
        'Socks',
        'Eyes',
        'Santa']
        emojis = ['🍅', '💛', '😡', '🍞', '😇', '😊', '🥑', '🍤', '🐡', '💒', '🍬', '🗽', '🐢', '🐑', '☁', '😗', '😲', '🐬', '💐']
        name = random.choice(titles) + ' ' + random.choice(prefixes) + ' ' + random.choice(suffixes) + ' ' + random.choice(emojis)

        await member.edit(nick = name)

        embed = discord.Embed(
            title = ctx.author.name + ' caked `' + member.name + '`!',
            description = 'Their name is now: `'+name+'`',
            color = discord.Color.teal()
        )
        await ctx.send(embed = embed)
        return

    @commands.command(aliases=['2019'])
    async def badge2019(self, ctx):
        user = self.meta.getProfile(ctx.author)
        badges = user['badges']
        if '2019' not in badges:
            badges.append('2019')
            self.dbConnection.updateProfile({"id": ctx.author.id}, {"$set": {"badges": badges}})
            await ctx.send(embed = self.meta.embedDone())
            return
        else:
            await ctx.send(embed = self.meta.embedOops())
            return

    @commands.command(aliases=['typerace', 'squadrace', 'squadracer', 'race'])
    async def typeracer(self, ctx, channel: discord.TextChannel = None):#rounds: int = 1, channel: discord.TextChannel = None):
        message = ctx.message
        if not self.meta.isAdmin(message.author):
            return

        if channel is None:
            channel = ctx.channel

        await ctx.message.delete()

        #for round in range(0, rounds):
        string = random.choice(self.typeracer_strings)
        amt = 25
        altered = ''

        punctuation = ['!', '@', '&', '.']
        for ch in string:
            altered += ch + random.choice(punctuation)

        altered = altered[:-1]

        embed = discord.Embed(
            title = 'Game On: Typeracer! | Win ' + str(amt) + ' Coins!',
            #title = 'Game On: Squad Racers!',
            color = discord.Color.teal()
        )

        embed.add_field(name='Be the first to type the sentence without any punctuation or symbols!',
        value='`' + altered + '`')
        #embed.set_footer(text = 'This expires in 3 minutes.')
        await channel.send(embed = embed)

        def check(m):
            return m.content.lower() == string and m.channel == channel

        msg = await self.client.wait_for('message', check=check)

        user = self.meta.getProfile(msg.author)
        '''
        elif user['squad'] == '':
            embed = discord.Embed(
                title = 'Sorry, you\'re not in a Squad yet! Join one by using `+squad tea/coffee`.',
                color = discord.Color.teal()
            )
            await channel.send(embed = embed)
            return

        squad = user['squad']
        if user['squad'] == 'Tea':
            self.tea_score += 1
        else:
            self.coffee_score += 1
        '''
        coins = user['coins'] + amt
        self.dbConnection.updateProfile({"id": msg.author.id}, {"$set": {"coins": coins}})

        embed2 = discord.Embed(
            title = msg.author.name + ', you\'ve just earned ' + str(amt) + ' coins!',
            description = 'Your total: `' + str(coins) + '` coins',
            color = discord.Color.teal()
        )
        '''
        embed2 = discord.Embed(
            title = msg.author.name + ' just earned `1` point for **' + squad + '**!',
            description = '**Tea Squad:** `' + str(self.tea_score) + '`\n**Coffee Squad:** `' + str(self.coffee_score) + '`',
            color = discord.Color.teal()
        )
        '''
        await channel.send(embed = embed2)
        return

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if isinstance(message.channel, discord.DMChannel):
            return

        #auto-highfive
        if random.random() < .05:
            past_timestamp = self.dbConnection.findMeta({'id':'server'})['highfive']
            if past_timestamp == '' or self.meta.hasBeenMinutes(60, past_timestamp, self.meta.getDateTime()):
                self.dbConnection.updateMeta({'id':'server'}, {'$set': {'highfive': self.meta.getDateTime()}})
                #casual = 593153723610693632 #cmd
                casual = 257751892241809408
                channels = [casual]
                channel = random.choice(channels)
                channel = message.guild.get_channel(channel)

                amt = 25

                embed = discord.Embed(
                    title = 'Game On: Highfive! | Win ' + str(amt) + ' Coins!',
                    color = discord.Color.teal()
                )

                embed.add_field(name=self.dbConnection.findBadge({"id":'GiftedByBean'})['literal'] + ': o/',
                value='Bean would like a highfive! Be the first to say `\o` to highfive him back!')
                embed.set_footer(text='This expires in 10 seconds, don\'t leave him hanging!')
                await channel.send(embed = embed, delete_after=10)

                def check(m):
                    return '\o' in m.content.lower() and m.channel == channel

                try:
                    msg = await self.client.wait_for('message', timeout=10.0, check=check)
                except asyncio.TimeoutError:
                    embed_d = discord.Embed(
                        title = 'Bean received no highfive. :(',
                        color = discord.Color.teal()
                    )
                    await channel.send(embed = embed_d, delete_after=3)
                    return
                else:
                    user = self.meta.getProfile(msg.author)

                    coins = user['coins'] + amt
                    self.dbConnection.updateProfile({"id": msg.author.id}, {"$set": {"coins": coins}})

                    embed2 = discord.Embed(
                        title = msg.author.name + ', you\'ve just earned `' + str(amt) + '` coins!',
                        description = 'Your total: `' + str(coins) + '` coins',
                        color = discord.Color.teal()
                    )

                    await channel.send(embed = embed2)
                return
        else:
            return

def setup(client):
    database_connection = Database()
    meta_class = Meta(database_connection)
    client.add_cog(Event(client, database_connection, meta_class))
