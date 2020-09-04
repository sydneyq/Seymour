import discord
from discord.ext import commands
from .meta import Meta
from database import Database
import secret
import json
import os


class Help(commands.Cog):

    def __init__(self, client, database, meta):
        self.client = client
        self.dbConnection = database
        self.meta = meta
        client.remove_command('help')

    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(
            title='Seymour the Bear Bot Help',
            description='Created by <@' + str(secret.OLIVE_ID) + '> ' + self.meta.getBadge('dev'),
            color=discord.Color.teal()
        )

        v='[In Development]'

        embed.add_field(name='Help Commands',
                        value=v,
                        inline=True)

        await ctx.send(embed=embed)

    @commands.command(aliases=['commands', 'cmds', 'command', 'cmd', 'funcmd', 'fcmd', 'fcmds'])
    async def funcmds(self, ctx):
        pass

    @commands.command(aliases=['mcmd', 'mcmds'])
    async def actions(self, ctx):
        embed = discord.Embed(
            title='Actions',
            color=discord.Color.teal()
        )

        actions = """`hug [@user]` - Hug someone!
        `punch [@user]` - Punch someone!
        `high5 [@user]` - AKA `highfive`, `hi5`. Highfive someone!
        `boop [@user]` - Boop someone!
        `blep` - Blep!"""
        embed.add_field(name='Actions', value=actions)

        await ctx.send(embed=embed)
        return

    @commands.command(aliases=['badgelist'])
    async def badges(self, ctx):
        embed = discord.Embed(
            title='Badge List',
            color=discord.Color.teal()
        )

        await ctx.send(embed=embed)
        return


def setup(client):
    database_connection = Database()
    meta_class = Meta(database_connection)
    client.add_cog(Help(client, database_connection, meta_class))
