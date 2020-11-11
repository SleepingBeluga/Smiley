from discord.ext import commands
import datetime

class ChanOrder(commands.Cog):
    '''
    For sorting channels
    '''

    def __init__(self, b):
        self.b = b
        self.time = None

    @commands.command()
    async def sort(self, ctx, *args):

        if self.time != None:
            delta = datetime.datetime.now() - self.time
            if delta.total_seconds() < 3600:
                await ctx.send("Sorry! This command may only be used once an hour, to avoid spam/abuse.")
                return

        self.time = datetime.datetime.now()

        await ctx.send("Sorting channels...")

        async with ctx.typing():

            wdGames = []
            pdGames = []
            archives = []
            pos = 0

            for server in self.b.guilds:
                for channel in server.channels:
                    if channel.category == None:
                        pass
                    elif channel.category.name in ('WeaverDice Games', 'WeaverDice Games 2'):
                        wdGames.append(channel)
                    elif channel.category.name in ('PactDice Games', 'PactDice Games 2'):
                        pdGames.append(channel)
                    elif channel.category.name in ('Archives', 'Archives 2'):
                        archives.append(channel)

            def getName(c):
                return c.name

            wdGames.sort(key=getName)
            for chan in wdGames:
                if chan.position != pos:
                    await chan.edit(position=pos)
                pos += 1

            pdGames.sort(key=getName)
            for chan in pdGames:
                if chan.position != pos:
                    await chan.edit(position=pos)
                pos += 1

            archives.sort(key=getName)
            for chan in archives:
                if chan.position != pos:
                    await chan.edit(position=pos)
                pos += 1

        await ctx.send("Channels sorted!")
