import discord
from discord.ext import commands
from discord.utils import get
import secret
from database import Database
import datetime
import json
import os
import asyncio

class Meta:

    def __init__(self, database):
        self.dbConnection = database

        dirname = os.path.dirname(__file__)
        '''
        filename = os.path.join(dirname, 'docs/store.json')
        filename2 = os.path.join(dirname, 'docs/emojis.json')
        filename3 = os.path.join(dirname, 'docs/ids.json')

        with open(filename) as json_file:
            self.store = json.load(json_file)

        with open(filename2) as json_file:
            self.emojis = json.load(json_file)

        with open(filename3) as json_file:
            self.ids = json.load(json_file)
        '''

    def embed(self, title, desc, color = None):
        if color is None:
            color = discord.Color.teal()
        elif color == 'red':
            color = discord.Color.red()
        elif color == 'gold':
            color = discord.Color.gold()

        embed = discord.Embed(
            title = title,
            description = desc,
            color = color
        )
        return embed

    async def confirm(self, context, client, responder: discord.Member, msg = None):
        if msg is None:
            msg = 'Are you sure?'

        embed = discord.Embed(
            title = msg,
            description = 'Please use the reactions of this message.',
            color = discord.Color.teal()
        )
        msg = await context.send(embed = embed)
        await msg.add_reaction('✅')
        await msg.add_reaction('⛔')

        emoji = ''
        def check(reaction, user2):
            nonlocal emoji
            emoji = str(reaction.emoji)
            return user2 == responder and (str(reaction.emoji) == '✅' or str(reaction.emoji) == '⛔')

        try:
            reaction, user2 = await client.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            embed = discord.Embed(
                title = msg,
                description = 'Choice timed out.',
                color = discord.Color.red()
            )
            await context.send(embed = embed)
            return False
        else:
            if emoji == '⛔':
                embed = discord.Embed(
                    title = 'Action canceled.',
                    color = discord.Color.red()
                )
                await context.send(embed = embed)
                return False
            return True

    async def sendEmbedToLog(self, ctx, embed):
        log = ctx.guild.get_channel(self.ids['LOG_CHANNEL'])
        await log.send(embed = embed)

    def hasRole(self, member:discord.Member, rolename):
        rolename = rolename.lower()
        if rolename in [role.name.lower() for role in member.roles]:
            return True
        else:
            return False

    def isBotOwner(self, member: discord.Member):
        if member.id == secret.OLIVE_ID or member.id == secret.SYD_ID:
            return True
        return False

    def isSelf(self, member: discord.Member):
        if member.id == secret.SEYMOUR_ID:
            return True
        return False

    #isMod
    def isMod(self, member: discord.Member):
        if self.isBotOwner(member):
            return True
        #if self.ids['MOD_ROLE'] in [role.id for role in member.roles]:
        #    return True
        return False

    #verified
    def isVerified(self, member: discord.Member):
        if self.ids['VERIFIED_ROLE'] in [role.id for role in member.roles]:
            return True
        return False

    #not allowed embed
    def embedNoAccess(self):
        embed = discord.Embed(
            title = 'Sorry, you don\'t have permission to do that!',
            color = discord.Color.teal()
        )
        return embed

    def embedDone(self):
        embed = discord.Embed(
            title = 'Consider it done! ✅',
            color = discord.Color.teal()
        )
        return embed

    def embedOops(self, desc = None):
        if desc is None:
            desc = 'Something went wrong.'
        embed = discord.Embed(
            title = 'Oops!',
            description = desc,
            color = discord.Color.red()
        )
        return embed

    def getProfile(self, member: discord.Member = None):
        if member is None:
            return

        id = member.id

        profile = self.dbConnection.findProfile({"id": id})
        if profile is None:
            self.dbConnection.insertProfile({'id': id, 'points': 0, 'coins': 50, 'gifts': 0, 'badges':[], 'cakes': 0})
            profile = self.dbConnection.findProfile({"id": id})

        return profile

    def profileDoesExist(self, id):
        profile = self.dbConnection.findProfile({"id": id})
        if profile is None:
            return False
        else:
            return True

    def getBadge(self, badge):
        b = self.dbConnection.findBadge({"id":badge})['literal']

        if b is None:
            b = self.emojis[badge]
        return b

    def hasBadge(self, member: discord.Member, badge):
        user = self.getProfile(member)
        badges = user['badges']
        if badge in badges:
            return True
        else:
            return False

    def addBadgeToProfile(self, member: discord.Member, badge):
        if self.hasBadge(member, badge):
            return False
        user = self.getProfile(member)
        badges = user['badges']
        badges.append(badge)
        self.dbConnection.updateProfile({"id": member.id}, {"$set": {"badges": badges}})
        return True

    def getTempSquad(self, member: discord.Member):
        temp_squads = self.dbConnection.findMeta({'id':'temp_squads'})
        if member.id in temp_squads['Tea']:
            return 'Tea'
        elif member.id in temp_squads['Coffee']:
            return 'Coffee'
        else:
            return ''

    def subCake(self, member: discord.Member, amt:int = 1):
        user = self.getProfile(member)
        cakes = user['cakes']
        cakes -= amt
        if (cakes < 0):
            return False
        self.dbConnection.updateProfile({"id": member.id}, {"$set": {"cakes": cakes}})
        return True

    def addCake(self, member: discord.Member, amt:int = 1):
        user = self.getProfile(member)
        cakes = user['cakes']
        cakes += amt
        self.dbConnection.updateProfile({"id": member.id}, {"$set": {"cakes": cakes}})
        return

    def subCoins(self, member: discord.Member, amt:int):
        user = self.getProfile(member)
        coins = user['coins']
        coins -= amt

        #cannot afford
        if coins < 0:
            return False

        self.dbConnection.updateProfile({"id": user['id']}, {"$set": {"coins": coins}})
        return True

    def addCoins(self, member: discord.Member, amt:int):
        user = self.getProfile(member)
        coins = user['coins']
        coins += amt
        self.dbConnection.updateProfile({"id": user['id']}, {"$set": {"coins": coins}})
        return True

    def subGems(self, member: discord.Member, amt:int):
        user = self.getProfile(member)
        gems = user['gems']
        gems -= amt

        #cannot afford
        if gems < 0:
            return False

        self.dbConnection.updateProfile({"id": user['id']}, {"$set": {"gems": gems}})
        return True

    def addGems(self, member: discord.Member, amt:int):
        user = self.getProfile(member)
        gems = user['gems']
        gems += amt
        self.dbConnection.updateProfile({"id": user['id']}, {"$set": {"gems": gems}})
        return True

    def getGems(self, member: discord.Member):
        user = self.getProfile(member)
        gems = user['gems']
        return gems

    def printCurrency(self, member: discord.Member):
        user = self.getProfile(member)
        helped = user['helped']
        coins = user['coins']
        gems = user['gems']
        return 'You have:\t`' + str(helped) + '` Help Points ' + self.emojis['HelpPoint'] + ' `' + str(coins) + '` Coins ' + self.emojis['Coin'] + ' `' + str(gems) + '` Gems ' + self.emojis['Gem']

    def getFullDateTime(self):
        return datetime.datetime.now()

    def formatDateTime(self, datetime):
        x = datetime
        data = {
            "month": x.strftime("%B"),
            "day": int(x.strftime("%d")),
            "hour": int(x.strftime("%H"))
        }
        return data

    def formatDateTimeString(self, datetime):
        data = self.formatDateTime(datetime)
        return str(data['hour']) + 'h, ' + str(data['day']) + ' ' + data['month']

    def getDateTime(self):
        x = datetime.datetime.now()
        data = {
            "weekday": int(x.strftime("%w")),
            "hour": int(x.strftime("%H")),
            "minute": int(x.strftime("%M"))
        }
        return data

    def hasBeen24Hours(self, previous, current):
        if previous['weekday'] == current['weekday']:
            return False
        elif (previous['weekday'] + 1 == current['weekday']) or (previous['weekday'] == 6 and current['weekday'] == 0):
            if previous['hour'] > current['hour']:
                return False
            elif previous['hour'] == current['hour']:
                if previous['minute'] > current['minute']:
                    return False
                else:
                    return True
            else:
                return True
        else:
            return True

    #currently only works with <60 min
    def hasBeenMinutes(self, mins: int, previous, current):
        if previous['hour'] == current['hour']:
            if abs(previous['minute'] - current['minute']) >= mins:
                return True
            else:
                return False
        elif abs(previous['hour'] - current['hour']) == 1:
            if ((60 - previous['minute']) + current['minute']) >= mins:
                return True
            else:
                return False
        else:
            return True

    def getMinuteDifference(self, previous, current):
        minutes = 0
        if previous['weekday'] != current['weekday']:
            minutes += 24 - current['hour'] + previous['hour']
        else:
            minutes += current['hour'] - previous['hour']

        minutes *= 60

        if previous['minute'] > current['minute']:
            minutes += (previous['minute'] - current['minute'])

        return abs(minutes - 1440)

    def changeCoins(self, member: discord.Member, val: int):
        user = self.getProfile(member)
        coins = user['coins']
        coins += val

        #cannot afford
        if coins < 0:
            return False

        self.dbConnection.updateProfile({"id": user['id']}, {"$set": {"coins": coins}})
        return True

    def update_points(self, member: discord.Member, val: int):
        user = self.getProfile(member)
        pts = user['pts']
        pts += val

        #cannot afford
        if pts < 0:
            return False

        self.dbConnection.updateProfile({"id": user['id']}, {"$set": {"pts": pts}})
        return True

    def hasWord(self, string, word):
        #case-insensitive, ignores punctuation: 32-96, 123-126 (not 97 - 122)
        string = string.lower()
        word = word.lower()
        filtered = ''
        #print('string: ' + filtered)
        #print('word: ' + filtered)

        if word not in string:
            return False

        for portion in string.split():
            filtered = ''
            #print('portion: ' + filtered)
            if word in portion:
                for c in portion:
                    ascii = ord(c)
                    if ascii >= 97 and ascii <= 122:
                        filtered += c
                #print('filtered: ' + filtered)

                if filtered == word:
                    return True

        return False

    def isModMailChannel(self, channel: discord.TextChannel):
        return channel.name.lower().startswith('mm-')

    def getMention(self, id:int):
        return '<@' + str(id) + '>'

    def getUserByID(self, client, id:int):
        return client.get_user(id)

    def getMemberByID(self, ctx, id:int):
        return ctx.guild.get_member(id)


