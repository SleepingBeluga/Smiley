from discord.ext import commands
import sheets, constants
import discord, difflib # Used to find closest name for enter command

class Game_Channels(commands.Cog):
    # - - - - Absolute mess of code below. Mostly channel stuff. Tread at your own risk. - - - -
    def __init__(self, b):
        self.b = b

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
        game_name = ''
        gameMaster = None
        #gameRole = None
        gamecat = None
        altcat = None

        for arg in args[1:]:
            game_name = game_name + str(arg).lower()

        # List of restricted titles
        restricted_names = ['all', 'allactive', 'inactive', 'active', 'wdall', 'allwd', 'allpd', 'pdall', 'allarchive', 'archived', 'archives']
        if game_name in restricted_names:
            await ctx.send(game_name + " is a restricted term and you can't name your game that. Sorry!")
            return

        for channel in ctx.guild.channels:
            if channel.name == game_name:
                await ctx.send('There\'s already a channel called ' + game_name +', use another name to avoid confusion.')
                return

        if game_name == '':
            await ctx.send("Please write out your game's name after the command (i.e. %addgame pd New York)")
        else:

            for role in ctx.message.guild.roles:
                if role.name == 'Game Master':
                    gameMaster = role
                if role.name == "Bot":
                    bot = role
            if gameMaster:
                await ctx.author.add_roles(gameMaster)

            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                #gameRole: discord.PermissionOverwrite(read_messages=True),
                ctx.author: discord.PermissionOverwrite(read_messages=True),
                ctx.me: discord.PermissionOverwrite(read_messages=True),
                bot: discord.PermissionOverwrite(read_messages=True)
            }
            cats = []

            for category in ctx.guild.categories:
                if gameType == 'pd' and category.name in constants.pd_categories:
                    cats.append(category)
                if gameType == 'wd' and category.name in constants.wd_categories:
                    cats.append(category)

            newChannel = None
            for cat in cats:
                try:
                    newChannel = await ctx.message.guild.create_text_channel(game_name, category=cat, overwrites=overwrites)
                    break
                except:
                    continue
            if newChannel:
                server = self.b.guilds[0]
                channels = [channel for channel in server.channels if channel.category and channel.category == newChannel.category]
                for i, chan in enumerate(sorted(channels, key=lambda c: c.name)):
                    if newChannel.name < chan.name:
                        await newChannel.edit(position=chan.position)
                        break
                await sheets.newgame(str('#' + game_name),str(ctx.author.id), str(gameType).upper())
                await ctx.send(f"{newChannel.mention} has been created in category {newChannel.category.name}")
            else:
                await ctx.send("Looks like there was a problem creating the channel. If the problem persists, please ping the bot team role")

    @commands.command()
    async def enter(self, ctx, *args):
        '''Join a game channel. Do not need to specify whether a wd or pd game.
        Usage: %enter <channel>
               %enter <group>
        Group arguments include wdall, pdall, allactive, allarchive, all
        '''
        game_name = ''
        game = None
        check = False
        debugging = False

        for arg in args:
            if arg.lower() == "-d":
                debugging = True
                continue
            game_name = game_name + str(arg).lower()

        if game_name == '':
            await ctx.send("Please write out the game you wish to access after the command (i.e. %enter New York)")
            return

        joinAllWD = game_name in ['wdall', 'allwd', 'all', 'allactive']
        joinAllPD = game_name in ['pdall', 'allpd', 'all', 'allactive']
        joinAllArchive = game_name in ['all', 'allarchive', 'inactive', 'archived', 'archives']

        applicableChannels = set()

        for channel in ctx.guild.channels:
            if not channel.category:
                continue
            # If the channel has no category, move to the next channel
            catName = channel.category.name
            if (catName in constants.wd_categories | constants.pd_categories | constants.archive_categories):
                applicableChannels.add(channel.name)
            if joinAllWD and catName in constants.wd_categories:
                if debugging:
                    await ctx.send("Trying to join " + channel.name)
                await channel.set_permissions(ctx.author, read_messages=True)
            elif joinAllPD and catName in constants.pd_categories:
                if debugging:
                    await ctx.send("Trying to join " + channel.name)
                await channel.set_permissions(ctx.author, read_messages=True)
            elif joinAllArchive and catName in constants.archive_categories:
                if debugging:
                    await ctx.send("Trying to join " + channel.name)
                await channel.set_permissions(ctx.author, read_messages=True)
            elif channel.name == game_name or 'wd' + channel.name == game_name or 'pd' + channel.name == game_name or '#' + channel.name == game_name:
                check = (catName in constants.wd_categories | constants.pd_categories | constants.archive_categories)
                if check:
                    await channel.set_permissions(ctx.author, read_messages=True)
                    return

        if check == False and not (joinAllWD or joinAllPD or joinAllArchive):
            closestChannels = difflib.get_close_matches(game_name, applicableChannels)
            if len(closestChannels) > 1:
                await ctx.send("That game could not be found, did you mean one of: " + ', '.join(closestChannels))
            elif len(closestChannels) == 1:
                await ctx.send("That game could not be found, did you mean " + closestChannels[0])
            else:
                await ctx.send("That game could not be found.")

    @commands.command()
    async def exit(self, ctx, *args):
        '''Leave a game channel
        Usage: %exit <channel>
               %exit <group>
        Group arguments include wdall, pdall, allactive, allarchive, all
        '''
        to_leave = ''
        check = False

        for arg in args:
            to_leave += str(arg).lower()

        if to_leave == '':
            await ctx.send("Please write out the game you wish to exit after the command (i.e. %exit New York)")
            return

        leavewd = to_leave in ['wdall', 'allwd', 'all', 'allactive']
        leavepd = to_leave in ['pdall', 'allpd', 'all', 'allactive']
        leavearchive = to_leave in ['all', 'allarchive', 'inactive', 'archived', 'archives']

        for channel in ctx.guild.channels:
            if not channel.category:
                continue
            # If the channel has no category, move to the next channel
            catName = channel.category.name
            if leavewd and catName in constants.wd_categories:
                check = True
                await channel.set_permissions(ctx.author, read_messages=False)
            elif leavepd and catName in constants.pd_categories:
                check = True
                await channel.set_permissions(ctx.author, read_messages=False)
            elif leavearchive and catName in constants.archive_categories:
                check = True
                await channel.set_permissions(ctx.author, read_messages=False)
            if channel.name == to_leave:
                game = channel
                check = (catName in constants.wd_categories | constants.pd_categories | constants.archive_categories)
                if check:
                    await channel.set_permissions(ctx.author, read_messages=False)
                    return

        if check == False:
            await ctx.send("That game could not be found.")

    @commands.command()
    async def archive(self, ctx, *args):
        '''Move an inactive game to archives
        '''
        game_name = ''
        game_cat = None
        wd_cats = []
        pd_cats = []
        archive_cats = []

        for arg in args:
            game_name = game_name + str(arg).lower()

        namecheck = (await sheets.gamecheck(ctx.author.id,game_name))
        moderator = False
        for role in ctx.author.roles:
            if str(role) == 'Mod Team':
                moderator = True
                break

        for category in ctx.message.guild.categories:
            if category.name in constants.pd_categories:
                pd_cats.append(category)
            elif category.name in constants.wd_categories:
                wd_cats.append(category)
            elif category.name in constants.archive_categories:
                archive_cats.append(category)

        for channel in ctx.message.guild.channels:
            if channel.name == game_name:
                game_cat = channel.category

        if game_name == '':
            await ctx.send("Please write out the game you wish to archive after the command (i.e. %archive New York)")
        elif game_cat in archive_cats:
            await ctx.send("That game is already archived.")
        elif namecheck == False and moderator == False:
            await ctx.send("You don't have permission to archive this.")
        else:
            if game_cat not in wd_cats and game_cat not in pd_cats:
                await ctx.send("That game could not be found.")
            else:
                for ctx.TextChannel in ctx.message.guild.text_channels:
                    if ctx.TextChannel.name == game_name:
                        success = False
                        for archive_cat in archive_cats:
                            try:
                                await ctx.TextChannel.edit(category=archive_cat)
                                success = True
                                break
                            except:
                                continue
                        if success:
                            await sheets.changeState(game_name,'N')
                        else:
                            await ctx.send("Error, could not archive that game.")

    @commands.command()
    async def unarchive(self, ctx, *args):
        '''Move an archived game back out of archives
        '''
        gameType = args[0].lower()
        argStart = 1
        if (gameType != 'wd' and gameType != 'pd'):
            gameType = None
            # We want to read from the sheet
            argStart = 0
            #await ctx.send("Please write out your game's name after the command (i.e. %unarchive pd New York)")
            #return
        game_name = ''
        gameRole = None
        gameChan = None
        game_cat = None
        wd_cats = []
        pd_cats = []
        archive_cats = []

        for category in ctx.message.guild.categories:
            if category.name in constants.pd_categories:
                pd_cats.append(category)
            elif category.name in constants.wd_categories:
                wd_cats.append(category)
            elif category.name in constants.archive_categories:
                archive_cats.append(category)

        for arg in args[argStart:]:
            game_name = game_name + str(arg).lower()

        namecheck = (await sheets.gamecheck(ctx.author.id,game_name))
        category = (await sheets.category(game_name))
        moderator = False
        for role in ctx.author.roles:
            if str(role) == 'Mod Team':
                moderator = True
                break

        for channel in ctx.message.guild.channels:
            if channel.name == game_name:
                game_cat = channel.category

        if game_name == '':
            await ctx.send("Please write out the game you wish to unarchive after the command (i.e. %unarchive New York)")
        elif game_cat in wd_cats or game_cat in pd_cats:
            await ctx.send("That game is already active.")
        elif namecheck == False and moderator == False:
            await ctx.send("You don't have permission to unarchive this.")
        else:
            if game_cat not in archive_cats:
                await ctx.send("That game could not be found.")
            else:
                for ctx.TextChannel in ctx.message.guild.text_channels:
                    if ctx.TextChannel.name == game_name:
                        # Prioritise on pd/wd override, then default to sheet data
                        if gameType is None:
                            gameType = category.lower()
                        if gameType == 'pd':
                            for pd_cat in pd_cats:
                                try:
                                    await ctx.TextChannel.edit(category=pd_cat)
                                    success = True
                                    break
                                except:
                                    continue
                        elif gameType == 'wd':
                            for wd_cat in wd_cats:
                                try:
                                    await ctx.TextChannel.edit(category=wd_cat)
                                    success = True
                                    break
                                except:
                                    continue
                        if success:
                            await sheets.changeState(game_name,'Y')
                        else:
                            await ctx.send("Error, could not unarchive that game.")

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
    async def pin(self, ctx, *args):
        '''Sets the message you are posting to be pinned to the channel if you are the owner of the channel.
        Usage: %pin This is the message that is being pinned.
        You can edit the message after the fact to remove the %pin element, if you like.
        '''
        c = ctx.message.channel
        owner = await sheets.ownercheck(c.name)
        if owner == str(ctx.author.id):
            await ctx.message.pin()
        else:
            await ctx.send("You are not the owner of this channel and cannot pin this message")

    @commands.command()
    async def owner(self, ctx, *args):
        '''Checks the owner of a given campaign
        Usage: %owner <game name>
        '''
        game_name = ''
        game = None
        check = False

        for arg in args:
            game_name = game_name + str(arg).lower()

        ownercheck = (await sheets.ownercheck(game_name))

        if ownercheck != '':
            await ctx.send('<@' + ownercheck + '> owns ' + game_name)
        else:
            await ctx.send('Could not find game ' + game_name)

    @commands.command()
    async def document(self, ctx, *, arguments):
        '''Adds or links to documents
        Usage (colons are important when adding):
        %document add Document name: link
        %document search word words
        %document Document name
        '''
        args = arguments.strip().split(" ")
        if len(args) == 0:
            return
        if args[0].lower() == "add":
            user_input = " ".join(args[1:])
            doc = user_input[:user_input.index(":")]
            link = user_input[user_input.index(":")+1:]
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
