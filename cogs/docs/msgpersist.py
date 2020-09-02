import discord
from discord.ext import commands

class MsgPersist(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        if isinstance(message.channel, discord.DMChannel):
            return

        if not(message.author.id == 592436047175221259 or message.author.id == 432038389663924225):
            guild = self.client.get_guild(257751892241809408) #Mind Café

            embed = discord.Embed(
                color = discord.Color.teal()
            )

            msgs = []

            async for msg in message.channel.history(limit=3):
                if (msg.author.id == 592436047175221259 or msg.author.id == 432038389663924225):
                    msgs.append(msg)
                    break

            if message.channel.id == 298171110695108618:
                await message.channel.delete_messages(msgs)

                embed.add_field(name = 'Welcome to no-reply!',
                value = '**Reminder that replying to anyone about what they say in here can result in a warning or sanction.**\nRespect others\' wishes when they\'d like to yell into the void.')
                embed.set_footer(text = 'Do not reply to anything here!')
                embed.set_thumbnail(url = 'https://cdn.discordapp.com/emojis/597263007608733709.png')

                await message.channel.send(embed = embed)

            if message.channel.id == 445668581372330005:
                await message.channel.delete_messages(msgs)

                embed.add_field(name = 'Welcome to trigger warning no-reply!',
                value = '**Reminder that replying to anyone about what they say in here can result in a warning or sanction.**\nRespect others\' wishes when they\'d like to yell into the void.')
                embed.set_footer(text = 'Do not reply to anything here!')
                embed.set_thumbnail(url = 'https://cdn.discordapp.com/emojis/597263007608733709.png')

                await message.channel.send(embed = embed)

def setup(client):
    client.add_cog(MsgPersist(client))