class Global(commands.Cog):

    def __init__(self, client, database, meta):
        self.client = client
        self.meta = meta
        self.dbConnection = database

    @commands.command()
    async def test(self, ctx):
        if self.meta.isBotOwner(ctx.author):
            guild = ctx.guild
            self.dbConnection.renameColumn("companions", "dex")
            self.dbConnection.makeColumn("redeemed", [])
            #self.dbConnection.removeColumn("cakes")
            '''
            profiles = self.dbConnection.findProfiles({})
            for profile in profiles:
                if profile['soulmates'] is None:
                    self.dbConnection.updateProfile({"id": profile['id']}, {"$set": {"soulmates": []}})
            '''
            await ctx.send(embed = self.meta.embedDone())
            print("Done!")

    @commands.command()
    async def ping(self, ctx):
        if (self.meta.isAdmin(ctx.message.author)):
            await ctx.send(f'Pong! `{round(self.client.latency * 1000)}ms`')

    @commands.command()
    async def status(self, ctx, *, msg):
        if (self.meta.isAdmin(ctx.message.author)):
            await self.client.change_presence(status=discord.Status.online, activity=discord.Game(msg))
        else:
            await ctx.send(embed = self.meta.embedNoAccess())

    @commands.command()
    async def echo(self, ctx, channel: discord.TextChannel, *, message):
        author = ctx.message.author
        isMod = True if self.meta.isMod(author) else False
        isStaff = True if self.meta.isStaff(author) else False
        isOfficialMod = True if isMod and isStaff else False
        isMgmt = True if self.meta.isMgmt(author) else False

        if not isOfficialMod and not isMgmt:
            await ctx.send(embed = self.meta.embedOops())
            return

        if not isMgmt:
            if ctx.channel.id != self.ids['MOD_CHANNEL']:
                await ctx.send(embed = self.meta.embedOops())
                return

        #check if they have permission to talk in that channel first
        if not author.permissions_in(channel).send_messages:
            await ctx.send(embed = self.meta.embedOops())
            return

        e = self.meta.embed('A Mind Café Staff Member Says:', message, 'red')
        await channel.send(embed = e)

        await ctx.message.delete()
        e.set_footer(text='' + ctx.author.name + ' in ' + channel.name, icon_url = ctx.author.avatar_url)
        await ctx.guild.get_channel(self.ids['MOD_CHANNEL']).send(embed = e)
        return

    @commands.command()
    async def say(self, ctx, channel: discord.TextChannel, *, message):
        if self.meta.isBotOwner(ctx.author) or self.meta.isMod(ctx.author):

            embed = discord.Embed(
                description = message,
                color = discord.Color.teal()
            )

            await channel.send(embed = embed)
        else:
            embed = discord.Embed(
                title = 'Sorry, you don\'t have permission to do that!',
                color = discord.Color.teal()
            )
            await ctx.send(embed = embed)


def setup(client):
    database_connection = Database()
    meta_class = Meta(database_connection)
    client.add_cog(Global(client, database_connection, meta_class))
