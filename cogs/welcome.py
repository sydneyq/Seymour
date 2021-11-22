import string

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

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Cloudy Bun Hypnosis
        # Verification
        verified_id = 828063151241035817
        newbie_id = 887506236164149298
        general_id = 811695521717551158
        if message.channel.id == 828084629264531476:
            if self.meta.isSelf(message.author) or self.meta.isMod(message.author):
                return

            if self.dbConnection.findServer({"id": str(message.guild.id)})['password'] in message.content.lower():
                await message.delete()
                roles = message.author.roles
                hypnosis_flag = False
                dm_flag = False

                hypnosis = [811695817164849176, 820102999396450344, 811696016641490994, 820102779472838687]
                dm = [828069277344858122, 828069286400229377, 828069280817872927]

                # Get all role ids
                for role in roles:
                    id = role.id
                    # Check if already verified
                    if id == verified_id:
                        msg = await message.channel.send(embed=self.meta.embedOops("You're already verified!"))
                        await msg.delete(delay=60)
                        return
                    # Check over for required roles
                    if id in hypnosis:
                        hypnosis_flag = True
                    elif id in dm:
                        dm_flag = True

                if not hypnosis_flag:
                    msg = await message.channel.send(
                        embed=self.meta.embedOops("You're missing a Hypnosis role. Please get one in #roles."))
                    await msg.delete(delay=60)
                    return
                if not dm_flag:
                    msg = await message.channel.send(
                        embed=self.meta.embedOops("You're missing a DM role. Please get one in #roles."))
                    await msg.delete(delay=60)
                    return

                # Ask if 18+ and read the rules.
                title = f"{message.author.name}'s Verification"
                desc = f"Hi {message.author.mention}!\n\nHow old are you? (for example, 20)." \
                       f"\n\nThis will time out in 2 minutes. "

                msg = await message.channel.send(embed=self.meta.embed(title, desc, 'gold'), delete_after=120)

                def check_age(m):
                    return m.author == message.author and m.channel == message.channel

                try:
                    reply = await self.client.wait_for('message', timeout=120.0, check=check_age)
                except asyncio.TimeoutError:
                    return
                try:
                    age = None
                    for item in reply.content:
                        if item.translate(None, string.punctuation).isnumeric():
                            age = item
                            break
                    age = int(age)
                except:
                    msg = await message.channel.send(embed=self.meta.embedOops(f"{message.author.mention}, I couldn't "
                                                                               f"seem to read your age. Please "
                                                                               f"restart the process."),
                                                     delete_after=120)
                    return

                if age < 18:
                    await message.channel.send(embed=self.meta.embedOops(f"{message.author.mention},\n"
                                              f"`{age}` doesn't seem to be over 18. "
                                              f"\nWe are an 18+ server. <@&828063717194727445>"))
                    return

                # SFW
                title = f"{message.author.name}'s Verification"
                desc = f"Great, {message.author.mention}!\n\nNow, please type and send `Safe For Work` " \
                       f"to verify that you know we're a SFW server. \n\nThis expires in 2 minutes."

                msg = await message.channel.send(embed=self.meta.embed(title, desc, 'gold'), delete_after=120)

                def check_msg(m):
                    return m.author == message.author and m.channel == message.channel \
                           and 'safe for work' in m.content.lower()

                try:
                    reply = await self.client.wait_for('message', timeout=120.0, check=check_msg)
                except asyncio.TimeoutError:
                    return
                if not reply:
                    return

                verified = message.guild.get_role(verified_id)
                newbie = message.guild.get_role(newbie_id)
                await message.author.add_roles(verified)
                await message.author.add_roles(newbie)
                await msg.delete()

                # Welcome in #general
                welcomer_id = 892221189274103868
                general = message.guild.get_channel(general_id)
                msg = f"🌟 **__Let's all welcome {message.author.mention} to {message.guild.name}!__** 🎉 <@&{welcomer_id}>"
                title = f"It's great to have you here, {message.author.name}."
                desc = f"Be sure to ask a moderator if you need any help. \nWhy not start with introducing yourself in " \
                       f"#intros? \nYou'll get access to #request-session and #selfies-and-media when you reach 30 " \
                       f"messages in the server. "
                embed = discord.Embed(
                    title=title,
                    description=desc,
                    color=discord.Color.gold()
                )
                embed.set_footer(text="Seymour, Your Bear Bot Friend",
                                 icon_url="https://media.discordapp.net/attachments"
                                          "/388576512359530499/784404037709725716"
                                          "/bear.png")
                embed.set_thumbnail(url=message.author.avatar_url)

                await general.send(content=msg, embed=embed)
                return
            else:
                msg = await message.channel.send(embed=self.meta.embedOops("Something's not right. Try checking the "
                                                                           "instructions again or your spelling."))
                await msg.delete(delay=60)
                await message.delete(delay=60)
        # 30 messages minimum requirement
        elif 811695521717551154 == message.guild.id:
            if newbie_id in [role.id for role in message.author.roles]:
                newbie = message.guild.get_role(newbie_id)
                profile = self.meta.getProfile(message.author)
                message_count = profile['message_count'] + 1
                if message_count >= 30:
                    await message.author.remove_roles(newbie)
                    general = message.guild.get_channel(general_id)
                    await general.send(f"**{message.author.mention}**, you've reached at least 30 messages and your "
                                       f"Newbie role is removed!")
                self.meta.update_profile(message.author, 'message_count', message_count)
                return


def setup(client):
    database_connection = Database()
    meta_class = Meta(database_connection)
    client.add_cog(Welcome(client, database_connection, meta_class))
