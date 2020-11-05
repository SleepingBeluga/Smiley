from discord.ext import commands
import random

class Rolls(commands.Cog):
    '''For rolling dice
    '''
    @commands.command()
    async def roll(self, ctx, *, arg='1d6 1d6'):
        '''Roll some dice
        '''
        roll = arg
        has_tag = ' ' in roll
        if has_tag:
            tag = roll[roll.find(' ')+1:]
            roll = roll[:roll.find(' ')]
        roll = roll.lower()
        # Separate the roll command from the tag

        if roll.find('l') > -1:
            dsplit = roll.find('l')
            type = 'low'
        elif roll.find('h') > -1:
            dsplit = roll.find('h')
            type = 'high'
        elif roll.find('d') > -1:
            dsplit = roll.find('d')
            type = 'sum'
        else:
            await ctx.send('Error rolling dice. Couldn\'t find an h, l, or d to indicate roll type')
            return -1
        # Determine which type of roll is needed and split the dice up

        if roll.find('x') > -1:
            try:
                reps = int(roll[roll.find('x') + 1:])
            except:
                await ctx.send('Error rolling dice. Make sure the number of repetitions is valid')
                return -1
            roll = roll[:roll.find('x')]
        else:
            reps = 1
        # Determine if repetitions are needed

        if roll[-1] == '!':
            btype = 'each'
            roll = roll[:-1]
        else:
            btype = 'all'
        # Determine bonus type

        has_bonus = False
        if roll.find('+') > -1:
            has_bonus = True
            bsplit = roll.find('+')
            bj = '+'
        elif roll.find('-') > -1:
            has_bonus = True
            bsplit = roll.find('-')
            bj = '-'
        if has_bonus:
            try:
                bonus = int(roll[roll.find(bj):])
            except:
                await ctx.send('Error rolling dice. Make sure the bonus/malus (+/-) is valid')
                return -1
            roll = roll[:bsplit]
        else:
            bonus = 0
        # Determine bonus

        try:
            sides = int(roll[dsplit + 1:])
        except:
            await ctx.send('Error rolling dice. Make sure the number of sides is valid')
            return -1
        # Split the sides

        if dsplit > 0:
            try:
                number = int(roll[:dsplit])
            except:
                await ctx.send('Error rolling dice. Make sure the number of dice is valid')
                return -1
        else:
            number = 1
        # Split the number

        if not (number > 0 and number <= 50):
            await ctx.send('Error rolling dice. The number of dice must be between 1 and 50')
            return -1
        if not (sides > 0 and sides <= 1000):
            await ctx.send('Error rolling dice. The number of sides must be between 1 and 1000')
            return -1
        if not (reps > 0 and reps <= 10):
            await ctx.send('Error rolling dice. The number of repetitions must be between 1 and 10')
            return -1
        # Check everything is within limits

        dice = [[random.randint(1,sides) for di in range(number)] for ri in range(reps)]
        # Roll the dice

        if btype == 'each':
            if type == 'high':
                results = [max(rep) + bonus for rep in dice]
            elif type == 'low':
                results = [min(rep) + bonus for rep in dice]
            elif type == 'sum':
                results = []
                for rep in dice:
                    result = ''
                    for die in rep:
                        result += str(die+bonus) + ', '
                    result = result[:-2]
                    results.append(result)
        else:
            if type == 'high':
                results = [max(rep) + bonus for rep in dice]
            elif type == 'low':
                results = [min(rep) + bonus for rep in dice]
            elif type == 'sum':
                results = [sum(rep) + bonus for rep in dice]
        # Calculate results

        response = ''
        if has_tag:
            response += '"' + tag + '" '
        for ind, rep in enumerate(dice):
            for die in rep:
                chosen = (type == 'sum' or type == 'high' and die == max(rep)
                                        or type == 'low'  and die == min(rep))
                if chosen:
                    response += '[' + str(die)
                else:
                    response += '(' + str(die)
                if btype == 'each' and bonus:
                    response += ' ' + bj + str(abs(bonus))
                if chosen:
                    response += '] '
                else:
                    response += ') '
            if btype == 'all' and bonus:
                response += bj + ' ' + str(abs(bonus)) + ' '
            response += '= ' + str(results[ind])
            if ind < reps - 1:
                response += ' :: '
        # Build the response string
        await ctx.send(response)

    @commands.command()
    async def card(self,ctx):
        '''Draw a random card from a standard deck'''
        suit = random.choice(('Hearts','Spades','Clubs','Diamonds'))
        value = random.choice(('Ace','Two','Three','Four','Five','Six',
                              'Seven','Eight','Nine','Ten','Jack','Queen','King'))
        await ctx.send(value + ' of '+ suit)

    @commands.command()
    async def tarot(self,ctx,type = 'any'):
        '''Draw a tarot card
        Can use `%tarot major` or `%tarot minor` to specify minor or major arcana'''
        type = type.lower()
        if not type in ('major','minor','any'):
            await ctx.send('The type of the card must be major, minor, or any.')
            return
        major = random.choice(('The Fool', 'I. The Magician',
                               'II. The High Priestess', 'III. The Empress',
                               'IV. The Emperor', 'V. The Hierophant',
                               'VI. The Lovers','VII. The Chariot',
                               'VIII. Justice', 'IX. The Hermit',
                               'X. Wheel of Fortune', 'XI. Strength',
                               'XII. The Hanged Man', 'XIII. Death',
                               'XIV. Temperance', 'XV. The Devil',
                               'XVI. The Tower', 'XVII. The Star',
                               'XVIII. The Moon', 'XIX. The Sun',
                               'XX. Judgement', 'XXI. The World'))
        value = random.choice(('Ace','Two','Three','Four','Five','Six',
                              'Seven','Eight','Nine','Ten','Page','Knight',
                              'Queen','King'))
        suit = random.choice(('Wands','Swords','Pentacles','Cups'))
        if type == 'any':
            if random.randint(1,78) > 56:
                type = 'major'
            else:
                type = 'minor'
        if type == 'major':
            await ctx.send(major)
        else:
            await ctx.send(value + ' of '+ suit)

    @commands.command()
    async def shuffle(self, ctx, *args):
        '''Shuffles space seperated arguments'''
        shuffled = []
        for arg in args:
            shuffled += [str(arg)]
        random.shuffle(shuffled)
        result = '[ '
        for i in shuffled:
            result += i + ', '

        result = result[:-2] + ' ]'
        await ctx.send(result)

    @commands.command()
    async def archetypes(self, ctx, *args):
        '''Generates random archetypes for PD character creation'''
        types = [
            'Lancer: +1 Brawn, +1 Athletics, ',
            'Fury: +1 Brawn, +1 Dexterity, ',
            'Gladiator: +1 Brawn, +1 Wits, ',
            'Bully: +1 Brawn, +1 Social, ',
            'Master: +1 Brawn, +1 Knowledge, ',
            'Titan: +1 Brawn, +1 Guts, ',
            'Raider: +1 Athletics, +1 Brawn, ',
            'Hunter: +1 Athletics, +1 Dexterity, ',
            'Stalker: +1 Athletics, +1 Wits, ',
            'Wayfarer: +1 Athletics, +1 Social, ',
            'Explorer: +1 Athletics, +1 Knowledge, ',
            'Interceptor: +1 Athletics, +1 Guts, ',
            'Assassin: +1 Dexterity, +1 Brawn, ',
            'Scoundrel: +1 Dexterity, +1 Athletics, ',
            'Marksman: +1 Dexterity, +1 Wits, ',
            'Broker: +1 Dexterity, +1 Social, ',
            'Craftsman: +1 Dexterity, +1 Knowledge, ',
            'Packrat: +1 Dexterity, +1 Guts, ',
            'Guard: +1 Wits, +1 Brawn, ',
            'Lookout: +1 Wits, +1 Athletics, ',
            'Monitor: +1 Wits, +1 Dexterity, ',
            'Handler: +1 Wits, +1 Social, ',
            'Investigator: +1 Wits, +1 Knowledge, ',
            'Sentinel: +1 Wits, +1 Guts, ',
            'Boss: +1 Social, +1 Brawn, ',
            'Lead: +1 Social, +1 Athletics, ',
            'Playboy: +1 Social, +1 Dexterity, ',
            'Psychologist: +1 Social, +1 Wits, ',
            'Manipulator: +1 Social, +1 Knowledge, ',
            'Holdout: +1 Social, +1 Guts, ',
            'Expert: +1 Knowledge, +1 Brawn, ',
            'Pioneer: +1 Knowledge, +1 Athletics, ',
            'Polymath: +1 Knowledge, +1 Dexterity, ',
            'Schemer: +1 Knowledge, +1 Wits, ',
            'Tactician: +1 Knowledge, +1 Social, ',
            'Architect: +1 Knowledge, +1 Guts, ',
            'Juggernaut: +1 Guts, +1 Brawn, ',
            'Horse: +1 Guts, +1 Athletics, ',
            'Tough: +1 Guts, +1 Dexterity, ',
            'Survivor: +1 Guts, +1 Wits, ',
            'Icon: +1 Guts, +1 Social, ',
            'Pillar: +1 Guts, +1 Knowledge, '
        ]
        minuses = [
            ['-1 Social', '-1 Social'],  # Lancer
            ['-1 Knowledge', '-1 Social'],
            ['-1 Knowledge', '-1 Knowledge'],
            ['-1 Dexterity', '-1 Dexterity'],
            ['-1 Dexterity', '-1 Wits'],
            ['-1 Wits', '-1 Wits'],
            ['-1 Social', '-1 Social'],  # Raider
            ['-1 Knowledge', '-1 Knowledge'],
            ['-1 Knowledge', '-1 Guts'],
            ['-1 Guts', '-1 Guts'],
            ['-1 Wits', '-1 Wits'],
            ['-1 Wits', '-1 Social'],
            ['-1 Social', '-1 Knowledge'],  # Assassin
            ['-1 Knowledge', '-1 Knowledge'],
            ['-1 Guts', '-1 Guts'],
            ['-1 Guts', '-1 Brawn'],
            ['-1 Brawn', '-1 Brawn'],
            ['-1 Social', '-1 Social'],
            ['-1 Knowledge', '-1 Knowledge'],  # Guard
            ['-1 Knowledge', '-1 Guts'],
            ['-1 Guts', '-1 Guts'],
            ['-1 Brawn', '-1 Brawn'],
            ['-1 Brawn', '-1 Athletics'],
            ['-1 Athletics', '-1 Athletics'],
            ['-1 Dexterity', '-1 Dexterity'],  # Boss
            ['-1 Guts', '-1 Guts'],
            ['-1 Guts', '-1 Brawn'],
            ['-1 Brawn', '-1 Brawn'],
            ['-1 Athletics', '-1 Athletics'],
            ['-1 Athletics', '-1 Dexterity'],
            ['-1 Dexterity', '-1 Wits'],  # Expert
            ['-1 Wits', '-1 Wits'],
            ['-1 Brawn', '-1 Brawn'],
            ['-1 Brawn', '-1 Athletics'],
            ['-1 Athletics', '-1 Athletics'],
            ['-1 Dexterity', '-1 Dexterity'],
            ['-1 Wits', '-1 Wits'],  # Juggernaut
            ['-1 Wits', '-1 Social'],
            ['-1 Social', '-1 Social'],
            ['-1 Athletics', '-1 Athletics'],
            ['-1 Athletics', '-1 Dexterity'],
            ['-1 Dexterity', '-1 Dexterity']
        ]
        specials = [
            'Champion: +2 Brawn, ',
            'Athlete: +2 Athletics, ',
            'Ace: +2 Dexterity, ',
            'Scout: +2 Wits, ',
            'Politician: +2 Social, ',
            'Genius: +2 Knowledge, ',
            'Indomitable: +2 Guts, '
        ]
        specialMinuses = [
            ['-1 Wits', '-1 Social'],
            ['-1 Social', '-1 Knowledge'],
            ['-1 Knowledge', '-1 Guts'],
            ['-1 Guts', '-1 Brawn'],
            ['-1 Brawn', '-1 Athletics'],
            ['-1 Athletics', '-1 Dexterity'],
            ['-1 Dexterity', '-1 Wits']
        ]
        output = ''

        if len(args) == 0:
            num = [random.randint(0, 41) for roll in range(3)]
            diffs = [random.randint(0, 1) for roll in range(3)]
            if len(set(num)) == 3:
                counter = 0
                for number in num:
                    output += types[number]
                    output += minuses[number][diffs[counter]]
                    output += '\n'
                    counter += 1

            elif len(set(num)) == 2:
                checker = []
                counter = 0
                for number in num:
                    if number in checker:
                        output += specials[int((number + 1) / 7)]
                        output += specialMinuses[int((number + 1) / 7)][diffs[counter]]
                        output += '\n'
                        counter += 1
                    else:
                        checker.append(number)
                        output += types[number]
                        output += minuses[number][diffs[counter]]
                        output += '\n'
                        counter += 1

            elif len(set(num)) == 1:
                output += "Triple!\n"
                output += types[num[1]]
                output += minuses[num[1]][diffs[0]]
                output += '\n'
                output += specials[int((num[1] + 1) / 7)]
                output += specialMinuses[int((num[1] + 1) / 7)][0]
                output += '\n'
                output += specials[int((num[1] + 1) / 7)]
                output += specialMinuses[int((num[1] + 1) / 7)][1]
                output += '\n'

        else:
            try:
                amount = int(args[0])
                if amount > 7:
                    output = "Error: This command is capped at 7 to avoid spam."
                elif amount < 1:
                    output = "Error: This command needs to provide at least 1 archetype."
                else:
                    types += specials
                    minuses += specialMinuses
                    rolls = [random.randint(0,48) for x in range(amount)]
                    diffs = [random.randint(0, 1) for x in range(amount)]
                    counter = 0
                    for roll in rolls:
                        output += types[roll]
                        output += minuses[roll][diffs[counter]]
                        output += '\n'
                        counter += 1

            except ValueError:
               output = "Error: Cannot parse input."

        await ctx.send(output)