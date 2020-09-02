import discord
from discord.ext import commands
from database import Database
from .meta import Meta
import json
import os
import asyncio
import random
import secret

class Squads(commands.Cog):

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

    def changeSquad(self, member: discord.Member, squad: str):
        self.dbConnection.updateProfile({"id": member.id}, {"$set": {"squad": squad}})
        return

    def getStats(self, squad):
        tea = self.dbConnection.findProfiles({'squad' : squad})
        teaMembers = tea.count()

        #total helped
        teaHelped = 0

        #top squad member
        teaTop = ''
        teaTopHelped = 0
        teaGifted = 0
        teaTopGifted = 0
        teaTopGifter = ''
        '''
        tea_water = 0
        tea_fire = 0
        tea_air = 0
        tea_earth = 0
        '''

        for doc in tea:
            #affinities
            '''
            aff = doc['affinity'].lower()
            if aff == 'water':
                tea_water += 1
            elif aff == 'air':
                tea_air += 1
            elif aff == 'fire':
                tea_fire += 1
            elif aff == 'earth':
                tea_earth += 1
            '''
            #helped
            teaHelped += doc['helped']
            if doc['helped'] > teaTopHelped:
                teaTop = '<@' + str(doc['id']) + '> (`' + str(doc['helped']) + '` Helped)'
                teaTopHelped = doc['helped']
            elif doc['helped'] == teaTopHelped:
                teaTop += '\n<@' + str(doc['id']) + '> (`' + str(doc['helped']) + '` Helped)'

        #tea_affinities = '`' + str(tea_earth) + '` Earth | `' + str(tea_air) + '` Air | `' + str(tea_fire) + '` Fire | `' + str(tea_water) + '` Water'
        teaStr = '`' + str(teaMembers) + '` Members | `' + str(teaHelped) + '` Helped\n**Most Helpful Member(s):**\n' + teaTop
        #teaStr = '`' + str(teaMembers) + '` Members | `' + str(teaHelped) + '` Helped | `' + str(teaGifted) + '` Gifts Given\n**Most Helpful Member(s):**\n' + teaTop + '\n**Most Generous Member(s):**\n' + teaTopGifter
        return teaStr

    @commands.command(aliases=['squads', 's', 'stats', 'leaderboard'])
    async def squadCount(self, ctx):
        embed = discord.Embed(
            title = 'Squad Leaderboard',
            color = discord.Color.teal()
        )

        #emojis
        teaName = self.emojis['Tea'] + ' Tea Squad '
        coffeeName = self.emojis['Coffee'] + ' Coffee Squad '
        '''
        if teaMembers > coffeeMembers:
            teaName = teaName + ' ' + secret.PEOPLE_EMOJI
        elif teaMembers < coffeeMembers:
            coffeeName = coffeeName + ' ' + secret.PEOPLE_EMOJI

        if teaHelped > coffeeHelped:
            teaName = teaName + ' ' + secret.HELPED2_EMOJI
        elif teaHelped < coffeeHelped:
            coffeeName = coffeeName + ' ' + secret.HELPED2_EMOJI
        '''
        '''
        if tea_earth > coffee_earth:
            teaName = teaName + '🌱'
        elif tea_earth < coffee_earth:
            coffeeName = coffeeName + '🌱'

        if tea_air > coffee_air:
            teaName = teaName + '🎐'
        elif tea_air < coffee_air:
            coffeeName = coffeeName + '🎐'

        if tea_fire > coffee_fire:
            teaName = teaName + '🔥'
        elif tea_fire < coffee_fire:
            coffeeName = coffeeName + '🔥'

        if tea_water > coffee_water:
            teaName = teaName + '💧'
        elif tea_water < coffee_water:
            coffeeName = coffeeName + '💧'
        '''
        embed.add_field(name=teaName,value=self.getStats('Tea'))
        embed.add_field(name=coffeeName,value=self.getStats('Coffee'), inline=False)

        await ctx.send(embed = embed)
        return

    def embedTempSquads(self):
        squads = self.dbConnection.findMeta({'id':'temp_squads'})

        title = 'Temporary Staff Squad Assignments'
        desc = 'These assignments are temporary and for the current event.'
        embed = self.meta.embed(title, desc)

        t = ''
        for person in squads['Tea']:
            t += self.meta.getMention(person) + '\n'
        embed.add_field(name='Tea Squad', value=t)

        c = ''
        for person in squads['Coffee']:
            c += self.meta.getMention(person) + '\n'
        embed.add_field(name='Coffee Squad', value=c)

        return embed

    #show temp squads
    @commands.command(aliases=['tempsquad', 'tempstaffsquads'])
    async def tempsquads(self, ctx):
        await ctx.send(embed = self.embedTempSquads())
        return

    #re-assign temp squads
    @commands.command(aliases=['reassigntempsquads', 'retempsquad', 'newtempsquads'])
    async def retempsquads(self, ctx):
        if not self.meta.isBotOwner(ctx.author):
            await ctx.send(embed = self.meta.embedOops())
            return

        guild = ctx.guild
        staff_role = guild.get_role(self.ids['STAFF_ROLE'])
        staff = staff_role.members
        tea_role = guild.get_role(self.ids['SQUAD_TEA_ROLE'])
        coffee_role = guild.get_role(self.ids['SQUAD_COFFEE_ROLE'])

        #no admins
        remove = []
        for staff_member in staff:
            if self.meta.isAdmin(staff_member):
                remove.append(staff_member)
        for r in remove:
            staff.remove(r)

        #remove ability for staff to see both squad channels
        tea_channel = guild.get_channel(self.ids['SQUAD_TEA_CHANNEL'])
        coffee_channel = guild.get_channel(self.ids['SQUAD_COFFEE_CHANNEL'])
        await tea_channel.set_permissions(staff_role, read_messages=False)
        await coffee_channel.set_permissions(staff_role, read_messages=False)

        #make lists of both tea & coffee
        random.shuffle(staff)
        index = 0
        c = []
        t = []
        while index < len(staff):
            t.append(staff[index])
            index += 1
            if index < len(staff):
                c.append(staff[index])
                index += 1

        #give them squad role
        c_ids = []
        t_ids = []

        for x in c:
            await x.add_roles(coffee_role)
            c_ids.append(x.id)

        for x in t:
            await x.add_roles(tea_role)
            t_ids.append(x.id)

        #assign to new meta.temp_squads
        self.dbConnection.updateMeta({"id": 'temp_squads'}, {"$set": {"Coffee": c_ids}})
        self.dbConnection.updateMeta({"id": 'temp_squads'}, {"$set": {"Tea": t_ids}})

        #send embed of temp squads
        await ctx.send(embed = self.embedTempSquads())
        return

    #disband temp squads (remove squad roles and return access)
    @commands.command(aliases=['untempsquads'])
    async def disbandtempsquads(self, ctx):
        #remove all squad roles
        guild = ctx.guild
        staff_role = guild.get_role(self.ids['STAFF_ROLE'])
        staff = staff_role.members
        tea_role = guild.get_role(self.ids['SQUAD_TEA_ROLE'])
        coffee_role = guild.get_role(self.ids['SQUAD_COFFEE_ROLE'])
        for staff_member in staff:
            await staff_member.remove_roles(coffee_role, tea_role)
        #give staff ability to see both squad channels again
        tea_channel = guild.get_channel(self.ids['SQUAD_TEA_CHANNEL'])
        coffee_channel = guild.get_channel(self.ids['SQUAD_COFFEE_CHANNEL'])
        await tea_channel.set_permissions(staff_role, read_messages=True)
        await coffee_channel.set_permissions(staff_role, read_messages=True)

        await ctx.send(embed = self.meta.embedDone())
        return

    @commands.command(aliases=['adminsquad'])
    async def asquad(self, ctx, member: discord.Member, *, squad):
        if not self.meta.isBotOwner(ctx.author):
            await ctx.send(embed = self.meta.embedOops())
            return
        self.changeSquad(member, squad)
        await ctx.send(embed = self.meta.embedDone())
        return

    @commands.command(aliases=['removesquad'])
    async def squadless(self, ctx, member:discord.Member):
        if not self.meta.isBotOwner(ctx.author):
            await ctx.send(embed = self.meta.embedOops())
            return
        self.changeSquad(member, 'Squadless')
        await ctx.send(embed = self.meta.embedDone())
        return

    @commands.command()
    async def squad(self, ctx, *, squad = None):
        if squad is None or (squad.lower() != 'coffee' and squad.lower() != 'tea'):
            embed = discord.Embed(
                description = 'Correct Usage: `+squad coffee` or `+squad tea`.',
                color = discord.Color.teal()
            )
            await ctx.send(embed = embed)
            return
        squad = squad.lower()

        id = ctx.author.id
        user = self.meta.getProfile(ctx.author)
        guild = ctx.guild

        if user['squad'] == "Tea":
            embed = discord.Embed(
                title = 'You\'re already part of the Tea Squad!',
                color = discord.Color.teal()
            )
            await ctx.send(embed = embed)
            return
        elif user['squad'] == "Coffee":
            embed = discord.Embed(
                title = 'You\'re already part of the Coffee Squad!',
                color = discord.Color.teal()
            )
            await ctx.send(embed = embed)
            return
        else:
            if 'tea' in squad:
                self.dbConnection.updateProfile({"id": id}, {"$set": {"squad": "Tea"}})
                embed = discord.Embed(
                    title = 'You\'ve joined the Tea Squad!',
                    color = discord.Color.teal()
                )
                await ctx.send(embed = embed)
                role = ctx.guild.get_role(612788003542401035)
                await ctx.author.add_roles(role)
                await guild.get_channel(self.ids['SQUAD_TEA_CHANNEL']).send(self.meta.msgWelcomeSquad(ctx.author))
                return
            elif 'coffee' in squad:
                self.dbConnection.updateProfile({"id": id}, {"$set": {"squad": "Coffee"}})
                embed = discord.Embed(
                    title = 'You\'ve joined the Coffee Squad!',
                    color = discord.Color.teal()
                )
                await ctx.send(embed = embed)
                role = ctx.guild.get_role(612788004926521365)
                await ctx.author.add_roles(role)
                await guild.get_channel(self.ids['SQUAD_COFFEE_CHANNEL']).send(self.meta.msgWelcomeSquad(ctx.author))
                return
            else:
                embed = discord.Embed(
                    title = 'That Squad doesn\'t exist. Please choose either Coffee or Tea.',
                    color = discord.Color.teal()
                )
                await ctx.send(embed = embed)
                return

    @commands.command()
    async def getSquadRole(self, ctx):
        id = ctx.author.id
        user = self.meta.getProfile(ctx.author)

        if user['squad'] == 'Coffee':
            role = ctx.guild.get_role(612788004926521365)
            await ctx.author.add_roles(role)
            embed = discord.Embed(
                title = 'Consider it done! ✅',
                color = discord.Color.teal()
            )
            await ctx.send(embed = embed)
        elif user['squad'] == 'Tea':
            role = ctx.guild.get_role(612788003542401035)
            await ctx.author.add_roles(role)
            embed = discord.Embed(
                title = 'Consider it done! ✅',
                color = discord.Color.teal()
            )
            await ctx.send(embed = embed)
        else:
            embed = discord.Embed(
                title = 'Couldn\'t find your Squad.',
                color = discord.Color.teal()
            )
            await ctx.send(embed = embed)
            return

def setup(client):
    database_connection = Database()
    meta_class = Meta(database_connection)
    client.add_cog(Squads(client, database_connection, meta_class))
