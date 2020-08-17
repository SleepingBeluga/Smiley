from discord.ext import commands
# Gonna copy and adjust some stuff in order to add a liveread function, as requested for the new channel

class Liveread(commands.Cog):
    @commands.command()
    async def liveread(self, ctx, *args):
        '''Join or leave the liveread channel.
        Usage: %liveread <enter/exit/rules> <Wormverse/Otherverse/Twigverse+/all> <I have read the rules>
               i.e. %liveread enter Wormverse I have read the rules
        '''
        entering = None
        game = None
        check = False

        if len(args) == 0:
            await ctx.send(
                "Error: Improper format. Provide  %liveread <enter/exit/rules> <Wormverse/Otherverse/Twigverse+/all> <I have read the rules>")
            return

        if args[0] == 'enter':
            entering = True
        elif args[0] == 'exit':
            entering = False
            check = True
        elif args[0] == 'rules':
            await ctx.send(
                "Here you go: https://docs.google.com/document/d/1wl_Wl_wk884MNzeBkfqOKgmj8BaGPsVpfou13pReBEg/edit?usp=sharing")
            return
        else:
            await ctx.send(
                "Error: Improper format. Only current liveread commands are enter, exit, or rules, i.e. %liveread exit Wormverse")
            return

        if len(args) == 1:
            await ctx.send(
                "Error: Improper format. Provide  %liveread <enter/exit/rules> <Wormverse/Otherverse/Twigverse+/all> <I have read the rules>")
            return

        if len(args) > 2:
            if args[2].lower() == "i":
                if args[3].lower() == "have":
                    if args[4].lower() == "read":
                        if args[5].lower() == "the":
                            if args[6].lower() == "rules":
                                check = True

        if check == False:
            await ctx.send("Error: please read the rules of the liveread channel.")
            await ctx.send(
                "They can be found here: https://docs.google.com/document/d/1wl_Wl_wk884MNzeBkfqOKgmj8BaGPsVpfou13pReBEg/edit?usp=sharing")
            return

        if args[1].lower() == 'wormverse':
            for channel in ctx.guild.channels:
                if channel.name == 'wormverse-livereads':
                    if entering:
                        await channel.set_permissions(ctx.author, read_messages=True)
                    elif not entering:
                        await channel.set_permissions(ctx.author, read_messages=False)
        elif args[1].lower() == 'otherverse':
            for channel in ctx.guild.channels:
                if channel.name == 'otherverse-livereads':
                    if entering:
                        await channel.set_permissions(ctx.author, read_messages=True)
                    elif not entering:
                        await channel.set_permissions(ctx.author, read_messages=False)
        elif args[1].lower() == 'twigverseplus':
            for channel in ctx.guild.channels:
                if channel.name == 'twigverseplus-livereads':
                    if entering:
                        await channel.set_permissions(ctx.author, read_messages=True)
                    elif not entering:
                        await channel.set_permissions(ctx.author, read_messages=False)
        elif args[1].lower() == 'all':
            for channel in ctx.guild.channels:
                if channel.name == 'wormverse-livereads':
                    if entering:
                        await channel.set_permissions(ctx.author, read_messages=True)
                    elif not entering:
                        await channel.set_permissions(ctx.author, read_messages=False)
                if channel.name == 'otherverse-livereads':
                    if entering:
                        await channel.set_permissions(ctx.author, read_messages=True)
                    elif not entering:
                        await channel.set_permissions(ctx.author, read_messages=False)
                if channel.name == 'twigverseplus-livereads':
                    if entering:
                        await channel.set_permissions(ctx.author, read_messages=True)
                    elif not entering:
                        await channel.set_permissions(ctx.author, read_messages=False)
        else:
            await ctx.send("Error: liveread category not found. Currently available liveread categories: Wormverse, Otherverse, TwigversePlus, all")
            return