from discord.ext import commands
import discord, sheets
import difflib # Used to find closest name for enter command

async def debug(ctx, message):
    '''Prints a message in the context passed
    '''
    await ctx.send(message)

class Game_Channels(commands.Cog):
    # - - - - Absolute mess of code below. Mostly channel stuff. Tread at your own risk. - - - -
    @commands.command()
    async def campaigns(self, ctx, *args):
        '''Get the link to the campaigns spreadsheet
        '''
        await ctx.send("Campaign list: https://docs.google.com/spreadsheets/d/" + sheets.ID1)

    @commands.command()
    async def addgame(self, ctx, *args):
        '''Create a WD or PD game with you as the GM
        '''
        gameType = args[0].lower()
        if (gameType != 'wd' and gameType != 'pd'):
            await ctx.send("Please write out your game's name after the command (i.e. %addgame pd New York)")
            return
        gameName = ''
        gameMaster = None
        #gameRole = None
        gamecat = None

        for arg in args[1:]:
            gameName = gameName + str(arg).lower()

        # List of restricted titles
        restricted_names = ['all', 'allactive', 'wdall', 'pdall', 'allarchive']
        if gameName in restricted_names:
            await ctx.send(gameName + " is a restricted term and you can't name your game that. Sorry!")
            return

        if gameName == '':
            await ctx.send("Please write out your game's name after the command (i.e. %addgame pd New York)")
        else:

        #    roleName = gameName + 'er'

        #    await ctx.guild.create_role(name=roleName)

            for role in ctx.message.guild.roles:
                if role.name == 'Game Master':
                    gameMaster = role
                #elif discord.Role.name == roleName:
                 #   gameRole = discord.Role

            await ctx.author.add_roles(gameMaster)

            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                #gameRole: discord.PermissionOverwrite(read_messages=True),
                ctx.author: discord.PermissionOverwrite(read_messages=True),
                ctx.me: discord.PermissionOverwrite(read_messages=True)
            }

            for category in ctx.guild.categories:
                if (category.name == 'PactDice Games' and gameType == 'pd'):
                    gamecat = category
                elif (category.name == 'WeaverDice Games' and gameType == 'wd'):
                    gamecat = category

            await ctx.message.guild.create_text_channel(gameName, category=gamecat, overwrites=overwrites)
            await sheets.newgame(str('#' + gameName),str(ctx.author.id), str(gameType).upper())

    @commands.command()
    async def enter(self, ctx, *args):
        '''Join a game channel. Do not need to specify whether a wd or pd game.

        Special argument includes wdall, pdall, allactive, allarchive, all
        '''
        gameName = ''
        game = None
        check = False
        debugging = False

        if args[0].lower() == "wd" or args[0].lower() == "pd":
            args[0] = ""

        for arg in args:
            if arg.lower() == "-d":
                debugging = True
                continue
            gameName = gameName + str(arg).lower()

        joinAllWD = False
        joinAllPD = False
        joinAllArchive = False

        if gameName in ['wdall', 'all', 'allactive']:
            joinAllWD = True
        if gameName in ['pdall', 'all', 'allactive']:
            joinAllPD = True
        if gameName in ['all', 'allarchive']:
            joinAllArchive = True

        # Let's track some info for debugging
        joining = "We are trying to join "
        channelsJoined = 0
        applicableChannels = []

        for channel in ctx.guild.channels:
            # First lets just check whether they want all games!
            if not channel.category:
                continue
            # If the channel has no category, move to the next channel
            catName = channel.category.name
            if (catName in ['PactDice Games', 'WeaverDice Games', 'Archives']):
                applicableChannels += [channel.name]
            if joinAllWD and catName == 'WeaverDice Games':
                joining += channel.name + ", "
                channelsJoined += 1
                await channel.set_permissions(ctx.author, read_messages=True)
            elif joinAllPD and catName == 'PactDice Games':
                joining += channel.name + ", "
                channelsJoined += 1
                await channel.set_permissions(ctx.author, read_messages=True)
            elif joinAllArchive and catName == 'Archives':
                joining += channel.name + ", "
                channelsJoined += 1
                await channel.set_permissions(ctx.author, read_messages=True)
            if channel.name == gameName:
                game = channel
                joining += game.name
                check = (catName in ['PactDice Games', 'WeaverDice Games', 'Archives'])

        # Let's do some debugging
        if debugging:
            await debug(ctx, joining)
            if channelsJoined > 0:
                await debug(ctx, "That is trying to join " + channelsJoined)

        if gameName == '':
            await ctx.send("Please write out the game you wish to access after the command (i.e. %enter New York)")
        elif check == False and not (joinAllWD or joinAllPD or joinAllArchive):
            closestChannels = difflib.get_close_matches(gameName, applicableChannels)
            if len(closestChannels) > 1:
                await ctx.send("That game could not be found, did you mean one of: " + closestChannels)
            elif len(closestChannels) == 1:
                await ctx.send("That game could not be found, did you mean " + closestChannels[0])
            else:
                await ctx.send("That game could not be found.")
         #   roleName = gameName + 'er'

          #  if roleName == 'Game Master':
           #     await ctx.send("You must think you're so clever.")
        else:
            await game.set_permissions(ctx.author, read_messages=True)

    @commands.command()
    async def exit(self, ctx, *args):
        '''Leave a game channel
        '''
        gameName = ''
        game = None
        check = False

        for arg in args:
            gameName = gameName + str(arg).lower()

        for channel in ctx.guild.channels:
            if channel.name == gameName:
                game = channel
                check = True

        if gameName == '':
            await ctx.send("Please write out where you wish to exit after the command (i.e. %exit New York)")
        elif check == False:
            await ctx.send("That game could not be found.")
        else:
            await game.set_permissions(ctx.author, read_messages=False)

    @commands.command()
    async def archive(self, ctx, *args):
        '''Move an inactive game to archives
        '''
        gameName = ''
        gameID = None
        archiveID = None
        PDID = None
        WDID = None

        for arg in args:
            gameName = gameName + str(arg).lower()

        namecheck = (await sheets.gamecheck(ctx.author.id,gameName))
        moderator = False
        for role in ctx.author.roles:
            if str(role) == 'Mod Team':
                moderator = True
                break

        for category in ctx.message.guild.categories:
            if category.name == 'PactDice Games':
                PDID = category
            if category.name == 'WeaverDice Games':
                WDID = category
            elif category.name == 'Archives':
                archiveID = category

        for channel in ctx.message.guild.channels:
            if channel.name == gameName:
                gameID = channel.category

        if gameName == '':
            await ctx.send("Please write out the game you wish to archive after the command (i.e. %archive New York)")
        elif gameID == archiveID:
            await ctx.send("That game is already archived.")
        elif namecheck == False and moderator == False:
            await ctx.send("You don't have permission to archive this.")
        else:
            if gameID != PDID and gameID != WDID:
                await ctx.send("That game could not be found.")
            else:
                for ctx.TextChannel in ctx.message.guild.text_channels:
                    if ctx.TextChannel.name == gameName:
                        await ctx.TextChannel.edit(category=archiveID)
                        await sheets.changeState(gameName,'N')

    @commands.command()
    async def unarchive(self, ctx, *args):
        '''Move an archived game back out of archives
        '''
        gameType = args[0].lower()
        argStart = 1
        if (gameType != 'wd' and gameType != 'pd'):
            # We want to read from the sheet
            argStart = 0
            #await ctx.send("Please write out your game's name after the command (i.e. %unarchive pd New York)")
            #return
        gameName = ''
        gameRole = None
        gameChan = None
        gameID = None
        archiveID = None
        PDID = None
        WDID = None

        for category in ctx.message.guild.categories:
            if category.name == 'PactDice Games':
                PDID = category
            elif category.name == 'WeaverDice Games':
                WDID = category
            elif category.name == 'Archives':
                archiveID = category

        for arg in args[argStart:]:
            gameName = gameName + str(arg).lower()

        namecheck = (await sheets.gamecheck(ctx.author.id,gameName))
        category = (await sheets.category(gameName))
        moderator = False
        for role in ctx.author.roles:
            if str(role) == 'Mod Team':
                moderator = True
                break

        for channel in ctx.message.guild.channels:
            if channel.name == gameName:
                gameID = channel.category

        if gameName == '':
            await ctx.send("Please write out the game you wish to unarchive after the command (i.e. %unarchive New York)")
        elif gameID == PDID or gameID == WDID:
            await ctx.send("That game is already active.")
        elif namecheck == False and moderator == False:
            await ctx.send("You don't have permission to unarchive this.")
        else:
            if gameID != archiveID:
                await ctx.send("That game could not be found.")
            else:
                for ctx.TextChannel in ctx.message.guild.text_channels:
                    if ctx.TextChannel.name == gameName:
                        if gameType == 'pd' or category.lower() == 'pd':
                            await ctx.TextChannel.edit(category=PDID)
                        elif gameType == 'wd' or category.lower() == 'wd':
                            await ctx.TextChannel.edit(category=WDID)
                        await sheets.changeState(gameName,'Y')

    @commands.command()
    async def link(self, ctx, *args):
        '''Sets the doc link on the spreadsheet for your game
        '''
        link = ''

        for arg in args[1:]:
            link += str(arg) + ' '
        link = link[:-1]

        failure = await sheets.addlink(ctx.author.id,args[0].lower(),link)
        if failure:
            await ctx.send('Error adding link, make sure you have the name right and you\'re the GM')
        else:
            # Let's make this the topic
            for channel in ctx.message.guild.channels:
                if channel.name == args[0].lower():
                    await channel.edit(topic=link)
            

    @commands.command()
    async def owner(self, ctx, *args):
        '''Checks the owner of a given campaign
        '''
        gameName = ''
        game = None
        check = False

        for arg in args:
            gameName = gameName + str(arg).lower()

        ownercheck = (await sheets.ownercheck(gameName))

        if ownercheck != '':
            await ctx.send('<@' + ownercheck + '> owns ' + gameName)
        else:
            await ctx.send('Could not find game ' + gameName)

    # - - - - End of Disaster Area - - - -
