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
        filename = os.path.join(dirname, 'docs/store.json')
        filename2 = os.path.join(dirname, 'docs/emojis.json')
        filename3 = os.path.join(dirname, 'docs/ids.json')

        with open(filename) as json_file:
            self.store = json.load(json_file)

        with open(filename2) as json_file:
            self.emojis = json.load(json_file)

        with open(filename3) as json_file:
            self.ids = json.load(json_file)

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
        if member.id == secret.BOT_OWNER_ID:
            return True
        return False

    def isBean(self, member: discord.Member):
        if member.id == secret.BEAN_ID:
            return True
        return False

    def isBeanOrJarvis(self, member: discord.Member):
        if member.id == secret.BEAN_ID or member.id == secret.JARVIS_ID:
            return True
        return False

    #isAdmin
    def isAdmin(self, member: discord.Member):
        if self.isBotOwner(member):
            return True
        if self.ids['ADMIN_ROLE'] in [role.id for role in member.roles]:
            return True
        return False

    #isDirector
    def isDirector(self, member: discord.Member):
        if self.isBotOwner(member):
            return True
        if self.ids['DIRECTOR_ROLE'] in [role.id for role in member.roles]:
            return True
        return False

    #isMgmt
    def isMgmt(self, member: discord.Member):
        return self.isAdmin(member) or self.isDirector(member)

    #isStaff
    def isStaff(self, member: discord.Member):
        if self.isBotOwner(member):
            return True
        if self.ids['STAFF_ROLE'] in [role.id for role in member.roles]:
            return True
        return False

    #isMod
    def isMod(self, member: discord.Member):
        if self.isBotOwner(member):
            return True
        if self.isAdmin(member):
            return True
        if self.ids['MOD_ROLE'] in [role.id for role in member.roles]:
            return True
        return False

    def isEventCoordinator(self, member: discord.Member):
        if self.ids['EVENTCOORDINATOR_ROLE'] in [role.id for role in member.roles]:
            return True
        return False

    def isMarketingOfficer(self, member: discord.Member):
        if self.ids['MARKETINGOFFICER_ROLE'] in [role.id for role in member.roles]:
            return True
        return False

    def isPatron(self, member: discord.Member):
        if self.ids['PATRON_ROLE'] in [role.id for role in member.roles]:
            return True
        return False

    #verified
    def isVerified(self, member: discord.Member):
        if self.ids['VERIFIED_ROLE'] in [role.id for role in member.roles]:
            return True
        return False

    #certified
    def isCertified(self, member: discord.Member):
        if self.ids['CERTIFIED_ROLE'] in [role.id for role in member.roles]:
            return True
        return False

    #blindfolded
    def isRestricted(self, member: discord.Member):
        if self.ids['BLINDFOLDED_ROLE'] in [role.id for role in member.roles]:
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

    def msgWelcomeSquad(self, member: discord.Member = None):
        if member is None:
            return

        user = self.getProfile(member)
        squad = user['squad']

        msg = '**__🎉 Let\'s all welcome <@' + str(member.id) + '> to the '+squad+' Squad! 🎉__**'
        msg += '\n> Say hello to your new teammate! You\'ll be working with them during events.'
        return msg

    def getProfile(self, member: discord.Member = None):
        if member is None:
            return

        id = member.id

        profile = self.dbConnection.findProfile({"id": id})
        if profile is None:
            self.dbConnection.insertProfile({'id': id, 'squad': '', 'helped': 0, 'coins': 50, 'companion': '', 'gifts': 0, 'affinity':'', 'daily': '', 'badges':[], 'booster': 0,'dex' : [], 'soulmates' : [], 'cakes': 0, 'gems': 0, 'redeemed': []})
            profile = self.dbConnection.findProfile({"id": id})

        squad = profile['squad']
        if self.isAdmin(member):
            profile['squad'] = 'Admin'
        elif self.isStaff(member):
            profile['squad'] = 'Staff'

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

    def inDex(self, member: discord.Member, companion):
        user = self.getProfile(member)
        companions = user['dex']
        if companion in companions:
            return True
        else:
            return False

    def addToDex(self, member: discord.Member, companion):
        if self.inDex(member, companion):
            return False
        user = self.getProfile(member)
        companions = user['dex']
        companions.append(companion)
        self.dbConnection.updateProfile({"id": member.id}, {"$set": {"dex": companions}})
        return True

    def inRedeemed(self, member: discord.Member, companion):
        user = self.getProfile(member)
        companions = user['redeemed']
        if companion in companions:
            return True
        else:
            return False

    def addToRedeemed(self, member: discord.Member, companion):
        if self.inDex(member, companion):
            return False
        user = self.getProfile(member)
        companions = user['redeemed']
        companions.append(companion)
        self.dbConnection.updateProfile({"id": member.id}, {"$set": {"redeemed": companions}})
        return True

    def hasAllEvolutionsOf(self, member: discord.Member, companion):
        user = self.getProfile(member)
        companions = user['dex']
        evolve = self.getStoreItem(companion)
        evolve = evolve['JSON']['evolve']
        for e in evolve:
            if not (e in companions):
                return False
        return True

    def changeAffinity(self, member: discord.Member, affinity):
        if not (affinity in self.getProfile(member)['badges']):
            self.addBadgeToProfile(member, affinity)

        if self.hasBadge(member, 'Fire') and self.hasBadge(member, 'Water') and self.hasBadge(member, 'Earth') and self.hasBadge(member, 'Air'):
            self.addBadgeToProfile(member, 'Avatar')

        self.dbConnection.updateProfile({"id": member.id}, {"$set": {"affinity": affinity, "booster":0}})

    #is directly buyable from store.json
    def isBuyable(self, item):
        if self.getStoreItem(item) == '':
            return False

        unbuyable_stores = ['Evolved Companions']

        for s in unbuyable_stores:
            for i in self.store[s]:
                if i['name'].lower() == item:
                    return False
        return True

    #returns the JSON data of the item in store.json
    def getStoreItem(self, item):
        item = item.lower()

        stores = ['Coin Companions',
        'Helped Companions',
        'Evolvable Companions',
        'Items',
        'Evolved Companions']

        for s in stores:
            for i in self.store[s]:
                if i['name'].lower() == item:
                    return {
                    "JSON": i,
                    "type": s
                    }

        return ''

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

    def changeHelped(self, member: discord.Member, val: int):
        user = self.getProfile(member)
        helped = user['helped']
        helped += val

        #cannot afford
        if helped < 0:
            return False

        self.dbConnection.updateProfile({"id": user['id']}, {"$set": {"helped": helped}})
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

    def getChannelOwnerID(self, channel: discord.TextChannel):
        if not '-' in channel.name:
            return -1
        channel_owner_id = channel.name[channel.name.rfind('-')+1:]
        try:
            channel_owner_id = int(channel_owner_id)
        except:
            return -1
        else:
            return channel_owner_id

    def getChannelOwner(self, ctx, channel: discord.TextChannel):
        return self.getMemberByID(self.getChannelOwnerID(channel))

    def isChannelOwner(self, member: discord.Member, channel: discord.TextChannel):
        channel_owner_id = self.getChannelOwnerID(channel)
        if type(channel_owner_id) is not int or channel_owner_id == -1:
            return -1
        return member.id == channel_owner_id

    def isSupportChannel(self, channel: discord.TextChannel):
        return channel.name.lower().startswith('s-')

    def isModMailChannel(self, channel: discord.TextChannel):
        return channel.name.lower().startswith('mm-')

    def isEeveelution(self, companion):
        eeveelutions = self.getEeveelutions()
        if companion in eeveelutions:
            return True
        return False

    def getEeveelutions(self):
        eeveelutions = ['Espeon',
        'Flareon',
        'Glaceon',
        'Jolteon',
        'Leafeon',
        'Sylveon',
        'Umbreon',
        'Vaporeon']
        return eeveelutions

    def getRecorded(self):
        list = self.getEeveelutions()
        list.append('Ditto')
        return list

    def isRecorded(self, companion):
        if companion in self.getRecorded():
            return True
        return False

    def getMention(self, id:int):
        return '<@' + str(id) + '>'

    def getUserByID(self, client, id:int):
        return client.get_user(id)

    def getMemberByID(self, ctx, id:int):
        return ctx.guild.get_member(id)

    def getSquadChannel(self, guild, squad):
        id = self.ids['SQUAD_COFFEE_CHANNEL']
        if squad == 'Tea':
            id = self.ids['SQUAD_TEA_CHANNEL']
        return guild.get_channel(id)

