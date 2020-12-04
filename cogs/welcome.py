import discord
from discord.ext import commands
from database import Database
from .meta import Meta
import asyncio


class Welcome(commands.Cog):

    def __init__(self, client, database, meta):
        self.client = client
        self.dbConnection = database
        self.meta = meta

    # Pig's Pen Hypnosis verification setup
    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.channel.id == 784389266574409788:
            return
        if self.meta.isSelf(message.author) or self.meta.isMod(message.author):
            return
        if self.dbConnection.findServer({"id": 720977242968293376})['password'] in message.content.lower():
            await message.delete()
            roles = message.author.roles
            hypnosis_flag = False
            pronoun_flag = False
            dm_flag = False
            verified_id = 728734641250500628

            hypnosis = [728729236176765039, 728729341063856169, 728729439730663464, 768402508624035880]
            pronoun = [750313724555821067, 751756598371680339, 751756617208299610, 751756588833832991]
            dm = [731580944745496638, 731580985874841652, 731581019697709147]

            # Get all role ids
            for role in roles:
                id = role.id
                # Check if already verified
                if id == verified_id:
                    await message.channel.send(embed=self.meta.embedOops("You're already verified!"))
                    return
                # Check over for required roles
                if id in hypnosis:
                    hypnosis_flag = True
                elif id in pronoun:
                    pronoun_flag = True
                elif id in dm:
                    dm_flag = True

            if not hypnosis_flag:
                msg = await message.channel.send(
                    embed=self.meta.embedOops("You're missing a Hypnosis role. Please get one in #getroles."))
                await msg.delete(delay=60)
                return
            if not pronoun_flag:
                msg = await message.channel.send(
                    embed=self.meta.embedOops("You're missing a Pronoun role. Please get one in #getroles."))
                await msg.delete(delay=60)
                return
            if not dm_flag:
                msg = await message.channel.send(
                    embed=self.meta.embedOops("You're missing a DM role. Please get one in #getroles."))
                await msg.delete(delay=60)
                return

            # Ask if 18+ and read the rules.
            title = f"{message.author.name}'s Verification"
            desc = f"Hi {message.author.mention}!\n\nPlease react with a ✅ to confirm you're **at least 18 years of " \
                   f"age** and " \
                   f"have **read over and accept all of our server rules!**\n\nThis will time out in 2 minutes. "

            msg = await message.channel.send(embed=self.meta.embed(title, desc, 'gold'))
            await msg.add_reaction('✅')

            def check(reaction, user):
                return str(reaction.emoji) == '✅' and user == message.author

            try:
                react, user = await self.client.wait_for('reaction_add', timeout=120.0, check=check)
            except asyncio.TimeoutError:
                await msg.delete()
                return
            else:
                verified = message.guild.get_role(verified_id)
                await message.author.add_roles(verified)
                await msg.delete()

            # Welcome in #general
            general_id = 728736226709864549
            general = message.guild.get_channel(general_id)
            msg = f"🌟 **__Let's all welcome {message.author.mention} to {message.guild.name}!__** 🎉"
            title = f"It's great to have you here, {message.author.name}."
            desc = f"Be sure to ask a moderator if you need any help. \nWhy not start with introducing yourself in " \
                   f"#introductions? "
            embed = discord.Embed(
                title=title,
                description=desc,
                color=discord.Color.gold()
            )
            embed.set_footer(text="Seymour, Your Bear Bot Friend", icon_url="https://media.discordapp.net/attachments"
                                                                            "/388576512359530499/784404037709725716"
                                                                            "/bear.png")
            embed.set_thumbnail(url=message.author.avatar_url)

            await general.send(content=msg, embed=embed)
            return
        else:
            msg = await message.channel.send(embed=self.meta.embedOops("Something's not right. Try checking the "
                                                                       "instructions again or your spelling."))
            await msg.delete(delay=60)
            message.delete(delay=60)


def setup(client):
    database_connection = Database()
    meta_class = Meta(database_connection)
    client.add_cog(Welcome(client, database_connection, meta_class))
