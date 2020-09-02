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

class Store(commands.Cog):

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

    @commands.command(aliases=['shop', 'companion', 'companions', 'pets', '$', 'sh', 'st'])
    async def store(self, ctx, type: str = None):
        id = ctx.author.id
        user = self.meta.getProfile(ctx.author)

        helped = user['helped']
        coins = user['coins']
        companions = user['dex']

        embed = discord.Embed(
            title = 'Store',
            description = self.meta.printCurrency(ctx.author),
            color = discord.Color.teal()
        )

        #default store
        if type is None:
            storeHelp = """Welcome to the Store! This is where you can reap the rewards of your hard work."""
            embed.add_field(name='Store Help', value=storeHelp, inline=False)

            storeDesc = """`+store c` - Coin Companion Store
            `+store h` - Helped Companion Store
            `+store i` - Item Store
            `+store e` - Evolvable/Evolved Companion List"""
            embed.add_field(name='Store Commands', value=storeDesc, inline=False)

            #embed.set_thumbnail(url = 'https://cdn.discordapp.com/emojis/602910572153143337.png?v=1')
            embed.set_footer(text = 'Need help with profiles or currency? Check #about-profiles!')
            await ctx.send(embed = embed)
            return
        #coin
        elif type.lower() == 'coin' or type.lower() == 'c' or type.lower() == 'coins':
            storeHelp = """You can buy these Companions with Coins and using `+buy companionName`. You do not keep a Coin Companion if you set or buy a different Companion. Buy an Evolution Stone to evolve an evolvable Companion. Evolved Companions have a higher chance for more daily coins."""
            embed.add_field(name='Store Help', value=storeHelp, inline=False)
            storeDesc = ''
            prevCost = 0

            for item in self.store['Coin Companions']:
                #same price, add to same line
                if item['price'] == prevCost:
                    storeDesc += ', ' + item['name']
                #different price, new line, update prevCost
                else:
                    storeDesc += '\n`' + str(item['price']) + ' coins:` ' + item['name']
                    prevCost = item['price']

            embed.add_field(name=self.emojis['Coin'] + ' Coin Companions', value=storeDesc, inline=False)

            storeDesc_special = ''
            for item in self.store['Evolvable Companions']:
                #same price, add to same line
                if item['price'] == prevCost:
                    storeDesc_special += ', ' + item['name']
                #different price, new line, update prevCost
                else:
                    storeDesc_special += '\n`' + str(item['price']) + ' coins:` ' + item['name']
                    prevCost = item['price']

            embed.add_field(name=self.emojis['Special'] + ' Evolvable Companions', value=storeDesc_special, inline=False)

            embed.set_footer(text = 'Earn coins by participating in server events! Use the "+help" command for more Bean commands.')
            await ctx.send(embed = embed)
            return
        #helped
        elif type.lower() == 'helped' or type.lower() == 'h':
            storeHelp = """You can unlock these Companions with Help Points and using `+set companionName`. After reaching the minimum amount of Help Points, you're able to keep these Companions!"""
            embed.add_field(name='Store Help', value=storeHelp, inline=False)
            storeDesc = ''
            prevCost = 0

            for item in self.store['Helped Companions']:
                #same price, add to same line
                if item['price'] == prevCost:
                    storeDesc += ', ' + item['name']
                #different price, new line, update prevCost
                else:
                    storeDesc += '\n`' + str(item['price']) + ' helped:` ' + item['name']
                    prevCost = item['price']

            embed.add_field(name=self.emojis['HelpPoint'] + ' Helped Companions', value=storeDesc, inline=False)
            #embed.set_thumbnail(url = 'https://img.pngio.com/mario-bros-star-png-png-image-mario-bros-star-png-240_215.png')
            embed.set_footer(text = 'Earn Help Points by supporting others!  Use the "+help" command for more Bean commands.')
            await ctx.send(embed = embed)
            return
        #item
        elif type.lower() == 'item' or type.lower() == 'i' or type.lower() == 'items':
            storeHelp = """You can buy these items with Coins. Some items will immediately be used upon purchase. Buy items using `+buy itemName`."""
            embed.add_field(name='Store Help', value=storeHelp, inline=False)
            storeDesc = ''
            prevCost = 0

            for item in self.store['Items']:
                #same price, add to same line
                if item['price'] == prevCost:
                    storeDesc += ', ' + item['name']
                #different price, new line, update prevCost
                else:
                    storeDesc += '\n`' + str(item['price']) + ' coins:` ' + item['name']
                    prevCost = item['price']

            embed.add_field(name=self.emojis['Coin'] + ' Items', value=storeDesc, inline=False)
            #embed.set_thumbnail(url = 'https://vignette.wikia.nocookie.net/mariokart/images/a/aa/Golden_Mushroom_-_Mario_Kart_Wii.png/revision/latest?cb=20180115185605')
            embed.set_footer(text = 'Earn coins by participating in server events!  Use the "+help" command for more Bean commands.')
            await ctx.send(embed = embed)
            return
        #special
        elif type.lower() == 'evolvable' or type.lower() == 'e' or type.lower() == 'evolve':
            storeHelp = """Some Evolved Companions cannot be bought with coins. All Evolved Companions give a higher chance of more daily Coins."""
            embed.add_field(name='Store Help', value=storeHelp, inline=False)
            storeDesc = ''
            prevCost = 0

            for item in self.store['Evolvable Companions']:
                #same price, add to same line
                if item['price'] == prevCost:
                    storeDesc += ', ' + item['name']
                #different price, new line, update prevCost
                else:
                    storeDesc += '\n`' + str(item['price']) + ' coins:` ' + item['name']
                    prevCost = item['price']

            embed.add_field(name=self.emojis['Special'] + ' Evolvable Companions', value=storeDesc, inline=False)

            storeDesc_special = ''
            for item in self.store['Evolved Companions']:
                if storeDesc_special == '':
                    storeDesc_special = item['name']
                else:
                    storeDesc_special += ', ' + item['name']

            embed.add_field(name=self.emojis['Special'] + ' Evolved Companions', value=storeDesc_special, inline=False)

            embed.set_footer(text = 'Earn coins by participating in server events!  Use the "+help" command for more Bean commands.')
            await ctx.send(embed = embed)
            return
        #unknown type
        else:
            embed2 = discord.Embed(
                description = 'Correct Usage: `+store [coin/helped/item/evolvable]`',
                color = discord.Color.teal()
            )
            await ctx.send(embed = embed2)
            return

    @commands.command(aliases=['set', 'purchase'])
    async def buy(self, ctx, *, input):
        user = self.meta.getProfile(ctx.author)
        id = ctx.author.id

        coins = user['coins']
        helped = user['helped']
        getStoreItem = self.meta.getStoreItem(input)

        if getStoreItem == '':
            await ctx.send(embed = self.meta.embedOops())
            return

        json = getStoreItem['JSON']
        category = getStoreItem['type']

        if json['name'] in user['redeemed']:
            self.dbConnection.updateProfile({"id": id}, {"$set": {"companion": companion}})
            await ctx.send(embed = self.meta.embedDone())
            return

        def embedAfford():
            nonlocal helped
            nonlocal coins
            embed = discord.Embed(
                title = 'You can\'t seem to afford that.',
                description = 'You have:\t`' + str(helped) + '` Help Points ' + self.emojis['HelpPoint'] + '\t`' + str(coins) + '` Coins ' + self.emojis['Coin'],
                color = discord.Color.teal()
            )
            return embed

        if getStoreItem == '' or category == 'Evolved Companions':
            await ctx.send(embed = self.meta.embedOops())
            return
        else:
            #coin-based items
            if category == 'Coin Companions' or category == 'Items' or category == 'Evolvable Companions':
                #cannot afford
                if coins < json['price']:
                    await ctx.send(embed = embedAfford())
                    return
                #subtract coins
                coins -= json['price']
            elif category == 'Helped Companions':
                #not enough help points
                if helped < json['price']:
                    await ctx.send(embed = embedAfford())
                    return

            title = 'Consider it done! ✅'

            #all companions
            if 'Companions' in category:
                companion = json['name']

                if category == 'Helped Companions':
                    self.dbConnection.updateProfile({"id": id}, {"$set": {"companion": companion}})
                else:
                    #case: ditto
                    dittos = ['Squirtle', 'Charmander', 'Bulbasaur']
                    if companion in dittos:
                        if random.random() < .05:
                            companion = 'Ditto'
                            title = 'Consider it — Oh? **Ditto** was caught! 🌟'
                            self.meta.addBadgeToProfile(ctx.author, 'CaughtDitto')
                            self.meta.addToDex(ctx.author, companion)

                    self.dbConnection.updateProfile({"id": id}, {"$set": {"coins": coins, "companion": companion}})
            #items
            elif category == 'Items':
                item = json['name']
                #affinity booster
                if item == 'Affinity Booster':
                    booster = user['booster']
                    if booster < 3:
                        booster += 1
                        self.dbConnection.updateProfile({"id": id}, {"$set": {"coins": coins, "booster": booster}})
                        user = self.meta.getProfile(ctx.author)
                        title += '\nBooster Level: `' + str(booster-1) + '->' + str(booster) + '`'
                    else:
                        await ctx.send(embed = self.meta.embedOops())
                        return
                #affinity swap
                elif item == 'Affinity Swap':
                    if user['affinity'] == '':
                        embed_oops = discord.Embed(
                            title = 'Sorry, you haven\'t set an affinity yet! You can do that by using `+affinity fire/water/air/earth`.',
                            color = discord.Color.teal()
                        )
                        await channel.send(embed = embed_oops)
                        return

                    embed = discord.Embed(
                        title = 'Swap to which affinity?',
                        description = '🌱 - Earth\n🎐 - Air\n🔥 - Fire\n💧 - Water\n⛔ - Cancel',
                        color = discord.Color.teal()
                    )
                    embed.set_footer(text='You\'ll lose your booster if you have one by changing affinities.')
                    msg = await ctx.send(embed = embed)
                    await msg.add_reaction('🌱')
                    await msg.add_reaction('🎐')
                    await msg.add_reaction('🔥')
                    await msg.add_reaction('💧')
                    await msg.add_reaction('⛔')

                    emoji = ''

                    def check(reaction, user):
                        nonlocal emoji
                        emoji = str(reaction.emoji)
                        return user == ctx.author and (str(reaction.emoji) == '🌱' or str(reaction.emoji) == '🎐' or str(reaction.emoji) == '🔥' or str(reaction.emoji) == '💧' or str(reaction.emoji) == '⛔')

                    try:
                        reaction, user = await self.client.wait_for('reaction_add', timeout=60.0, check=check)
                    except asyncio.TimeoutError:
                        await channel.send('Affinity Swap timed out.')
                    else:
                        if emoji == '⛔':
                            embed = discord.Embed(
                                title = 'Affinity Swap canceled.',
                                color = discord.Color.teal()
                            )
                            await ctx.send(embed = embed)
                            return

                        aff = ''
                        if emoji == '🌱':
                            aff = 'Earth'
                        elif emoji == '🎐':
                            aff = 'Air'
                        elif emoji == '🔥':
                            aff = 'Fire'
                        elif emoji == '💧':
                            aff = 'Water'

                        self.dbConnection.updateProfile({"id": id}, {"$set": {"coins": coins}})
                        self.meta.changeAffinity(ctx.author, aff)

                        title += '\nYour affinity is now `' + aff + '`.'
                #evolution stone
                elif item == 'Evolution Stone':
                    companion = user['companion']
                    companion_getStoreItem = self.meta.getStoreItem(companion)
                    companion_json = companion_getStoreItem['JSON']
                    companion_category = companion_getStoreItem['type']
                    evolve = companion_json['evolve']
                    #no evolution form
                    if len(evolve) == 0:
                        await ctx.send(embed = self.meta.embedOops())
                        return
                    else:
                        result = random.choice(evolve)
                        self.meta.addToDex(ctx.author, result)
                        self.dbConnection.updateProfile({"id": id}, {"$set": {"coins": coins, "companion": result}})
                        title += '\nYour companion is now a `' + result + '`!'
                        if companion == 'Eevee':
                            if self.meta.hasAllEvolutionsOf(ctx.author, 'Eevee'):
                                title += '\nAnd with this, you got all Eeveelutions! Here, take this badge: ' + self.meta.getBadge('EeveeLover')
                                self.meta.addBadgeToProfile(ctx.author, 'EeveeLover')

                #coin gift
                elif item == 'Coin Gift':
                    gifts = user['gifts']
                    gifts += 1
                    self.dbConnection.updateProfile({"id": id}, {"$set": {"coins": coins, "gifts": gifts}})
                #heckinrich badge
                elif item == 'HeckinRich Badge':
                    if self.meta.hasBadge(ctx.author, 'HeckinRich'):
                        await ctx.send(embed = self.meta.embedOops())
                        return
                    else:
                        self.meta.addBadgeToProfile(ctx.author, 'HeckinRich')
                        self.dbConnection.updateProfile({"id": id}, {"$set": {"coins": coins}})
                #squad swap
                elif item == 'Squad Swap':
                    embed = discord.Embed(
                        title = 'Swap to where?',
                        description = '🔰 - Swap to other Squad\n⚠ - Leave Squad\n⛔ - Cancel',
                        color = discord.Color.teal()
                    )
                    msg = await ctx.send(embed = embed)
                    await msg.add_reaction('🔰')
                    await msg.add_reaction('⚠')
                    await msg.add_reaction('⛔')

                    emoji = ''

                    def check(reaction, user2):
                        nonlocal emoji
                        emoji = str(reaction.emoji)
                        return user2 == ctx.author and (str(reaction.emoji) == '🔰' or str(reaction.emoji) == '⚠' or str(reaction.emoji) == '⛔')

                    try:
                        reaction, user2 = await self.client.wait_for('reaction_add', timeout=60.0, check=check)
                    except asyncio.TimeoutError:
                        await channel.send('Squad Swap timed out.')
                    else:
                        if emoji == '⛔':
                            embed = discord.Embed(
                                title = 'Squad Swap canceled.',
                                color = discord.Color.teal()
                            )
                            await ctx.send(embed = embed)
                            return

                        guild = ctx.guild
                        tea_role = guild.get_role(self.ids['SQUAD_TEA_ROLE'])
                        coffee_role = guild.get_role(self.ids['SQUAD_COFFEE_ROLE'])

                        if emoji == '⚠':
                            self.dbConnection.updateProfile({"id": id}, {"$set": {"squad": ''}})
                            await ctx.author.remove_roles(coffee_role, tea_role)
                            title += '\nYou\'ve left your Squad.'
                        elif emoji == '🔰':
                            if user['squad'] == 'Coffee':
                                self.dbConnection.updateProfile({"id": id}, {"$set": {"coins": coins, "squad": 'Tea'}})
                                await ctx.author.add_roles(tea_role)
                                await ctx.author.remove_roles(coffee_role)
                                await guild.get_channel(self.ids['SQUAD_TEA_CHANNEL']).send(self.meta.msgWelcomeSquad(ctx.author))
                            else:
                                self.dbConnection.updateProfile({"id": id}, {"$set": {"coins": coins, "squad": 'Coffee'}})
                                await ctx.author.add_roles(coffee_role)
                                await ctx.author.remove_roles(tea_role)
                                await guild.get_channel(self.ids['SQUAD_COFFEE_CHANNEL']).send(self.meta.msgWelcomeSquad(ctx.author))
                else:
                    await ctx.send(embed = self.meta.embedOops())
                    return
            else:
                await ctx.send(embed = self.meta.embedOops())
                return
            #send embed
            embed = discord.Embed(
                title = title,
                color = discord.Color.teal()
            )
            await ctx.send(embed = embed)
            return

    #members can gift coin companions or lotto tickets
    @commands.command(aliases=['give'])
    async def gift(self, ctx, member: discord.Member, *, item = 'gift'):
        if ctx.author == member:
            embed = discord.Embed(
                title = 'You can\'t gift yourself!',
                color = discord.Color.teal()
            )
            await ctx.send(embed = embed)
            return

        user = self.meta.getProfile(ctx.author)

        if member.bot and member.id != 592436047175221259:
            embed = discord.Embed(
                title = 'You can\'t gift a bot that\'s not me!',
                color = discord.Color.teal()
            )
            await ctx.send(embed = embed)
            return

        member_discord = member
        member = self.meta.getProfile(member)
        item = item.lower()
        coins = user['coins']
        badges = user['badges']

        if item == 'gift' or item == 'coin gift' or item == 'coins' or item == 'coingift':
            if user['gifts'] > 0:
                gifts = user['gifts'] - 1
                id = ctx.author.id
                self.dbConnection.updateProfile({"id": id}, {"$set": {"gifts": gifts}})

                elements = [50, 75, 100]
                weights = [0.25, 0.5, 0.25]
                amt = choice(elements, p=weights)

                giftee_coins = member['coins'] + int(amt)
                self.dbConnection.updateProfile({"id": member_discord.id}, {"$set": {"coins": giftee_coins}})

                #bean
                if member_discord.id == 592436047175221259:
                    if random.random() < .05 and 'GiftedByBean' not in badges:
                        embed = discord.Embed(
                            title = 'Wow, thanks so much! Here, take a gift: ' + self.dbConnection.findBadge({'id':'GiftedByBean'})['literal'],
                            color = discord.Color.teal()
                        )
                        await ctx.send(embed = embed)
                        badges.append('GiftedByBean')
                        self.dbConnection.updateProfile({"id": id}, {"$set": {"badges": badges}})
                        return
                    else:
                        embed = discord.Embed(
                            title = 'Oh, thanks! I appreciate it!',
                            color = discord.Color.teal()
                        )
                        await ctx.send(embed = embed)
                        return
                else:
                    embed = discord.Embed(
                        title = 'Gifted! ' + self.emojis['Gift'],
                        description = '<@' + str(member_discord.id) + '> is now `' + str(amt) + '` coins richer!',
                        color = discord.Color.teal()
                    )
                    await ctx.send(embed = embed)
            else:
                embed = discord.Embed(
                    title = 'You haven\'t bought any gifts from the Item Store yet!',
                    description = 'Buy one using `+buy coin gift`.',
                    color = discord.Color.teal()
                )
                await ctx.send(embed = embed)
        else:
            isFound = False
            c = ''
            for comp in self.store['Coin Companions']:
                if comp['name'].lower() == item:
                    isFound = True
                    c = comp

            if not isFound:
                for comp in self.store['Evolvable Companions']:
                    if comp['name'].lower() == item:
                        isFound = True
                        c = comp

            if not isFound:
                embed = discord.Embed(
                    title = 'I couldn\'t seem to find that companion or item.',
                    color = discord.Color.teal()
                )
                await ctx.send(embed = embed)
                return

            price = int(c['price'])
            if coins - price < 0:
                embed = discord.Embed(
                    title = 'You can\'t seem to afford that item.',
                    color = discord.Color.teal()
                )
                await ctx.send(embed = embed)
                return

            coins = coins - price
            embed = discord.Embed(
                title = 'Gift Confirmation',
                description = 'Buy `' + c['name'] + '` for <@' + str(member_discord.id) + '>?\nReact to this message with a ✅ for yes, ⛔ for no.\nYou have 60 seconds to decide!',
                color = discord.Color.teal()
            )
            msg = await ctx.send(embed = embed)
            await msg.add_reaction('✅')
            await msg.add_reaction('⛔')

            emoji = ''
            def check(reaction, user2):
                nonlocal emoji
                emoji = str(reaction.emoji)
                return user2 == ctx.author and (str(reaction.emoji) == '✅' or str(reaction.emoji) == '⛔')

            try:
                reaction, user2 = await self.client.wait_for('reaction_add', timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await channel.send('Timed out.')
            else:
                if emoji == '⛔':
                    embed = discord.Embed(
                        title = 'Gift canceled.',
                        color = discord.Color.teal()
                    )
                    await ctx.send(embed = embed)
                    return
                embed = discord.Embed(
                    title = 'Accept Gift?',
                    description = '<@' + str(member_discord.id) + '>, would you like `' + c['name'] + '` to be your new Companion?\nReact to this message with a ✅ for yes, ⛔ for no.\nYou have 60 seconds to decide!',
                    color = discord.Color.teal()
                )
                msg = await ctx.send(embed = embed)
                await msg.add_reaction('✅')
                await msg.add_reaction('⛔')

                emoji = ''

                def check(reaction, user3):
                    nonlocal emoji
                    emoji = str(reaction.emoji)
                    return user3 == member_discord and (str(reaction.emoji) == '✅' or str(reaction.emoji) == '⛔')

                try:
                    reaction, user3 = await self.client.wait_for('reaction_add', timeout=60.0, check=check)
                except asyncio.TimeoutError:
                    await channel.send('Timed out.')
                else:
                    if emoji == '⛔':
                        embed = discord.Embed(
                            title = 'Gift canceled.',
                            color = discord.Color.teal()
                        )
                        await ctx.send(embed = embed)
                        return

                    self.dbConnection.updateProfile({"id": member_discord.id}, {"$set": {"companion": c['name']}})
                    self.dbConnection.updateProfile({"id": ctx.author.id}, {"$set": {"coins": coins}})

                    embed = discord.Embed(
                        title = ctx.author.name + ' gifted ' + member_discord.name + ' `' + c['name'] + '`! ' + self.emojis['Gift'],
                        color = discord.Color.teal()
                    )
                    await ctx.send(embed = embed)
                    return

def setup(client):
    database_connection = Database()
    meta_class = Meta(database_connection)
    client.add_cog(Store(client, database_connection, meta_class))
