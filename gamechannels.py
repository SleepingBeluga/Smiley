async def debug(ctx, message):
    '''Prints a message in the context passed
    '''
    await ctx.send(message)

class Game_Channels:
    # - - - - Absolute mess of code below. Mostly channel stuff. Tread at your own risk. - - - -
    @b.command()
    async def campaigns(ctx, *args):
        '''Get the link to the campaigns spreadsheet
        '''
        await ctx.send("Campaign list: https://docs.google.com/spreadsheets/d/1Foxb_C_zKvLuSMOB4HN5tRMpVwtPrkq6tdlokKSgEqY")

    @b.command()
    async def addgame(ctx, *args):
        '''Create a WD or PD game with you as the GM
        '''
        gameType = args[0].lower()
        if (gameType != 'wd' and gameType != 'pd'):
            await ctx.send("Please write out your game's name after the command (i.e. ~addgame pd New York)")
            return
        gameName = ''
        gameMaster = None
        #gameRole = None
        gamecat = None

        for arg in args[1:]:
            gameName = gameName + str(arg)

        # List of restricted titles
        restricted_names = ['all', 'allactive', 'wdall', 'pdall', 'allarchive']
        if gameName in restricted_names:
            await ctx.send(gameName + " is a restricted term and you can't name your game that. Sorry!")
            return

        if gameName == '':
            await ctx.send("Please write out your game's name after the command (i.e. ~addgame pd New York)")
        else:

        #    roleName = gameName + 'er'

        #    await ctx.guild.create_role(name=roleName)

            for discord.Role in ctx.message.guild.roles:
                if discord.Role.name == 'Game Master':
                    gameMaster = discord.Role
                #elif discord.Role.name == roleName:
                 #   gameRole = discord.Role

            await ctx.author.add_roles(gameMaster)

            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                #gameRole: discord.PermissionOverwrite(read_messages=True),
                ctx.author: discord.PermissionOverwrite(read_messages=True),
                ctx.me: discord.PermissionOverwrite(read_messages=True)
            }

            for discord.CategoryChannel in ctx.guild.categories:
                if (discord.CategoryChannel.name == 'PactDice Games' and gameType == 'pd'):
                    gamecat = discord.CategoryChannel
                elif (discord.CategoryChannel.name == 'WeaverDice Games' and gameType == 'wd'):
                    gamecat = discord.CategoryChannel

            await ctx.message.guild.create_text_channel(gameName, category=gamecat, overwrites=overwrites)
            await sheets.newgame(str('#' + gameName),str(ctx.author.display_name), str(gameType).upper())

    @b.command()
    async def enter(ctx, *args):
        '''Join a game channel
        '''
        gameName = ''
        game = None
        check = False
        debugging = False

        for arg in args:
            if arg.lower() == "-d":
                debugging = True
                continue
            gameName = gameName + str(arg)

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

        for discord.Guild.TextChannel in ctx.guild.channels:
            # First lets just check whether they want all games!
            if not discord.Guild.TextChannel.category:
                continue
            # If the channel has no category, move to the next channel
            catName = discord.Guild.TextChannel.category.name
            if joinAllWD and catName == 'WeaverDice Games':
                joining += discord.Guild.TextChannel.name + ", "
                channelsJoined += 1
                await discord.Guild.TextChannel.set_permissions(ctx.author, read_messages=True)
            elif joinAllPD and catName == 'PactDice Games':
                joining += discord.Guild.TextChannel.name + ", "
                channelsJoined += 1
                await discord.Guild.TextChannel.set_permissions(ctx.author, read_messages=True)
            elif joinAllArchive and catName == 'Archives':
                joining += discord.Guild.TextChannel.name + ", "
                channelsJoined += 1
                await discord.Guild.TextChannel.set_permissions(ctx.author, read_messages=True)
            if discord.Guild.TextChannel.name == gameName:
                game = discord.Guild.TextChannel
                joining += game.name
                check = (catName in ['PactDice Games', 'WeaverDice Games', 'Archives'])

        # Let's do some debugging
        if debugging:
            await debug(ctx, joining)
            if channelsJoined > 0:
                await debug(ctx, "That is trying to join " + channelsJoined)

        if gameName == '':
            await ctx.send("Please write out the game you wish to access after the command (i.e. ~enter New York)")
        elif check == False:
            await ctx.send("That game could not be found.")
         #   roleName = gameName + 'er'

          #  if roleName == 'Game Master':
           #     await ctx.send("You must think you're so clever.")
        else:
            await game.set_permissions(ctx.author, read_messages=True)

    @b.command()
    async def exit(ctx, *args):
        '''Leave a game channel
        '''
        gameName = ''
        game = None
        check = False

        for arg in args:
            gameName = gameName + str(arg)

        for discord.Guild.TextChannel in ctx.guild.channels:
            if discord.Guild.TextChannel.name == gameName:
                game = discord.Guild.TextChannel
                check = True

        if gameName == '':
            await ctx.send("Please write out where you wish to exit after the command (i.e. ~exit New York)")
        elif check == False:
            await ctx.send("That game could not be found.")
        else:
            await game.set_permissions(ctx.author, read_messages=False)

    @b.command()
    async def archive(ctx, *args):
        '''Move an inactive game to archives
        '''
        gameName = ''
        gameID = None
        archiveID = None
        PDID = None
        WDID = None

        for arg in args:
            gameName = gameName + str(arg)

        namecheck = (await sheets.gamecheck(ctx.author.display_name,gameName))
        moderator = ('Mod Team' in ctx.author.roles)

        for discord.Guild.CategoryChannel in ctx.message.guild.categories:
            if discord.Guild.CategoryChannel.name == 'PactDice Games':
                PDID = discord.Guild.CategoryChannel
            if discord.Guild.CategoryChannel.name == 'WeaverDice Games':
                WDID = discord.Guild.CategoryChannel
            elif discord.Guild.CategoryChannel.name == 'Archives':
                archiveID = discord.Guild.CategoryChannel

        for discord.Guild.TextChannel in ctx.message.guild.channels:
            if discord.Guild.TextChannel.name == gameName:
                gameID = discord.Guild.TextChannel.category

        if gameName == '':
            await ctx.send("Please write out the game you wish to archive after the command (i.e. ~archive New York)")
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

    @b.command()
    async def unarchive(ctx, *args):
        '''Move an archived game back out of archives
        '''
        gameType = args[0].lower()
        if (gameType != 'wd' and gameType != 'pd'):
            await ctx.send("Please write out your game's name after the command (i.e. ~unarchive pd New York)")
            return
        gameName = ''
        gameRole = None
        gameChan = None
        gameID = None
        archiveID = None
        PDID = None
        WDID = None

        for discord.Guild.CategoryChannel in ctx.message.guild.categories:
            if discord.Guild.CategoryChannel.name == 'PactDice Games':
                PDID = discord.Guild.CategoryChannel
            elif discord.Guild.CategoryChannel.name == 'WeaverDice Games':
                WDID = discord.Guild.CategoryChannel
            elif discord.Guild.CategoryChannel.name == 'Archives':
                archiveID = discord.Guild.CategoryChannel

        for arg in args[1:]:
            gameName = gameName + str(arg)

        namecheck = (await sheets.gamecheck(ctx.author.display_name,gameName))
        moderator = ('Mod Team' in ctx.author.roles)

        for discord.Guild.TextChannel in ctx.message.guild.channels:
            if discord.Guild.TextChannel.name == gameName:
                gameID = discord.Guild.TextChannel.category

        if gameName == '':
            await ctx.send("Please write out the game you wish to unarchive after the command (i.e. ~unarchive New York)")
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
                        if gameType == 'pd':
                            await ctx.TextChannel.edit(category=PDID)
                        elif gameType == 'wd':
                            await ctx.TextChannel.edit(category=WDID)
                        await sheets.changeState(gameName,'Y')

    @b.command()
    async def link(ctx, *args):
        '''Sets the doc link on the spreadsheet for your game
        '''
        link = ''

        for arg in args:
            link += str(arg) + ' '
        link = link[:-1]

        await sheets.addlink(ctx.author.display_name,link)


    # - - - - End of Disaster Area - - - -
