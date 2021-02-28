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
        #user = await self.client.fetch_user(int(profile['id']))
        #if not user:
        #    return None
        title = f"{user.name}#{user.discriminator}"
        if profile['sfw']:
            title = title + ' (SFW)'
        else:
            title = title + ' (NSFW)'
        if profile['active']:
            title = title + ' - ACTIVE'
        else:
            title = title + ' - DEACTIVATED'

        embed = discord.Embed(color=discord.Color.magenta(), title=title)

        embed.add_field(name="Gender(s), Pronoun(s) | LF (Looking For) ",
                        value=", ".join(profile['gender'] + ", " +
                                        profile['pronouns']) +
                              " `| LF` " +
                              ", ".join(profile['lf-gender']), inline=False)

        embed.add_field(name="Role(s) | LF (Looking For)",
                        value=", ".join(profile['role']) +
                              ' `| LF` ' +
                              ", ".join(profile['lf-role']), inline=False)

        embed.add_field(name="Medium(s)", value=", ".join(profile['medium']), inline=True)
        embed.add_field(name="Looking For Term(s)", value=", ".join(profile['lf-term']), inline=True)
        embed.add_field(name="Interest(s)", value=profile['interests'], inline=False)
        embed.add_field(name="Limit(s)", value=profile['limits'], inline=False)
        embed.add_field(name="Detail(s)", value=profile['details'], inline=False)

        #try:
        #    if user:
        #        embed.set_thumbnail(url=user.avatar_url)
        #finally:
        #    pass
        embed.set_footer(text=str(profile['id']))
        return embed

    def get_picknic(self, member: discord.Member):
        return self.get_picknic_by_id(member.id)

    def get_picknic_by_id(self, _id):
        profile = self.dbConnection.findPicknic({"id": str(_id)})
        return profile

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
        # for now, limit to testers
        if not self.meta.isBotOwner(ctx.author):
            return

        # menu
        title = 'Welcome to Picknic!'
        desc = "__What would you like to do today?__\n" \
               "[🏕] **Setup** a Picknic Profile\n" \
               "[♻️] **Edit** your Picknic Profile\n" \
               "[⚠️] **Report** a Picknic Profile\n" \
               "[🍐] **Reset** Picknic Swipe history\n" \
               "[🛰] **Search** through Picknic Matches"
        msg = await ctx.send(embed=self.meta.embed(title, desc))
        options = ['🏕', '♻', '⚠', '🍐', '🛰']
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

        await msg.clear_reactions()
        #print(f"emoji: {emoji}\temoji.emoji: {emoji.emoji}")

        # create profile
        if emoji.emoji == '🏕':
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
                await msg.clear_reactions()
                if react.emoji == '⛔':
                    await msg.edit(embed=self.meta.embed("Thanks for being honest.", "We hope you take care!"))
                    return

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

                await msg.edit(embed=self.meta.embed('Are you open to NSFW partners?', 'Please react with the corresponding emoji.'))
                options = ['✅', '⛔']
                for option in options:
                    await msg.add_reaction(option)
                try:
                    react, reacter = await self.client.wait_for('reaction_add', timeout=60.0, check=check_menu)
                except asyncio.TimeoutError:
                    await msg.edit(embed=self.meta.embedOops("Picknic menu timed out. You took too long to reply!"))
                    return
                await msg.clear_reactions()
                if react == '⛔':
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
        elif emoji == '♻':
            # check that the user has a profile to edit
            if not self.picknic_does_exist(ctx.author.id):
                await msg.edit(embed=self.meta.embedOops("You don't have a Picknic profile yet! "
                                                         "Try going back to the menu to create one."))
                return

            title = "What would you like to edit?"
            desc = "`[1]` Enable/Disable my profile." \
                   "`[2]` Change my name." \
                   "`[3]` Change my gender(s)." \
                   "`[4]` Change my pronoun(s)." \
                   "`[5]` Change my role(s)." \
                   "`[6]` Change my medium(s)." \
                   "`[7]` Toggle my profile as NSFW/SFW." \
                   "`[8]` Change the gender(s) I'm looking for." \
                   "`[9]` Change the role(s) I'm looking for." \
                   "`[10]` Change my interest(s)." \
                   "`[11]` Change my limit(s)." \
                   "`[12]` Change my detail(s)." \
                   "`[13]` Change the term(s) I'm looking for."
            return
        # report profile
        elif emoji == '⚠':
            guild = 751294304764428372  # BotHub
            channel = 752069374617059438  # issues
            await ctx.send(embed=self.meta.embed("Please send the ID of the person you'd like to report."))

            await ctx.send(embed=self.meta.embed("Please describe what you're reporting them for."))

            await ctx.send(embed=self.meta.embed("Do you have any screenshots or evidence you'd be able to link?"))

            await ctx.send(embed=self.meta.embed("Would you be alright with being contacted for "
                                                 "further queries about your report?"))

            await ctx.send(embed=self.meta.embed("Thank you! Your report has been sent."))
            return
        # reset swipes
        elif emoji == '🍐':
            return
        # flip through profile
        elif emoji == '🛰':
            # check that the requesting user has a profile themselves first
            # check that it's in dms
            if not isinstance(ctx.channel, discord.DMChannel):
                await ctx.send(embed=self.meta.embedOops('Try using this command in a private message to me!'))
                return
            else:
                return


def setup(client):
    database_connection = Database()
    meta_class = Meta(database_connection)
    client.add_cog(Picknic(client, database_connection, meta_class))
