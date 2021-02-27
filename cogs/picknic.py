import discord
from discord.ext import commands
from database import Database
from .meta import Meta
import asyncio


def get_picknic_embed(profile):
    title = profile['name']
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

    embed.set_footer(text=str(profile['id']))
    return embed


class Picknic(commands.Cog):

    def __init__(self, client, database, meta):
        self.client = client
        self.dbConnection = database
        self.meta = meta

    def get_picknic(self, member: discord.Member):
        return self.get_picknic_by_id(str(member.id))

    def get_picknic_by_id(self, _id):
        profile = self.dbConnection.findPicknic({"id": _id})
        if profile is None:
            profile = {'id': _id,
                       'name': '', 'gender': [], 'pronouns': '',
                       'role': [], 'sfw': False, 'medium': [],
                       'lf-term': [], 'lf-role': [], 'lf-gender': [],
                       'interests': '', 'limits': '', 'details': '', 'active': True,
                       'yes': [], 'no': []}
            self.dbConnection.insertPicknic(profile)
        return profile

    def edit_picknic(self, member: discord.Member, key, value):
        profile = self.dbConnection.updatePicknic({"id": str(member.id)}, {"$set": {key: value}})

    def picknic_does_exist(self, _id):
        profile = self.dbConnection.findPicknic({"id": str(_id)})
        if profile is None:
            return False
        else:
            return True

    def get_picknic_embed_from_id(self, _id):
        return get_picknic_embed(self.get_picknic_by_id(_id))

    def get_picknic_embed_from_member(self, member: discord.Member):
        return get_picknic_embed(self.get_picknic(member))

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
            await ctx.send(embed=self.get_picknic_embed_from_id(_id))
        else:
            await ctx.send(embed=self.meta.embedNoAccess())

    @commands.command(aliases=['pn'])
    async def picknic(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        if not self.picknic_does_exist(member):
            await ctx.send(embed=self.meta.embedOops('This user has not yet set up a Picknic Profile.'))
            return
        await ctx.send(embed=self.get_picknic_embed_from_member(member))

    @commands.command(aliases=['spn', 'picknicmenu'])
    async def startpicknic(self, ctx):
        # for now, limit to testers
        if not self.meta.isBotOwner(ctx.author):
            return

        # menu
        title = 'Welcome to Picknic!'
        desc = "What would you like to do today?" \
               "[🏕] **Setup** a Picknic Profile" \
               "[♻️] **Edit** your Picknic Profile" \
               "[⚠️] **Report** a Picknic Profile" \
               "[🍐] **Reset** Picknic Swipe history" \
               "[🛰] **Search** through Picknic Matches"
        msg = await ctx.send(embed=self.meta.embed(title, desc))
        options = ['🏕', '♻', '⚠', '🍐', '🛰']
        for option in options:
            await msg.add_reaction(option)

        emoji = ''

        def check(react, responder):
            nonlocal emoji
            emoji = str(react.emoji)
            return str(react.emoji) in options and responder == ctx.author

        try:
            react, reacter = await self.client.wait_for('reaction_add', timeout=120.0, check=check)
        except asyncio.TimeoutError:
            await msg.edit(embed=self.meta.embedOops("Picknic menu timed out. You took too long to reply!"))
            return

        await msg.clear_reactions()

        # create profile
        if emoji == '🏕':
            if self.picknic_does_exist(ctx.author().id):
                await msg.edit(embed=self.meta.embedOops('You already have a Picknic profile! '
                                                         'Try going back to the menu and editing it.'))
                return
            else:
                await msg.edit(embed=self.meta.embed('First, are you over 18 years of age? ',
                                                     'Users who are found or suspected to be '
                                                     'underage will be banned from the system.'
                                                     'By using our platform and space, you agree to '
                                                     'follow our rules, including following Discord ToS.'))

                await msg.edit(embed=self.meta.embed('What would you like to be named?'))
                await msg.edit(embed=self.meta.embed('What are your pronouns?'))

                await msg.edit(embed=self.meta.embed('What gender label(s) fit you best? '
                                                     'Please type the numbers separated by commas.',
                                                     "`[1]` Male\n"
                                                     "`[2]` Female\n"
                                                     "`[3]` Non-binary\n"
                                                     "`[4]` Agender\n"
                                                     "`[5]` Genderfluid"
                                                     "`[6]` Prefer not to specify"))

                await msg.edit(embed=self.meta.embed('What gender labels are you looking for?'))
                await msg.edit(embed=self.meta.embed('What role(s) do you fit?'))
                await msg.edit(embed=self.meta.embed('What role(s) are you looking for (LF)?'))
                await msg.edit(embed=self.meta.embed('What mediums do you use for hypnosis?'))
                await msg.edit(embed=self.meta.embed('What term(s) are you looking for (LF)?'))
                await msg.edit(embed=self.meta.embed('Are you open to NSFW partners?'))
                await msg.edit(embed=self.meta.embed("Type what you'd like your interests on your profile to say."))
                await msg.edit(embed=self.meta.embed("Type what you'd like your limits on your profile to say."))
                await msg.edit(embed=self.meta.embed("Type what you'd like your details on your profile to say."))
                await msg.edit(embed=self.meta.embed("And we're done!",
                                                     "Feel free to check out your profile using the `;pn` command."))
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
