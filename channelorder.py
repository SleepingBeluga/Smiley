from discord.ext import commands
import constants
import datetime, asyncio

class ChanOrder(commands.Cog):
    '''
    For sorting channels
    '''

    def __init__(self, b):
        self.b = b
        self.time = None

    @commands.command()
    async def sort(self, ctx, *args):
        await ctx.send("Sorry! This command has been disabled.")
        return

        if self.time != None:
            delta = datetime.datetime.now() - self.time
            if delta.total_seconds() < 10000:
                await ctx.send("Sorry! This command has been used too recently.")
                return

        self.time = datetime.datetime.now()

        await ctx.send("Sorting channels. Be patient, this process is intentionally slow so as not to mess anything up!")

        async with ctx.typing():

            wdGames = []
            pdGames = []
            archives = []

            for category in constants.wd_categories | constants.pd_categories | constants.archive_categories:
                await sortCategory(self.b.guilds[0], category, ctx)

        await ctx.send("Finished sorting channels!")


async def sortCategory(server, category, ctx):
    channels = [channel for channel in server.channels if channel.category and channel.category.name == category]
    if channels and len(channels):
        start = datetime.datetime.now()
        channels.sort(key=lambda c: c.name)
        base = min(channels, key=lambda c: c.position).position
        for i, channel in enumerate(channels):
            pos = i + base
            attempts = 0
            while pos != channel.position and attempts < 5:
                attempts += 1
                await channel.edit(position=pos)
                await asyncio.sleep(30 + 60 * attempts)
        time_spent = (datetime.datetime.now() - start).total_seconds() / 60
        await ctx.send(f"Sorted {len(channels)} channels in {category} in {time_spent:.1f} minutes.")
