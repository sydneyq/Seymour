    #rules, rules, rules
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if isinstance(message.channel, discord.DMChannel):
            return

        if random.random() < .1:
            past_timestamp = self.dbConnection.findMeta({'id':'server'})['event']
            if past_timestamp == '' or self.meta.hasBeenMinutes(20, past_timestamp, self.meta.getDateTime()):
                self.dbConnection.updateMeta({'id':'server'}, {'$set': {'event': self.meta.getDateTime()}})
                channels = [257751892241809408, 599757443362193408]

                #channel_id = 593153723610693632 #cmd
                channel_id = random.choice(channels)
                channel = message.guild.get_channel(channel_id)

                num = random.randint(1, len(self.rules))
                rule = self.rules[num]

                title = 'Rules, Rules, Rules!'
                desc = 'Be the first to say the corresponding rule number to earn coins!'
                e = self.meta.embed(title, desc, 'gold')
                n = 'What `rule number` does this rule title or desciption belong to?'
                v = random.choice([rule['TITLE'], rule['DESC']])
                v = f'`{v}`'
                e.add_field(name=n, value=v)
                e.set_footer(text='Expires in 20 seconds.')
                await channel.send(embed = e)

                def check(m):
                    return m.content.lower() == str(num) and m.channel == channel

                try:
                    msg = await self.client.wait_for('message', timeout=20.0, check=check)
                except asyncio.TimeoutError:
                    await channel.send(embed = self.meta.embed('Expired','20 seconds have passed!'))
                    return
                else:
                    amt = 25
                    user = self.meta.getProfile(msg.author)

                    coins = user['coins'] + amt
                    self.dbConnection.updateProfile({"id": msg.author.id}, {"$set": {"coins": coins}})

                    embed2 = discord.Embed(
                        title = msg.author.name + ', you\'ve just earned `' + str(amt) + '` coins!',
                        description = 'Your total: `' + str(coins) + '` coins',
                        color = discord.Color.teal()
                    )

                    await channel.send(embed = embed2)
                    return
            return

    @commands.command(aliases=['pts', 'points'])
    async def listeners(self, ctx):
        tea_num = 0
        tea_names = ''
        coffee_num = 0
        coffee_names = ''

        tea = self.getNum(ctx, 'Tea')
        tea_num = tea['num']
        tea_names = tea['names']

        coffee = self.getNum(ctx, 'Coffee')
        coffee_num = coffee['num']
        coffee_names = coffee['names']

        embed2 = discord.Embed(
            title = 'Squad Listeners',
            color = discord.Color.teal()
        )

        embed2.add_field(name=self.emojis['Tea'] + ' Tea Squad `('+str(tea_num)+')`',value=tea_names)
        embed2.add_field(name=self.emojis['Coffee'] + ' Coffee Squad `('+str(coffee_num)+')`',value=coffee_names)

        if tea_num > coffee_num:
            embed2.set_thumbnail(url = 'https://cdn.discordapp.com/attachments/591611902459641856/613918428293627914/teamteaBean.png')
        elif coffee_num > tea_num:
            embed2.set_thumbnail(url = 'https://cdn.discordapp.com/attachments/591611902459641856/613918442034298890/teamcoffeeBean.png')

        await ctx.send(embed = embed2)

    #unscramble
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if random.random() < .1:
            past_timestamp = self.dbConnection.findMeta({'id':'server'})['event']
            if past_timestamp == '' or self.meta.hasBeenMinutes(3, past_timestamp, self.meta.getDateTime()):
                self.dbConnection.updateMeta({'id':'server'}, {'$set': {'event': self.meta.getDateTime()}})
                #event_channel = 593153723610693632 #cmd
                event_channel = 623746736677978133
                channel = message.guild.get_channel(event_channel)

                words = ['figurative',
                'winter',
                'replacement',
                'mountain',
                'wondrous',
                'training',
                'pouring',
                'tailgate',
                'expressive',
                'frightened',
                'laughable',
                'updated',
                'frying',
                'lioness',
                'australia',
                'headphones',
                'flipper',
                'thousand',
                'swirl',
                'megabyte',
                'spiritual',
                'golfing',
                'specified',
                'journalism',
                'environmental',
                'network',
                'language',
                'koala',
                'memorization',
                'sunken',
                'airplane',
                'malibu',
                'identical',
                'temperate',
                'challenger',
                'complicated',
                'spelling',
                'painter',
                'universal',
                'director',
                'trance',
                'telekinesis',
                'index',
                'attempt',
                'rainforest',
                'conductor',
                'electric',
                'wellfare',
                'greeting',
                'acrylic',
                'bandage',
                'skies',
                'autumn',
                'imagine',
                'construction']

                word = random.choice(words).lower()

                def scramble(string):
                    str = string
                    scrambled = ''

                    while len(str) > 0:
                        ch = random.randrange(len(str))
                        ch = str[ch]
                        scrambled += ch
                        str = str.replace(ch, '', 1)

                    return scrambled

                embed = discord.Embed(
                    title = 'Game On: Unscramble!',
                    color = discord.Color.teal()
                )

                scrambled = scramble(word)

                embed.add_field(name=scrambled,
                value='Unscramble the word above and say it first to win a point for your Squad!')
                embed.set_footer(text='Expires in 3 minutes.')
                await channel.send(embed = embed, delete_after=180)

                def check(m):
                    return m.content.lower() == word and m.channel == channel

                cont = True
                while (cont):
                    try:
                        msg = await self.client.wait_for('message', timeout=180.0, check=check)
                    except asyncio.TimeoutError:
                        return
                    else:
                        user = self.meta.getProfile(msg.author)
                        squad = user['squad']

                        if squad == '':
                            embed2 = discord.Embed(
                                title = msg.author.name + ', you\'re not in a Squad yet!',
                                color = discord.Color.teal()
                            )
                            await channel.send(embed = embed2, delete_after=60)
                            continue
                        elif squad == 'Tea':
                            self.tea_score += 1
                        elif squad == 'Coffee':
                            self.coffee_score += 1

                        embed = discord.Embed(
                            title = msg.author.name + ' just earned `1` point for ' + squad + '!',
                            description = '**Tea Squad:** `' + str(self.tea_score) + '`\n**Coffee Squad:** `' + str(self.coffee_score) + '`',
                            color = discord.Color.teal()
                        )

                        await channel.send(embed = embed)
                        cont = False
                        return
            return

    #influencer w temp staff squads
    @commands.command(aliases=['influence', 'justsayit', 'repeatafterme'])
    async def influencer(self, ctx, influencer_channel: discord.TextChannel):
        if not self.meta.isBotOwner(ctx.author):
            return

        #tea_words = ['leaf', 'teapot']
        #coffee_words = ['latte', 'creamer']

        tea_words = ['crash', #1
        '', #2
        'finally', #3
        'glee', #4
        'world', #5
        'dino', #6
        'under', #7
        'realize', #8
        'eyes', #9
        'design', #10
        'talk', #11
        'thor', #12
        'hire', #13
        'mind', #14
        'prince']
        coffee_words = ['print', #1
        '', #2
        'march', #3
        'yesterday', #4
        'fix', #5
        'romance', #6
        'time', #7
        'netflix', #8
        'salad', #9
        'along', #10
        'invent', #11
        'watch', #12
        'forget', #13
        'pikachu', #14
        'website']

        guild = ctx.guild
        tea_index = 0
        coffee_index = 0
        tea_channel = guild.get_channel(self.ids['SQUAD_TEA_CHANNEL'])
        coffee_channel = guild.get_channel(self.ids['SQUAD_COFFEE_CHANNEL'])
        #tea_channel = guild.get_channel(self.ids['WORKSHOP_CHANNEL'])
        #coffee_channel = guild.get_channel(self.ids['WORKSHOP_CHANNEL'])
        tea_icon = 'https://cdn.discordapp.com/attachments/591611902459641856/613918428293627914/teamteaBean.png'
        coffee_icon = 'https://cdn.discordapp.com/attachments/591611902459641856/613918442034298890/teamcoffeeBean.png'

        def embedNext(squad, word):
            nonlocal tea_icon
            nonlocal coffee_icon

            url = tea_icon
            if squad == 'Coffee':
                url = coffee_icon

            embed = discord.Embed(
                title = 'Game On: Influencer!',
                description = 'Get the other team to say your word! Be careful, they\'ll be trying to get one of your members to say theirs!',
                color = discord.Color.teal()
            )
            embed.add_field(name='Your new word is: `' + word + '`', value='If the word is in another word or mixed capitals, it still counts!')
            embed.set_thumbnail(url = url)
            return embed

        def embedGotcha(squad, message, word):
            nonlocal tea_icon
            nonlocal coffee_icon

            url = tea_icon
            enemy_squad = 'Coffee'

            if squad == 'Coffee':
                url = coffee_icon
                enemy_squad = 'Tea'

            embed = discord.Embed(
                title = squad + ' got ' + message.author.name + ' from ' + enemy_squad + ' to say their word, `' + word + '`!',
                description = '+1 point to ' + squad + '!\n' + message.jump_url,
                color = discord.Color.teal()
            )
            embed.add_field(name='Current Points', value='Tea Squad: `' + str(self.tea_score) + '`\nCoffee Squad: `' + str(self.coffee_score) + '`')
            embed.set_thumbnail(url = url)
            return embed

        def embedWon(squad):
            nonlocal tea_icon
            nonlocal coffee_icon

            url = tea_icon
            enemy_squad = 'Coffee'

            if squad == 'Coffee':
                url = coffee_icon
                enemy_squad = 'Tea'

            embed = discord.Embed(
                title = squad + ' got ' + enemy_squad + ' to say all their words!',
                description = 'Congratulations to the ' + squad + ' Squad! ' + self.emojis['Trophy'],
                color = discord.Color.teal()
            )
            embed.set_thumbnail(url = url)
            return embed

        await tea_channel.send(embed = embedNext('Tea', tea_words[tea_index]))
        await coffee_channel.send(embed = embedNext('Coffee', coffee_words[coffee_index]))

        while (tea_index < len(tea_words) and coffee_index < len(coffee_words)):
            tea_trigger = False
            coffee_trigger = False

            def check(m):
                #tea got a coffee to say it?
                nonlocal tea_trigger
                tea_trigger = tea_words[tea_index] in m.content.lower()
                #coffee got a tea to say it?
                nonlocal coffee_trigger
                coffee_trigger = coffee_words[coffee_index] in m.content.lower()
                #check is in public channel
                return (tea_trigger or coffee_trigger) and m.channel.category_id == 363477215377358848

            msg = await self.client.wait_for('message', check=check)

            user = self.meta.getProfile(msg.author)
            squad = user['squad']

            if self.meta.isStaff(msg.author):
                squad = self.meta.getTempSquad(msg.author)

            if squad == '':
                continue
            if tea_trigger and squad == 'Coffee':
                self.tea_score += 1
                await msg.channel.send(embed = embedGotcha('Tea', msg, tea_words[tea_index]))
                await influencer_channel.send(embed = embedGotcha('Tea', msg, tea_words[tea_index]))
                tea_index += 1
                if tea_index >= len(tea_words):
                    await influencer_channel.send(embed = embedWon('Tea'))
                await tea_channel.send(embed = embedNext('Tea', tea_words[tea_index]))
                continue
            elif coffee_trigger and squad == 'Tea':
                self.coffee_score += 1
                await msg.channel.send(embed = embedGotcha('Coffee', msg, coffee_words[coffee_index]))
                await influencer_channel.send(embed = embedGotcha('Coffee', msg, coffee_words[coffee_index]))
                coffee_index += 1
                if coffee_index >= len(coffee_words):
                    await influencer_channel.send(embed = embedWon('Coffee'))
                    return
                await coffee_channel.send(embed = embedNext('Coffee', coffee_words[coffee_index]))
                continue
            else:
                continue

    #original influencer
    @commands.command(aliases=['influence', 'justsayit', 'repeatafterme'])
    async def influencer(self, ctx):
        if not self.meta.isAdmin(ctx.author):
            return

        #tea_words = ['leaf', 'teapot']
        #coffee_words = ['latte', 'creamer']

        tea_words = ['bear', #1
        'snow', #2
        'finally', #3
        'glee', #4
        'world', #5
        'yesterday', #6
        'under', #7
        'realize', #8
        'eyes', #9
        'design', #10
        'talk', #11
        'thor', #12
        'hire', #13
        'mind', #14
        'prince']
        coffee_words = ['drop', #1
        'hero', #2
        'march', #3
        'dino', #4
        'fix', #5
        'valentine', #6
        'time', #7
        'netflix', #8
        'salad', #9
        'along', #10
        'invent', #11
        'watch', #12
        'forget', #13
        'pikachu', #14
        'website']

        guild = ctx.guild
        tea_index = 0
        coffee_index = 0
        influencer_channel = guild.get_channel(622465906152570880)
        tea_channel = guild.get_channel(self.ids['SQUAD_TEA_CHANNEL'])
        coffee_channel = guild.get_channel(self.ids['SQUAD_COFFEE_CHANNEL'])
        #tea_channel = guild.get_channel(self.ids['WORKSHOP_CHANNEL'])
        #coffee_channel = guild.get_channel(self.ids['WORKSHOP_CHANNEL'])
        tea_icon = 'https://cdn.discordapp.com/attachments/591611902459641856/613918428293627914/teamteaBean.png'
        coffee_icon = 'https://cdn.discordapp.com/attachments/591611902459641856/613918442034298890/teamcoffeeBean.png'

        def embedNext(squad, word):
            nonlocal tea_icon
            nonlocal coffee_icon

            url = tea_icon
            if squad == 'Coffee':
                url = coffee_icon

            embed = discord.Embed(
                title = 'Game On: Influencer!',
                description = 'Get the other team to say your word! Be careful, they\'ll be trying to get one of your members to say theirs!',
                color = discord.Color.teal()
            )
            embed.add_field(name='Your new word is: `' + word + '`', value='If the word is in another word or mixed capitals, it still counts!')
            embed.set_thumbnail(url = url)
            return embed
        '''
        def embedPoint(squad):
            nonlocal tea_icon
            nonlocal coffee_icon

            url = tea_icon
            enemy_squad = 'Coffee'

            if squad == 'Coffee':
                url = coffee_icon
                enemy_squad = 'Tea'

            embed = discord.Embed(
                title = 'Point!',
                description = '+1 point to ' + squad + '!\n' + message.jump_url,
                color = discord.Color.teal()
            )
            embed.add_field(name='Current Points', value='Tea Squad: `' + str(self.tea_score) + '`\nCoffee Squad: `' + str(self.coffee_score) + '`')
            embed.set_thumbnail(url = url)
            return embed
            '''

        def embedGotcha(squad, message, word):
            nonlocal tea_icon
            nonlocal coffee_icon

            url = tea_icon
            enemy_squad = 'Coffee'

            if squad == 'Coffee':
                url = coffee_icon
                enemy_squad = 'Tea'

            embed = discord.Embed(
                title = squad + ' got ' + message.author.name + ' from ' + enemy_squad + ' to say their word, `' + word + '`!',
                description = '+1 point to ' + squad + '!\n' + message.jump_url,
                color = discord.Color.teal()
            )
            embed.add_field(name='Current Points', value='Tea Squad: `' + str(self.tea_score) + '`\nCoffee Squad: `' + str(self.coffee_score) + '`')
            embed.set_thumbnail(url = url)
            return embed

        def embedWon(squad):
            nonlocal tea_icon
            nonlocal coffee_icon

            url = tea_icon
            enemy_squad = 'Coffee'

            if squad == 'Coffee':
                url = coffee_icon
                enemy_squad = 'Tea'

            embed = discord.Embed(
                title = squad + ' got ' + enemy_squad + ' to say all their words!',
                description = 'Congratulations to the ' + squad + ' Squad! ' + self.emojis['Trophy'],
                color = discord.Color.teal()
            )
            embed.set_thumbnail(url = url)
            return embed

        await tea_channel.send(embed = embedNext('Tea', tea_words[tea_index]))
        await coffee_channel.send(embed = embedNext('Coffee', coffee_words[coffee_index]))

        while (tea_index < len(tea_words) and coffee_index < len(coffee_words)):
            tea_trigger = False
            coffee_trigger = False

            def check(m):
                #tea got a coffee to say it?
                nonlocal tea_trigger
                tea_trigger = tea_words[tea_index] in m.content.lower()
                #coffee got a tea to say it?
                nonlocal coffee_trigger
                coffee_trigger = coffee_words[coffee_index] in m.content.lower()
                #check is in public channel
                return (tea_trigger or coffee_trigger) and m.channel.category_id == 363477215377358848

            msg = await self.client.wait_for('message', check=check)

            user = self.meta.getProfile(msg.author)
            squad = user['squad']
            if squad == '':
                continue
            if tea_trigger and squad == 'Coffee':
                self.tea_score += 1
                await msg.channel.send(embed = embedGotcha('Tea', msg, tea_words[tea_index]))
                await influencer_channel.send(embed = embedGotcha('Tea', msg, tea_words[tea_index]))
                tea_index += 1
                if tea_index >= len(tea_words):
                    await influencer_channel.send(embed = embedWon('Tea'))
                await tea_channel.send(embed = embedNext('Tea', tea_words[tea_index]))
                continue
            elif coffee_trigger and squad == 'Tea':
                self.coffee_score += 1
                await msg.channel.send(embed = embedGotcha('Coffee', msg, coffee_words[coffee_index]))
                await influencer_channel.send(embed = embedGotcha('Coffee', msg, coffee_words[coffee_index]))
                coffee_index += 1
                if coffee_index >= len(coffee_words):
                    await influencer_channel.send(embed = embedWon('Coffee'))
                    return
                await coffee_channel.send(embed = embedNext('Coffee', coffee_words[coffee_index]))
                continue
            else:
                continue

    '''
    #on-message avatar
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if isinstance(message.channel, discord.DMChannel):
            return

        if random.random() < .1:
            past_timestamp = self.dbConnection.findMeta({'id':'server'})['event']
            if past_timestamp == '' or self.meta.hasBeenMinutes(10, past_timestamp, self.meta.getDateTime()):
                self.dbConnection.updateMeta({'id':'server'}, {'$set': {'event': self.meta.getDateTime()}})
                channels = [257751892241809408, 599757443362193408, 595384066618949692]
                channel = message.guild.get_channel(random.choice(channels))

                embed = discord.Embed(
                    title = 'Game On: Avatar!',
                    description = 'Bean is the Avatar and needs teachers from each element!',
                    color = discord.Color.teal()
                )

                choices = ['Water', 'Air', 'Fire', 'Earth']
                result = random.choice(choices)
                pic = ''

                if result == 'Water':
                    pic = 'http://dpegb9ebondhq.cloudfront.net/product_photos/15204550/water-01_large.jpg'
                elif result == 'Air':
                    pic = 'https://d3u67r7pp2lrq5.cloudfront.net/product_photos/15204511/air-01_original.jpg'
                elif result == 'Fire':
                    pic = 'https://dzasv7x7a867v.cloudfront.net/product_photos/15204544/Fire-01_original.jpg'
                elif result == 'Earth':
                    pic = 'http://d3u67r7pp2lrq5.cloudfront.net/product_photos/15204526/earth-01_400w.jpg'

                embed.add_field(name='Affinity: ' + result, value='Get someone from your Squad with the correct Affinity to post the 💥 emoji before the other Squad to gain a point!')
                embed.set_thumbnail(url = pic)
                await channel.send(embed = embed)

                def check(m):
                    return '💥' in m.content.lower() and m.channel == channel

                cont = True
                while (cont):
                    msg = await self.client.wait_for('message', check=check)
                    user = self.meta.getProfile(msg.author)
                    squad = user['squad']
                    affinity = user['affinity']

                    if squad == '' or squad == 'Squadless' or squad == 'Admin':
                        await channel.send(embed = self.meta.embedOops('You don\'t have an elligible Squad!'))
                        continue
                    elif affinity is None or affinity == '' or affinity != result:
                        await channel.send(embed = self.meta.embedOops('You don\'t have the right Affinity!'))
                        continue
                    else:
                        cont = False

                        #staff temp squads
                        if self.meta.isStaff(msg.author):
                            temp_squads = self.dbConnection.findMeta({'id':'temp_squads'})
                            if msg.author.id in temp_squads['Tea']:
                                squad = 'Tea'
                            else:
                                squad = 'Coffee'

                        if squad == 'Tea':
                            self.tea_score += 1
                        else:
                            self.coffee_score += 1

                        embed2 = discord.Embed(
                            title = msg.author.name + ' just earned `1` point for ' + squad + '!',
                            description = '**Tea Squad:** `' + str(self.tea_score) + '`\n**Coffee Squad:** `' + str(self.coffee_score) + '`',
                            color = discord.Color.teal()
                        )

                        if self.tea_score > self.coffee_score:
                            embed2.set_thumbnail(url = 'https://cdn.discordapp.com/attachments/591611902459641856/613918428293627914/teamteaBean.png')
                        elif self.coffee_score > self.tea_score:
                            embed2.set_thumbnail(url = 'https://cdn.discordapp.com/attachments/591611902459641856/613918442034298890/teamcoffeeBean.png')


                        await channel.send(embed = embed2)

                        return

    @commands.command()
    async def avatar(self, ctx, channel: discord.TextChannel = None):
        message = ctx.message
        if not self.meta.isAdmin(message.author):
            return

        if channel is None:
            channel = ctx.channel

        await ctx.message.delete()

        embed = discord.Embed(
            title = 'Game On: Avatar!',
            description = 'Bean is the Avatar and needs teachers from each element!',
            color = discord.Color.teal()
        )

        choices = ['Water', 'Air', 'Fire', 'Earth']
        result = random.choice(choices)
        pic = ''

        if result == 'Water':
            pic = 'http://dpegb9ebondhq.cloudfront.net/product_photos/15204550/water-01_large.jpg'
        elif result == 'Air':
            pic = 'https://d3u67r7pp2lrq5.cloudfront.net/product_photos/15204511/air-01_original.jpg'
        elif result == 'Fire':
            pic = 'https://dzasv7x7a867v.cloudfront.net/product_photos/15204544/Fire-01_original.jpg'
        elif result == 'Earth':
            pic = 'http://d3u67r7pp2lrq5.cloudfront.net/product_photos/15204526/earth-01_400w.jpg'

        embed.add_field(name='Affinity: ' + result, value='Get someone from your Squad with the correct Affinity to post the 💥 emoji before the other Squad to gain a point!')
        embed.set_thumbnail(url = pic)
        await channel.send(embed = embed)

        def check(m):
            return m.content.lower() == '💥' and m.channel == channel

        cont = True

        while (cont):
            msg = await self.client.wait_for('message', check=check)

            user = self.meta.getProfile(msg.author)

            if user['squad'] == '':
                embed = discord.Embed(
                    title = 'Sorry, you\'re not in a Squad yet! Join one by using `+squad tea/coffee`.',
                    color = discord.Color.teal()
                )
                await channel.send(embed = embed)
                cont = True
                continue
            elif user['affinity'] is None or user['affinity'] == '':
                embed = discord.Embed(
                    title = 'Sorry, you haven\'t set an affinity yet! You can do that by using `+affinity fire/water/air/earth`.',
                    color = discord.Color.teal()
                )
                await channel.send(embed = embed)
                cont = True
                continue
            elif user['affinity'] != result:
                embed = discord.Embed(
                    title = 'You don\'t have the required affinity! You\'re looking for someone who\'s `' + result + '`.',
                    color = discord.Color.teal()
                )
                await channel.send(embed = embed)
                cont = True
                continue
            elif user['affinity'] == result:
                cont = False

                squad = user['squad']
                if squad == 'Tea':
                    self.tea_score += 1
                else:
                    self.coffee_score += 1

                embed2 = discord.Embed(
                    title = msg.author.name + ' just earned `1` point for ' + squad + '!',
                    description = '**Tea Squad:** `' + str(self.tea_score) + '`\n**Coffee Squad:** `' + str(self.coffee_score) + '`',
                    color = discord.Color.teal()
                )

                if self.tea_score > self.coffee_score:
                    embed2.set_thumbnail(url = 'https://cdn.discordapp.com/attachments/591611902459641856/613918428293627914/teamteaBean.png')
                elif self.coffee_score > self.tea_score:
                    embed2.set_thumbnail(url = 'https://cdn.discordapp.com/attachments/591611902459641856/613918442034298890/teamcoffeeBean.png')


                await channel.send(embed = embed2)

                return
    '''
    '''
    @commands.command(aliases=['traffic', 'trafficlight', 'rlgl'])
    async def redlightgreenlight(self, ctx, channel: discord.TextChannel = None):
        message = ctx.message
        if not self.meta.isAdmin(message.author):
            return

        if channel is None:
            channel = ctx.channel

        await ctx.message.delete()

        which = ['pic', 'text']
        ref = random.choice(which)
        desc = 'Look at the text, not the picture!'

        if ref == 'pic':
            desc = 'Look at the picture, not the text!'

        embed = discord.Embed(
            title = 'Game On: Red Light, Green Light!',
            description = desc,
            color = discord.Color.teal()
        )

        elements = ['Red', 'Green', 'Yellow']
        weights = [0.45, 0.45, 0.10]
        text = choice(elements, p=weights)

        color_pics = ['https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/Disc_Plain_red.svg/2000px-Disc_Plain_red.svg.png',
        'https://upload.wikimedia.org/wikipedia/commons/thumb/f/ff/Green_icon.svg/1024px-Green_icon.svg.png',
        'https://upload.wikimedia.org/wikipedia/en/thumb/f/fb/Yellow_icon.svg/1024px-Yellow_icon.svg.png']
        pic = choice(elements, p=weights)

        embed.add_field(name='Light: ' + text, value='Say `go` if the Light is Green, `stop` if the Light is Red, or `slow` if the Light is Yellow before the other Squad!\nWrong answers deduct points from your Squad. Getting a Yellow Light correct deducts from the other Squad!')

        url = color_pics[0]
        if pic == 'Green':
            url = color_pics[1]
        elif pic == 'Yellow':
            url = color_pics[2]

        embed.set_thumbnail(url = url)
        await channel.send(embed = embed)
        input = ''

        def check(m):
            nonlocal input
            input = m.content.lower()
            return (m.content.lower() == 'stop' or m.content.lower() == 'go' or m.content.lower() == 'slow') and m.channel == channel

        cont = True

        while (cont):
            msg = await self.client.wait_for('message', check=check)

            user = self.meta.getProfile(msg.author)

            if user['squad'] == '':
                embed = discord.Embed(
                    title = 'Sorry, you\'re not in a Squad yet! Join one by using `+squad tea/coffee`.',
                    color = discord.Color.teal()
                )
                await channel.send(embed = embed)
                cont = True
                continue
            else:
                cont = False
                correct = False
                answer = text

                if ref == 'pic':
                    answer = pic

                if answer == 'Red':
                    if input == 'stop':
                        correct = True
                elif answer == 'Green':
                    if input == 'go':
                        correct = True
                elif answer == 'Yellow':
                    if input == 'slow':
                        correct = True

                squad = user['squad']

                if correct:
                    if answer == 'Yellow':
                        opposquad = 'Tea'
                        if squad == 'Tea':
                            opposquad = 'Coffee'
                            self.coffee_score -= 10
                        else:
                            self.tea_score -= 10
                        embed2 = discord.Embed(
                            title = msg.author.name + ' just deducted `10` points from ' + opposquad + '!',
                            description = '**Tea Squad:** `' + str(self.tea_score) + '`\n**Coffee Squad:** `' + str(self.coffee_score) + '`',
                            color = discord.Color.teal()
                        )
                    else:
                        if squad == 'Tea':
                            self.tea_score += 5
                        else:
                            self.coffee_score += 5
                        embed2 = discord.Embed(
                            title = msg.author.name + ' just earned `5` points for ' + squad + '!',
                            description = '**Tea Squad:** `' + str(self.tea_score) + '`\n**Coffee Squad:** `' + str(self.coffee_score) + '`',
                            color = discord.Color.teal()
                        )
                else:
                    if squad == 'Tea':
                        self.tea_score -= 10
                    else:
                        self.coffee_score -= 10
                    embed2 = discord.Embed(
                        title = msg.author.name + ' just dropped ' + squad + '\'s score by `10` points!',
                        description = '**Tea Squad:** `' + str(self.tea_score) + '`\n**Coffee Squad:** `' + str(self.coffee_score) + '`',
                        color = discord.Color.teal()
                    )

                if self.tea_score > self.coffee_score:
                    embed2.set_thumbnail(url = 'https://cdn.discordapp.com/attachments/591611902459641856/613918428293627914/teamteaBean.png')
                elif self.coffee_score > self.tea_score:
                    embed2.set_thumbnail(url = 'https://cdn.discordapp.com/attachments/591611902459641856/613918442034298890/teamcoffeeBean.png')

                await channel.send(embed = embed2)

                return
    '''
    '''
    @commands.command(aliases=['pewpew', 'pewpewpew', 'teamwork', 'teambattle'])
    async def pew(self, ctx, channel: discord.TextChannel = None):
        message = ctx.message
        if not self.meta.isAdmin(message.author):
            return

        if channel is None:
            channel = ctx.channel

        await ctx.message.delete()

        embed = discord.Embed(
            title = 'Game On: Pewpew!',
            description = 'Get three people from your Squad to say \"pewpew\" first to gain a point!',
            color = discord.Color.teal()
        )

        await channel.send(embed = embed)

        isFull = False
        local_tea_score = 0
        local_coffee_score = 0

        tea_shooters = []
        coffee_shooters = []

        while not isFull:
            def check(m):
                return (m.content.lower() == 'pew pew' or m.content.lower() == 'pewpew') and m.channel == channel

            msg = await self.client.wait_for('message', check=check)

            user = self.dbConnection.findProfile({'id' : msg.author.id})
            if user is None:
                embed = discord.Embed(
                    title = 'Sorry, you don\'t have a profile yet! You can make one by using +profile.',
                    color = discord.Color.teal()
                )
                await channel.send(embed = embed)
                continue

            elif user['squad'] == '':
                embed = discord.Embed(
                    title = 'Sorry, you\'re not in a Squad yet! Join one by using `+squad tea/coffee`.',
                    color = discord.Color.teal()
                )
                await channel.send(embed = embed)
                continue

            squad = user['squad']

            if squad == 'Tea':
                if msg.author.id in tea_shooters:
                    embed = discord.Embed(
                        title = 'Sorry, you\'ve already shot in this round!',
                        color = discord.Color.teal()
                    )
                    await channel.send(embed = embed)
                    continue
                else:
                    tea_shooters.append(msg.author.id)

                local_tea_score += 1
            else:
                if msg.author.id in coffee_shooters:
                    embed = discord.Embed(
                        title = 'Sorry, you\'ve already shot in this round!',
                        color = discord.Color.teal()
                    )
                    await channel.send(embed = embed)
                    continue
                else:
                    coffee_shooters.append(msg.author.id)

                local_coffee_score += 1

            if local_tea_score == 3 or local_coffee_score == 3:
                isFull = True

            embed3 = discord.Embed(
                title = 'Current Attacks',
                color = discord.Color.teal()
            )

            tea_shooters_str = ''
            for shooter in tea_shooters:
                tea_shooters_str += '<@' + str(shooter) + '>\n'

            if tea_shooters_str == '':
                tea_shooters_str = 'N/A'

            embed3.add_field(name='Tea Shooters (' + str(len(tea_shooters)) + '/3)', value=tea_shooters_str)

            coffee_shooters_str = ''
            for shooter in coffee_shooters:
                coffee_shooters_str += '<@' + str(shooter) + '>\n'

            if coffee_shooters_str == '':
                coffee_shooters_str = 'N/A'

            embed3.add_field(name='Coffee Shooters (' + str(len(coffee_shooters)) + '/3)', value=coffee_shooters_str)

            await channel.send(embed = embed3)

        if local_tea_score == 3:
            self.tea_score += 1
        else:
            self.coffee_score += 1

        embed2 = discord.Embed(
            title = squad + ' Squad just earned `1` point!',
            description = '**Tea Squad:** `' + str(self.tea_score) + '`\n**Coffee Squad:** `' + str(self.coffee_score) + '`',
            color = discord.Color.teal()
        )

        await channel.send(embed = embed2)

        return
    '''

    #karaoke event
    '''
    @commands.Cog.listener()
    async def on_message(self, message):
        if not isinstance(message.channel, discord.TextChannel):
            return

        if ('karaoke' in message.channel.name):
            id = message.author.id
            if ('add me' in message.content.lower()):
                if id not in self.queue:
                    self.queue.append(id)
                    embed = discord.Embed(
                        title = 'Added you to the queue!',
                        color = discord.Color.teal()
                    )
                    await message.channel.send(embed = embed)
                else:
                    embed = discord.Embed(
                        title = 'You\'re already in the queue!',
                        color = discord.Color.teal()
                    )
                    await message.channel.send(embed = embed)
            elif ('remove me' in message.content.lower()):
                if id in self.queue:
                    embed = discord.Embed(
                        title = 'I\'ve removed you from the queue.',
                        color = discord.Color.teal()
                    )
                    await message.channel.send(embed = embed)

                    self.queue.remove(id)
                else:
                    embed = discord.Embed(
                        title = 'You\'re not in the queue!',
                        color = discord.Color.teal()
                    )
                    await message.channel.send(embed = embed)
            elif ('queue' in message.content.lower()):
                say = ''

                for id in self.queue:
                    say += self.client.get_user(id).name + '\n'
                embed = discord.Embed(
                    title = 'Current Queue',
                    color = discord.Color.teal(),
                    description = say
                )
                await message.channel.send(embed = embed)
            elif 'skip' == message.content.lower() and ('angels' in [role.name for role in message.author.roles] or 'mechanic' in [role.name for role in message.author.roles]):
                self.queue.pop()
                embed = discord.Embed(
                    title = 'I\'ve skipped to the next person.',
                    color = discord.Color.teal()
                )
                await message.channel.send(embed = embed)
                self.queue.remove(id)
    '''

    #team names in names event
    '''
    @commands.command(aliases=['snames'])
    async def squadnames(self, ctx):
        guild = ctx.guild
        members = guild.members

        embed = discord.Embed(
            title = 'Squad Names',
            color = discord.Color.teal()
        )

        tea = 0
        teaMembers = ''
        coffee = 0
        coffeeMembers = ''

        for member in members:
            if not self.meta.isVerified(member):
                continue
            if member.nick is not None:
                if self.meta.hasWord(member.nick, 'tea'):
                    tea += 1
                    teaMembers += '<@' + str(member.id) + '>\n'
                if self.meta.hasWord(member.nick, 'coffee'):
                    coffee += 1
                    coffeeMembers += '<@' + str(member.id) + '>\n'
            else:
                if self.meta.hasWord(member.name, 'tea'):
                    tea += 1
                    teaMembers += '<@' + str(member.id) + '>\n'
                if self.meta.hasWord(member.name, 'coffee'):
                    coffee += 1
                    coffeeMembers += '<@' + str(member.id) + '>\n'

        embed.add_field(name='Members with \"tea\"', value= '`' + str(tea) + '` Members\n' + teaMembers)
        embed.add_field(name='Members with \"coffee\"', value= '`' + str(coffee) + '` Members\n' + coffeeMembers)

        await ctx.send(embed = embed)
        return
    '''

    '''
    @commands.command(aliases=['first1kmembers', 'first1k', '1k'])
    async def happy1k(self, ctx):
        if not self.meta.isAdmin(ctx.author):
            return

        guild = ctx.guild
        profiles = self.dbConnection.findProfiles({})

        for doc in profiles:
            id = doc['id']
            user = ctx.guild.get_member(id)
            if user is None:
                self.dbConnection.removeProfile({"id": id})

        members = guild.members
        for member in members:
            self.meta.getProfile(member)
            self.meta.addBadgeToProfile(member, 'First1kMembers')

        await ctx.send(embed = self.meta.embedDone())

    def getNum(self, ctx, squad):
        num = 0
        names = ''
        profiles = self.dbConnection.findProfiles({'squad' : squad})
        for doc in profiles:
            id = doc['id']
            user = ctx.guild.get_member(id)
            if user is None:
                self.dbConnection.removeProfile({"id": id})
                return
            if 'Listeners' in [role.name for role in user.roles]:
                num += 1
                names += '<@' + str(user.id) + '>, '

        names = names[:len(names) - 2]
        stats = {
            "num":num,
            "names":names
        }
        return stats
    '''
