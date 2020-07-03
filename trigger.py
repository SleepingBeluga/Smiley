from discord.ext import commands
import discord, sheets, random

async def longsend(ctx, content):
    if len(content) > 1990:
        msgs = content.split('\n')
    else:
        msgs = [content]
    found_too_long = True
    while found_too_long:
        found_too_long = False
        for i, msg in enumerate(msgs):
            if len(msg) > 1990:
                found_too_long = True
                msgs[i] = msg[:1990]
                msgs.insert(i+1,msg[1990:])
    for msg in msgs:
        await ctx.send(msg)

class Triggers_And_More(commands.Cog):
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
            await longsend(ctx, t)
            await ctx.author.send("You have rolled a trigger, presumably for a " +
            "game. Make sure at the end of the gen that your GM performs `%claim` " +
            "and `%increment`. Have them make sure the trigger remains in the " +
            "same place using `%trigger {}`".format(t.split(":")[0]))
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
            await longsend(ctx, t)
        else:
            await ctx.send("Could not find a used trigger at " + str(index))

    @commands.command()
    async def claim(self, ctx, *args):
        '''Moves a trigger from unrolled triggers to used triggers
        Format for claim: `%claim <number>, <game>, <player>, <short description of power>`
        The commas are important!'''
        astr = ' '.join(args)
        alist = [s.strip() for s in astr.split(',')]
        if len(alist) < 4:
            await ctx.send("Not enough arguments. Format for claim: %claim <number>, <game>, <player>, <short description of power>")
            await ctx.send("The commas are important!")
            return
        if len(alist) > 4:
            await ctx.send("Too many arguments. You might have commas in the description. Format for claim: %claim <number>, <game>, <player>, <short description of power>")
            return
        try:
            num = int(alist[0])
        except:
            await ctx.send("Couldn't parse trigger number. Format for claim: %claim <number>, <game>, <player>, <short description of power>")
        game = alist[1]
        player = alist[2]
        desc = alist[3]
        res = await sheets.claim(num, game, player, desc)
        await ctx.send(res)

    @commands.command()
    async def increment(self, ctx, *args):
        '''Increments a category amount on the trigger sheet.
        Can do decimal values, if, for example, your newly genned cape is part blaster part mover
        %increment mover 0.3
        %increment blaster 0.7
        Single cape's categories should sum to 1
        '''
        if len(args) != 2:
            await ctx.send("Please increment using the category of power and amount (ie `%increment trump 0.7`)")
            return
        
        category = args[0].lower()
        categories = [
            'mover',
            'shaker',
            'brute',
            'breaker',
            'master',
            'tinker',
            'blaster',
            'thinker',
            'striker',
            'changer',
            'trump',
            'stranger'
        ]
        if category not in categories:
            await ctx.send("Category {} is not recognised".format(args[0]))
            return

        try:
            value = float(args[1])
        except:
            await ctx.send("Could not cast {} to a number".format(args[1]))
            return

        success = (await sheets.increment(category,value))
        if success:
            await ctx.send("Incremented {} by {}".format(args[0],args[1]))
        else:
            await ctx.send("Failed to increment")

    @commands.command()
    async def luck(self, ctx, *args):
        '''Get randomised luck. Can also search by passing the title.
        '''
        if args:
            to_find = ' '.join(args)
            for col in range(1,5):
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
            else:
                search_perk = " ".join(args)
                for i in [ 1, 2 ]:
                    output = await sheets.luck(i, False, search_perk)
                    if output:
                        if i == 1:
                            await ctx.send("*Life Perk*: " + output)
                        else:
                            await ctx.send("*Power Perk*: " + output)
                        return
                await ctx.send(f"Perk {search_perk} could not be found")
                return

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
            else:
                search_flaw = " ".join(args)
                for i in [ 3, 4 ]:
                    output = await sheets.luck(i, False, search_flaw)
                    if output:
                        if i == 3:
                            await ctx.send("*Life Flaw*: " + output)
                        else:
                            await ctx.send("*Power Flaw*: " + output)
                        return
                await ctx.send(f"Flaw {search_flaw} could not be found")
                return

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
        if args:
            to_find = ' '.join(args)
            for col in range(1,5):
                output = await sheets.luck(col, True, to_find)
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
            else:
                search_perk = " ".join(args)
                for i in [ 1, 2 ]:
                    output = await sheets.luck(i, True, search_perk)
                    if output:
                        if i == 1:
                            await ctx.send("*Life Perk*: " + output)
                        else:
                            await ctx.send("*Power Perk*: " + output)
                        return
                await ctx.send(f"Fan Perk {search_perk} could not be found")
                return

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
            else:
                search_flaw = " ".join(args)
                for i in [ 3, 4 ]:
                    output = await sheets.luck(i, True, search_flaw)
                    if output:
                        if i == 3:
                            await ctx.send("*Life Flaw*: " + output)
                        else:
                            await ctx.send("*Power Flaw*: " + output)
                        return
                await ctx.send(f"Fan Flaw {search_flaw} could not be found")
                return

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

    @commands.command()
    async def skill(self, ctx, *args):
        '''Return info on a specified skill. Can also specify a pip number or specialities for extra information.

            Arguments appended to skill:
            basic - Basic rundown/description of skill, default argument if none is specified
            short - Lists the short version of all pips
            1-5 - Lists long version of specified pip
            specialities - Lists specialities

            Arguments instead of skill name:
            list - lists all of the skills in a comma separated string
            Athletics/Brawn/etc. - Specify a Stat and get a comma separated string of relevant stats
        '''
        if len(args) == 0:
            await ctx.send("Need to specify the skill!")
            return
        output = ""
        if len(args) == 1:
            output = (await sheets.skill(str(args[0]), "basic"))
        else:
            output = (await sheets.skill(str(args[0]), str(args[1])))

        await ctx.send("```{}```".format(str(output)))

    @commands.command()
    async def status(self, ctx, name, name2 = ''):
        '''Return info on a specified status effect.

           The single argument is the name of a status effect.
        '''
        status_d = {'bleed': "Bleed - If the subject does not take a full round to patch themselves up, they suffer a minor wound after [Guts score] turns.",
                    'scar': "Scar - The injury looks bad, it’s hard to hide, and it takes twice as long to recover from, whether through rest/over time or by way of medical attention.",
                    'blinded': "Blinded - Similar to Disabled. Must roll Wits for even mundane attempts to see surroundings (those that would not have to be rolled for). Make roll at -2 penalty, typically a 4+ to succeed; attempts at evasion or other factors may make this more difficult. Otherwise limited to sensing things within 5’. Deafened is the same thing, but for hearing/communication.",
                    'deafened': "Blinded - Similar to Disabled. Must roll Wits for even mundane attempts to hear surroundings (those that would not have to be rolled for). Make roll at -2 penalty, typically a 4+ to succeed; attempts at evasion or other factors may make this more difficult. Otherwise limited to sensing things within 5’. Blinded is the same thing, but for sight.",
                    'disabled': "Disabled - Typically affects a limb. Must roll [appropriate stat] for even mundane attempts to use limb (those that wound not have to be rolled for). Make roll at -2 penalty, typically a 4+ to succeed. Can use arms for very light (5 lbs or less) burdens, can move at walking pace.",
                    'disarmed': "Disarmed - Held item is knocked into a space within 10’. 5’ for items weighing 5 lbs or more.",
                    'knocked down': "Knocked Down - Ass hits the floor. Standing or attempting a close-quarters attack and failing provokes an attack from those nearby, movement allowance is reduced by half in the process of getting up.",
                    'staggered': "Staggered - Off balance, shoved away. Get moved back a distance, typically 5’. Adjust by 5’ one way or the other depending on difference in Brawn, size; heavier people and armored individuals move less. Staggered individuals are penalized on their next turn: attacks suffer -1 and their movement is reduced by ½ if they try to move in a direction they weren’t pushed in, by ¾ if they try to move against that direction.",
                    'confused': "Confused - Concussed, thoughts scattered. Wits roll (4+) to identify targets, directions, where things are respective to each other. On a failure, can still act, but targets are chosen randomly, movement runs risk of stumbling into wall.",
                    'pain': "Pain - Suffer a temporary minor wound when exerting the affected part, or when the part is struck again, with the wound fading at the end of the next turn, if another wasn’t inflicted. ‘Exertion’ is respective to body part - arm is limited in tests of strength, rare Athletics checks (ie. climbing), leg is movements faster than a walk, jumping, climbing, body is making any Guts or Athletic checks for stamina, and head is any Wits or Know check (typically only a psychic attack).",
                    'death sentence': "Death Sentence - Subject is dying. Each round, an empty wound slot fills up with a moderate wound. Once filled, moderate wounds start becoming critical ones. Typically helpless, intervention can stop or slow progression."}
        if not name:
            await ctx.send("Please specify a status effect")
            return
        name = (name.lower() + ' ' + name2.lower()).strip()
        if not name in status_d:
            await ctx.send("I don't know that status effect")
            return
        else:
            await ctx.send(status_d[name])
