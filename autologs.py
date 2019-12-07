from discord.ext import commands
import docs, datetime, json

class AutoLogs(commands.Cog):

    @commands.command()
    async def set(self,ctx,*args):
        '''Set options for autologging. Format: %set [timezone] [No comments?] [No marks?] [Format rolls?] [Format discord?]
        Timezone is your timezone's hour difference from UTC, the others are y/n. Example: %set 5 n y y y'''
        data = {}
        with open('logchansets.json', 'r+') as filechan:
            if len(filechan.read()):
                filechan.seek(0)
                data = json.load(filechan)
        if ctx.channel.name not in data:
            data[ctx.channel.name] = {
                'timezone': 5,
                'nocomments': True,
                'nomarks': True,
                'rolls': True,
                'discord': True
            }
        try:
            data[ctx.channel.name]['timezone'] = int(args[0])
        except:
            x=1
        else:
            if len(args) == 5:
                if args[1].lower() == 'y':
                    data[ctx.channel.name]['nocomments'] = True
                elif args[1].lower() == 'n':
                    data[ctx.channel.name]['nocomments'] = False
                if args[2].lower() == 'y':
                    data[ctx.channel.name]['nomarks'] = True
                elif args[2].lower() == 'n':
                    data[ctx.channel.name]['nomarks'] = False
                if args[3].lower() == 'y':
                    data[ctx.channel.name]['rolls'] = True
                elif args[3].lower() == 'n':
                    data[ctx.channel.name]['rolls'] = False
                if args[4].lower() == 'y':
                    data[ctx.channel.name]['discord'] = True
                elif args[4].lower() == 'n':
                    data[ctx.channel.name]['discord'] = False
                with open('logchansets.json', 'w+') as filechan:
                    json.dump(data, filechan)
                await ctx.send("Settings updated.")

        if args[0] == 'default':
            data[ctx.channel.name] = {
                'timezone': 5,
                'nocomments': True,
                'nomarks': True,
                'rolls': True,
                'discord': True
            }
            with open('logchansets.json', 'w+') as filechan:
                json.dump(data, filechan)
            await ctx.send("Settings set to defaults.")

        if args[0] == 'timezone':
            data[ctx.channel.name]['timezone'] = int(args[1])
            with open('logchansets.json', 'w+') as filechan:
                json.dump(data, filechan)
            await ctx.send("Timezone set to UTC(" + args[1] + ").")

        if args[0] == 'nocomments':
            if args[1].lower() == 'y':
                data[ctx.channel.name]['nocomments'] = True
            elif args[1].lower() == 'n':
                data[ctx.channel.name]['nocomments'] = False
            with open('logchansets.json', 'w+') as filechan:
                json.dump(data, filechan)
            await ctx.send("Remove comments? set to " + args[1].upper() + ".")

        if args[0] == 'nomarks':
            if args[1].lower() == 'y':
                data[ctx.channel.name]['nomarks'] = True
            elif args[1].lower() == 'n':
                data[ctx.channel.name]['nomarks'] = False
            with open('logchansets.json', 'w+') as filechan:
                json.dump(data, filechan)
            await ctx.send("Remove marks? set to " + args[1].upper() + ".")

        if args[0] == 'rolls':
            if args[1].lower() == 'y':
                data[ctx.channel.name]['rolls'] = True
            elif args[1].lower() == 'n':
                data[ctx.channel.name]['rolls'] = False
            with open('logchansets.json', 'w+') as filechan:
                json.dump(data, filechan)
            await ctx.send("Format rolls? set to " + args[1].upper() + ".")

        if args[0] == 'discord':
            if args[1].lower() == 'y':
                data[ctx.channel.name]['discord'] = True
            elif args[1].lower() == 'n':
                data[ctx.channel.name]['discord'] = False
            with open('logchansets.json', 'w+') as filechan:
                json.dump(data, filechan)
            await ctx.send("Format discord? set to " + args[1].upper() + ".")

        if args[0] == 'reset':
            data = {}
            with open('logchansets.json', 'w+') as filechan:
                json.dump(data, filechan)
            await ctx.send("Channel settings reset.")


    @commands.command()
    async def log(self, ctx, *args):
        '''Create a log with the current options. Format: %log [yy]-[MM]-[dd]-[hh]-[mm] [yy]-[MM]-[dd]-[hh]-[mm]
        First date/time is where to start logging, last date/time is where to stop. Use military time for hours.'''
        data = {}
        with open('logchansets.json', 'r+') as filechan:
            if len(filechan.read()):
                filechan.seek(0)
                data = json.load(filechan)
        if ctx.channel.name not in data:
            data[ctx.channel.name] = {
                'timezone': 5,
                'nocomments': True,
                'nomarks': True,
                'rolls': True,
                'discord': True
            }

        thing = {}
        plyrs = []
        authCheck = ''
        postStarts = []
        nameEnds = []
        text = ''
        postCount = 0
        rollInds = []
        boldInds = []
        italicInds = []
        underInds = []
        strikeInds = []
        priorPoster = ''

        date1 = datetime.datetime.strptime(args[0],'%y-%m-%d-%H-%M') - datetime.timedelta(hours=(data[ctx.channel.name]['timezone']))
        date2 = datetime.datetime.strptime(args[1],'%y-%m-%d-%H-%M') + datetime.timedelta(seconds=59) - datetime.timedelta(hours=(data[ctx.channel.name]['timezone']))


        async with ctx.typing():
            if len(args) == 2:
                async for message in ctx.history(limit=10000,oldest_first=True,after=date1,before=date2):
                    if message.author.display_name not in plyrs:
                        plyrs.append(message.author.display_name)
            else:
                await ctx.send("Error with input. Correct command format for start and end log dates: %log [yy-MM-dd-hh-mm] [yy-MM-dd-hh-mm]")
                return

        out = await docs.new_log_doc(thing, ctx.channel.name, plyrs)

        async with ctx.typing():
            async for message in ctx.history(limit=10000,oldest_first=True,after=date1,before=date2):
                if message.author.display_name != authCheck:
                    postCount += 1
                    authCheck = message.author.display_name
                    postStarts.append(len(text) + out[1])
                    nameEnds.append(len(text) + out[1] + len(message.author.display_name))
                    text += message.author.display_name + '\n' + \
                            message.content.replace('\n\n', '\n') + '\n'
                else:
                    text += message.content.replace('\n\n','\n') + '\n'
                if data[ctx.channel.name]['nomarks']:
                    text = text.replace('\n|', '').replace('|', '').replace('\n...\n', '\n')
                if data[ctx.channel.name]['nocomments']:
                    comStart = text.find('((')
                    while (comStart != -1):
                        comEnd = text.find('))')
                        if comEnd != -1:
                            oldtext = text
                            text = oldtext[:comStart] + oldtext[comEnd + 3:]
                        comStart = text.find('((')
                if data[ctx.channel.name]['rolls']:
                    rollStart = text.find('\n%')
                    if rollStart != -1:
                        rollEnd = text.find('[^_^]')
                        if rollEnd == -1:
                            priorPoster = message.author.display_name
                            postCount -= 1
                        else:
                            authCheck = priorPoster
                            rollInds.append([rollStart, postCount, rollStart + len(message.content) + 11])
                            oldtext = text
                            text = oldtext[:rollStart] + "\n    ROLL: " + oldtext[rollEnd + 6:]
                            postStarts.pop(len(postStarts)-1)
                            nameEnds.pop(len(nameEnds)-1)
                if data[ctx.channel.name]['discord']:
                    starStart = text.find('*')
                    dashStart = text.find('__')
                    squigStart = text.find('~~')
                    while (starStart != -1) or (dashStart != -1) or (squigStart != -1):
                        if starStart < 0:
                            starStart += 2000000000
                        if dashStart < 0:
                            dashStart += 2000000000
                        if squigStart < 0:
                            squigStart += 2000000000
                        if (0 < starStart < squigStart) and (0 < starStart < dashStart ):
                            if text[starStart + 1] == '*':
                                starEnd = text.find('**', starStart + 3)
                                if starEnd != -1:
                                    boldInds.append([starStart - 1, postCount, starEnd - 3])
                                text = text.replace('**', '', 2)
                            else:
                                starEnd = text.find('*', starStart + 2)
                                if starEnd != -1:
                                    italicInds.append([starStart - 1, postCount, starEnd - 2])
                                text = text.replace('*', '', 2)
                        elif (0 < dashStart < squigStart) and (0 < dashStart < starStart):
                            dashEnd = text.find('__', dashStart + 3)
                            if dashEnd != -1:
                                underInds.append([dashStart - 1, postCount, dashEnd - 3])
                            text = text.replace('__', '', 2)
                        elif (0 < squigStart < starStart) and (0 < squigStart < dashStart):
                            squigEnd = text.find('~~', squigStart + 3)
                            if squigEnd != -1:
                                strikeInds.append([squigStart - 1, postCount, squigEnd - 3])
                            text = text.replace('~~', '', 2)
                        starStart = text.find('*')
                        dashStart = text.find('__')
                        squigStart = text.find('~~')

        inds = [rollInds,boldInds,italicInds,underInds,strikeInds]
        postStarts.append(len(text))
        await docs.add_text(out, postStarts, nameEnds, text=text, ind=inds)
        await ctx.send('Logs: https://docs.google.com/document/d/' + str(out[0]))

        with open('logchansets.json', 'w+') as filechan:
            json.dump(data, filechan)
