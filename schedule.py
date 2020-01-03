from discord.ext import commands
import datetime

class Session():

    def __init__(self, channel, gm, players, time, summary):
        self.channel = channel
        self.gm = gm
        self.players = players
        self.time = time
        self.summary = summary

    def __str__(self):
        string = "Session in #" + self.channel
        string = "\nGM: <@" + gm + ">"
        if len(players) > 0:
            string += "\n layers: <@" + players[0] + ">"
            for i in players[1:]:
                string += ", <@" + i + ">"
        string += "\nTime: " + time.__str__() + " UTC"
        string += "\nSummary: " + summary
        return string


class Scheduling(commands.Cog):

    def __init__(self):
        self.sched = []

    def isPlayer(self, name):
        match = re.match(r"\<\@[0-9]+\>", name)
        if match:
            return True
        else:
            return False

    @commands.command()
    async def showShed(self, ctx, *args):
        if len(self.sched) == 0:
            await ctx.send("There are no sessions scheduled")
        else:
            for i in self.sched:
                await ctx.send(i.__str__())

    @commands.command()
    async def schedule(self, ctx, *args):
        '''Schedule a session for a given campaign
        Usage: %schedule <game name> <@player> <@player2>... yyyy/mm/dd hh:mm UTC+<timezone> <summary>
        '''
        index = 0
        gameName = args[index].lower()
        found = False
        for ctx.TextChannel in ctx.message.guild.text_channels:
            if (ctx.TextChannel.name == gameName and 
              (ctx.TextChannel.category.name == 'PactDice Games' or 
               ctx.TextChannel.category.name == 'WeaverDice Games')):
                found = ctx.TextChannel
                index += 1
                break

        if not found:
            # Might be running in a channel and assuming it would work
            # Idiot proof this command!
            thisChannel = ctx.message.channel
            if (thisChannel.category.name == 'PactDice Games' or 
               ctx.TextChannel.category.name == 'WeaverDice Games'):
               found = thisChannel
            else:
                await ctx.send("Please specify a real channel")
                return

        gm = str(ctx.message.author.id)

        players = []
        while isPlayer(args[index]):
            players += [ args[index][2:-1] ]
            index += 1

        year, month, day = args[index].split("/")
        index += 1
        hour, minute = args[index].split("/")
        index += 1

        utcOffset = int(args[index][3:])
        index += 1
        summary = ""
        for i in args[index:]:
            summary += i + " "

        time = datetime.datetime(int(year),int(month),int(day),int(hour)+utcOffset,int(minute))
        session = Session(found, gm, players, time, summary)

        self.sched += [ session ]

