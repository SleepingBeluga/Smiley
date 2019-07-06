from discord.ext import commands
import discord, sheets, random

class Trigger(commands.Cog):

    @commands.command()
    async def trigger(self, ctx, *args):
        '''Get a trigger for a character. Can specify index starting from 1.
        '''
        if len(args) > 0:
            index = int(args[0])
            t = (await sheets.trigger(index))
        else:
            index = 0
            t = (await sheets.trigger(0))

        if str(t) != "":
            await ctx.send(t)
        else:
            await ctx.send("Could not find a trigger at " + str(index))

    @commands.command()
    async def used(self, ctx, *args):
        '''Get a used trigger. Can specify index starting from 1.
        '''
        if len(args) > 0:
            index = int(args[0])
            t = (await sheets.used(index))
        else:
            index = 0
            t = (await sheets.used(0))

        if str(t) != "":
            await ctx.send(t)
        else:
            await ctx.send("Could not find a used trigger at " + str(index))

    @commands.command()
    async def luck(self, ctx, *args):
        '''Get randomised luck. Can also search by passing the title.
        '''
        if args:
            to_find = ' '.join(args)
            for col in range(1,4):
                output = await sheets.luck(col, False, to_find)
                if output:
                    if (col == 1):
                        await ctx.send("*Life Perk*: " + output)
                    elif (col == 2):
                        await ctx.send("*Power Perk*: " + output)
                    elif (col == 3):
                        await ctx.send("*Life Flaw*: " + output)
                    elif (col == 4):
                        await ctx.send("*Power Flaw*: " + output)
                    return
            await ctx.send('Couldn\'t find a perk or flaw matching \'' + to_find + '\'')
        else:
            for _ in range(2):
                choice = random.randint(1, 4)
                # Ordering for these is Perk Life, Perk Power, Flaw Life, Flaw Power
                output = (await sheets.luck(choice))
                #await ctx.send("Doing some luck stuff!")
                if (choice == 1):
                    await ctx.send("*Life Perk*: " + output)
                elif (choice == 2):
                    await ctx.send("*Power Perk*: " + output)
                elif (choice == 3):
                    await ctx.send("*Life Flaw*: " + output)
                elif (choice == 4):
                    await ctx.send("*Power Flaw*: " + output)

    @commands.command()
    async def perk(self, ctx, *args):
        '''Get randomised perk. Can specify power or life.
        '''
        column = 0
        if len(args) > 0:
            if args[0].lower() == "life":
                column = 1
            elif args[0].lower() == "power":
                column = 2

        if column == 0:
            column = random.randint(1, 2)

        output = (await sheets.luck(column))

        if column == 1:
            await ctx.send("*Life Perk*: " + output)
        else:
            await ctx.send("*Power Perk*: " + output)

    @commands.command()
    async def flaw(self, ctx, *args):
        '''Get randomised flaw. Can specify power or life.
        '''
        column = 0
        if len(args) > 0:
            if args[0].lower() == "life":
                column = 3
            elif args[0].lower() == "power":
                column = 4

        if column == 0:
            column = random.randint(3, 4)

        output = (await sheets.luck(column))

        if column == 3:
            await ctx.send("*Life Flaw*: " + output)
        else:
            await ctx.send("*Power Flaw*: " + output)

    @commands.command()
    async def power(self, ctx, p_or_f = ""):
        '''Get a random power perk or flaw. Optionally specify whether you want a perk or flaw.
        '''
        p_or_f = p_or_f.lower()
        if p_or_f == 'perk':
            column = 2
        elif p_or_f == 'flaw':
            column = 4
        else:
            column = random.choice((2,4))

        output = (await sheets.luck(column))
        if column == 2:
            await ctx.send("*Power Perk*: " + output)
        else:
            await ctx.send("*Power Flaw*: " + output)

    @commands.command()
    async def life(self, ctx, p_or_f = ""):
        '''Get a random life perk or flaw. Optionally specify whether you want a perk or flaw.
        '''
        p_or_f = p_or_f.lower()
        if p_or_f == 'perk':
            column = 1
        elif p_or_f == 'flaw':
            column = 3
        else:
            column = random.choice((1,3))

        output = (await sheets.luck(column))
        if column == 1:
            await ctx.send("*Life Perk*: " + output)
        else:
            await ctx.send("*Life Flaw*: " + output)

    @commands.command()
    async def fanluck(self, ctx, *args):
        '''Get randomised luck.
        '''
        i = 0
        while i < 2:
            choice = random.randint(1, 4)
            # Ordering for these is Perk Life, Perk Power, Flaw Life, Flaw Power
            output = (await sheets.luck(choice, True))
            #await ctx.send("Doing some luck stuff!")
            if (choice == 1):
                await ctx.send("*Life Perk*: " + output)
            elif (choice == 2):
                await ctx.send("*Power Perk*: " + output)
            elif (choice == 3):
                await ctx.send("*Life Flaw*: " + output)
            elif (choice == 4):
                await ctx.send("*Power Flaw*: " + output)
            i += 1

    @commands.command()
    async def fanperk(self, ctx, *args):
        '''Get randomised perk. Can specify power or life. (Includes fanmade results)
        '''
        column = 0
        if len(args) > 0:
            if args[0].lower() == "life":
                column = 1
            elif args[0].lower() == "power":
                column = 2

        if column == 0:
            column = random.randint(1, 2)

        output = (await sheets.luck(column, True))

        if column == 1:
            await ctx.send("*Life Perk*: " + output)
        else:
            await ctx.send("*Power Perk*: " + output)

    @commands.command()
    async def fanflaw(self, ctx, *args):
        '''Get randomised flaw. Can specify power or life. (Includes fanmade results)
        '''
        column = 0
        if len(args) > 0:
            if args[0].lower() == "life":
                column = 3
            elif args[0].lower() == "power":
                column = 4

        if column == 0:
            column = random.randint(3, 4)

        output = (await sheets.luck(column, True))

        if column == 3:
            await ctx.send("*Life Flaw*: " + output)
        else:
            await ctx.send("*Power Flaw*: " + output)

    @commands.command()
    async def fanpower(self, ctx, p_or_f = ""):
        '''Get a random power perk or flaw. Optionally specify whether you want a perk or flaw. (Includes fanmade results)
        '''
        p_or_f = p_or_f.lower()
        if p_or_f == 'perk':
            column = 2
        elif p_or_f == 'flaw':
            column = 4
        else:
            column = random.choice((2,4))

        output = (await sheets.luck(column, True))
        if column == 2:
            await ctx.send("*Power Perk*: " + output)
        else:
            await ctx.send("*Power Flaw*: " + output)

    @commands.command()
    async def fanlife(self, ctx, p_or_f = ""):
        '''Get a random life perk or flaw. Optionally specify whether you want a perk or flaw.(Includes fanmade results)
        '''
        p_or_f = p_or_f.lower()
        if p_or_f == 'perk':
            column = 1
        elif p_or_f == 'flaw':
            column = 3
        else:
            column = random.choice((1,3))

        output = (await sheets.luck(column, True))
        if column == 1:
            await ctx.send("*Life Perk*: " + output)
        else:
            await ctx.send("*Life Flaw*: " + output)
