import discord
from discord.ext import commands
from discord.utils import get
from .meta import Meta
from database import Database
import secret
import json
import os

class Support(commands.Cog):

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

    #support-ticket reset
    @commands.command(aliases=['resetST'])
    async def reset(self, ctx):
        isAdmin = self.meta.isAdmin(ctx.author)
        isMod = self.meta.isMod(ctx.author)
        isCertified = self.meta.isCertified(ctx.author)
        isChannelOwner = self.meta.isChannelOwner(ctx.author, ctx.channel)
        log = ctx.guild.get_channel(self.ids['LOG_CHANNEL'])
        channel = ctx.channel
        guild = ctx.guild

        if isMod or isCertified or isChannelOwner:
            if channel.name.startswith('s-'):
                channel = ctx.message.channel
                guild = self.client.get_guild(257751892241809408) #Mind Café
                userID = int(channel.name[channel.name.rfind('-')+1:])
                category = 0
                log = 0
                message = ctx.message

                #finding log channel
                for ch in guild.text_channels:
                    if ch.name.lower() == 'log':
                        log = guild.get_channel(ch.id)
                        break

                await channel.edit(sync_permissions = True)

                embed = discord.Embed(
                    title = 'Channel reset! ✅',
                    color = discord.Color.teal()
                )
                await ctx.send(embed = embed)
            else:
                embed = discord.Embed(
                    title = 'This doesn\'t seem to be a Support Ticket channel...',
                    color = discord.Color.teal()
                )
                await ctx.send(embed = embed)
        else:
            embed = discord.Embed(
                title = 'Sorry, only the Support Ticket Owner and Moderators+ are able to use that command.',
                color = discord.Color.teal()
            )
            await ctx.send(embed = embed)

    #support-ticket certified only
    @commands.command(aliases=['deny'])
    async def remove(self, ctx, member: discord.Member):
        isAdmin = self.meta.isAdmin(ctx.author)
        isMod = self.meta.isMod(ctx.author)
        isCertified = self.meta.isCertified(ctx.author)
        isChannelOwner = self.meta.isChannelOwner(ctx.author, ctx.channel)
        log = ctx.guild.get_channel(self.ids['LOG_CHANNEL'])
        channel = ctx.channel
        guild = ctx.guild

        if not isMod or isCertified or isChannelOwner:
            await ctx.send(embed = self.meta.embedOops())
            return

        if self.meta.isMod(member) or self.meta.isCertified(member) or isChannelOwner(member, ctx.channel):
            await ctx.send(embed = self.meta.embedOops())
            return

        if not channel.name.startswith('s-') and not isAdmin:
                await ctx.send(embed = self.meta.embedOops())
                return
        channel = ctx.message.channel
        guild = self.client.get_guild(257751892241809408) #Mind Café
        userID = int(channel.name[channel.name.rfind('-')+1:])
        category = 0
        log = 0
        message = ctx.message

        #finding log channel
        for ch in guild.text_channels:
            if ch.name.lower() == 'log':
                log = guild.get_channel(ch.id)
                break

        newChannel = channel

        if (member != None):
            await newChannel.set_permissions(member, send_messages=False)

            embed = discord.Embed(
                title = 'Removed ' + str(member.name) + '! ✅',
                color = discord.Color.teal()
            )
            await ctx.send(embed = embed)
        else:
            embed = discord.Embed(
                title = 'Please pass in a member you\'d like to remove.',
                color = discord.Color.teal()
            )
            await ctx.send(embed = embed)

    #support-ticket certified only
    @commands.command(aliases=['invite'])
    async def add(self, ctx, member: discord.Member = None):
        isAdmin = self.meta.isAdmin(ctx.author)
        isMod = self.meta.isMod(ctx.author)
        isCertified = self.meta.isCertified(ctx.author)
        isChannelOwner = self.meta.isChannelOwner(ctx.author, ctx.channel)
        log = ctx.guild.get_channel(self.ids['LOG_CHANNEL'])
        channel = ctx.channel
        guild = ctx.guild

        if isMod or isCertified or isChannelOwner:
            if channel.name.startswith('s-'):
                channel = ctx.message.channel
                guild = self.client.get_guild(257751892241809408) #Mind Café
                userID = int(channel.name[channel.name.rfind('-')+1:])
                category = 0
                log = 0
                message = ctx.message

                #finding log channel
                for ch in guild.text_channels:
                    if ch.name.lower() == 'log':
                        log = guild.get_channel(ch.id)
                        break

                newChannel = channel

                if (member != None):
                    await newChannel.set_permissions(member, read_messages=True, send_messages=True)

                    embed = discord.Embed(
                        title = 'Added ' + str(member.name) + '! ✅',
                        color = discord.Color.teal()
                    )
                    await ctx.send(embed = embed)
                else:
                    embed = discord.Embed(
                        title = 'Please pass in a member you\'d like to invite.',
                        color = discord.Color.teal()
                    )
                    await ctx.send(embed = embed)
            else:
                embed = discord.Embed(
                    title = 'This doesn\'t seem to be a Support Ticket channel...',
                    color = discord.Color.teal()
                )
                await ctx.send(embed = embed)
        else:
            embed = discord.Embed(
                title = 'Sorry, only the Support Ticket Owner and Moderators+ are able to use that command.',
                color = discord.Color.teal()
            )
            await ctx.send(embed = embed)

    #support-ticket lockdown
    @commands.command(aliases=['lockdown', 'lockST', 'lockdownST'])
    async def lock(self, ctx):
        isAdmin = self.meta.isAdmin(ctx.author)
        isMod = self.meta.isMod(ctx.author)
        isCertified = self.meta.isCertified(ctx.author)
        isChannelOwner = self.meta.isChannelOwner(ctx.author, ctx.channel)
        log = ctx.guild.get_channel(self.ids['LOG_CHANNEL'])
        channel = ctx.channel
        guild = ctx.guild

        if isMod or isCertified or isChannelOwner:
            if channel.name.startswith('s-'):
                channel = ctx.message.channel
                guild = self.client.get_guild(257751892241809408) #Mind Café
                userID = int(channel.name[channel.name.rfind('-')+1:])
                category = 0
                log = 0
                message = ctx.message

                #finding log channel
                for ch in guild.text_channels:
                    if ch.name.lower() == 'log':
                        log = guild.get_channel(ch.id)
                        break

                newChannel = channel

                role = guild.get_role(257751892241809408)
                spiritsRole = guild.get_role(591398086635552788)
                certifiedRole = guild.get_role(597781064718745660)
                modRole = guild.get_role(592070664169455616)
                await newChannel.set_permissions(role, read_messages=False)
                await newChannel.set_permissions(spiritsRole, read_messages=True, send_messages=False)
                await newChannel.set_permissions(self.client.get_user(userID), read_messages=True, send_messages=True)
                await newChannel.set_permissions(certifiedRole, read_messages=True, send_messages=False)
                await newChannel.set_permissions(modRole, read_messages=True, send_messages=True)

                await log.send('<@' + str(message.author.id) + '> has switched ' + '<#' + str(newChannel.id) + '> to Lockdown.')

                embed = discord.Embed(
                    title = 'Channel is on Lockdown! ✅',
                    color = discord.Color.teal()
                )
                await ctx.send(embed = embed)
            else:
                embed = discord.Embed(
                    title = 'This doesn\'t seem to be a Support Ticket channel...',
                    color = discord.Color.teal()
                )
                await ctx.send(embed = embed)
        else:
            embed = discord.Embed(
                title = 'Sorry, only the Support Ticket Owner and Moderators+ are able to use that command.',
                color = discord.Color.teal()
            )
            await ctx.send(embed = embed)

    #support-ticket certified only
    @commands.command()
    async def peerlock(self, ctx):
        isAdmin = self.meta.isAdmin(ctx.author)
        isMod = self.meta.isMod(ctx.author)
        isCertified = self.meta.isCertified(ctx.author)
        isChannelOwner = self.meta.isChannelOwner(ctx.author, ctx.channel)
        log = ctx.guild.get_channel(self.ids['LOG_CHANNEL'])
        channel = ctx.channel
        guild = ctx.guild

        if isMod or isCertified or isChannelOwner:
            if channel.name.startswith('s-'):
                channel = ctx.message.channel
                guild = self.client.get_guild(257751892241809408) #Mind Café
                userID = int(channel.name[channel.name.rfind('-')+1:])
                category = 0
                log = 0
                message = ctx.message

                #finding log channel
                for ch in guild.text_channels:
                    if ch.name.lower() == 'log':
                        log = guild.get_channel(ch.id)
                        break

                newChannel = channel

                role = guild.get_role(257751892241809408)
                spiritsRole = guild.get_role(591398086635552788)
                certifiedRole = guild.get_role(597781064718745660)
                modRole = guild.get_role(592070664169455616)
                await newChannel.set_permissions(role, read_messages=False)
                await newChannel.set_permissions(spiritsRole, read_messages=True, send_messages=False)
                await newChannel.set_permissions(self.client.get_user(userID), read_messages=True, send_messages=True)
                await newChannel.set_permissions(certifiedRole, read_messages=True, send_messages=True)
                await newChannel.set_permissions(modRole, read_messages=True, send_messages=True)

                await log.send('<@' + str(message.author.id) + '> has switched ' + '<#' + str(newChannel.id) + '> to Certified.')

                embed = discord.Embed(
                    title = 'Channel is now Certified-only! ✅',
                    color = discord.Color.teal()
                )
                await ctx.send(embed = embed)
            else:
                embed = discord.Embed(
                    title = 'This doesn\'t seem to be a Support Ticket channel...',
                    color = discord.Color.teal()
                )
                await ctx.send(embed = embed)
        else:
            embed = discord.Embed(
                title = 'Sorry, only the Support Ticket Owner and Moderators+ are able to use that command.',
                color = discord.Color.teal()
            )
            await ctx.send(embed = embed)

    #support-ticket create channel
    @commands.command()
    async def support(self, ctx, *, topic = ''):
        if self.meta.isRestricted(ctx.author):
            await ctx.send(embed = self.meta.embed('Oops!', 'Sorry, those with the Blindfolded role are not able to create support channels.'))
            return

        if ('support' in ctx.message.channel.name):
            channel = ctx.message.channel
            guild = self.client.get_guild(257751892241809408) #Mind Café
            category = 0
            log = 0
            message = ctx.message

            log = guild.get_channel(self.ids['LOG_CHANNEL'])

            #finding support-ticket category
            for c in guild.categories:
                if c.name.lower() == 'support-tickets':
                    category = c #Support-Tickets

            #error message if no support-ticket category exists
            if category == 0 and log != 0:
                await log.send('I can\'t seem to find Support-Tickets.')
                return

            newChannel = await guild.create_text_channel('s-' + message.author.name + '-' + str(message.author.id), category = category)

            embed = discord.Embed(
                title = 'Support Ticket Setup',
                description = 'Gotcha! ✅\n<#' + str(newChannel.id) + '>',
                color = discord.Color.teal()
            )

            await ctx.send(embed = embed)
            await newChannel.set_permissions(ctx.author, read_messages=True, send_messages=True)

            if (topic != ''):
                await newChannel.edit(topic = topic)

            if ('nsfw' in topic.lower() or self.meta.hasWord(topic.lower(), 'tw')):
                await newChannel.edit(nsfw = True)
                role = guild.get_role(257751892241809408)
                spiritsRole = guild.get_role(591398086635552788)
                nsfwRole = guild.get_role(445667601386045450)
                await newChannel.set_permissions(role, read_messages=False)
                await newChannel.set_permissions(spiritsRole, read_messages=False)
                await newChannel.set_permissions(message.author, read_messages=True)
                await newChannel.set_permissions(nsfwRole, read_messages=True)


            if ('test' not in topic.lower()):
                await newChannel.send('__New Support Ticket created by **<@' + str(message.author.id) + '>**.__ <@&300743585584906240>')

            embed2 = discord.Embed(
                title = 'Support Ticket Help',
                description = 'Only Support Ticket Owners, Peer Listeners, and Moderators+ may use commands.',
                color = discord.Color.teal()
            )

            embed2.add_field(name = 'Control Commands',
            value = '`+archive`\t\tArchive this channel when finished\n`+switch`\t\tChange this channel to Trigger Warning (TW)')

            embed2.add_field(name = 'Access Commands',
            value = '`+lockdown`\t\tRemove all public access to type in the channel\n`+invite <@user>`\t\tAllow a specific person to type in the channel\n`+remove <@user>`\t\tDisallow a specific person to type in the channel\n`+reset`\t\tReset the channel to default access')

            embed2.add_field(name = 'Help Repping',
            value = 'Want to thank someone for supporting you? `+helpedby @user` gives them a Help point!')

            msg = await newChannel.send(embed = embed2)
            await msg.pin()

            await log.send('New Support Ticket created by <@' + str(message.author.id) + '>. ' + '<#' + str(newChannel.id) + '>')
            if (topic != ''):
                msg = await newChannel.send("Topic: " + topic)
                await msg.pin()

async def setup(client):
    database_connection = Database()
    meta_class = Meta(database_connection)
    await client.add_cog(Support(client, database_connection, meta_class))
