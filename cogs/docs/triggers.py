import discord
from discord.ext import commands
from discord.utils import get
import secret
import json
import os
from database import Database
from .meta import Meta

class Triggers(commands.Cog):

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

    @commands.command()
    async def hotlines(self, ctx):
        embed = discord.Embed(
            title = 'Hotlines and Resources',
            description = '[Click here for hotlines in the USA.](https://www.dosomething.org/us/about/hotline-list)\n[Click here for a list of emergency telephone numbers for all areas.](https://en.wikipedia.org/wiki/List_of_emergency_telephone_numbers)',
            color = discord.Color.teal()
        )
        await ctx.send(embed = embed)

    #@commands.Cog.listener()
    #async def on_message(self, message):
    #    return

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        guild = self.client.get_guild(257751892241809408)
        updates = guild.get_channel(655191315130089493)
        heaven = guild.get_channel(594657206251814963)
        events = guild.get_channel(594641130545741834)
        mods = guild.get_channel(592030367796690975)
        marketing = guild.get_channel(594641226330800153)
        announcements = guild.get_channel(257760030034624513)

        def embedRoleAdded(role):
            embed = discord.Embed(
                title = after.name + ' has been given the ' + role + ' role!',
                color = discord.Color.gold()
            )
            embed.set_author(name = 'Mind Café', icon_url = 'https://media.discordapp.net/attachments/591611902459641856/595372970843701258/Mind_Cafe_Icon.png')
            embed.set_footer(text = 'Congratulations! 🎉')
            return embed

        def embedRoleRemoved(role):
            embed = discord.Embed(
                title = after.name + ' has been removed from the ' + role + ' role.',
                color = discord.Color.gold()
            )
            return embed

        def roleWasAdded(id):
            nonlocal before
            nonlocal after
            if (id in [role.id for role in after.roles]) and (id not in [role.id for role in before.roles]):
                return True
            return False

        def roleWasRemoved(id):
            nonlocal before
            nonlocal after
            if (id in [role.id for role in before.roles]) and (id not in [role.id for role in after.roles]):
                return True
            return False

        #in-trial angel added
        if roleWasAdded(self.ids['TRIAL_ROLE']):
            await heaven.send(embed = mbedRoleAdded('In-Trial Angels'))
        #in-trial angel removed
        elif roleWasRemoved(self.ids['TRIAL_ROLE']):
            await heaven.send(embed = embedRoleRemoved('In-Trial Angels'))
        #staff added
        elif roleWasAdded(self.ids['STAFF_ROLE']):
            await heaven.send(embed = embedRoleAdded('Angels'))
            await updates.send(embed = embedRoleAdded('Angels'))
            tea_role = guild.get_role(self.ids['SQUAD_TEA_ROLE'])
            coffee_role = guild.get_role(self.ids['SQUAD_COFFEE_ROLE'])
            await ctx.author.remove_roles(coffee_role, tea_role)
        #staff removed
        elif roleWasRemoved(self.ids['STAFF_ROLE']):
            await heaven.send(embed = embedRoleRemoved('Angels'))
        #mod added
        elif roleWasAdded(self.ids['MOD_ROLE']):
            e = embedRoleAdded('Mods')
            await heaven.send(embed = e)
            await mods.send(embed = e)
        #mod removed
        elif roleWasRemoved(self.ids['MOD_ROLE']):
            e = embedRoleRemoved('Mods')
            await heaven.send(embed = e)
            await mods.send(embed = e)
        #PM added
        elif roleWasAdded(self.ids['MARKETINGOFFICER_ROLE']):
            e = embedRoleAdded('Partnership Managers')
            await heaven.send(embed = e)
            await marketing.send(embed = e)
        #PM removed
        elif roleWasRemoved(self.ids['MARKETINGOFFICER_ROLE']):
            e = embedRoleRemoved('Partnership Managers')
            await heaven.send(embed = e)
            await marketing.send(embed = e)
        #EC added
        elif roleWasAdded(self.ids['EVENTCOORDINATOR_ROLE']):
            e = embedRoleAdded('Event Coordinators')
            await heaven.send(embed = e)
            await events.send(embed = e)
        #EC removed
        elif roleWasRemoved(self.ids['EVENTCOORDINATOR_ROLE']):
            e = embedRoleRemoved('Event Coordinators')
            await heaven.send(embed = e)
            await events.send(embed = e)
        #PL added
        elif roleWasAdded(self.ids['CERTIFIED_ROLE']):
            await updates.send(embed = embedRoleAdded('Peer Listeners'))
        #listener added
        elif roleWasAdded(self.ids['LISTENER_ROLE']):
            await updates.send(embed = embedRoleAdded('Listeners'))

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        msg = message.content.lower()
        channel = message.channel
        t = ''
        d = ''

        if 'how do i get coins' in msg:
            t = 'How to get Coins ' + self.emojis['Coin']
            d = '**[+]** Join in on server events that offer coins!'
            d += '\n**[+]** Use the `daily` command if you have a Companion!'
            d += '\n**[+]** Catch a highfive when Bean asks for one!'
            await channel.send(embed = self.meta.embed(t,d))
        elif 'how do i get a companion' in msg:
            t = 'How to get a Companion'
            d = '**[+]** Buy one with Coins in the Store `+store c`!'
            d += '\n**[+]** Get enough Help Points for a Helped Companion `+store h`'
            await channel.send(embed = self.meta.embed(t,d))

async def setup(client):
    database_connection = Database()
    meta_class = Meta(database_connection)
    await client.add_cog(Triggers(client, database_connection, meta_class))
