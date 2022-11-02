import discord
from discord.ext import commands
from database import Database
from .meta import Meta
import random
import pymongo
from bson import objectid
import os
import json

class Moderation(commands.Cog):

    def __init__(self, client, database, meta):
        self.client = client
        self.dbConnection = database
        self.meta = meta

        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, 'docs/rules.json')
        filename2 = os.path.join(dirname, 'docs/emojis.json')
        filename3 = os.path.join(dirname, 'docs/ids.json')

        with open(filename) as json_file:
            self.rules = json.load(json_file)

        with open(filename2) as json_file:
            self.emojis = json.load(json_file)

        with open(filename3) as json_file:
            self.ids = json.load(json_file)

    def getModLogs(self, member: discord.Member):
        return self.dbConnection.findModLogs({'id' : member.id})

    def modProfileExists(self, id):
        profile = self.dbConnection.findModProfile({"id": id})
        if profile is None:
            return False
        else:
            return True

    def getModProfile(self, member: discord.Member):
        if member is None:
            return

        id = member.id

        profile = self.dbConnection.findModProfile({"id": id})
        if profile is None:
            self.dbConnection.insertModProfile({'id': id, 'strikes':0})
            profile = self.dbConnection.findModProfile({"id": id})

        return profile

    async def checkStrikes(self, ctx, member: discord.Member):
        profile = self.getModProfile(member)
        strikes = profile['strikes']

        if strikes >= 10:
            await self.ban_func(ctx, member)
            return 'The member was permabanned.'
        elif strikes >= 9:
            await self.blindfold_func(ctx, member)
            return 'The member was Blindfolded.'
        elif strikes >= 7:
            await self.mute_func(ctx, member, 72)
            return 'The member was muted for 72h.'
        elif strikes >= 5:
            await self.mute_func(ctx, member, 24)
            return 'The member was muted for 24h.'
        elif strikes >= 3:
            await self.mute_func(ctx, member, 6)
            return 'The member was muted for 6h.'

    def embedMuted(self, hours: int = -1):
        title = 'You have been muted'
        if hours != -1:
            title += ' for `'+str(hours)+'` hours'
        embed = discord.Embed(
            title = title,
            color = discord.Color.red()
        )
        return embed

    def embedBanned(self):
        embed = discord.Embed(
            title = 'You have been banned from Mind Café',
            color = discord.Color.red()
        )
        return embed

    def embedBlindfolded(self):
        embed = discord.Embed(
            title = 'You have been blindfolded',
            description = 'You no longer have access to casual channels and may only receive support through requesting support DMs',
            color = discord.Color.red()
        )
        return embed

    def embedUnmuted(self):
        embed = discord.Embed(
            title = 'You have been unmuted',
            color = discord.Color.red()
        )
        return embed

    def embedUnblindfolded(self):
        embed = discord.Embed(
            title = 'You have been unblindfolded',
            color = discord.Color.red()
        )
        return embed

    async def ban_func(self, ctx, user: discord.User):
        await ban(user)
        try:
            await member.send(embed = self.embedBanned())
        except:
            return

    async def unban_func(self, user: discord.User):
        await unban(user)
        return

    async def mute_func(self, ctx, member: discord.Member, hrs: int = -1):
        muted = ctx.guild.get_role(445398365606248448)
        await member.add_roles(muted)
        try:
            await member.send(embed = self.embedMuted(hrs))
        except:
            return

    async def unmute_func(self, ctx, member: discord.Member):
        muted = ctx.guild.get_role(445398365606248448)
        await member.remove_roles(muted)
        try:
            await member.send(embed = self.embedUnmuted())
        except:
            return

    async def blindfold_func(self, ctx, member: discord.Member):
        role = guild.get_role(self.ids['BLINDFOLDED_ROLE'])
        await member.add_roles(role)
        try:
            await member.send(embed = self.embedBlindfolded())
        except:
            return

    async def unblindfold_func(self, member: discord.Member):
        role = guild.get_role(self.ids['BLINDFOLDED_ROLE'])
        await member.remove_roles(role)
        try:
            await member.send(embed = self.embedUnblindfolded())
        except:
            return

    def changeStrikes(self, member:discord.Member, strikes:int):
        if not self.modProfileExists(member.id):
            return False
        self.dbConnection.updateModProfile({"id": member.id}, {"$set": {"strikes": strikes}})
        return True

    def changeModLogReason(self, id, reason):
        if self.dbConnection.findModLog({"_id": id}) is None:
            return False
        self.dbConnection.updateModLog({"_id": id}, {"$set": {"reason": reason}})
        return True

    def getRuleJSON(self, rule: int):
        rule_json = self.rules[rule]
        return rule_json

    def getAmtStrikesFromRule(self, rule: int):
        rule_json = self.getRuleJSON(rule)
        return int(rule_json['STRIKES'])

    @commands.command(aliases=['warn', 'sanction'])
    async def strike(self, ctx, member: discord.Member, rule:int, *, reason = None):
        if not self.meta.isMod(ctx.author):
            await ctx.send(embed = self.meta.embedOops())
            return
        elif member.bot: #or self.isAdmin(member):
            await ctx.send(embed = self.meta.embedOops())
            return
        if rule < 0 or rule > 14:
            await ctx.send(embed = self.meta.embedOops())
            return

        #await ctx.message.delete()

        if reason is None or reason == None:
            reason = 'No custom message provided'

        profile = self.getModProfile(member)
        before_strikes = profile['strikes']
        after_strikes = profile['strikes'] + self.getAmtStrikesFromRule(rule)
        if not (self.changeStrikes(member, after_strikes)):
            await ctx.send(embed = self.meta.embedOops())
            return
        self.dbConnection.insertModLog({'id': member.id, 'rule': rule, 'reason': reason, 'staff': ctx.author.id, 'date': self.meta.getFullDateTime()})

        embed = discord.Embed(
            color = discord.Color.red()
        )
        n = 'You\'ve been striked for: Rule `'+str(rule)+'`'
        v = 'Strikes: `'+str(before_strikes)+'->'+str(after_strikes)+'`'
        embed.add_field(name=n, value=v)
        n = 'Rule `'+str(rule)+'` description'
        v = self.getRuleJSON(rule)['DESC']
        embed.add_field(name=n, value=v, inline=False)
        n = 'Moderator\'s custom message'
        v = reason
        embed.add_field(name=n, value=v)

        try:
            await member.send(embed = embed)
        except:
            await ctx.send('Could not send them Strike message.')

        action = 'No further action was taken.'
        if not (before_strikes == after_strikes):
            a = await self.checkStrikes(ctx, member)
            if (a is not None):
                action = a

        embed = discord.Embed(
            color = discord.Color.red()
        )
        n = 'New Strike'
        v = member.mention + ' has been striked. `['+ str(before_strikes) + '->' + str(after_strikes)+']`'
        v += '\n**Moderator:** ' + ctx.author.mention
        v += '\nRule `'+str(rule)+'`: ```' + reason + '```'
        embed.add_field(name=n, value=v)
        embed.set_footer(text = action)
        await ctx.send(embed = embed)
        await self.meta.sendEmbedToLog(ctx, embed)

    @commands.command(aliases=['updatestrike', 'changestrike'])
    async def editstrikes(self, ctx, member: discord.Member, strikes:int):
        if not self.meta.isAdmin(ctx.author):
            await ctx.send(embed = self.meta.embedOops())
            return

        embed = discord.Embed(
            color = discord.Color.teal()
        )

        profile = self.getModProfile(member)
        s = str(profile['strikes'])

        n = 'Strike Count Change'
        v = '' + ctx.author.mention + ' changed ' + member.mention + '\'s Strikes'
        v += '\n`' + s + '->' + str(strikes) + '`'
        embed.add_field(name = n, value = v)
        self.changeStrikes(member, strikes)

        await ctx.send(embed = embed)
        await self.meta.sendEmbedToLog(ctx, embed)

    @commands.command(aliases=['deletestrike', 'delstrike'])
    async def removestrike(self, ctx, strikeID: objectid.ObjectId = None):
        if not self.meta.isMod(ctx.author):
            await ctx.send(embed = self.meta.embedOops())
            return

        if strikeID is None:
            embed = discord.Embed(
                description = 'Correct Usage: `+removestrike strikeID`.',
                color = discord.Color.teal()
            )
            await ctx.send(embed = embed)
            return

        modlog = self.dbConnection.findModLog({'_id' : strikeID})
        if modlog is None:
            await ctx.send(embed = self.meta.embedOops())
            return

        member = self.client.get_user(modlog['id'])
        profile = self.getModProfile(member)
        before_strikes = profile['strikes']
        after_strikes = before_strikes - self.getAmtStrikesFromRule(modlog['rule'])
        self.changeStrikes(member, after_strikes)

        self.dbConnection.removeModLog({'_id' : strikeID})

        embed = discord.Embed(
            title = 'Consider it done! ✅',
            description = member.name + '\'s Strikes: `'+str(before_strikes)+'->'+str(after_strikes)+'`',
            color = discord.Color.red()
        )
        await ctx.send(embed = embed)

    @commands.command(aliases=['clearModLog'])
    async def clearLog(self, ctx, member: discord.Member):
        if not self.meta.isAdmin(ctx.author):
            await ctx.send(embed = self.meta.embedOops())
            return

        docs = self.dbConnection.findModLogs({'id' : member.id})
        for doc in docs:
            self.dbConnection.removeModLog({'_id' : doc['_id']})

        await ctx.send(embed = self.meta.embedDone())

    @commands.command(aliases=['demute'])
    async def unmute(self, ctx, member:discord.Member):
        if not self.meta.isMod(ctx.author):
            return
        await self.unmute_func(ctx, member)
        await ctx.send(embed = self.meta.embedDone())

    @commands.command()
    async def mute(self, ctx, member:discord.Member, hrs: int = -1):
        if not self.meta.isMod(ctx.author):
            return
        await self.mute_func(ctx, member, hrs)
        await ctx.send(embed = self.meta.embedDone())

    @commands.command()
    async def ban(self, ctx, member:discord.Member, hrs: int, *, reason):
        if not self.meta.isAdmin(ctx.author):
            return
        await self.ban_func(ctx, member)
        await ctx.send(embed = self.meta.embedDone())

    @commands.command(aliases=['mp', 'modlog', 'ml', 'log', 'strikes'])
    async def modprofile(self, ctx, member: discord.Member = None):
        channel = ctx.channel
        #must be by mod
        if not self.meta.isMod(ctx.author):
            if member is None:
                channel = ctx.author
            else:
                await ctx.send(self.meta.embedOops())
                return
        #for non-admins, must be in modlog channel
        elif not self.meta.isAdmin(ctx.author):
            if ctx.channel.id != 367863780627185685:
                await ctx.send(self.meta.embedOops())
                return

        if member is None:
            member = ctx.author

        logs = self.getModLogs(member)
        numLogs = logs.count()
        #they have no logs
        if not self.modProfileExists(member.id):
            embed = discord.Embed(
                title = member.name + ' has no logs.',
                description = 'Strikes: `'+str(self.getModProfile(member)['strikes'])+'`',
                color = discord.Color.teal()
            )
            try:
                await channel.send(embed = embed)
            except:
                await ctx.send(embed = self.meta.embedOops())
            return

        profile = self.getModProfile(member)

        title = member.name + '\'s Log'
        desc = 'Total Strikes: `' + str(profile['strikes']) + '`'
        desc += '\nNumber of Logs: `' + str(numLogs) + '`'

        embed = discord.Embed(
            title = title,
            description = desc,
            color = discord.Color.red()
        )

        for doc in logs:
            n = 'Rule `' + str(doc['rule']) + '`  @ ' + self.meta.formatDateTimeString(doc['date'])
            v = '<@' + str(doc['staff']) + '>: ' + str(doc['_id'])
            embed.add_field(name=n, value=v)

        pic = member.avatar_url
        embed.set_thumbnail(url = pic)

        try:
            await channel.send(embed = embed)
        except:
            await ctx.send(embed = self.meta.embedOops())
        return

    @commands.command(aliases=['strikecase', 'seestrike'])
    async def case(self, ctx, case_id: objectid.ObjectId = None):
        if not self.meta.isMod(ctx.author):
            return

        if case_id is None:
            embed = discord.Embed(
                description = 'Correct Usage: `+case caseID`.',
                color = discord.Color.red()
            )
            ctx.send(embed = embed)
            return

        case = self.dbConnection.findModLog({'_id' : case_id})

        embed = discord.Embed(
            title = 'Case `'+str(case_id)+'`',
            color = discord.Color.red()
        )

        n = 'Details'
        v = '**Offender:** ' + self.meta.getMention(case['id'])
        v += '\n**Moderator:** ' + self.meta.getMention(case['staff'])
        v += '\n**Date:** ' + self.meta.formatDateTimeString(case['date'])
        embed.add_field(name=n, value=v, inline=False)
        n = 'Rule `' + str(case['rule']) + '`'
        v = '**Custom message:** ' + case['reason']
        embed.add_field(name=n, value=v)
        embed.set_thumbnail(url = self.meta.getUserByID(self.client, case['id']).avatar_url)

        await ctx.send(embed = embed)

    @commands.command(aliases=['reason'])
    async def updateCase(self, ctx, case_id: objectid.ObjectId, *, reason):
        if not self.meta.isMod(ctx.author):
            return

        if (self.changeModLogReason(case_id, reason)):
            await ctx.send(embed = self.meta.embedDone())
        else:
            await ctx.send(embed = self.meta.embedOops())

    @commands.command()
    async def rules(self, ctx):
        embed = discord.Embed(
            color = discord.Color.red()
        )

        n = 'Mind Café Rules'
        v = ''
        for rule in self.rules:
            v += '\n**'+ str(rule["NUM"]) + ' - ' + rule['TITLE'] + '**'
            v += ' | `'+str(rule['STRIKES'])+'` Strikes'
        embed.add_field(name = n, value = v, inline = False)

        await ctx.send(embed = embed)
        return

async def setup(client):
    database_connection = Database()
    meta_class = Meta(database_connection)
    await client.add_cog(Moderation(client, database_connection, meta_class))
