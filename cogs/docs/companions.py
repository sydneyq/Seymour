import discord
from discord.ext import commands
from database import Database
from .meta import Meta
import json
import os
import asyncio
import random
import secret

class Companions(commands.Cog):

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

    def getCompanionByID(self, id):
        companion = self.dbConnection.findCompanion({"s1": str(member.id)})
        return companion

    def getActiveCompanion(self, member: discord.Member):
        user = self.meta.getProfile(member)
        id = user['companion']
        companion = self.getCompanionByID(id)
        return companion

    def getCompanions(self, member: discord.Member):
        pass

    #s1 & s2 are stored as strings because of mongodb's int64 truncating
    #https://dzone.com/articles/long-numbers-are-truncated-in-mongodb-shell
    def addSoulmate(self, member: discord.Member, member2: discord.Member):
        if member.bot or member2.bot or member == member2:
            return False
        #don't have spots
        if (not self.canAddSoulmate(member)) or (not self.canAddSoulmate(member2)) :
            return False
        #already soulmates
        if self.areSoulmates(member, member2):
            return False

        self.dbConnection.insertSoulmatePair({'s1': str(member.id), 's2': str(member2.id)})
        return True

    def removeSoulmate(self, member: discord.Member, member2: discord.Member):
        s1 = self.dbConnection.findSoulmatePairs({"s1": str(member.id)})
        s2 = self.dbConnection.findSoulmatePairs({"s2": str(member.id)})
        done = True

        try:
            self.dbConnection.removeSoulmatePair({"s1": str(member.id), "s2": str(member2.id)})
        except:
            done = False

        try:
            self.dbConnection.removeSoulmatePair({"s1": str(member2.id), "s2": str(member.id)})
        except:
            done = False

        return done

    def printSoulmates(self, member: discord.Member):
        sms = ''
        soulmates = self.getSoulmates(member)
        if soulmates is not None:
            for soulmate in soulmates:
                sms += self.meta.getMention(soulmate) + '\n'
        if sms == '':
            sms = 'N/A'
        return sms

    @commands.command(aliases=['spouses', 'spouse', 'soulmate', 'marriages', 'sm', 'sms'])
    async def soulmates(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        num = self.getNumSoulmates(member)
        soulmate_spots = self.getSoulmateSpots(member)
        desc = self.printSoulmates(member)

        embed = discord.Embed(
            title = member.name + '\'s Soulmates `[' + str(num) + '/' + str(soulmate_spots)  + ']`',
            description = desc,
            color = discord.Color.teal()
        )
        embed.set_footer(text = 'For every 10 Help Points, you gain a soulmate spot!')
        await ctx.send(embed = embed)
        return

    @commands.command(aliases=['propose'])
    async def marry(self, ctx, member: discord.Member = None):
        if member is None:
            embed = discord.Embed(
                description = 'Correct Usage: `+marry @user`.',
                color = discord.Color.teal()
            )
            await ctx.send(embed = embed)
            return

        if ctx.author.bot or member.bot:
            embed = discord.Embed(
                title = 'You can\'t marry a bot!',
                color = discord.Color.teal()
            )
            await ctx.send(embed = embed)
            return
        if member == ctx.author:
            embed = discord.Embed(
                title = 'You can\'t marry yourself!',
                color = discord.Color.teal()
            )
            await ctx.send(embed = embed)
            return

        if not self.canAddSoulmate(ctx.author) or not self.canAddSoulmate(member):
            embed = discord.Embed(
                title = 'One of you doesn\'t have enough soulmate spots!',
                color = discord.Color.teal()
            )
            await ctx.send(embed = embed)
            return

        embed = discord.Embed(
            title = ctx.author.name + ' proposed to ' + member.name + '!',
            description = member.name + ', react to this message with a ❤ for yes, 💔 for no.\nYou have 60 seconds to decide!',
            color = discord.Color.teal()
        )
        msg = await ctx.send(embed = embed)
        await msg.add_reaction('❤')
        await msg.add_reaction('💔')

        emoji = ''

        def check(reaction, user2):
            nonlocal emoji
            emoji = str(reaction.emoji)
            return user2 == member and (str(reaction.emoji) == '❤' or str(reaction.emoji) == '💔')

        try:
            reaction, user2 = await self.client.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send(embed = self.meta.embed('Marriage Time Out', 'Your partner didn\'t respond within 60 seconds!'))
            return
        else:
            if emoji == '💔':
                embed = discord.Embed(
                    title = 'Yikes',
                    description = '<@' + str(member.id) + '> said no!',
                    color = discord.Color.teal()
                )
                await ctx.send(embed = embed)
                return

            confirmed = self.addSoulmate(ctx.author, member)
            if not (confirmed):
                await ctx.send(embed = self.meta.embedOops())
                return

            choices = ['https://i.gifer.com/S3lf.gif',
                'https://66.media.tumblr.com/ed485a688fc03e4e8f5cdb3f4d01678b/tumblr_oyfmbl9N5W1rl58vno1_500.gif',
                'https://data.whicdn.com/images/330205015/original.gif',
                'https://66.media.tumblr.com/b46302ea92abcc8b1af97dd51f9cc434/tumblr_otrlkinIp61rdvr0eo1_500.gif',
                'https://media1.giphy.com/media/rnJuusfoWyu0U/giphy.gif',
                'https://www.alamedageek.com.br/wp-content/uploads/2017/01/upaltasaventuras.gif']

            embed = discord.Embed(
                title = 'Congratulations to the Newlyweds!',
                description = ctx.author.name + ' and ' + member.name + ' are now married!',
                color = discord.Color.teal()
            )
            embed.set_image(url = random.choice(choices))
            await ctx.send(embed = embed)

    @commands.command()
    async def release(self, ctx, id):

        msg = f'Release {id} - {companion_name}?'
        ans = await self.meta.confirm(ctx, self.client, ctx.author, msg)

        if not ans:
            return

        if (self.removeSoulmate(ctx.author, member)):
            await ctx.send(embed = self.meta.embedDone())
        else:
            await ctx.send(embed = self.meta.embedOops())
        return

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        id = member.id

        try:
            self.dbConnection.removeSoulmatePair({"s1": str(id)})
        except:
            pass

        try:
            self.dbConnection.removeSoulmatePair({"s2": str(id)})
        except:
            pass

def setup(client):
    database_connection = Database()
    meta_class = Meta(database_connection)
    client.add_cog(Companions(client, database_connection, meta_class))
