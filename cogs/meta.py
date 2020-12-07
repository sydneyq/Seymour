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
        self.teams = self.dbConnection.findMeta({"id": "teams"})

    async def confirm(self, context, client, responder: discord.Member, msg=None):
        if msg is None:
            msg = 'Are you sure?'

        embed = discord.Embed(
            title=msg,
            description='Please use the reactions of this message.',
            color=discord.Color.teal()
        )
        msg = await context.send(embed=embed)
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
                title=msg,
                description='Choice timed out.',
                color=discord.Color.red()
            )
            await context.send(embed=embed)
            return False
        else:
            if emoji == '⛔':
                embed = discord.Embed(
                    title='Action canceled.',
                    color=discord.Color.red()
                )
                await context.send(embed=embed)
                return False
            return True

    async def sendEmbedToLog(self, ctx, embed):
        log = ctx.guild.get_channel(self.ids['LOG_CHANNEL'])
        await log.send(embed=embed)

    def hasRole(self, member: discord.Member, rolename):
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

    # isMod
    def isMod(self, member: discord.Member):
        if self.isBotOwner(member):
            return True
        if member.guild_permissions.ban_members:
            return True
        return False

    # verified
    def isVerified(self, member: discord.Member):
        if self.ids['VERIFIED_ROLE'] in [role.id for role in member.roles]:
            return True
        return False

    # not allowed embed
    def embedNoAccess(self):
        embed = discord.Embed(
            title='Sorry, you don\'t have permission to do that!',
            color=discord.Color.teal()
        )
        return embed

    def embedDone(self, desc=None):
        if desc is None:
            desc = 'Consider it done ✅'
        embed = discord.Embed(
            title='Gotcha!',
            description=desc,
            color=discord.Color.teal()
        )
        return embed

    def embedOops(self, desc=None):
        if desc is None:
            desc = 'Something went wrong.'
        embed = discord.Embed(
            title='Oops!',
            description=desc,
            color=discord.Color.red()
        )
        return embed

    def embed(self, title, desc, color=None):
        if color is None:
            color = discord.Color.orange()
        elif color == 'red':
            color = discord.Color.red()
        elif color == 'gold':
            color = discord.Color.gold()
        elif color == 'teal':
            color = discord.Color.teal()

        embed = discord.Embed(
            title=title,
            description=desc,
            color=color
        )
        return embed

    def getServer(self):
        """
        will get server by id
        or if None then addServer()
        :return: db server dict obj
        """
        pass

    def addServer(self):
        """
        will add server to database with
        name: str, id: int, mod: int, verified: int
        :return: bool
        """
        pass

    def getProfile(self, member: discord.Member = None):
        if member is None:
            return False

        id = member.id

        profile = self.dbConnection.findProfile({"id": id, "server": str(member.guild.id)})
        if profile is None:
            profile = {'id': id, 'server': str(member.guild.id),
                       'pts': 0, 'coins': 0, 'gifts': 0,
                       'pies': 0, 'bumps': 0, 'badges': []}
            self.dbConnection.insertProfile(profile)

        return profile

    def profileDoesExist(self, id):
        profile = self.dbConnection.findProfile({"id": id})
        if profile is None:
            return False
        else:
            return True

    def makeBadge(self, badge_id, badge_literal: str):
        # check if badge_id already exists
        if not self.badgeExists(badge_id):
            self.dbConnection.insertBadge({"id": badge_id, "literal": badge_literal})
            return True
        return False

    def deleteBadge(self, badge_id: str):
        if not self.badgeExists(badge_id):
            return False
        self.dbConnection.removeBadge({"id": badge_id})
        return True

    def badgeExists(self, badge):
        return not self.dbConnection.findBadge({"id": badge}) is None

    def getBadge(self, badge):
        if self.badgeExists(badge):
            return self.dbConnection.findBadge({"id": badge})['literal']
        else:
            return None

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

    def removeBadgeFromProfile(self, member: discord.Member, badge):
        if not self.hasBadge(member, badge):
            return False
        user = self.getProfile(member)
        badges = user['badges']
        badges.remove(badge)
        self.dbConnection.updateProfile({"id": member.id}, {"$set": {"badges": badges}})
        return True

    def getTempSquad(self, member: discord.Member):
        temp_squads = self.dbConnection.findMeta({'id': 'temp_squads'})
        if member.id in temp_squads['Tea']:
            return 'Tea'
        elif member.id in temp_squads['Coffee']:
            return 'Coffee'
        else:
            return ''

    def subCake(self, member: discord.Member, amt: int = 1):
        user = self.getProfile(member)
        cakes = user['cakes']
        cakes -= amt
        if (cakes < 0):
            return False
        self.dbConnection.updateProfile({"id": member.id}, {"$set": {"cakes": cakes}})
        return True

    def addCake(self, member: discord.Member, amt: int = 1):
        user = self.getProfile(member)
        cakes = user['cakes']
        cakes += amt
        self.dbConnection.updateProfile({"id": member.id}, {"$set": {"cakes": cakes}})
        return

    def subCoins(self, member: discord.Member, amt: int):
        user = self.getProfile(member)
        coins = user['coins']
        coins -= amt

        # cannot afford
        if coins < 0:
            return False

        self.dbConnection.updateProfile({"id": user['id']}, {"$set": {"coins": coins}})
        return True

    def addCoins(self, member: discord.Member, amt: int):
        user = self.getProfile(member)
        coins = user['coins']
        coins += amt
        self.dbConnection.updateProfile({"id": user['id']}, {"$set": {"coins": coins}})
        return True

    def subGems(self, member: discord.Member, amt: int):
        user = self.getProfile(member)
        gems = user['gems']
        gems -= amt

        # cannot afford
        if gems < 0:
            return False

        self.dbConnection.updateProfile({"id": user['id']}, {"$set": {"gems": gems}})
        return True

    def addGems(self, member: discord.Member, amt: int):
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
        return 'You have:\t`' + str(helped) + '` Help Points ' + self.emojis['HelpPoint'] + ' `' + str(
            coins) + '` Coins ' + self.emojis['Coin'] + ' `' + str(gems) + '` Gems ' + self.emojis['Gem']

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

    # currently only works with <60 min
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

    def changeCurrency(self, member: discord.Member, val: int, currency: str):
        currency = currency.lower()

        if currency not in ['coins', 'bumps', 'pts', 'points', 'pies', 'gift', 'gifts', 'pie', 'pies']:
            return False

        if currency == 'points':
            currency = 'pts'
        elif currency == 'pie':
            currency = 'pies'
        elif currency == 'gift':
            currency = 'gifts'

        user = self.getProfile(member)
        total = user[currency]
        total += val

        self.dbConnection.updateProfile({"id": member.id, "server": str(member.guild.id)}, {"$set": {currency: total}})
        return total

    def addBumps(self, member: discord.Member, val: int):
        user = self.getProfile(member)
        bumps = user['bumps']
        bumps += val

        self.dbConnection.updateProfile({"id": user['id']}, {"$set": {"bumps": bumps}})
        return bumps

    def changePoints(self, member: discord.Member, val: int):
        user = self.getProfile(member)
        pts = user['pts']
        pts += val

        # cannot afford
        if pts < 0:
            return False

        self.dbConnection.updateProfile({"id": user['id']}, {"$set": {"pts": pts}})
        return pts

    def hasWord(self, string, word):
        # case-insensitive, ignores punctuation: 32-96, 123-126 (not 97 - 122)
        string = string.lower()
        word = word.lower()
        filtered = ''
        # print('string: ' + filtered)
        # print('word: ' + filtered)

        if word not in string:
            return False

        for portion in string.split():
            filtered = ''
            # print('portion: ' + filtered)
            if word in portion:
                for c in portion:
                    ascii = ord(c)
                    if ascii >= 97 and ascii <= 122:
                        filtered += c
                # print('filtered: ' + filtered)

                if filtered == word:
                    return True

        return False

    def isModMailChannel(self, channel: discord.TextChannel):
        return channel.name.lower().startswith('mm-')

    def getMention(self, id: int):
        return '<@' + str(id) + '>'

    def getUserByID(self, client, id: int):
        return client.get_user(id)

    def getMemberByID(self, ctx, id: int):
        return ctx.guild.get_member(id)

    def hash_ID(self: int):
        # (id - E, swap(first 2 numbers, last 2 numbers), * 2) + 1
        user_id = self - ord('E')
        user_id = str(user_id)[-2:] + str(user_id)[2:-2] + str(user_id)[:2]
        # user_id = (int(user_id) * 2) + 1
        return int(user_id) + 1

    def unhash_ID(self: int):
        # (id-1 / 2), swap(first 2 numbers, last 2 numbers), + E
        # user_id = int((self - 1)/2)
        user_id = self - 1
        user_id = str(user_id)[-2:] + str(user_id)[2:-2] + str(user_id)[:2]
        user_id = int(user_id) + ord('E')
        return user_id

    def edit_actions(self, member: discord.Member, actions: list):
        self.dbConnection.updateProfile({"id": member.id, "server": str(member.guild.id)}, {"$set": {"actions": actions}})

    def get_actions(self, member: discord.Member):
        profile = self.getProfile(member)
        actions = profile['actions']
        return actions

    def has_action(self, member: discord.Member, action: str):
        return action in self.get_actions(member)

    def add_action(self, member: discord.Member, action: str):
        if self.has_action(member, action):
            return False
        actions = self.get_actions(member)
        actions.append(action)
        self.edit_actions(member, actions)
        return True

    def remove_action(self, member: discord.Member, action: str):
        if not self.has_action(member, action):
            return False
        actions = self.get_actions(member)
        actions.remove(action)
        self.edit_actions(member, actions)
        return True

    def is_pieable(self, member: discord.Member):
        return self.getProfile(member)['pieable']

    def change_team(self, member: discord.Member, team):
        self.dbConnection.updateProfile({"id": member.id, "server": str(member.guild.id)}, {"$set": {"team": team}})

    def refresh_teams(self):
        return self.dbConnection.findMeta({"id": "teams"})


