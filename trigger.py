from discord.ext import commands
import discord, sheets

class Trigger(commands.Cog):
    
    @commands.command()
    async def trigger(self, ctx, *args):
        '''Get a trigger for a character. Can specify index starting from 1.
        '''
        if len(args) > 0:
            index = int(args[0])
            t = (await sheets.trigger(index))
        else:
            index = 0
            t = (await sheets.trigger(0))

        if str(t) != "":
            await ctx.send(t)
        else:
            await ctx.send("Could not find a trigger at " + str(index))

    @commands.command()
    async def used(self, ctx, *args):
        '''Get a used trigger. Can specify index starting from 1.
        '''
        if len(args) > 0:
            index = int(args[0])
            t = (await sheets.used(index))
        else:
            index = 0
            t = (await sheets.used(0))
        
        if str(t) != "":
            await ctx.send(t)
        else:
            await ctx.send("Could not find a used trigger at " + str(index))

        