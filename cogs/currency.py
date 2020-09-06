import discord
from discord.ext import commands
from database import Database
from .meta import Meta
import random
import json
import os
import asyncio
from numpy.random import choice
import secret


class Currency(commands.Cog):

    def __init__(self, client, database, meta):
        self.client = client
        self.dbConnection = database
        self.meta = meta

    @commands.command(aliases=['pt', 'rep'])
    async def point(self, ctx, member: discord.Member, amt: int = 1):
        """
        give someone points with 50c/each
        :param amt:
        :param ctx:
        :param member:
        :return:
        """
        if not self.meta.isMod(ctx.author):
            return

        profile = self.meta.getProfile(member)
        og_pts = profile['pts']
        og_coins = profile['coins']

        add_coins = amt * 50
        total = self.meta.changeCurrency(member, amt, 'pts')
        coins = self.meta.changeCurrency(member, add_coins, 'coins')

        desc = f"**{member.name}** has been given `{amt}` points and `50` coins for each point (`{add_coins}`)!"
        desc += f"\n**Points:** `{og_pts}` -> `{total}`"
        desc += f"\n**Coins:** `{og_coins}` -> `{coins}`"

        embed = discord.Embed(
            title=f"{member.name} has been given `{amt}` points!",
            description=f"Total: `{total}` points",
            color=discord.Color.gold()
        )

        if amt > 0:
            try:
                await member.send(embed=embed)
            except:
                print('Could not send private message.')

        await ctx.send(embed=embed)

    @commands.command(aliases=['take'])
    async def give(self, ctx, member: discord.Member, amt: int, currency: str):
        """
        as in 'give @member 50 coins'
        take into account plural/single
        :param ctx:
        :param member:
        :param amt:
        :param currency:
        :return:
        """

        if not self.meta.isMod(ctx.author):
            return

        total = 0
        profile = self.meta.getProfile(member)
        if currency in ['coin', 'coins', 'c', 'cs']:
            currency = 'coins'
        elif currency in ['point', 'points', 'pts', 'pt']:
            currency = 'points'
        elif currency in ['pie', 'pies']:
            currency = 'pies'
        elif currency in ['bumps', 'bump']:
            currency = 'bumps'
        else:
            await ctx.send(embed=self.meta.embedOops('Invalid currency type.'))
            return

        # bumps & pies bot-owner only
        if currency == 'bumps' or currency == 'pies':
            if not self.meta.isBotOwner(ctx.author):
                await ctx.send(embed=self.meta.embedOops())
                return

        total = self.meta.changeCurrency(member, amt, currency)

        if not total:
            await ctx.send(embed=self.meta.embedOops())
            return

        embed = discord.Embed(
            title=f"{member.name} has been given `{amt}` {currency}!",
            description=f"Total: `{total}` {currency}",
            color=discord.Color.gold()
        )

        if amt > 0:
            try:
                await member.send(embed=embed)
            except:
                print('Could not send private message.')

        await ctx.send(embed=embed)

    @commands.command(aliases=[])
    async def pie(self, ctx, member: discord.Member):
        profile = self.meta.getProfile(ctx.author)

        # check if the author has a pie
        if not self.meta.isBotOwner(ctx.author):
            if profile['pies'] > 0:
                self.meta.changeCurrency(ctx.author, -1, 'pies')
            else:
                await ctx.send(embed=self.meta.embedOops('Not enough pies! Buy one at the `store`.'))
                return

        first = ['Fun-Loving', 'Groovy', 'Wavy',
                 'Partying', 'Dancing', 'Cheesy',
                 'Bubble', 'Gravy', 'Pizza',
                 'Pie', 'Sleepy', 'Vibing',
                 'Creamy', 'Nerdy', 'Angry',
                 'Huggable', 'Undercover', 'Cursed',
                 'Cinnamon', 'Ice Cream', 'Glitter',
                 'Sparkly', 'Disco', 'Fuzzy',
                 'Potato Salad', 'Lovable', 'Friendly',
                 'Beloved', 'Hypnotized', 'Surfing',
                 'Sweet and Sour', 'Fluffy', 'Rainbow'
                 ]
        last = ['Pirate', 'Dinosaur', 'Plant',
                'Dolphin', 'Pillow', 'Bear',
                'Bunny', 'President', 'Swimmer',
                'Pie', 'Boss', 'Challenger',
                'Unicorn', 'Rock Star', 'Dancer',
                'Robot', 'Lunch', 'Pumpkin',
                'Chef', 'Mango', 'Penguin',
                'Bill Nye', 'Pudding',
                'Overlord', 'Cupcake', 'Pastry',
                'Bee'
                ]
        emoji = ['😍', '😇', '🥳', '😎', '🤓',
                 '🤯', '🥴', '🤖', '👻', '🦌',
                 '🥓', '🧜', '🧐', '🥧', '💥',
                 '🌈', '⛄️', '🐸', '🐨', '😳',
                 '🍗', '🍤', '🍬', '🧡', '💚',
                 '🍄', '🦄', '🐙', '🐱', '🤟',
                 '✌️', '👍', '🙌', '🖖', '💪',
                 '😘', '😉', '😏'
                 ]

        nick = f'{random.choice(first)} {random.choice(last)} {random.choice(emoji)}'

        # edit the nickname of the member
        try:
            await member.edit(nick=nick)
        except:
            # if no edit nick perms
            # safety: add 1 pie back
            print('Edit nickname failed.')
            await ctx.send(embed=self.meta.embedOops('Edit nickname failed.'))
            self.meta.changeCurrency(ctx.author, 1, 'pies')
            return

        await ctx.send(embed=self.meta.embedDone(f"**{member.name}**'s nickname has been changed to **{nick}**."))

    @commands.command(aliases=[])
    async def gift(self, ctx, member: discord.Member):
        profile = self.meta.getProfile(ctx.author)

        # check author has gift
        if profile['gifts'] > 0:
            self.meta.changeCurrency(ctx.author, -1, 'gifts')
        else:
            await ctx.send(embed=self.meta.embedOops('You don\'t have enough gifts! Buy one at the `store`.'))
            return

        # randomize amt & give to member
        amt = random.choice([50, 75, 100])
        member_profile = self.meta.getProfile(member)
        self.meta.changeCurrency(member, amt, 'coins')

        await ctx.send(embed=self.meta.embedDone(f"{ctx.author.name} just gifted {member.name} `{amt}` coins!"))
        return

    @commands.command(aliases=[])
    async def buy(self, ctx, item: str):
        found = self.dbConnection.findStoreItem({"id": item})
        if found is None:
            await ctx.send(embed=self.meta.embedOops("I couldn't find the item."))
            return

        profile = self.meta.getProfile(ctx.author)
        if profile['coins'] >= found['price']:
            if self.meta.changeCurrency(ctx.author, 1, item):
                coins = self.meta.changeCurrency(ctx.author, (found['price'] * -1), 'coins')
                await ctx.send(embed=self.meta.embedDone(f"Done! You now have `{coins}` coins."))
            else:
                await ctx.send(embed=self.meta.embedOops("Something went wrong when adding the item."))
                return
        else:
            await ctx.send(embed=self.meta.embedOops("You don't have enough coins."))
            return

    @commands.command(aliases=['store', 's'])
    async def shop(self, ctx):
        """
        pies: 200 (?)c
        gifts: ??? coins
        :param ctx:
        :param member:
        :return:
        """

        embed = discord.Embed(color=discord.Color.orange(), title="Store", description="Buy something with `buy <item>`.")

        items = self.dbConnection.findStoreItems({})
        for item in items:
            embed.add_field(name=f"{item['price']}c: {item['id']}", value=item['desc'], inline=False)

        await ctx.send(embed=embed)

def setup(client):
    database_connection = Database()
    meta_class = Meta(database_connection)
    client.add_cog(Currency(client, database_connection, meta_class))