class Global(commands.Cog):

    def __init__(self, client, database, meta):
        self.client = client
        self.meta = meta
        self.dbConnection = database

    @commands.command()
    async def test(self, ctx):
        if self.meta.isBotOwner(ctx.author):
            # guild = ctx.guild
            # self.dbConnection.renameColumn("companions", "dex")
            self.dbConnection.makeColumn("actions", [])
            self.dbConnection.makeColumn("pieable", True)
            self.dbConnection.makeColumn("team", -1)
            # self.dbConnection.removeColumn("cakes")
            '''
            profiles = self.dbConnection.findProfiles({})
            for profile in profiles:
                if profile['soulmates'] is None:
                    self.dbConnection.updateProfile({"id": profile['id']}, {"$set": {"soulmates": []}})
            '''
            await ctx.send(embed=self.meta.embedDone())
            print("Done!")

    @commands.command()
    async def ping(self, ctx):
        if (self.meta.isBotOwner(ctx.message.author)):
            await ctx.send(f'Pong! `{round(self.client.latency * 1000)}ms`')

    @commands.command()
    async def status(self, ctx, *, msg):
        if self.meta.isBotOwner(ctx.message.author):
            await self.client.change_presence(activity=discord.Game(msg))
            await ctx.send(embed=self.meta.embedDone())
        else:
            await ctx.send(embed=self.meta.embedNoAccess())

    @commands.command(aliases=['echo'])
    async def say(self, ctx, channel: discord.TextChannel, *, message):
        if self.meta.isBotOwner(ctx.author):
            await channel.send(message)
            await ctx.message.delete()
        else:
            return
            # await ctx.send(embed=self.meta.embedNoAccess())

    @commands.command(aliases=['echoembed', 'embedecho'])
    async def sayembed(self, ctx, channel: discord.TextChannel, *, message):
        if self.meta.isMod(ctx.author):

            embed = discord.Embed(
                description=message,
                color=discord.Color.teal()
            )

            hashed = Meta.hash_ID(ctx.author.id)
            embed.set_footer(text=f"Sent by a Staff Member * [{hashed}]")

            await channel.send(embed=embed)
            await ctx.message.delete()
        else:
            await ctx.send(embed=self.meta.embedNoAccess())

    @commands.command(aliases=['echoedit', 'editecho'])
    async def edit(self, ctx, msg_id: int, *, msg_edited: str = None):
        if not self.meta.isBotOwner(ctx.author):
            return

        msg = await ctx.channel.fetch_message(msg_id)
        await msg.edit(content=msg_edited)

        await ctx.message.delete()

    @commands.command(aliases=['embededit'])
    async def editembed(self, ctx, msg_id: int, *, msg_edited: str = None):
        if not self.meta.isMod(ctx.author):
            return

        if msg_edited is not None:
            msg_edited = discord.Embed(
                description=msg_edited,
                color=discord.Color.teal()
            )
            hashed = Meta.hash_ID(ctx.author.id)
            msg_edited.set_footer(text=f"Edited by a Staff Member * [{hashed}]")

        msg = await ctx.channel.fetch_message(msg_id)
        await msg.edit(embed=msg_edited)

        await ctx.message.delete()

    @commands.command(aliases=[])
    async def unhash(self, ctx, user_id: int):
        if not self.meta.isMod(ctx.author):
            return

        unhashed = Meta.unhash_ID(user_id)

        embed = discord.Embed(
            title='Unhash',
            description=f"`{user_id}` -> `{unhashed}`",
            color=discord.Color.teal()
        )

        await ctx.send(embed=embed)

    @commands.command(aliases=["editteam", "changeteam"])
    async def team(self, ctx, member: discord.Member, team: int):
        if not self.meta.isBotOwner(ctx.author):
            return

        self.meta.change_team(member, team)
        await ctx.send(embed=self.meta.embedDone())

    @commands.command()
    async def refreshteams(self, ctx):
        self.meta.refresh_teams()
        await ctx.send(embed=self.meta.embedDone())

    @commands.command(aliases=["printteams", "teamnums"])
    async def teams(self, ctx):
        teams = self.meta.teams
        await ctx.send(embed=self.meta.embed("Teams", f"`{0}`: {teams['0']}\n`{1}`: {teams['1']}\n`{2}`: {teams['2']}"))


def setup(client):
    database_connection = Database()
    meta_class = Meta(database_connection)
    client.add_cog(Global(client, database_connection, meta_class))