class Global(commands.Cog):

    def __init__(self, client, database, meta):
        self.client = client
        self.meta = meta
        self.dbConnection = database

        dirname = os.path.dirname(__file__)
        filename2 = os.path.join(dirname, 'docs/emojis.json')
        filename3 = os.path.join(dirname, 'docs/ids.json')

        with open(filename2) as json_file:
            self.emojis = json.load(json_file)

        with open(filename3) as json_file:
            self.ids = json.load(json_file)

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
    async def verify(self, ctx, *, squad = None):
        member = ctx.author
        if not self.meta.isVerified(member):
            guild = ctx.guild
            #spirits
            verified_role = guild.get_role(self.ids['VERIFIED_ROLE'])
            await member.add_roles(verified_role)
            #basicroles
            basicroles = guild.get_role(593065193966403587)
            await member.add_roles(basicroles)
            #helpingothers
            helpingothers = guild.get_role(593064902038650880)
            await member.add_roles(helpingothers)
            #welcome
            #casual = guild.get_channel(secret.WORKSHOP_CHANNEL)
            casual = guild.get_channel(self.ids['GENERAL_CHANNEL'])
            msg = '**__🎉 Let\'s all welcome <@' + str(member.id) + '> to Mind Cafe! 🎉__**'
            msg += '\n> **Need Support?** Take a look at <#601444570600964097> and get started in <#597026335835291659>.'
            msg += '\n> **Want to join a Squad?** Go to <#621499838856560642> and say `+profile` to get started.'
            await casual.send(msg)
            #delete command
            await ctx.message.delete()
            if squad != None:
                id = member.id
                user = self.meta.getProfile(member)
                guild = ctx.guild

                if 'tea' in squad:
                    self.dbConnection.updateProfile({"id": id}, {"$set": {"squad": "Tea"}})
                    role = ctx.guild.get_role(612788003542401035)
                    await ctx.author.add_roles(role)
                    await guild.get_channel(self.ids['SQUAD_TEA_CHANNEL']).send(self.meta.msgWelcomeSquad(member))
                elif 'coffee' in squad:
                    self.dbConnection.updateProfile({"id": id}, {"$set": {"squad": "Coffee"}})
                    role = ctx.guild.get_role(612788004926521365)
                    await ctx.author.add_roles(role)
                    await guild.get_channel(self.ids['SQUAD_COFFEE_CHANNEL']).send(self.meta.msgWelcomeSquad(member))
                else:
                    embed = discord.Embed(
                        title = 'That Squad doesn\'t exist. Please choose either Coffee or Tea.',
                        color = discord.Color.teal()
                    )
                    await ctx.send(embed = embed, delete_after=10)
                    return

    @commands.command()
    async def bean(self, ctx, channel: discord.TextChannel, *, message):
        if self.meta.isBotOwner(ctx.author):

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

    #clear archive
    @commands.command(aliases=['clearA'])
    async def clearArchive(self, ctx):
        async with ctx.channel.typing():
            guild = self.client.get_guild(257751892241809408)
            author = ctx.message.author
            archive = 0

            if (self.meta.isAdmin(author)):
                for ch in guild.categories:
                    if ch.name.lower() == 'archive':
                        archive = ch
                        break
            else:
                await ctx.send(embed = self.meta.noAccessEmbed())
                return

            for ch in archive.channels:
                await ch.delete(reason='Archive clear')

        embed = discord.Embed(
            title = 'Archive cleared! ✅',
            color = discord.Color.teal()
        )
        await ctx.send(embed = embed)

    #switch
    @commands.command(aliases=['swapST', 'swap', 'switchST'])
    async def switch(self, ctx):
        isAdmin = self.meta.isAdmin(ctx.author)
        isMod = self.meta.isMod(ctx.author)
        isCertified = self.meta.isCertified(ctx.author)
        isChannelOwner = self.meta.isChannelOwner(ctx.author, ctx.channel)
        log = ctx.guild.get_channel(self.ids['LOG_CHANNEL'])
        channel = ctx.channel
        guild = ctx.guild

        if not isAdmin:
            if ((not isMod) and (not isChannelOwner) and (not isCertified)) or (not self.meta.isSupportChannel(channel)):
                embed = discord.Embed(
                    title = 'Sorry, that command can only be used in Support Ticket channels by the Support Ticket Owner, Certifieds, or Moderators+.',
                    color = discord.Color.teal()
                )
                await ctx.send(embed = embed)
                return

        if channel.is_nsfw():
            #change to sfw
            await channel.edit(nsfw = False)
            await channel.edit(sync_permissions = True)
            await channel.set_permissions(self.meta.getChannelOwner(ctx, ctx.channel), read_messages=True, send_messages=True)

            await log.send('<@' + str(ctx.author.id) + '> has switched ' + '<#' + str(channel.id) + '> to SFW.')

            embed = discord.Embed(
                title = 'Switched support channel to SFW! ✅',
                color = discord.Color.teal()
            )
            await ctx.send(embed = embed)
        else:
            await channel.set_permissions(ctx.author, read_messages=True, send_messages=True)
            await channel.edit(nsfw = True)
            #await newChannel.set_permissions(guild.default_role, read_messages=False)
            await channel.set_permissions(guild.get_role(self.ids['VERIFIED_ROLE']), read_messages=False)
            await channel.set_permissions(self.meta.getChannelOwner(ctx, ctx.channel), read_messages=True, send_messages=True)
            await channel.set_permissions(guild.get_role(self.ids['NSFW_ROLE']), read_messages=True)

            await log.send('<@' + str(ctx.author.id) + '> has switched ' + '<#' + str(channel.id) + '> to NSFW.')

            embed = discord.Embed(
                title = 'Switched support channel to NSFW! ✅',
                color = discord.Color.teal()
            )
            await ctx.send(embed = embed)

    #archive
    @commands.command(aliases=['archivest'])
    async def archive(self, ctx):
        isAdmin = self.meta.isAdmin(ctx.author)
        isMod = self.meta.isMod(ctx.author)
        isCertified = self.meta.isCertified(ctx.author)
        isChannelOwner = self.meta.isChannelOwner(ctx.author, ctx.channel)
        log = ctx.guild.get_channel(self.ids['LOG_CHANNEL'])
        channel = ctx.channel
        guild = ctx.guild

        category = 0
        for c in ctx.guild.categories:
            if c.name.lower() == 'archive':
                category = c #Archive

        if self.meta.isSupportChannel(channel):
            isChannelOwner = self.meta.isChannelOwner(ctx.author, ctx.channel)
            if not isChannelOwner and not isMod and not isCertified:
                await ctx.send(embed = self.meta.embedNoAccess())
                return

            embed = discord.Embed(
                title = 'Thanks for talking with us!',
                description = 'If you felt a Listener was supportive, you can use the command `+helpedby @user` in #botspam to show them how much you appreciated their help!',
                color = discord.Color.teal()
            )
            embed.set_thumbnail(url = 'https://cdn.discordapp.com/emojis/602887275289772052.png?v=1')

            channel_owner_id = self.meta.getChannelOwnerID(channel)
            if channel_owner_id != -1:
                user = self.client.get_user(channel_owner_id)
                try:
                    await user.send(embed = embed)
                except:
                    print('Could not send private message.')

            await log.send('Support Ticket [**' + channel.name + '**] has been archived.')
        elif self.meta.isModMailChannel(channel):
            if not isMod:
                await ctx.send(embed = self.meta.embedNoAccess())
                return
            await log.send('ModMail Ticket [**' + channel.name + '**] has been archived.')
        else:
            if not isAdmin:
                await ctx.send(embed = self.meta.embedNoAccess())
                return

        await ctx.message.channel.edit(name = 'archived-'+ channel.name)
        try:
            await ctx.message.channel.edit(category = category, sync_permissions = True)
        except:
            async with ctx.channel.typing():
                embed = discord.Embed(
                    title = 'Archive full. Clearing archive...',
                    color = discord.Color.teal()
                )
                await ctx.send(embed = embed)

                for ch in category.channels:
                    await ch.delete(reason='Archive clear')

                embed = discord.Embed(
                    title = 'Archive auto-cleared! ✅',
                    color = discord.Color.teal()
                )
                await log.send(embed = embed)
                await ctx.send(embed = embed)
            await ctx.message.channel.edit(category = category, sync_permissions = True)

    #close/delete
    @commands.command(aliases=['delete'])
    async def close(self, ctx):
        if self.meta.isAdmin(ctx.author):
            await ctx.message.channel.delete(reason='Deleted by ' + ctx.author.name)
        else:
            await ctx.send(embed = self.meta.embedNoAccess())

    #lock

    '''
    #edit msg example
    @commands.command()
    async def test(self, ctx):
        channel = ctx.guild.get_channel(612449175686086667)
        msg = channel.last_message

        if msg.author != self.client.user:
            embed = discord.Embed(
                title = 'edit me',
                color = discord.Color.teal()
            )

            await channel.send(embed = embed)
        else:
            embeds = msg.embeds
            embed = embeds[0]
            embed2 = discord.Embed(
                title = 'edited wow',
                color = discord.Color.gold()
            )

            await msg.edit(embed = embed2)
    '''

def setup(client):
    database_connection = Database()
    meta_class = Meta(database_connection)
    client.add_cog(Global(client, database_connection, meta_class))
