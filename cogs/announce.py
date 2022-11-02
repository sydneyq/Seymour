import discord
from discord.ext import commands
from database import Database
from .meta import Meta
import os
import json

class Announce(commands.Cog):

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

    @commands.command()
    async def msg_verify(self, ctx):
        if self.meta.isAdmin(ctx.author):
            await ctx.message.delete()
            embed = discord.Embed(
                color = discord.Color.teal(),
                title = '**Welcome to Mind Café!**',
                description = 'Be sure to read `#rules` for our server rules. When you verify and participate in our server, you are automatically agreeing to them.\nYou are currently unverified.'
            )

            embed.set_footer(text = 'Thanks for joining our family!')
            embed.set_thumbnail(url = 'https://cdn.discordapp.com/emojis/593214693573787654.png')

            embed.add_field(name = '**Verify Yourself**',
            value = '`+verify tea` - Verify and join the Tea Squad\n`+verify coffee` - Verify and join the Coffee Squad\n`+verify` - Verify without joining a Squad\n\nAsk a Mod if you need assistance!')

            await ctx.send(embed = embed)
        else:
            await ctx.send(embed = self.meta.embedOops())

    @commands.command()
    async def msg_about(self, ctx):
        if self.meta.isAdmin(ctx.author):
            await ctx.message.delete()
            embed = discord.Embed(
                color = discord.Color.teal(),
                title = '**Welcome to Mind Café!**',
                description = 'We aim to provide others with a place of support and comfort. When you need a friend, someone to listen, or a place to socialize, we\'ll be here for you.'
            )

            embed.add_field(name = 'Have feedback, a question, or a repeal request?',
            value = 'Please contact one of our moderators or use ModMail by simply messaging our bot Bean the Corgi.')

            embed.add_field(name = 'How does this work?',
            value = 'Anyone can volunteer as a Supporter and devote their time to helping others, though they\'re also always welcome to ask for support themselves.')

            embed.set_thumbnail(url = 'https://cdn.discordapp.com/attachments/591611902459641856/595372970843701258/Mind_Cafe_Icon.png')

            await ctx.send(embed = embed)
        else:
            await ctx.send(embed = self.meta.embedOops())

    @commands.command()
    async def msg_rules(self, ctx):
        if self.meta.isAdmin(ctx.author):
            await ctx.message.delete()
            title = 'Mind Café Server Rules!'
            desc = 'Need help? Message a moderator (<@&592070664169455616>) or Bean for ModMail! We operate on a point-based offense system. [Click here to see the spreadsheet for points and sanctions.](https://docs.google.com/spreadsheets/d/1t3ppHecBITclZdoQ7t-VQMdBHsQ_-5tepOvdw3qLQlU/edit#gid=0)'
            e = self.meta.embed(title, desc)

            e.set_footer(text = 'By participating in our server you agree to abide by our server rules and respect our staff decisions.')
            await ctx.send(embed = e)

            for num in range(1, len(self.rules)):
                await ctx.send(embed = self.print_rule(num))
        else:
            await ctx.send(embed = self.meta.embedOops())

    def print_rule(self, num:int):
        rule = self.rules[num]
        title = f"`{num}:` {rule['TITLE']}"
        desc = rule['DESC']
        e = self.meta.embed(title, desc, 'red')
        return e

    @commands.command()
    async def rule(self, ctx, num:int):
        num = int(num)
        if num < 0:
            await ctx.send(self.meta.embedOops())
            return
        elif num > len(self.rules):
            await ctx.send(self.meta.embedOops())
            return
        await ctx.send(embed = self.print_rule(num))

    @commands.command(aliases=['strikehelp', 'modsystem', 'strikesheet'])
    async def strikesystem(self, ctx):
        title = 'Moderation Strike System',
        desc = 'See the spreadsheet here: https://docs.google.com/spreadsheets/d/1t3ppHecBITclZdoQ7t-VQMdBHsQ_-5tepOvdw3qLQlU',

        e = self.meta.embed(title, desc, 'red')
        await ctx.send(embed = e)
        return

async def setup(client):
    database_connection = Database()
    meta_class = Meta(database_connection)
    await client.add_cog(Announce(client, database_connection, meta_class))
