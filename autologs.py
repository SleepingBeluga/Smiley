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
            }
        if args[0] == 'default':
            data[ctx.channel.name] = {
                'start': '||||',
                'end': '||||',
                'GM': ctx.author.display_name,
                'num': 1,
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
        if args[0] == 'reset':
            data = {}
            with open('logchansets.json', 'w+') as filechan:
                json.dump(data, filechan)
            await ctx.send("Channel settings reset.")


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
            }
        endMarker = data[ctx.channel.name]['end']
        startMarker = data[ctx.channel.name]['start']
        GM = data[ctx.channel.name]['GM']
        num = data[ctx.channel.name]['num']
        out = ['error',0]
        thing = {}
        plyrs = []
        loop2startmarkfound = False
        loop2endmarkfound = False
        allmarksfound = False
        loop1startmarkfound = False
        loop1endmarkfound = False
        authCheck = ''
        date = datetime.datetime(int(args[0]),int(args[1]),int(args[2]))
        sets = []
        text = ''

        async with ctx.typing():
            if len(args) == 3:
                async for message in ctx.history(limit=10000,oldest_first=True,after=date):
                        if endMarker in message.content and loop1startmarkfound is True and loop1endmarkfound is False:
                            loop1endmarkfound = True
                            enddate = message.created_at
                            print('check4')
                        if startMarker in message.content and loop1startmarkfound is False and loop1endmarkfound is False:
                            loop1startmarkfound = True
                        if loop1startmarkfound == True and loop1endmarkfound == False and '%' not in message.content and message.author.bot == False:
                            if message.author.display_name not in plyrs and message.author.display_name != GM:
                                plyrs.append(message.author.display_name)
            else:
                await ctx.send("Error with input. Correct command format: %log [year] [month] [day]")

        if loop1startmarkfound == False:
            await ctx.send("Error: Start Marker not found.")
            allmarksfound = True

        if loop1endmarkfound == False:
            await ctx.send("Error: End Marker not found.")
            allmarksfound = True

        # if mark3 == False:
        #     async with ctx.typing():
        #         async for message in ctx.history(limit=10000,oldest_first=True,after=date,before=enddate):
        #             if endMarker in message.content and mark1 is True:
        #                 mark1 = False
        #                 await ctx.send('Logs: https://docs.google.com/document/d/' + str(out[0]))
        #                 return
        #             if startMarker in message.content and mark1 is False:
        #                 mark1 = True
        #                 out = await docs.new_log_doc(thing, ctx.channel.name.capitalize(), num, plyrs)
        #             elif mark1 == True and '%' not in message.content and message.author.bot == False:
        #                 await asyncio.sleep(1)
        #                 if message.author.display_name != authCheck:
        #                     authCheck = message.author.display_name
        #                     out = await docs.add_post(out, message.author.display_name, message.content.replace('||',''))
        #                 else:
        #                     out = await docs.append(out, message.content.replace('||',''))

        if allmarksfound is False:
            async with ctx.typing():
                async for message in ctx.history(limit=10000,oldest_first=True,after=date):
                    if endMarker in message.content and loop2startmarkfound is True and loop2endmarkfound is False:
                        print('check2')
                        await docs.add_text(out, sets, text=text)
                        await ctx.send('Logs: https://docs.google.com/document/d/' + str(out[0]))
                        loop2endmarkfound = True
                    if startMarker in message.content and loop2startmarkfound is False and loop2endmarkfound is False:
                        print('check1')
                        out = await docs.new_log_doc(thing, ctx.channel.name.capitalize(), num, plyrs)
                        loop2startmarkfound = True
                    elif loop2startmarkfound is True and loop2endmarkfound is False and '%' not in message.content and message.author.bot is False:
                        print('check')
                        if message.author.display_name != authCheck:
                            authCheck = message.author.display_name
                            sets.append([len(text)+out[1] + 77,len(text)+out[1]+len(message.author.display_name) + 77])
                            text += " ___________________________________________________________________________\n" + \
                                    message.author.display_name + '\n' + message.content.replace('||','') + '\n'

                        else:
                            text += message.content.replace('||','') + '\n'
                        print('check3')