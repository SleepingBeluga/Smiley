from discord.ext import commands
import discord, sheets
import difflib # Used to find closest name for enter command

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
        Usage: %addgame <pd/wd> <game name>
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
        restricted_names = ['all', 'allactive', 'inactive', 'active', 'wdall', 'allwd', 'allpd', 'pdall', 'allarchive']
        if gameName in restricted_names:
            await ctx.send(gameName + " is a restricted term and you can't name your game that. Sorry!")
            return

        for channel in ctx.guild.channels:
            if channel.name == gameName:
                await ctx.send('There\'s already a channel called ' + gameName +', use another name to avoid confusion.')
                return

        if gameName == '':
            await ctx.send("Please write out your game's name after the command (i.e. %addgame pd New York)")
        else:

        #    roleName = gameName + 'er'

        #    await ctx.guild.create_role(name=roleName)

            for role in ctx.message.guild.roles:
                if role.name == 'Game Master':
                    gameMaster = role
                if role.name == "Bot":
                    bot = role
                #elif discord.Role.name == roleName:
                 #   gameRole = discord.Role

            await ctx.author.add_roles(gameMaster)

            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                #gameRole: discord.PermissionOverwrite(read_messages=True),
                ctx.author: discord.PermissionOverwrite(read_messages=True),
                ctx.me: discord.PermissionOverwrite(read_messages=True),
                bot: discord.PermissionOverwrite(read_messages=True)
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
        Usage: %enter <channel>
               %enter <group>
        Group arguments include wdall, pdall, allactive, allarchive, all
        '''
        gameName = ''
        game = None
        check = False
        debugging = False

        for arg in args:
            if arg.lower() == "-d":
                debugging = True
                continue
            gameName = gameName + str(arg).lower()

        joinAllWD = False
        joinAllPD = False
        joinAllArchive = False

        if gameName in ['wdall', 'allwd', 'all', 'allactive']:
            joinAllWD = True
        if gameName in ['pdall', 'allpd', 'all', 'allactive']:
            joinAllPD = True
        if gameName in ['all', 'allarchive']:
            joinAllArchive = True

        # Let's track some info for debugging
        joining = "We are trying to join "
        channelsJoined = 0
        applicableChannels = []

        for channel in ctx.guild.channels:
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
            elif channel.name == gameName or \
              'wd' + channel.name == gameName or \
              'pd' + channel.name == gameName:
                game = channel
                joining += game.name
                check = (catName in ['PactDice Games', 'WeaverDice Games', 'Archives'])
                break

        # Let's do some debugging
        if debugging:
            await ctx.send(joining)
            if channelsJoined > 0:
                await ctx.send("That is trying to join " + channelsJoined)

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
        else:
            await game.set_permissions(ctx.author, read_messages=True)

    @commands.command()
    async def exit(self, ctx, *args):
        '''Leave a game channel
        Usage: %exit <channel>
               %exit <group>
        Group arguments include wdall, pdall, allactive, allarchive, all
        '''
        to_leave = ''
        game = None
        check = False

        for arg in args:
            to_leave += str(arg).lower()

        leavepd = to_leave == 'pdall' or to_leave == 'allpd'
        leavewd = to_leave == 'wdall' or to_leave == 'allwd'
        leavearchive = to_leave == 'inactive' or to_leave == 'archived' or to_leave == 'allarchive'
        if to_leave == 'allactive' or to_leave == 'active':
            leavepd = True
            leavewd = True
        if to_leave == 'all':
            leavepd = True
            leavewd = True
            leavearchive = True

        for channel in ctx.guild.channels:
            if not channel.category:
                continue
            # If the channel has no category, move to the next channel
            catName = channel.category.name
            if leavewd and catName == 'WeaverDice Games':
                check = True
                await channel.set_permissions(ctx.author, read_messages=False)
            elif leavepd and catName == 'PactDice Games':
                check = True
                await channel.set_permissions(ctx.author, read_messages=False)
            elif leavearchive and catName == 'Archives':
                check = True
                await channel.set_permissions(ctx.author, read_messages=False)
            if channel.name == to_leave:
                game = channel
                check = (catName in ['PactDice Games', 'WeaverDice Games', 'Archives'])
                if check:
                    await channel.set_permissions(ctx.author, read_messages=False)


        if to_leave == '':
            await ctx.send("Please write out where you wish to exit after the command (i.e. %exit New York)")
        elif check == False:
            await ctx.send("That game could not be found.")

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
                        # Prioritise on pd/wd override, then default to sheet data
                        if gameType == 'pd':
                            await ctx.TextChannel.edit(category=PDID)
                        elif gameType == 'wd':
                            await ctx.TextChannel.edit(category=WDID)
                        elif category and category.lower() == 'pd':
                            await ctx.TextChannel.edit(category=PDID)
                        elif category and category.lower() == 'wd':
                            await ctx.TextChannel.edit(category=WDID)
                        await sheets.changeState(gameName,'Y')

    @commands.command()
    async def link(self, ctx, *args):
        '''Sets the channel topic and the link on the spreadsheet for your game
        Usage: %link <game name> <link for topic>
        Note that you have to be the GM of the channel.
        '''
        link = ''
        channelName = args[0].lower()
        c = None
        for channel in ctx.message.guild.channels:
            if channel.name == channelName:
                c = channel
                index = 1
        
        if not c:
            # Assume that they want to apply to the current channel
            c = ctx.message.channel
            index = 0

        for arg in args[index:]:
            link += str(arg) + ' '
        link = link[:-1]

        failure = await sheets.addlink(ctx.author.id,c.name,link)
        if failure:
            await ctx.send('Error adding link, make sure you have the name right and you\'re the GM')
        else:
            # Let's make this the topic
            link = "GM is <@{}> | ".format(ctx.author.id) + link
            await c.edit(topic=link)


    @commands.command()
    async def owner(self, ctx, *args):
        '''Checks the owner of a given campaign
        Usage: %owner <game name>
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

    @commands.command()
    async def document(self, ctx, *args):
        '''Adds or links to documents
        Usage (colons are important when adding):
        %document add Document name: link
        %document search word words
        %document Document name
        '''
        if len(args) == 0:
            return
        if args[0].lower() == "add":
            user_input = " ".join(args[1:])
            doc, link = user_input.split(":")
            link = link.strip()
            # Check that it doesn't already exist
            data = (await sheets.documents())
            if doc in data:
                await ctx.send("A document already exists for {}".format(doc))
                return
            # Now add it!
            await sheets.add_document(doc, link, "{} - ({})".format(ctx.author.name, ctx.author.id))
        elif args[0].lower() == "search":
            user_input = " ".join(args[1:])
            data = (await sheets.documents())
            matching = []
            for i in data:
                if user_input.lower() in i.lower():
                    matching += [ i ]
            if len(matching) == 0:
                await ctx.send("Could not find any documents matching {}".format(user_input))
            else:
                await ctx.send("Found documents [{}]".format(", ".join(matching)))
        else:
            user_input = " ".join(args)
            data = (await sheets.documents())
            if user_input in data:
                # Add a quote in front of this so there is no way for people to inject commands
                # into Smiley using this functionality
                await ctx.send("> " + data[user_input])
            else:
                await ctx.send("Could not find this document, trying using `%document search`")


    # - - - - End of Disaster Area - - - -
