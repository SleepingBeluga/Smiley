from discord.ext import commands
import discord, sheets

class Capes(commands.Cog):
    @commands.command()
    async def cape(self, ctx, *args):
        # Search for the cape name
        name = ""
        for arg in args:
            name += arg + " "

        name = name[:-1]
        cape_info = (await sheets.cape(name))
        if cape_info:
            await ctx.send(str(cape_info))
        else:
            await ctx.send("Couldn't find cape!")
