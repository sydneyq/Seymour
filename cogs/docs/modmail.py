import discord
from discord.ext import commands
from database import Database
from cogs.meta import Meta

class ModMail(commands.Cog):

    def __init__(self, client, database, meta):
        self.client = client
        self.dbConnection = database
        self.meta = meta

    @commands.command(aliases=['mm', 'mmreply', 'reply', 'modmail'])
    async def replymm(self, ctx):
        if not self.meta.isMod(ctx.author):
            return
        if not self.meta.isModMailChannel(ctx.channel):
            return

        user_id = self.meta.getChannelOwnerID(ctx.channel)
        user = discord.utils.get(self.client.get_all_members(), id=user_id)

        if user is None:
            await ctx.send('Sorry, I can\'t send your message. The user has left the server.')

        content = ctx.message.clean_content
        #if content.startswith('+'):
        content = content[content.find(' ') + 1:]
        content = content.replace('+mm', '')
        content = content.replace('=mm', '')
        attachments = ctx.message.attachments
        #links = ''
        #for attachment in attachments:
        #    links += '\n' + attachment.url
        link = ''
        if not (attachments is None or len(attachments) <= 0):
            link = attachments[0].url
        else:
            if content == '' or content == ' ':
                return

        embed = discord.Embed(
            title = 'A Staff Member says:',
            description = content,
            color = discord.Color.red()
        )
        if link != '':
            embed.set_image(url = link)

        await user.send(embed = embed)

        embed.set_footer(text=ctx.author.name, icon_url = ctx.author.avatar_url)

        await ctx.message.delete()
        await ctx.send(embed = embed)

    #modmail DM listener
    @commands.Cog.listener()
    async def on_message(self, message):
        #the bot itself
        if self.meta.isSelf(message.author):
            return

        if isinstance(message.channel, discord.DMChannel):
            #check if Modmail category has a channel of them already
            guild = self.client.get_guild(257751892241809408) #Mind Café
            category = 0

            for c in guild.categories:
                if c.name.lower() == 'modmail':
                    category = c #ModMail

            if category == 0:
                #await message.author.dm_channel.send('I can\'t seem to find ModMail.')
                return

            channels = category.text_channels
            userChannel = 0

            attachments = message.attachments
            link = ''
            if not (attachments is None or len(attachments) <= 0):
                link = attachments[0].url

            embed = discord.Embed(
                title = message.author.name + ' says:',
                description = message.content,
                color = discord.Color.teal()
            )

            if link != '':
                embed.set_image(url = link)

            embed.set_footer(text=message.author.name, icon_url = message.author.avatar_url)

            for channel in channels:
                if channel.name.endswith(str(message.author.id)):
                    userChannel = channel.id
                    #await message.author.dm_channel.send('I\'ve found the channel.')

            #if yes, send their msg in that category
            if userChannel != 0:
                #await message.author.dm_channel.send('I\'m sending into an existing channel.')
                chn = guild.get_channel(userChannel)
                await chn.send(embed = embed)
            #if not, create new channel then send msg
            else:
                #await message.author.dm_channel.send('I\'m creating a new channel.')
                newChannel = await guild.create_text_channel('MM-' + message.author.name + '-' + str(message.author.id), category = category)
                await newChannel.send('__New ModMail ticket created by **' + message.author.name + '**.__ <@&592070664169455616>')
                await newChannel.send(embed = embed)

async def setup(client):
    database_connection = Database()
    meta_class = Meta(database_connection)
    await client.add_cog(ModMail(client, database_connection, meta_class))
