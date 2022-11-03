import discord
from discord.ext import commands
from database import Database
from .meta import Meta
import random
import pymongo
from bson import objectid


class Quotes(commands.Cog):

    def __init__(self, client, database, meta):
        self.client = client
        self.dbConnection = database
        self.meta = meta

    @commands.command(aliases=['specificq', 'squote', 'spq'])
    async def specificQuote(self, ctx, quoteID: objectid.ObjectId = None):
        if quoteID is None:
            embed = discord.Embed(
                description='Correct Usage: `+quote quoteID`.',
                color=discord.Color.teal()
            )
            ctx.send(embed=embed)
            return

        quote = self.dbConnection.findQuote({'_id': quoteID})

        await ctx.send(
            '**Quote ' + str(quote['_id']) + '** by ' + self.client.get_user(quote['author']).name + '>:\n' + quote[
                'quote'])

    @commands.command(aliases=['q'])
    async def quote(self, ctx, member: discord.Member = None):
        if member is None:
            quotes = self.dbConnection.findQuotes({})
            count = quotes.count()
            quote = quotes[random.randrange(count)]
        else:
            quotes = self.dbConnection.findQuotes({'author': member.id})

            if quotes.count() == 0:
                embed = discord.Embed(
                    title=member.name + ' has no quotes.',
                    color=discord.Color.teal()
                )
                await ctx.send(embed=embed)
                return

            count = quotes.count()
            quote = quotes[random.randrange(count)]

        if member is None:
            member = self.client.get_user(quote['author'])

        await ctx.send('Quote **' + str(quote['_id']) + '** by ' + member.name + ':\n' + quote['quote'])

    @commands.command(aliases=['listquotes', 'allquotes', 'qs'])
    async def quotes(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        embed = discord.Embed(
            color=discord.Color.teal()
        )

        quotes = self.dbConnection.findQuotes({'author': member.id})
        numQuotes = quotes.count()

        title = member.name + '\'s Quotes'
        desc = 'Total: `' + str(numQuotes) + '`'

        for doc in quotes:
            # desc += '\n[ **' + str(doc['_id']) + '** ]: ' + str(doc['quote'])
            desc += '\n' + str(doc['_id'])

        embed.add_field(name=title, value=desc)
        pic = member.avatar_url
        embed.set_thumbnail(url=pic)

        await ctx.send(embed=embed)
        return

    #   Goes through certain elements of a users data in the database
    #   and puts them into an embed to send to the user through the bot
    @commands.command(aliases=['addq'])
    async def addQuote(self, ctx, member: discord.Member, *, quote=None):
        if not self.meta.isStaff(ctx.author):
            embed = discord.Embed(
                title='Sorry, you need to be staff to do that.',
                color=discord.Color.teal()
            )
            await ctx.send(embed=embed)
            return

        if quote is None:
            embed = discord.Embed(
                description='Correct Usage: `+addquote @user quoteLink`.\nThe quoteLink should be a screenshot link.',
                color=discord.Color.teal()
            )
            await ctx.send(embed=embed)
            return

        if 'http' not in quote:
            embed = discord.Embed(
                title='Sorry, I was expecting a screenshot link.',
                color=discord.Color.teal()
            )
            await ctx.send(embed=embed)
            return

        self.dbConnection.insertQuote({'author': member.id, 'quote': quote})

        embed = discord.Embed(
            title='Consider it done! ✅',
            color=discord.Color.teal()
        )
        await ctx.send(embed=embed)

    @commands.command(aliases=['rquote', 'removeq', 'deletequote', 'dquote'])
    async def removeQuote(self, ctx, quoteID: objectid.ObjectId = None):
        if not self.meta.isStaff(ctx.author):
            embed = discord.Embed(
                title='Sorry, you need to be staff to do that.',
                color=discord.Color.teal()
            )
            await ctx.send(embed=embed)
            return

        if quoteID is None:
            embed = discord.Embed(
                description='Correct Usage: `+quote quoteID`.',
                color=discord.Color.teal()
            )
            await ctx.send(embed=embed)
            return

        self.dbConnection.removeQuote({'_id': quoteID})

        embed = discord.Embed(
            title='Consider it done! ✅',
            color=discord.Color.teal()
        )
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        id = member.id
        self.dbConnection.removeQuote({"id": id})


async def setup(client):
    database_connection = Database()
    meta_class = Meta(database_connection)
    await client.add_cog(Quotes(client, database_connection, meta_class))
