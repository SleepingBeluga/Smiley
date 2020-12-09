from discord.ext import commands
import discord

class MessageMin(commands.Cog):

    def __init__(self, b):
        self.b = b
        self.lims = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id in self.lims:
            if (not message.author.bot) and (('Mod Team' not in (str(role) for role in message.author.roles)) or ('Author' not in (str(role) for role in message.author.roles))):
                if len(message.content) < self.lims[message.channel.id]:
                    await message.delete()
                    try:
                        await message.author.send("Sorry, #" + str(message.channel.name) + " currently has a minimum character requirement of "  + str(self.lims[message.channel.id]) + ". Your message: ```" + str(message.content) + "``` has been deleted.")
                    except discord.errors.Forbidden:
                        return

    @commands.command()
    async def setmin(self, ctx, *args):
        '''Moderators only. Establish a mimimum character limit for messages in the current channel.
        '''
        if ('Mod Team' not in (str(role) for role in ctx.author.roles)) or ('Author' not in (str(role) for role in ctx.author.roles)):
            await ctx.send("Only moderators may use this command.")
            return
        elif len(args) > 0:
            try:
                self.lims[ctx.message.channel.id] = int(args[0])
                if int(args[0]) == 0:
                    del self.lims[ctx.message.channel.id]
                await ctx.send("Character minimum set to " + args[0] + ".")
            except ValueError:
                await ctx.send("Error: no number found. Please input a character minimum. (I.e. %setmin 20)")
                return
        else:
            await ctx.send("Error: improper format. Please input a character minimum. (I.e. %setmin 20)")
            return
