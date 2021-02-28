import discord
from discord.ext import commands
from database import Database
from .meta import Meta
import asyncio


class Picknic(commands.Cog):

    def __init__(self, client, database, meta):
        self.client = client
        self.dbConnection = database
        self.meta = meta

    def get_picknic_embed(self, profile):
        user = self.client.get_user(int(profile['id']))
        if not user:
            return None
        title = f"{user.name}#{user.discriminator}"

        if not profile['active']:
            desc = 'Deactivated account.\nNeed to activate it again? Use the `;pnm` command to reactivate it.'
            embed = discord.Embed(color=discord.Color.magenta(), title=title, description=desc)
            try:
                if user:
                    embed.set_thumbnail(url=user.avatar_url)
            finally:
                pass
            embed.set_footer(text=f"ID: {str(profile['id'])}")
            return embed

        if not profile['sfw']:
            title = title + ' 🌶'

        embed = discord.Embed(color=discord.Color.magenta(), title=title)

        embed.add_field(name=", ".join(profile['gender']).capitalize() + ", " + profile['pronouns'],
                        value="`LF (Looking For)` \n" +
                              ", ".join(profile['lf-gender']).capitalize(), inline=False)

        embed.add_field(name=profile['role'].capitalize(),
                        value='`LF (Looking For)` \n' +
                              ", ".join(profile['lf-term']).capitalize() + "\n" +
                              ", ".join(profile['lf-role']).capitalize() + "\n" +
                              ", ".join(profile['medium']).capitalize()
                        , inline=False)

        embed.add_field(name="Interest(s)", value=profile['interests'], inline=False)
        embed.add_field(name="Limit(s)", value=profile['limits'], inline=False)
        embed.add_field(name="Detail(s)", value=profile['details'], inline=False)

        try:
            if user:
                embed.set_thumbnail(url=user.avatar_url)
        finally:
            pass
        embed.set_footer(text=f"ID: {str(profile['id'])}")
        return embed

    def get_picknic(self, member: discord.Member):
        return self.get_picknic_by_id(member.id)

    def get_picknic_by_id(self, _id):
        profile = self.dbConnection.findPicknic({"id": str(_id)})
        return profile

    def report_picknic(self, reporter_id, reportee_id):
        guild = 751294304764428372  # BotHub
        channel = 752069374617059438  # issues
        self.client.get_guild(guild).get_channel(channel).send(f"New report from {reporter_id}\n{reportee_id}")
        return

    def create_picknic_from_profile(self, profile=None):
        if profile is not None:
            self.dbConnection.insertPicknic(profile)

    def create_picknic(self, _id, gender: list, pronouns: str, role, sfw: bool, medium: list, lf_term: list,
                       lf_role: list, lf_gender: list, interests: str, limits: str, details: str):
        p = self.dbConnection.findProfile({"id": str(_id)})
        if p is None:
            p = {
                'id': str(_id),
                'gender': gender,
                'pronouns': pronouns,
                'role': role,
                'sfw': sfw,
                'medium': medium,
                'lf-term': lf_term,
                'lf-role': lf_role,
                'lf-gender': lf_gender,
                'interests': interests,
                'limits': limits,
                'details': details,
                'active': True,
                'yes': [],
                'no': []
            }
            self.dbConnection.insertPicknic(p)
        else:
            return False

    def edit_picknic(self, member: discord.Member, key, value):
        profile = self.dbConnection.updatePicknic({"id": str(member.id)}, {"$set": {key: value}})

    def picknic_does_exist(self, _id):
        profile = self.dbConnection.findPicknic({"id": str(_id)})
        if profile is None:
            return False
        else:
            return True

    def get_picknic_embed_from_id(self, _id):
        p = self.get_picknic_by_id(_id)
        if p is not None:
            return self.get_picknic_embed(p)
        else:
            return None

    def get_picknic_embed_from_member(self, member: discord.Member):
        p = self.get_picknic(member)
        if p is not None:
            return self.get_picknic_embed(p)
        else:
            return None

    @commands.command()
    async def removepicknic(self, ctx, _id):
        if self.meta.isBotOwner(ctx.message.author):
            if self.picknic_does_exist():
                self.dbConnection.removePicknic({"id": str(_id)})
            await ctx.send(embed=self.meta.embedDone())
        else:
            await ctx.send(embed=self.meta.embedNoAccess())

    @commands.command(aliases=['pnid'])
    async def getpicknicbyid(self, ctx, _id):
        if self.meta.isBotOwner(ctx.message.author):
            p = self.get_picknic_embed_from_id(_id)
            if p is None:
                await ctx.send(embed=self.meta.embedOops('This user has not yet set up a Picknic Profile.'))
                return
            await ctx.send(embed=p)
        else:
            await ctx.send(embed=self.meta.embedNoAccess())

    @commands.command(aliases=['pn'])
    async def picknic(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        p = self.get_picknic_embed_from_member(member)

        if p is None:
            await ctx.send(embed=self.meta.embedOops('This user has not yet set up a Picknic Profile.'))
            return
        await ctx.send(embed=p)

    @commands.command(aliases=['spn', 'picknicmenu', 'pnm'])
    async def startpicknic(self, ctx):
        isDM = isinstance(ctx.channel, discord.DMChannel)
        # menu
        title = 'Welcome to Picknic!'
        desc = "__What would you like to do today?__\n" \
               "[🏕] **Setup** a Picknic Profile\n" \
               "[🛠] **Edit** your Picknic Profile\n" \
               "[🧨] **Report** a Picknic Profile\n" \
               "[🍐] **Reset** Picknic Swipe history\n" \
               "[🛰] **Search** through Picknic Matches"
        msg = await ctx.send(embed=self.meta.embed(title, desc))
        options = ['🏕', '🛠', '🧨', '🍐', '🛰']
        for option in options:
            await msg.add_reaction(option)

        def check_menu(react, responder):
            return str(react.emoji) in options and responder == ctx.author

        def check_msg(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            emoji, reacter = await self.client.wait_for('reaction_add', timeout=120.0, check=check_menu)
        except asyncio.TimeoutError:
            await msg.edit(embed=self.meta.embedOops("Picknic menu timed out. You took too long to reply!"))
            return
        emoji = emoji.emoji

        if isDM:
            await msg.delete()
            msg = await ctx.send(embed=self.meta.embed("Loading...", "Please wait."))
        else:
            await msg.clear_reactions()
        print(f"emoji: [{emoji}]")  # \temoji.emoji: [{emoji.emoji}]")

        # create profile
        if emoji == '🏕':
            if self.picknic_does_exist(ctx.author.id):
                await msg.edit(embed=self.meta.embedOops('You already have a Picknic profile! '
                                                         'Try going back to the menu and editing it.'))
                return
            else:
                await msg.edit(embed=self.meta.embed('First, are you at least 18 years of age? ',
                                                     'Users who are found or suspected to be '
                                                     'underage will be banned from the system. '
                                                     'By using our platform and space, you agree to '
                                                     'follow our rules, including following Discord ToS.'))
                options = ['✅', '⛔']
                for option in options:
                    await msg.add_reaction(option)
                try:
                    react, reacter = await self.client.wait_for('reaction_add', timeout=60.0, check=check_menu)
                except asyncio.TimeoutError:
                    await msg.edit(embed=self.meta.embedOops("Picknic menu timed out. You took too long to reply!"))
                    return
                if react.emoji == '⛔':
                    await msg.edit(embed=self.meta.embed("Thanks for being honest.", "We hope you take care!"))
                    return

                if isDM:
                    await msg.delete()
                    msg = await ctx.send(embed=self.meta.embed("Loading...", "Please wait."))
                else:
                    await msg.clear_reactions()

                await msg.edit(embed=self.meta.embed('What are your pronouns?', 'e.g. she/her, they/them, etc.'))
                try:
                    reply = await self.client.wait_for('message', timeout=60.0, check=check_msg)
                except asyncio.TimeoutError:
                    await msg.edit(embed=self.meta.embedOops("Picknic menu timed out. You took too long to reply!"))
                    return
                pronouns = reply.content
                await reply.delete()

                await msg.edit(embed=self.meta.embed('What gender label(s) fit you best? '
                                                     'Please type the numbers separated by commas.',
                                                     "`[1]` Male\n"
                                                     "`[2]` Female\n"
                                                     "`[3]` Non-binary\n"
                                                     "`[4]` Agender\n"
                                                     "`[5]` Genderfluid\n"
                                                     "`[6]` Prefer not to specify"))
                try:
                    reply = await self.client.wait_for('message', timeout=60.0, check=check_msg)
                except asyncio.TimeoutError:
                    await msg.edit(embed=self.meta.embedOops("Picknic menu timed out. You took too long to reply!"))
                    return
                temp = [x.strip() for x in reply.content.split(',')]
                gender = []
                for t in temp:
                    if t == '1':
                        gender.append('male')
                    elif t == '2':
                        gender.append('female')
                    elif t == '3':
                        gender.append('non-binary')
                    elif t == '4':
                        gender.append('agender')
                    elif t == '5':
                        gender.append('genderfluid')
                    elif t == '6':
                        gender.append('mystery')
                await reply.delete()

                await msg.edit(embed=self.meta.embed('What gender label(s) are you looking for? '
                                                     'Please type the numbers separated by commas.',
                                                     "`[1]` Male\n"
                                                     "`[2]` Female\n"
                                                     "`[3]` Non-binary\n"
                                                     "`[4]` Agender\n"
                                                     "`[5]` Genderfluid\n"
                                                     "`[6]` Prefer not to specify"))
                try:
                    reply = await self.client.wait_for('message', timeout=60.0, check=check_msg)
                except asyncio.TimeoutError:
                    await msg.edit(embed=self.meta.embedOops("Picknic menu timed out. You took too long to reply!"))
                    return
                temp = [x.strip() for x in reply.content.split(',')]
                lf_gender = []
                for t in temp:
                    if t == '1':
                        lf_gender.append('male')
                    elif t == '2':
                        lf_gender.append('female')
                    elif t == '3':
                        lf_gender.append('non-binary')
                    elif t == '4':
                        lf_gender.append('agender')
                    elif t == '5':
                        lf_gender.append('genderfluid')
                    elif t == '6':
                        lf_gender.append('mystery')
                await reply.delete()

                await msg.edit(embed=self.meta.embed('What primary role do you best fit? (Choose one.) '
                                                     'Please react with the corresponding emoji.',
                                                     "`[1]` Hypnotist\n"
                                                     "`[2]` Hypnoswitch\n"
                                                     "`[3]` Subject\n"))
                options = ['1️⃣', '2️⃣', '3️⃣']
                for option in options:
                    await msg.add_reaction(option)
                try:
                    role, reacter = await self.client.wait_for('reaction_add', timeout=60.0, check=check_menu)
                except asyncio.TimeoutError:
                    await msg.edit(embed=self.meta.embedOops("Picknic menu timed out. You took too long to reply!"))
                    return
                if isDM:
                    await msg.delete()
                    msg = await ctx.send(embed=self.meta.embed("Loading...", "Please wait."))
                else:
                    await msg.clear_reactions()
                role = role.emoji
                if role == '1️⃣':
                    role = 'hypnotist'
                elif role == '2️⃣':
                    role = 'hypnoswitch'
                elif role == '3️⃣':
                    role = 'subject'

                await msg.edit(embed=self.meta.embed('What role(s) are you looking for (LF)? '
                                                     'Please type the numbers separated by commas.',
                                                     "`[1]` Hypnotist\n"
                                                     "`[2]` Hypnoswitch\n"
                                                     "`[3]` Subject\n"))
                try:
                    reply = await self.client.wait_for('message', timeout=60.0, check=check_msg)
                except asyncio.TimeoutError:
                    await msg.edit(embed=self.meta.embedOops("Picknic menu timed out. You took too long to reply!"))
                    return
                temp = [x.strip() for x in reply.content.split(',')]
                lf_roles = []
                for t in temp:
                    if t == '1':
                        lf_roles.append('hypnotist')
                    elif t == '2':
                        lf_roles.append('hypnoswitch')
                    elif t == '3':
                        lf_roles.append('subject')
                await reply.delete()

                await msg.edit(embed=self.meta.embed('What mediums do you use for hypnosis?'
                                                     'Please type the numbers separated by commas.',
                                                     "`[1]` Text\n"
                                                     "`[2]` Audio\n"
                                                     "`[3]` Video\n"
                                                     "`[4]` In-person"))
                try:
                    reply = await self.client.wait_for('message', timeout=60.0, check=check_msg)
                except asyncio.TimeoutError:
                    await msg.edit(embed=self.meta.embedOops("Picknic menu timed out. You took too long to reply!"))
                    return
                temp = [x.strip() for x in reply.content.split(',')]
                mediums = []
                for t in temp:
                    if t == '1':
                        mediums.append('text')
                    elif t == '2':
                        mediums.append('audio')
                    elif t == '3':
                        mediums.append('video')
                    elif t == '4':
                        mediums.append('in-person')
                await reply.delete()

                await msg.edit(embed=self.meta.embed('What term(s) are you looking for (LF)? '
                                                     'Please type the numbers separated by commas.',
                                                     "`[1]` Long-term\n"
                                                     "`[2]` Short-term"))
                try:
                    reply = await self.client.wait_for('message', timeout=60.0, check=check_msg)
                except asyncio.TimeoutError:
                    await msg.edit(embed=self.meta.embedOops("Picknic menu timed out. You took too long to reply!"))
                    return
                temp = [x.strip() for x in reply.content.split(',')]
                terms = []
                for t in temp:
                    if t == '1':
                        terms.append('long-term')
                    elif t == '2':
                        terms.append('short-term')
                await reply.delete()

                await msg.edit(embed=self.meta.embed('Are you open to NSFW (🌶) partners?',
                                                     'Those who are will have a 🌶 displayed on their profile.'))
                options = ['✅', '⛔']
                for option in options:
                    await msg.add_reaction(option)
                try:
                    react, reacter = await self.client.wait_for('reaction_add', timeout=60.0, check=check_menu)
                except asyncio.TimeoutError:
                    await msg.edit(embed=self.meta.embedOops("Picknic menu timed out. You took too long to reply!"))
                    return
                if isDM:
                    await msg.delete()
                    msg = await ctx.send(embed=self.meta.embed("Loading...", "Please wait."))
                else:
                    await msg.clear_reactions()
                if react.emoji == '⛔':
                    sfw = True
                else:
                    sfw = False

                await msg.edit(embed=self.meta.embed("Time for interests!",
                                                     "Type what you'd like your interests on your profile to say."))
                try:
                    reply = await self.client.wait_for('message', timeout=180.0, check=check_msg)
                except asyncio.TimeoutError:
                    await msg.edit(embed=self.meta.embedOops("Picknic menu timed out. You took too long to reply!"))
                    return
                interests = reply.content
                await reply.delete()

                await msg.edit(embed=self.meta.embed("How about your limits?",
                                                     "Type what you'd like your limits on your profile to say."))
                try:
                    reply = await self.client.wait_for('message', timeout=180.0, check=check_msg)
                except asyncio.TimeoutError:
                    await msg.edit(embed=self.meta.embedOops("Picknic menu timed out. You took too long to reply!"))
                    return
                limits = reply.content
                await reply.delete()

                await msg.edit(embed=self.meta.embed("And lastly, any other details you'd like people to know?",
                                                     "Type what you'd like your details on your profile to say."))
                try:
                    reply = await self.client.wait_for('message', timeout=180.0, check=check_msg)
                except asyncio.TimeoutError:
                    await msg.edit(embed=self.meta.embedOops("Picknic menu timed out. You took too long to reply!"))
                    return
                details = reply.content
                await reply.delete()

                await msg.edit(embed=self.meta.embed(f"And we're done, {ctx.author.name}!",
                                                     f"{ctx.author.mention}, "
                                                     f"feel free to check out your profile using the `;pn` command.\n"
                                                     "Leaving all servers with Seymour will deactivate your profile."))

                self.create_picknic(ctx.author.id, gender, pronouns, role, sfw, mediums, terms,
                                    lf_roles, lf_gender, interests, limits, details)
                return
        # edit profile
        elif emoji == '🛠':
            # check that the user has a profile to edit
            if not self.picknic_does_exist(ctx.author.id):
                await msg.edit(embed=self.meta.embedOops("You don't have a Picknic profile yet! "
                                                         "Try going back to the menu to create one."))
                return

            title = "What would you like to edit?\n"
            desc = "`[1]` Enable/Disable my profile or toggle my profile as NSFW/SFW.\n" \
                   "`[2]` Change my gender(s) or the gender(s) I'm looking for.\n" \
                   "`[3]` Change my role or the role(s) I'm looking for.\n" \
                   "`[4]` Change my pronouns, interest(s), limit(s), or detail(s).\n" \
                   "`[5]` Change the term(s) or medium(s) I'm looking for."
            await msg.edit(embed=self.meta.embed(title, desc))

            options = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']
            for option in options:
                await msg.add_reaction(option)
            try:
                choice, reacter = await self.client.wait_for('reaction_add', timeout=60.0, check=check_menu)
            except asyncio.TimeoutError:
                await msg.edit(embed=self.meta.embedOops("Picknic menu timed out. You took too long to reply!"))
                return
            if isDM:
                await msg.delete()
                msg = await ctx.send(embed=self.meta.embed("Loading...", "Please wait."))
            else:
                await msg.clear_reactions()
            choice = choice.emoji
            # [1] Enable/Disable my profile or toggle my profile as NSFW/SFW.
            if choice == '1️⃣':
                title = "Enable/Disable and NSFW/SFW"
                desc = "`[1]` Enable my profile.\n" \
                       "`[2]` Disable my profile.\n" \
                       "`[3]` Make my profile NSFW-allowed.\n" \
                       "`[4]` Make my profile SFW-only."
                await msg.edit(embed=self.meta.embed(title, desc))
                options = ['1️⃣', '2️⃣', '3️⃣', '4️⃣']
                for option in options:
                    await msg.add_reaction(option)
                try:
                    choice, reacter = await self.client.wait_for('reaction_add', timeout=60.0, check=check_menu)
                except asyncio.TimeoutError:
                    await msg.edit(embed=self.meta.embedOops("Picknic menu timed out. You took too long to reply!"))
                    return
                if isDM:
                    await msg.delete()
                    msg = await ctx.send(embed=self.meta.embed("Loading...", "Please wait."))
                else:
                    await msg.clear_reactions()
                choice = choice.emoji
                if choice == '1️⃣':
                    self.edit_picknic(ctx.author, 'active', True)
                elif choice == '2️⃣':
                    self.edit_picknic(ctx.author, 'active', False)
                elif choice == '3️⃣':
                    self.edit_picknic(ctx.author, 'sfw', False)
                elif choice == '4️⃣':
                    self.edit_picknic(ctx.author, 'sfw', True)
                await msg.edit(embed=self.meta.embedDone())
                return
            # [2] Change my gender(s) or the gender(s) I'm looking for.
            elif choice == '2️⃣':
                title = "Genders"
                desc = "`[1]` Change my gender(s).\n" \
                       "`[2]` Change the gender(s) I'm looking for.\n"
                await msg.edit(embed=self.meta.embed(title, desc))
                options = ['1️⃣', '2️⃣']
                for option in options:
                    await msg.add_reaction(option)
                try:
                    choice, reacter = await self.client.wait_for('reaction_add', timeout=60.0, check=check_menu)
                except asyncio.TimeoutError:
                    await msg.edit(embed=self.meta.embedOops("Picknic menu timed out. You took too long to reply!"))
                    return
                if isDM:
                    await msg.delete()
                    msg = await ctx.send(embed=self.meta.embed("Loading...", "Please wait."))
                else:
                    await msg.clear_reactions()
                if choice == '1️⃣':
                    await msg.edit(embed=self.meta.embed('What gender label(s) fit you best? '
                                                         'Please type the numbers separated by commas.',
                                                         "`[1]` Male\n"
                                                         "`[2]` Female\n"
                                                         "`[3]` Non-binary\n"
                                                         "`[4]` Agender\n"
                                                         "`[5]` Genderfluid\n"
                                                         "`[6]` Prefer not to specify"))
                    try:
                        reply = await self.client.wait_for('message', timeout=60.0, check=check_msg)
                    except asyncio.TimeoutError:
                        await msg.edit(embed=self.meta.embedOops("Picknic menu timed out. You took too long to reply!"))
                        return
                    temp = [x.strip() for x in reply.content.split(',')]
                    gender = []
                    for t in temp:
                        if t == '1':
                            gender.append('male')
                        elif t == '2':
                            gender.append('female')
                        elif t == '3':
                            gender.append('non-binary')
                        elif t == '4':
                            gender.append('agender')
                        elif t == '5':
                            gender.append('genderfluid')
                        elif t == '6':
                            gender.append('mystery')
                    await reply.delete()
                    self.edit_picknic(ctx.author, 'gender', gender)
                    await msg.edit(embed=self.meta.embedDone())
                    return
                else:
                    await msg.edit(embed=self.meta.embed('What gender label(s) are you looking for? '
                                                         'Please type the numbers separated by commas.',
                                                         "`[1]` Male\n"
                                                         "`[2]` Female\n"
                                                         "`[3]` Non-binary\n"
                                                         "`[4]` Agender\n"
                                                         "`[5]` Genderfluid\n"
                                                         "`[6]` Prefer not to specify"))
                    try:
                        reply = await self.client.wait_for('message', timeout=60.0, check=check_msg)
                    except asyncio.TimeoutError:
                        await msg.edit(embed=self.meta.embedOops("Picknic menu timed out. You took too long to reply!"))
                        return
                    temp = [x.strip() for x in reply.content.split(',')]
                    lf_gender = []
                    for t in temp:
                        if t == '1':
                            lf_gender.append('male')
                        elif t == '2':
                            lf_gender.append('female')
                        elif t == '3':
                            lf_gender.append('non-binary')
                        elif t == '4':
                            lf_gender.append('agender')
                        elif t == '5':
                            lf_gender.append('genderfluid')
                        elif t == '6':
                            lf_gender.append('mystery')
                    await reply.delete()
                    self.edit_picknic(ctx.author, 'lf-gender', lf_gender)
                    await msg.edit(embed=self.meta.embedDone())
                    return
            # [3] Change my role or the role(s) I'm looking for
            elif choice == '3️⃣':
                title = "Roles"
                desc = "`[1]` Change my role.\n" \
                       "`[2]` Change the role(s) I'm looking for.\n"
                await msg.edit(embed=self.meta.embed(title, desc))
                options = ['1️⃣', '2️⃣']
                for option in options:
                    await msg.add_reaction(option)
                try:
                    choice, reacter = await self.client.wait_for('reaction_add', timeout=60.0, check=check_menu)
                except asyncio.TimeoutError:
                    await msg.edit(embed=self.meta.embedOops("Picknic menu timed out. You took too long to reply!"))
                    return
                if isDM:
                    await msg.delete()
                    msg = await ctx.send(embed=self.meta.embed("Loading...", "Please wait."))
                else:
                    await msg.clear_reactions()
                if choice == '1️⃣':
                    await msg.edit(embed=self.meta.embed('What primary role do you best fit? (Choose one.) '
                                                         'Please react with the corresponding emoji.',
                                                         "`[1]` Hypnotist\n"
                                                         "`[2]` Hypnoswitch\n"
                                                         "`[3]` Subject\n"))
                    options = ['1️⃣', '2️⃣', '3️⃣']
                    for option in options:
                        await msg.add_reaction(option)
                    try:
                        role, reacter = await self.client.wait_for('reaction_add', timeout=60.0, check=check_menu)
                    except asyncio.TimeoutError:
                        await msg.edit(embed=self.meta.embedOops("Picknic menu timed out. You took too long to reply!"))
                        return
                    if isDM:
                        await msg.delete()
                        msg = await ctx.send(embed=self.meta.embed("Loading...", "Please wait."))
                    else:
                        await msg.clear_reactions()
                    role = role.emoji
                    if role == '1️⃣':
                        role = 'hypnotist'
                    elif role == '2️⃣':
                        role = 'hypnoswitch'
                    elif role == '3️⃣':
                        role = 'subject'
                    self.edit_picknic(ctx.author, 'role', role)
                    await msg.edit(embed=self.meta.embedDone())
                    return
                else:
                    await msg.edit(embed=self.meta.embed('What role(s) are you looking for (LF)? '
                                                         'Please type the numbers separated by commas.',
                                                         "`[1]` Hypnotist\n"
                                                         "`[2]` Hypnoswitch\n"
                                                         "`[3]` Subject\n"))
                    try:
                        reply = await self.client.wait_for('message', timeout=60.0, check=check_msg)
                    except asyncio.TimeoutError:
                        await msg.edit(embed=self.meta.embedOops("Picknic menu timed out. You took too long to reply!"))
                        return
                    temp = [x.strip() for x in reply.content.split(',')]
                    lf_roles = []
                    for t in temp:
                        if t == '1':
                            lf_roles.append('hypnotist')
                        elif t == '2':
                            lf_roles.append('hypnoswitch')
                        elif t == '3':
                            lf_roles.append('subject')
                    await reply.delete()
                    self.edit_picknic(ctx.author, 'lf-role', lf_roles)
                    await msg.edit(embed=self.meta.embedDone())
                    return
            # [4] Change my pronouns, interest(s), limit(s), or detail(s).
            elif choice == '4️⃣':
                title = "Pronouns, Interests, Limits, Details"
                desc = "`[1]` Change my pronouns.\n" \
                       "`[2]` Change my interest(s).\n" \
                       "`[3]` Change my limit(s).\n" \
                       "`[4]` Change my detail(s)."
                await msg.edit(embed=self.meta.embed(title, desc))
                options = ['1️⃣', '2️⃣', '3️⃣', '4️⃣']
                for option in options:
                    await msg.add_reaction(option)
                try:
                    choice, reacter = await self.client.wait_for('reaction_add', timeout=60.0, check=check_menu)
                except asyncio.TimeoutError:
                    await msg.edit(embed=self.meta.embedOops("Picknic menu timed out. You took too long to reply!"))
                    return
                if isDM:
                    await msg.delete()
                    msg = await ctx.send(embed=self.meta.embed("Loading...", "Please wait."))
                else:
                    await msg.clear_reactions()

                title = "What would you like to change it to?"
                desc = "Type it out!"
                try:
                    reply = await self.client.wait_for('message', timeout=180.0, check=check_msg)
                except asyncio.TimeoutError:
                    await msg.edit(embed=self.meta.embedOops("Picknic menu timed out. You took too long to reply!"))
                    return
                response = reply.content
                await reply.delete()

                choice = choice.emoji
                if choice == '1️⃣':
                    self.edit_picknic(ctx.author, 'pronouns', response)
                elif choice == '2️⃣':
                    self.edit_picknic(ctx.author, 'interests', response)
                elif choice == '3️⃣':
                    self.edit_picknic(ctx.author, 'limits', response)
                elif choice == '4️⃣':
                    self.edit_picknic(ctx.author, 'details', response)
                await msg.edit(embed=self.meta.embedDone())
                return
            # [5] Change the term(s) or medium(s) I'm looking for.
            elif choice == '5️⃣':
                title = "Terms and Mediums"
                desc = "`[1]` Change my term(s).\n" \
                       "`[2]` Change my medium(s).\n"
                await msg.edit(embed=self.meta.embed(title, desc))
                options = ['1️⃣', '2️⃣']
                for option in options:
                    await msg.add_reaction(option)
                try:
                    choice, reacter = await self.client.wait_for('reaction_add', timeout=60.0, check=check_menu)
                except asyncio.TimeoutError:
                    await msg.edit(embed=self.meta.embedOops("Picknic menu timed out. You took too long to reply!"))
                    return
                if isDM:
                    await msg.delete()
                    msg = await ctx.send(embed=self.meta.embed("Loading...", "Please wait."))
                else:
                    await msg.clear_reactions()
                if choice == '1️⃣':
                    await msg.edit(embed=self.meta.embed('What term(s) are you looking for (LF)? '
                                                         'Please type the numbers separated by commas.',
                                                         "`[1]` Long-term\n"
                                                         "`[2]` Short-term"))
                    try:
                        reply = await self.client.wait_for('message', timeout=60.0, check=check_msg)
                    except asyncio.TimeoutError:
                        await msg.edit(embed=self.meta.embedOops("Picknic menu timed out. You took too long to reply!"))
                        return
                    temp = [x.strip() for x in reply.content.split(',')]
                    terms = []
                    for t in temp:
                        if t == '1':
                            terms.append('long-term')
                        elif t == '2':
                            terms.append('short-term')
                    await reply.delete()
                    self.edit_picknic(ctx.author, 'lf-term', terms)
                    await msg.edit(embed=self.meta.embedDone())
                    return
                else:
                    await msg.edit(embed=self.meta.embed('What mediums do you use for hypnosis?'
                                                         'Please type the numbers separated by commas.',
                                                         "`[1]` Text\n"
                                                         "`[2]` Audio\n"
                                                         "`[3]` Video\n"
                                                         "`[4]` In-person"))
                    try:
                        reply = await self.client.wait_for('message', timeout=60.0, check=check_msg)
                    except asyncio.TimeoutError:
                        await msg.edit(embed=self.meta.embedOops("Picknic menu timed out. You took too long to reply!"))
                        return
                    temp = [x.strip() for x in reply.content.split(',')]
                    mediums = []
                    for t in temp:
                        if t == '1':
                            mediums.append('text')
                        elif t == '2':
                            mediums.append('audio')
                        elif t == '3':
                            mediums.append('video')
                        elif t == '4':
                            mediums.append('in-person')
                    await reply.delete()
                    self.edit_picknic(ctx.author, 'medium', mediums)
                    await msg.edit(embed=self.meta.embedDone())
                    return

            return
        # report profile
        elif emoji == '️🧨':
            title = "Report A User"
            desc = "Please send the user ID of the person you're trying to report. " \
                   "Your ID will be saved as the reporter. By reporting another user, " \
                   "you give us permission to reach out to you for any further questions about the situation. " \
                   "Type 'cancel' to cancel."
            try:
                reply = await self.client.wait_for('message', timeout=60.0, check=check_msg)
            except asyncio.TimeoutError:
                await msg.edit(embed=self.meta.embedOops("Picknic menu timed out. You took too long to reply!"))
                return
            response = reply.content
            await reply.delete()
            if response.lower() == 'cancel':
                await msg.edit(embed=self.meta.embedDone(f"Cancelled report."))
                return
            await msg.edit(embed=self.meta.embedDone(f"Reported {response}!"))
            return
        # reset swipes
        elif emoji == '🍐':
            self.edit_picknic(ctx.author, 'no', [])
            self.edit_picknic(ctx.author, 'yes', [])
            await msg.edit(embed=self.meta.embedDone())
            return
        # flip through profile
        elif emoji == '🛰':
            # check that it's in dms
            if not isDM:
                await msg.edit(embed=self.meta.embedOops('Try using this command in a private message to me!'))
                return
            # check that the requesting user has a profile themselves first
            if not self.picknic_does_exist(ctx.author):
                await ctx.send(embed=self.meta.embedOops('You need a Picknic profile yourself first!'))
                return
            # check that the requesting user's profile is active
            profile = self.get_picknic(ctx.author)
            if not profile['active']:
                await ctx.send(
                    embed=self.meta.embedOops('Your profile is deactivated! It needs to be active to search.'))
                return
            await msg.delete()
            picknics = self.dbConnection.findPicknics({'active': True, 'sfw': profile['sfw']})
            yes = profile['yes']
            no = profile['no']
            for p in picknics:
                await self.client.send_typing(ctx.channel):
                    if p['id'] == str(ctx.author.id):
                        continue
                    if p['id'] in profile['no'] or profile['id'] in p['no']:
                        continue
                    if p['id'] in profile['yes']:
                        continue
                    if not any(check in p['gender'] for check in profile['lf-gender']):
                        continue
                    if not any(check in p['medium'] for check in profile['medium']):
                        continue
                    if not any(check in p['role'] for check in profile['lf-role']):
                        continue
                msg = await ctx.send(embed=self.get_picknic_embed(p))
                options = ['👍', '👎', '🧨', '🛑', '➡️']
                for option in options:
                    await msg.add_reaction(option)
                try:
                    choice, reacter = await self.client.wait_for('reaction_add', timeout=180.0, check=check_menu)
                except asyncio.TimeoutError:
                    await msg.edit(embed=self.meta.embedOops("Picknic menu timed out. You took too long to reply!"))
                    return
                if choice == '👍':
                    if profile['id'] in p['yes']:
                        match = self.client.get_user(int(profile['id']))
                        await ctx.send(embed=self.meta.embed("You got a match!",
                                                             f"{ctx.author.mention}, you matched with {match.mention}!"))
                    yes.append(profile['id'])
                    self.edit_picknic(ctx.author, 'yes', yes)
                    await msg.delete()
                elif choice == '👎':
                    no.append(profile['id'])
                    self.edit_picknic(ctx.author, 'no', no)
                    await msg.delete()
                elif choice == '🧨':
                    reportee = self.client.get_user(int(profile['id']))
                    report_msg = await ctx.send(embed=self.meta.embed('Report Confirmation',
                                                                      f'Are you sure you want to report {reportee.mention}?\n'
                                                                      f'Your ID will be saved as the reporter. By '
                                                                      f'reporting another user, '
                                                                      f'you give us permission to reach out to you for '
                                                                      f'any further questions about the situation.'))
                    options = ['✅', '⛔']
                    for option in options:
                        await msg.add_reaction(option)
                    try:
                        react, reacter = await self.client.wait_for('reaction_add', timeout=60.0, check=check_menu)
                    except asyncio.TimeoutError:
                        await report_msg.edit(embed=self.meta.embedOops("Picknic menu timed out. "
                                                                        "You took too long to reply!"))
                        return
                    if isDM:
                        await msg.delete()
                        msg = await ctx.send(embed=self.meta.embed("Loading...", "Please wait."))
                    else:
                        await msg.clear_reactions()
                    if react.emoji == '⛔':
                        await report_msg.delete()
                        continue
                    else:
                        self.report_picknic(ctx.author.id, p['id'])
                        await report_msg.edit(embed=self.meta.embedDone(f"Reported {reportee.mention}!"))
                        await asyncio.sleep(5)
                        await report_msg.delete()
                        no.append(profile['id'])
                        self.edit_picknic(ctx.author, 'no', no)
                        await msg.delete()
                elif choice == '➡️':
                    await msg.delete()
                    continue
                elif choice == '🛑':
                    await msg.edit(embed=self.meta.embedDone("Thanks for using Picknic. Come back soon!"))
                    return
            await msg.edit(embed=self.meta.embedDone("We don't have any new Picknic profiles for you right now.",
                                                     "Check back later!"))
            return


def setup(client):
    database_connection = Database()
    meta_class = Meta(database_connection)
    client.add_cog(Picknic(client, database_connection, meta_class))
