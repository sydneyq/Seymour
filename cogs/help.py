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
            description=f"Created by <@{str(secret.OLIVE_ID)}> {self.meta.getBadge('dev')} on Sept 2, 2020."
                        + '\n`[]` = optional, `<>` = required',
            color=discord.Color.teal()
        )

        v = '[In Development]'
        v += '\n`profile [@member]` aka `p`: show profile'
        v += '\n`actions`: show action commands'
        v += '\n`badge <badge_id>` aka `showbadge`: display a badge'

        embed.add_field(name='Help Commands',
                        value=v,
                        inline=True)

        await ctx.send(embed=embed)

    @commands.command()
    async def actions(self, ctx):
        embed = discord.Embed(
            title='Actions',
            description='`[]` = optional, `<>` = required',
            color=discord.Color.teal()
        )

        actions = """`hug [@user]` - Hug someone!
        `punch [@user]` - Punch someone!
        `high5 [@user]` - AKA `highfive`, `hi5`. Highfive someone!
        `boop [@user]` - Boop someone!
        `pat [@user]` - Pat someone!"""
        embed.add_field(name='Actions', value=actions)

        await ctx.send(embed=embed)
        return

    @commands.command(aliases=['badgelist'])
    async def badges(self, ctx):
        desc = []
        badges = self.dbConnection.findBadges({})
        for badge in badges:
            desc.append(badge['id'])

        desc = ", ".join(desc)

        await ctx.send(embed=self.meta.embed('Badges', desc))
        return

    @commands.command()
    async def roleinfo(self, ctx, *, role_name):
        role_name = role_name.lower()
        for role in ctx.guild.roles:
            if role.name.lower() == role_name:
                title = role.name
                desc = f"{role.mention}\nID: `{role.id}`\n`{len(role.members)}` members with this role."
                await ctx.send(embed=self.meta.embed(title, desc))
                return
        await ctx.send(embed=self.meta.embedOops("I couldn't find a role with that name."))
        return


def setup(client):
    database_connection = Database()
    meta_class = Meta(database_connection)
    client.add_cog(Help(client, database_connection, meta_class))
