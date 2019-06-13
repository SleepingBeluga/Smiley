from discord.ext import commands
import random

class Rolls(commands.Cog):
    '''For rolling dice
    '''
    __init__ (self):
        self.r = self.roll

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
