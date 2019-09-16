from discord.ext import commands
import docs, discord, datetime, json, asyncio

class AutoLogs(commands.Cog):

    @commands.command()
    async def logtest(self,ctx,*args):
        test = {}
        out = await docs.new_log_doc(test, 'Test', 1, ['Jack','Jill','Jane','Joe'])
        await ctx.send('Logs: https://docs.google.com/document/d/' + str(out[0]))

        out = await docs.add_post(out, 'Jack', 'fuck u Jill')
        out = await docs.add_post(out, 'Jill', 'no fuck u')
        out = await docs.add_post(out, 'Jane', 'stfu')


    @commands.command()
    async def set(self,ctx,*args):
        data = {}
        with open('logchansets.json', 'r+') as filechan:
            if len(filechan.read()):
                filechan.seek(0)
                data = json.load(filechan)
        if ctx.channel.name not in data:
            data[ctx.channel.name] = {
                'start':'||||',
                'end':'||||',
                'GM':ctx.author.display_name,
                'num':1,
                'pause':'|||'
            }
        if args[0] == 'default':
            data[ctx.channel.name] = {
                'start': '||||',
                'end': '||||',
                'GM': ctx.author.display_name,
                'num': 1,
                'pause':'|||'
            }
            with open('logchansets.json', 'w+') as filechan:
                json.dump(data, filechan)
            await ctx.send("Settings set to defaults.")
        if args[0] == 'start':
            data[ctx.channel.name]['start'] = args[1]
            with open('logchansets.json', 'w+') as filechan:
                json.dump(data, filechan)
            await ctx.send("Start mark set to " + args[1] + ".")
        if args[0] == 'end':
            data[ctx.channel.name]['end'] = args[1]
            with open('logchansets.json', 'w+') as filechan:
                json.dump(data, filechan)
            await ctx.send("End mark set to " + args[1] + ".")
        if args[0] == 'GM':
            data[ctx.channel.name]['GM'] = args[1]
            with open('logchansets.json', 'w+') as filechan:
                json.dump(data, filechan)
            await ctx.send("GM set to " + args[1] + ".")
        if args[0] == 'num':
            data[ctx.channel.name]['num'] = int(args[1])
            with open('logchansets.json', 'w+') as filechan:
                json.dump(data, filechan)
            await ctx.send("Session number set to " + args[1] + ".")
        if args[0] == 'pause':
            data[ctx.channel.name]['pause'] = args[1]
            with open('logchansets.json', 'w+') as filechan:
                json.dump(data, filechan)
            await ctx.send("Pause marker set to " + args[1] + ".")


    @commands.command()
    async def log(self, ctx, *args):
        data = {}
        with open('logchansets.json', 'r+') as filechan:
            if len(filechan.read()):
                filechan.seek(0)
                data = json.load(filechan)
        if ctx.channel.name not in data:
            data[ctx.channel.name] = {
                'start':'||||',
                'end':'||||',
                'GM':ctx.author.display_name,
                'num':1,
                'pause':'|||'
            }
        endMarker = data[ctx.channel.name]['end']
        startMarker = data[ctx.channel.name]['start']
        GM = data[ctx.channel.name]['GM']
        num = data[ctx.channel.name]['num']
        pause = data[ctx.channel.name]['pause']
        out = ['error',0]
        thing = {}
        plyrs = []
        mark1 = False
        mark2 = False
        mark3 = False
        mark4 = False
        mark5 = False
        mark6 = False
        mark7 = False
        authCheck = ''
        date = datetime.datetime(int(args[0]),int(args[1]),int(args[2]))

        async with ctx.typing():
            async for message in ctx.history(limit=10000,oldest_first=True,after=date):
                if len(args) == 3:
                    if message.created_at.year == int(args[0]) and message.created_at.month == int(args[1]) and message.created_at.day == int(args[2]):
                        mark4 = True
                    if mark4 == True:
                        if message.content==endMarker and mark5 is True:
                            mark6 = True
                        if message.content==startMarker and mark5 is False:
                            mark5 = True
                        elif mark5 == True and '%' not in message.content and message.author.display_name is not '[＾_＾]':
                            if message.author.display_name not in plyrs and message.author.display_name != GM:
                                plyrs.append(message.author.display_name)
                else:
                    await ctx.send("Error with input. Correct command format: %log [year] [month] [day]")
        if mark4 == False:
            await ctx.send("Error: Given date not found.")
            return
        elif mark5 == False:
            await ctx.send("Error: Start Marker not found.")
            return
        elif mark6 == False:
            await ctx.send("Error: End Marker not found.")
            return
        else:
            mark3 = True

        async with ctx.typing():
            if mark3 == True:
                async for message in ctx.history(limit=10000,oldest_first=True,after=date):
                    if message.created_at.year == int(args[0]) and message.created_at.month == int(args[1]) and message.created_at.day == int(args[2]):
                        mark2 = True
                    if mark2 == True:
                        if endMarker in message.content and mark1 is True:
                            mark1 = False
                            await ctx.send('Logs: https://docs.google.com/document/d/' + str(out[0]))
                            return
                        if message.content == pause and mark1 is True:
                            if mark7 == False:
                                mark7 = True
                            else:
                                mark7 = False
                        if startMarker in message.content and mark1 is False:
                            mark1 = True
                            out = await docs.new_log_doc(thing, ctx.channel.name.capitalize(), num, plyrs)
                        elif mark1 == True and mark7 == False and  '%' not in message.content and message.author.display_name is not '[＾_＾]':
                            await asyncio.sleep(1)
                            if message.author.display_name != authCheck:
                                authCheck = message.author.display_name
                                out = await docs.add_post(out, message.author.display_name, message.content)
                            else:
                                out = await docs.append(out, message.content)
