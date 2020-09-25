import discord
import random
from discord.ext import commands
from database import Database
from .meta import Meta


class Actions(commands.Cog):

    def __init__(self, client, database, meta):
        self.client = client
        self.dbConnection = database
        self.meta = meta

    def action(self, author, msg, gif, action_done, action_undone):
        mentions = msg.mentions

        if len(mentions) > 0:
            embed = discord.Embed(
                title=f"{action_undone}!",
                description=f"{', '.join(mention.mention for mention in mentions)}, "
                            f"you've just been {action_done} by {author.mention}!",
                color=discord.Color.teal()
            )
            embed.set_thumbnail(url=gif)
            return embed
        else:
            embed = discord.Embed(
                title=action_undone + '!',
                color=discord.Color.teal()
            )
            embed.set_thumbnail(url=gif)
            return embed

    def has_action(self, member: discord.Member, action: str):
        return False

    @commands.command(pass_context=True, aliases=['*boop*', 'bop', '*bop*'])
    async def boop(self, ctx):
        if not self.has_action(ctx.author, 'boop'):
            await ctx.send(embed=self.meta.embedOops("You need to buy this action to use it!"))
            return

        responses = ['https://media1.tenor.com/images/083ccb85ea107a76b5030cbcb43cbf36/tenor.gif?itemid=7296714',
                     'https://media.tenor.com/images/f6f87118730878c578e0f188da5270fc/tenor.gif',
                     'https://media2.giphy.com/media/12BGUcW8xxpPRS/giphy.gif',
                     'https://i.pinimg.com/originals/ee/85/19/ee851944b03a008493b05b17c1591eac.gif',
                     'http://forgifs.com/gallery/d/245318-2/Sneaky-cat-nose-boop.gif',
                     'https://i.imgur.com/5xTll0w.gif',
                     'https://i.imgur.com/dkLJLrt.gif?noredirect',
                     'https://media1.tenor.com/images/5bd848735bbb12a2b7fa0561de918a0c/tenor.gif?itemid=5375919']

        await ctx.send(embed=self.action(ctx.author, ctx.message, random.choice(responses), 'booped', 'boop'))

    @commands.command(pass_context=True, aliases=['pet', '*pet*', '*pat*'])
    async def pat(self, ctx):
        responses = ['https://cdn.discordapp.com/attachments/257751892241809408/597979644725166097/unknown.gif',
                     'https://i.gifer.com/7A80.gif',
                     'https://media1.tenor.com/images/9bd2eb038544102aa4bb36fb8b0d01f9/tenor.gif?itemid=12437651',
                     'https://25.media.tumblr.com/14be64e13a802d9b16063411134f29b7/tumblr_mfz90qdzaV1r4az5so1_400.gif',
                     'https://media.tenor.com/images/dfe3267cca9596be840fbf9d5e86b747/tenor.gif',
                     'https://media1.tenor.com/images/d6a91b652fd260f7d063bee23cd7f9ee/tenor.gif?itemid=8102480',
                     'https://data.whicdn.com/images/38611077/original.gif',
                     'https://media1.tenor.com/images/ca552807b4720928130e5f188cfbe2c9/tenor.gif?itemid=8061431',
                     'https://media1.tenor.com/images/b89e2aa380639d37b9521b72a266d498/tenor.gif?itemid=4215410']

        await ctx.send(embed=self.action(ctx.author, ctx.message, random.choice(responses), 'patted', 'patpat'))

    @commands.command(pass_context=True, aliases=['*hug*', 'huggle', 'snuggle', 'cuddle', 'snug'])
    async def hug(self, ctx):
        responses = ['https://media1.giphy.com/media/Lb3vIJjaSIQWA/source.gif',
                     'https://treasuredscriptcom.files.wordpress.com/2018/09/hiro-hugging-baymax1.gif',
                     'https://media.giphy.com/media/17Q92poP1qJwI/giphy.gif',
                     'https://gifrific.com/wp-content/uploads/2015/05/Sloth-Hugs-Toy-Animal-and-Falls-Over.gif',
                     'https://media.giphy.com/media/6dsQ68HCZZ1xm/giphy.gif',
                     'https://media2.giphy.com/media/ZaBHSbiLQTmFi/source.gif',
                     'https://media3.giphy.com/media/hdOrhnBB6Enuw/source.gif',
                     'https://i.pinimg.com/originals/f3/48/a9/f348a9ffee1943fbe248fa2dc7eb3f19.gif',
                     'https://66.media.tumblr.com/51a12abd75d1f8f6f9a3846e6d2bd528/tumblr_inline_nmm9z1X2sS1s8zbfz_500.gif',
                     'https://66.media.tumblr.com/c27d1adbe7410191d24c8f62a68695a9/tumblr_inline_nmmazxORzb1s8zbfz_500.gif',
                     'https://media.discordapp.net/attachments/728736226709864549/757723733623570612/tenor.gif']

        await ctx.send(embed=self.action(ctx.author, ctx.message, random.choice(responses), 'hugged', 'hug'))

    @commands.command(aliases=['hit'])
    async def punch(self, ctx):
        if not self.has_action(ctx.author, 'punch'):
            await ctx.send(embed=self.meta.embedOops("You need to buy this action to use it!"))
            return

        responses = ['https://media1.tenor.com/images/e27431e7f3ae7f5e2e8fc4fe4f399754/tenor.gif',
                     'https://media.giphy.com/media/A9sF6v36DEoF2/giphy.gif',
                     'https://media1.tenor.com/images/023ab6036cecc5f2950fb5cada385e2c/tenor.gif',
                     'https://media3.giphy.com/media/xUO4t2gkWBxDi/giphy.gif',
                     'https://i.kym-cdn.com/photos/images/original/001/039/474/715.gif',
                     'https://i.pinimg.com/originals/bc/96/17/bc9617a2460e4640fcd9cf474bea2c10.gif',
                     'https://i.pinimg.com/originals/8d/50/60/8d50607e59db86b5afcc21304194ba57.gif',
                     'https://45.media.tumblr.com/e0697003e811d72dec99dce19599b861/tumblr_o5ubxan17q1rgagxfo1_500.gif',
                     'https://i.imgur.com/Ov3Czn7.gif',
                     'https://thumbs.gfycat.com/PerkyQuickHippopotamus-size_restricted.gif',
                     'https://media1.tenor.com/images/a5eccaade81efc6a496a8d868dde7965/tenor.gif?itemid=5980497',
                     'https://media1.giphy.com/media/1AIPDGxuA35OqWcfGS/giphy.gif',
                     'https://media2.giphy.com/media/PBE8X9yYdoZiw/giphy.gif',
                     'https://media1.giphy.com/media/26BGOkzGKBvrffii4/source.gif',
                     'https://thumbs.gfycat.com/LargeGrimAnkolewatusi-size_restricted.gif',
                     'https://media1.tenor.com/images/3def875ba3e6d95048763aa78182fbfc/tenor.gif',
                     'https://thumbs.gfycat.com/WeepyOrderlyAngelwingmussel-size_restricted.gif',
                     'https://media1.tenor.com/images/d43dbf172a5a795134e54f01ea71e791/tenor.gif']
        await ctx.send(embed=self.action(ctx.author, ctx.message, random.choice(responses), 'punched', 'punch'))

    @commands.command(aliases=['highfive', 'hi5', 'hifive'])
    async def high5(self, ctx):
        responses = ['http://25.media.tumblr.com/f958003a5b13cd0470afc736373ab519/tumblr_n0os0yvKQw1tnvwmho1_500.gif',
                     'https://media2.giphy.com/media/3oEduV4SOS9mmmIOkw/source.gif',
                     'https://i.kym-cdn.com/photos/images/original/001/243/126/c3f.gif',
                     'https://i.pinimg.com/originals/5d/ef/be/5defbe81dc43fe590cd2d6d9a9284ae4.gif',
                     'https://static.fjcdn.com/gifs/High+five_000cd3_5489107.gif',
                     'https://media1.tenor.com/images/1d9b884cf8e3fbb2b86c29e3387b5c0a/tenor.gif?itemid=13496809',
                     'https://media1.tenor.com/images/19e2d653676ce30584b9f0f58245d245/tenor.gif?itemid=9330808',
                     'https://thumbs.gfycat.com/OrnateSaneGerbil-size_restricted.gif',
                     'https://media2.giphy.com/media/3oEjHV0z8S7WM4MwnK/giphy.gif',
                     'https://i.pinimg.com/originals/fc/b1/44/fcb1446b74166b0860ace50ed8b33686.gif']

        await ctx.send(embed=self.action(ctx.author, ctx.message, random.choice(responses), 'highfived', 'highfive'))

    @commands.command()
    async def salute(self, ctx):
        responses = ['https://media0.giphy.com/media/3o7qE5ceqLBHRR0C64/source.gif',
                     'https://media.tenor.co/videos/d114042b809a8804ed3b19b999173595/mp4',
                     'https://media.tenor.co/videos/e63e1f0e1851142a19af9181bee2f7bb/mp4',
                     'https://i.pinimg.com/originals/74/37/ad/7437ade393b61b4993fe79b3bb94c3dc.gif',
                     'https://media3.giphy.com/media/26DNfpeNpx1hSQf1C/giphy.gif',
                     'https://i.gifer.com/AYoH.gif',
                     'https://media.tenor.com/images/8dcf457f157a440d92d59362d1dc83e1/tenor.gif',
                     'https://media1.tenor.com/images/30523d002f276f8436dbcd1e5289ff96/tenor.gif',
                     'https://media1.giphy.com/media/VG1jCySAPvTD2JNyi8/giphy.gif',
                     'https://media.tenor.com/images/b24a29cfbaed590c3632fd7fe3be6a18/tenor.gif',
                     'https://derpicdn.net/img/2017/4/16/1413545/large.gif',
                     'https://3.bp.blogspot.com/-mgQDV6p-2-Q/W1kpETxpe9I/AAAAAAALjeI/-T9g_ash1ZoagB1ICvofpfuD34ONmlR0ACLcBGAs/s1600/AS0004244_04.gif']
        await ctx.send(embed=self.action(ctx.author, ctx.message, random.choice(responses), 'saluted', 'salute'))


def setup(client):
    database_connection = Database()
    meta_class = Meta(database_connection)
    client.add_cog(Actions(client, database_connection, meta_class))
