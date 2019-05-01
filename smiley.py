#!/usr/bin/env python
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import time, random, sheets, asyncio

'''
My (Smiley's) Main Script

I'm friendly, and I can do Pact Dice drafts and dice rolls!
'''

b = commands.Bot(command_prefix=('~'))
memory = {}
fopen = open

async def setup():
    '''
    My initializing function.
    '''

    memory['channel'] = None
    memory['phase'] = 'none'
    memory['round'] = None
    memory['bidding'] = False
    memory['clashing'] = False
    # Set all the 'state' indicators to defaults

    memory['players'] = []
    memory['to resolve'] = []
    memory['player colors'] = []

    memory['pending trades'] = []
    memory['trade contents'] = {}

    memory['proper names'] = {}
    memory['bids'] = {}
    memory['clash choices'] = {}
    memory['black marks'] = {}
    memory['white marks'] = {}
    memory['limits'] = {}
    # Make empty arrays for all the player things

    memory['rows to show'] = 0

    memory['clash'] = False

    memory['quitconfirm'] = False

    memory['cats'] = ('puissance', 'longevity', 'access', 'executions', 'research', \
                          'schools',   'priority',  'family')
    memory['puissance']  = ['', '', '', '', '',    '', '', '']
    memory['longevity']  = ['', '', '', '', '',    '', '', '']
    memory['access']     = ['', '', '', '', '',    '', '', '']
    memory['executions'] = ['', '', '', '', '',    '', '', '']
    memory['research']   = ['', '', '', '', '',    '', '', '']
    memory['schools']    = ['', '', '', '', '',    '', '', '']
    memory['priority']   = ['', '', '', '', '',    '', '', '']
    memory['family']     = ['', '', '', '', '',    '', '', '']

    memory['clashes'] = [[],[],[]]
    # More empty things

    memory['colors'] = {"purple": (0.2,0.1,0.5),
                        "blue":   (0.1,0.3,0.8),
                        "green":  (0.2,0.5,0.1),
                        "yellow": (0.7,0.6,0.0), # Leave out first
                        "orange": (0.7,0.4,0.0), # Leave out second
                        "red":    (0.6,0.0,0.0)
                        }
    # Define colors

    memory['clashesin'] = asyncio.Event()
    memory['bidsin'] = asyncio.Event()
    # Events for the end of clash and bids

async def subround(clash):
    '''
    My main loop. Executes subrounds and resolves clashes.
    Parameter: bool clash - True if function should handle post-clash bids
                            False if function should do a full round
    Return: None
    '''
    if not clash:
        await memory['channel'].send('It\'s the beginning of round ' + str(memory['round']) + '! (Submit your bids by PMing me with e.x. ~bid Executions 2)')
        # Start a full round & tell players to submit bids
    else:
    # Resolve clashes
        to_say = 'We need to finish resolving the clashes! '
        for player in memory['to resolve']:
            to_say = to_say + memory['proper names'][player] + ', '
        if len(memory['to resolve']) > 1:
            to_say = to_say + 'please submit your bids by PMing me with e.x. ~bid Executions 2'
        else:
            to_say = to_say + 'please submit your bid by PMing me with e.x. ~bid Executions 2'
        await memory['channel'].send(to_say)
        await memory['channel'].send('Remember, bids are restricted by the results of the clashes.')
        # Tell players to submit bids
    await get_bids()
    # Wait until bids are all submitted

    if memory['phase'] == 'none':
        return
    # Make sure the draft hasn't been reset

    await calc_clashes()
    # See if there are any clashes

    while memory['clash']:
        await do_clash(False)
        if memory['phase'] == 'none':
            return
    # Handle any and all clashes

    await update_sheet()
    # Post results to the google sheet

    if len(memory['to resolve']) > 0:
        await subround(True)
    # If the clashes need to be resolved, do another subround for those bids

    elif memory['round'] == 8:
        await memory['channel'].send('That\'s the end of the draft! Thanks for playing!')
        await setup()
    # If it's the last round, end the draft

    else:
        memory['to resolve'] = memory['players']
        memory['round'] += 1
        await subround(False)
    # Go on to the next full round!

async def show_cats():
    '''
    Displays the categories so you can see who has what.
    This function is not called by anything, and has been replaced by google
     sheets integration.
    '''

    for cat in memory['cats']:
        to_say = cat.capitalize()
        for i in range(11 - len(cat)):
            to_say += ' '
        to_say += '| '
        for i in range(memory['rows to show']):
            if memory[cat][i] == '':
                for j in range(14):
                    to_say += ' '
            else:
                to_say += ' ' + memory['proper names'][memory[cat][i]][:-1] + '​' + memory['proper names'][memory[cat][i]][-1]
                for j in range(13 - len(memory[cat][i])):
                    to_say += ' '
            to_say += '|'
        await memory['channel'].send(to_say)

    for player in memory['players']:
        to_say = memory['proper names'][player][:-1] + '​' + memory['proper names'][player][-1] + ': '
        for i in range(memory['white marks'][player]):
            to_say += '☆'
        to_say += ' | '
        for i in range(memory['black marks'][player]):
            to_say += '★'
        await memory['channel'].send(to_say)

async def blank_sheet():
    '''
    Makes a new sheet for a PD Draft.
    Parameters: none
    Return: None
    '''
    num_players = len(memory["players"])
    memory["sheetID"] = await sheets.new_blank_sheet(memory, num_players)
    await memory['channel'].send('Click here to follow: https://docs.google.com/spreadsheets/d/' + memory["sheetID"])

async def update_sheet():
    '''
    Goes through my memory and copies current draft results
    to the google sheet.
    Parameters: none
    Return: None
    '''
    if memory['rows to show'] > len(memory['players']):
        # Extend sheet at some point in the future
        do_nothing_here_yet = 0
    for cat in memory['cats']:
        for rank in range(memory['rows to show']):
            if not memory[cat][rank] == '':
                player = memory[cat][rank]
                index = memory['players'].index(player)
                row = memory['cats'].index(cat) + 1
                col = rank + 1
                await sheets.write_cell(memory, (row,col), memory['proper names'][player], memory['colors'][memory['player colors'][index]], (1,1,1))
    # Write into each filled category the player who has it

    for index in range(len(memory['players'])):
        player = memory['players'][index]
        row = index + 11
        to_write = ''
        for i in range(memory['white marks'][player]):
            to_write += '★'
        await sheets.write_cell(memory, (row,1), to_write, (0.15,0.15,0.15), (1,1,1))
        to_write = ''
        for i in range(memory['black marks'][player]):
            to_write += '☆'
        await sheets.write_cell(memory, (row,2), to_write, (0.15,0.15,0.15), (1,1,1))
    # Write each player's karma into the karma table

async def do_player_karma_labels():
    for index in range(len(memory['players'])):
        player = memory['players'][index]
        await sheets.write_cell(memory, (11+index,0), memory['proper names'][player], memory['colors'][memory['player colors'][index]], (1,1,1))

async def get_bids():
    for player in memory['players']:
        if player not in memory['to resolve']:
            memory['bids'][player] = 0
        else:
            memory['bids'][player] = None
    memory['bidding'] = True
    #asyncio.run(bid_reminder())
    await memory['bidsin'].wait()
    memory['bidsin'].clear()
    memory['bidding'] = False
    for player in memory['players']:
        memory['limits'][player] = 0
'''
Tells players to submit bids, and waits until all bids are done.
'''

async def bid_reminder():
    asyncio.sleep(240)
    while not memory['bidsin'].is_set():
        to_say = 'Still waiting for '
        for player in memory['to resolve']:
            if memory['bids'][player] == None:
                to_say = to_say + memory['proper names'][player] + ', '
        if to_say[-2:] == ', ':
            to_say = to_say[:-2]
        memory['channel'].send(to_say)
        if not memory['bidding']:
            return
        asyncio.sleep(240)

async def calc_clashes():
    bid = None
    bid_player = None
    clashes_so_far = 0
    found_clash = False
    for player in memory['to resolve']:
        if not (player in memory['clashes'][0] or \
                player in memory['clashes'][1] or \
                player in memory['clashes'][2]):
            bid = memory['bids'][player]
            for player2 in memory['to resolve']:
                if not (player2 in memory['clashes'][0] or \
                        player2 in memory['clashes'][1] or \
                        player2 in memory['clashes'][2]):
                    if bid == memory['bids'][player2] and not player == player2:
                        memory['clashes'][clashes_so_far].append(player2)
                        if not player in memory['clashes'][clashes_so_far]:
                            memory['clashes'][clashes_so_far].append(player)
                            found_clash = True
        if found_clash:
            clashes_so_far += 1
            found_clash = False
    if clashes_so_far == 0:
        await memory['channel'].send('There are no clashes.')
    elif clashes_so_far == 1:
        await memory['channel'].send('There\'s a clash!')
    else:
        await memory['channel'].send('There are ' + str(clashes_so_far) + ' clashes!')

    for player in memory['to resolve']:
        if not (player in memory['clashes'][0] or \
                player in memory['clashes'][1] or \
                player in memory['clashes'][2]):
            memory[memory['bids'][player][0]][memory['bids'][player][1] - 1] = player

    if clashes_so_far > 0:
        memory['clash'] = True
    memory['to resolve'] = []
'''
Figures out if there are clashes and who's in each.
'''

async def do_clash(continued):
    if not continued:
        to_say = 'Clash: '
        for player in memory['clashes'][0]:
            to_say = to_say + memory['proper names'][player] + ', '
        to_say = to_say[:-2] + ' for ' + memory['bids'][memory['clashes'][0][0]][0].capitalize() \
                             + ' ' + str(memory['bids'][memory['clashes'][0][0]][1]) + '! ' \
                             + 'Please PM me with either ~stay or ~concede'
        await memory['channel'].send(to_say)

    number_of_clashers = len(memory['clashes'][0])

    if number_of_clashers == 2:
        player0 = memory['clashes'][0][0]
        player1 = memory['clashes'][0][1]
        for player in memory['players']:
            memory['clash choices'][player] = ""
        await get_clash_choices()
        if memory['clash choices'][player0] == 'stay':
            if memory['clash choices'][player1] == 'stay':
                await memory['channel'].send('They both stayed!')

                # Anti luck manipulation barriers around the random parts

                # MUSA DERELINQUAS ME SERMONIBUS          🐀
                coin0 = random.choice(('heads','tails')) #🐀
                coin1 = random.choice(('heads','tails')) #🐀
                # Thal, stay away.                        🐀

                to_say = 'Flipping a coin for ' + memory['proper names'][player0] + ': ' + coin0.capitalize() + '! '
                if coin0 == 'heads':
                    to_say = to_say + memory['proper names'][player0] + ' loses the spot and will have to rebid at least two rungs lower.'
                    memory['to resolve'].append(player0)
                    memory['limits'][player0] = memory['bids'][memory['clashes'][0][0]][1] + 2
                    if memory['bids'][memory['clashes'][0][0]][1] + 2 > memory['rows to show']:
                        memory['rows to show'] = memory['bids'][memory['clashes'][0][0]][1] + 2

                else:
                    to_say = to_say + memory['proper names'][player0] + ' gets a black mark.'
                    memory['black marks'][player0] += 1
                await memory['channel'].send(to_say)
                to_say = 'Flipping a coin for ' + memory['proper names'][player1] + ': ' + coin1.capitalize() + '! '
                if coin1 == 'heads':
                    to_say = to_say + memory['proper names'][player1] + ' loses the spot and will have to rebid at least two rungs lower.'
                    memory['to resolve'].append(player1)
                    memory['limits'][player1] = memory['bids'][memory['clashes'][0][0]][1] + 2
                    if memory['bids'][memory['clashes'][0][0]][1] + 2 > memory['rows to show']:
                        memory['rows to show'] = memory['bids'][memory['clashes'][0][0]][1] + 2

                else:
                    to_say = to_say + memory['proper names'][player1] + ' gets a black mark.'
                    memory['black marks'][player1] += 1
                await memory['channel'].send(to_say)

                if coin0 == 'tails' and coin1 == 'tails':
                    await memory['channel'].send('The clash continues! Please choose either ~stay or ~concede again.')
                    await do_clash(True)
                    return
                elif coin0 == 'tails':
                    memory[memory['bids'][memory['clashes'][0][0]][0]][memory['bids'][memory['clashes'][0][0]][1] - 1] \
                        = player0
                elif coin1 == 'tails':
                    memory[memory['bids'][memory['clashes'][0][0]][0]][memory['bids'][memory['clashes'][0][0]][1] - 1] \
                        = player1

            if memory['clash choices'][player1] == 'concede':
                # FORTUNA RERUM NATURALIUM               🐀
                coin = random.choice(('heads','tails')) #🐀
                # Thal, get out                          🐀
                to_say = memory['proper names'][player0] + ' stayed. ' + memory['proper names'][player1] + ' conceded. Flipping a coin: ' + coin + '! '
                if coin == 'heads':
                    to_say += memory['proper names'][player1] + ' gets a white mark and chooses a category at a lower rung. ' + \
                              memory['proper names'][player0] + ' gets the spot.'
                    memory['white marks'][player1] += 1
                else:
                    to_say += memory['proper names'][player1] + ' loses the spot and will have to choose a category at a lower rung. ' + \
                              memory['proper names'][player0] + ' gets the spot and a black mark.'
                    memory['black marks'][player0] += 1
                await memory['channel'].send(to_say)
                memory['limits'][player1] = memory['bids'][memory['clashes'][0][0]][1] + 1
                if memory['bids'][memory['clashes'][0][0]][1] + 1 > memory['rows to show']:
                    memory['rows to show'] = memory['bids'][memory['clashes'][0][0]][1] + 1
                memory['to resolve'].append(player1)
                memory[memory['bids'][memory['clashes'][0][0]][0]][memory['bids'][memory['clashes'][0][0]][1] - 1] \
                        = player0

        elif memory['clash choices'][player0] == 'concede':
            if memory['clash choices'][player1] == 'stay':
                # EX TALIS MAGA                                🐀
                coin = random.choice(('heads','tails'))       #🐀
                # I'm serious, Thal. This code is witch-proof  🐀
                to_say = player1 + ' stayed. ' + memory['proper names'][player0] + ' conceded. Flipping a coin: ' + coin + '! '
                if coin == 'heads':
                    to_say += memory['proper names'][player0] + ' gets a white mark and chooses a category at a lower rung. ' + \
                              memory['proper names'][player1] + ' gets the spot.'
                    memory['white marks'][player0] += 1
                else:
                    to_say += memory['proper names'][player0] + ' loses the spot and will have to choose a category at a lower rung. ' + \
                              memory['proper names'][player1] + ' gets the spot and a black mark.'
                    memory['black marks'][player1] += 1
                await memory['channel'].send(to_say)
                memory['limits'][player0] = memory['bids'][memory['clashes'][0][0]][1] + 1
                if memory['bids'][memory['clashes'][0][0]][1] + 1 > memory['rows to show']:
                    memory['rows to show'] = memory['bids'][memory['clashes'][0][0]][1] + 1
                memory['to resolve'].append(player0)
                memory[memory['bids'][memory['clashes'][0][0]][0]][memory['bids'][memory['clashes'][0][0]][1] - 1] \
                        = player1

            elif memory['clash choices'][player1] == 'concede':
                await memory['channel'].send('They both conceded, and will need to rebid for a lower rung.')
                memory['limits'][player0] = memory['bids'][memory['clashes'][0][0]][1] + 1
                memory['limits'][player1] = memory['bids'][memory['clashes'][0][0]][1] + 1
                if memory['bids'][memory['clashes'][0][0]][1] + 1 > memory['rows to show']:
                    memory['rows to show'] = memory['bids'][memory['clashes'][0][0]][1] + 1
                memory['to resolve'].append(player0)
                memory['to resolve'].append(player1)

    else:
        to_mark = []
        clashers = []
        remaining = []
        for player in memory['players']:
            memory['clash choices'][player] = ""
        await get_clash_choices()
        for i in range(number_of_clashers):
            clashers.append(memory['clashes'][0][i])
        for player in clashers:
            if memory['clash choices'][player] == 'concede':
                memory['to resolve'].append(player)
                memory['limits'][player] = memory['bids'][memory['clashes'][0][0]][1] + 1
                if memory['bids'][memory['clashes'][0][0]][1] + 1 > memory['rows to show']:
                    memory['rows to show'] = memory['bids'][memory['clashes'][0][0]][1] + 1
                number_of_clashers -= 1
                memory['clashes'][0].remove(player)
                await memory['channel'].send(memory['proper names'][player] + ' conceded, and will have to rebid for a lower rung.')
            elif memory['clash choices'][player] == 'stay':
                # MAGICAE NON INTERMIXTI                                 🐀
                coin = random.choice(('heads','tails'))                 #🐀
                # Let's see you get around that foolproof magic barrier  🐀
                to_say = memory['proper names'][player] + ' stayed. Flipping a coin: ' + coin + '! '
                if coin == 'heads':
                    to_say += memory['proper names'][player] + ' loses the spot, and will have to choose a rung at least two lower.'
                    memory['limits'][player] = memory['bids'][memory['clashes'][0][0]][1] + 2
                    if memory['bids'][memory['clashes'][0][0]][1] + 2 > memory['rows to show']:
                        memory['rows to show'] = memory['bids'][memory['clashes'][0][0]][1] + 2
                    memory['to resolve'].append(player)
                    number_of_clashers -= 1
                    memory['clashes'][0].remove(player)
                elif coin == 'tails':
                    to_say += memory['proper names'][player] + ' remains.'
                    to_mark.append(player)
                    remaining.append(player)
                await memory['channel'].send(to_say)
        if number_of_clashers <= 2 and number_of_clashers > 0:
            to_say = 'Since there are 2 or less clashers remaining, black marks will be doled out to '
            for player in to_mark:
                to_say += memory['proper names'][player] + ', '
                memory['black marks'][player] += 1
            to_say = to_say[:-2] + '!'
            await memory['channel'].send(to_say)
        if number_of_clashers > 1:
            await memory['channel'].send('There\'s more than one clasher remaining! Remaining clashers, PM me with ~stay or ~concede again!')
            await do_clash(True)
            return
        elif number_of_clashers == 1:
            player = remaining[0]
            await memory['channel'].send('There\'s only ' + memory['proper names'][player] + ' left! They get the spot!')
            memory[memory['bids'][memory['clashes'][0][0]][0]][memory['bids'][memory['clashes'][0][0]][1] - 1] \
                = player
        else:
            await memory['channel'].send('No one gets the spot this round!')

    memory['clashes'][0] = memory['clashes'][1]
    memory['clashes'][1] = memory['clashes'][2]
    memory['clashes'][2] = []

    if memory['clashes'][0] == []:
        memory['clash'] = False
'''
Performs clashes and adds players who need to rebid to 'to resolve'.
'''

async def get_clash_choices():
    for player in memory['players']:
        if player not in memory['clashes'][0]:
            memory['clash choices'][player] = ""
        else:
            memory['clash choices'][player] = None
    memory['clashing'] = True
    #asyncio.run(clash_reminder())
    await memory['clashesin'].wait()
    memory['clashesin'].clear()
    memory['clashing'] = False
'''
Tells players to submit clash choices, and waits until all clash choices are done.
'''

async def all_resolved():
    if any(x == '' for x in memory['puissance'][:len(memory['players'])]):
        return False
    if any(x  == ''  for x in memory['longevity'][:len(memory['players'])]):
        return False
    if any(x  == ''  for x in memory['access'][:len(memory['players'])]):
        return False
    if any(x  == ''  for x in memory['executions'][:len(memory['players'])]):
        return False
    if any(x  == ''  for x in memory['research'][:len(memory['players'])]):
        return False
    if any(x  == ''  for x in memory['schools'][:len(memory['players'])]):
        return False
    if any(x  == ''  for x in memory['priority'][:len(memory['players'])]):
        return False
    if any(x  == ''  for x in memory['family'][:len(memory['players'])]):
        return False
    return True
'''
Not used because it doesn't work yet. Ideally should calculate when future rounds can be autofilled, but with insigs/abysmal that's not an easy check.
'''

@b.command()
async def hi(ctx, *args):
    await ctx.send('Hi, ' + ctx.author.display_name + '!')
'''
The hi command. I'll greet the user.
'''

@b.command()
async def open(ctx, *args):
    if memory['phase'] == 'none':
        memory['phase'] = 'setup'
        await ctx.send('Opening a draft! (Use ~join to join, and then ~start to begin)')
    else:
        await ctx.send('A draft is already ongoing! Finish it before trying again.')
'''
Begins a draft so people can join.
'''

@b.command()
async def join(ctx, *args):
    if memory['phase'] == 'setup':
        if not str(ctx.author) in memory['players']:
            memory['players'].append(str(ctx.author))
            memory['proper names'][str(ctx.author)] = ctx.author.display_name
            await ctx.send(ctx.author.display_name + ' has joined!')
        else:
            await ctx.send('You\'ve already joined!')
    elif memory['phase'] == 'none':
        await ctx.send('You can\'t join because there\'s no draft going on! (Use ~open to start one)')
    else:
        await ctx.send('You can\'t join right now, we\'re in ' + memory['phase'] + '!')
'''
Lets you join a draft.
'''

@b.command()
async def start(ctx, *args):
    if memory['phase'] == 'setup':
        if len(memory['players']) >= 1 and len(memory['players']) <= 6:
            await ctx.send('Starting the draft!')
            memory['channel'] = ctx
            memory['phase'] = 'the draft'
            memory['round'] = 1
            memory['to resolve'] = memory['players']
            for player in memory['players']:
                memory['black marks'][player] = 0
                memory['white marks'][player] = 0
            for player in memory['players']:
                memory['limits'][player] = 0
            if len(memory['players']) == 4:
                memory['player colors'] = ['red','green','blue','purple']
            elif len(memory['players']) == 5:
                memory['player colors'] = ['red','orange','green','blue','purple']
            elif len(memory['players']) == 6:
                memory['player colors'] = ['red','orange','yellow','green','blue','purple']
            memory['rows to show'] = len(memory['players'])
            await blank_sheet()
            await do_player_karma_labels()
            await subround(False)
        else:
            await ctx.send('You must have between 4 and 6 players to start.')
    elif memory['phase'] == 'none':
        await ctx.send('You can\'t start the draft yet, you need players first! (Use ~open to let players join)')
    else:
        await ctx.send('You can\'t start a draft right now, we\'re in ' + memory['phase'] + '!')
'''
Starts the draft after players join.
'''

@b.command()
async def reset(ctx, *args):
    if not memory['quitconfirm']:
        await ctx.send('Are you sure? This will reset any drafts in progress. (Use ~reset again to confirm)')
        memory['quitconfirm'] = True
        await asyncio.sleep(60)
        memory['quitconfirm'] = False
    else:
        await ctx.send('OK, I\'ve reset.')
        await setup()
'''
Resets me, stopping any drafts in progress.
'''

@b.command()
async def bid(ctx, *args):
    if not type(ctx.channel) == discord.DMChannel:
        await ctx.send('This command only works in DMs.')
        return
    lower_args = [arg.lower() for arg in args]
    if memory['bidding']:
        if str(ctx.author) in memory['to resolve']:
            if len(lower_args) == 2:
                cat = lower_args[0]
                rung = int(lower_args[1])
                if cat in memory['cats']:
                    if not str(ctx.author) in memory[cat]:
                        if (rung <= len(memory['players']) and rung >= memory['limits'][str(ctx.author)]) or rung == memory['limits'][str(ctx.author)]:
                            if memory[cat][rung - 1] == '':
                                await ctx.send('Got it!')
                                memory['bids'][str(ctx.author)] = (cat, rung)
                                await check_bids()
                            else:
                                await ctx.send('That one\'s taken, please choose another.')
                        else:
                            to_say = 'Please choose a rung between '
                            if memory['limits'][str(ctx.author)] == 0:
                                to_say += '1'
                            else:
                                to_say += str(memory['limits'][str(ctx.author)])
                            to_say += ' and '
                            if memory['limits'][str(ctx.author)] <= len(memory['players']):
                                to_say += str(len(memory['players']))
                            else:
                                to_say += str(memory['limits'][str(ctx.author)])
                            to_say += '. Format your message like this: ~bid puissance 4'
                            await ctx.send(to_say)
                    else:
                        await ctx.send('You already have a rung in that category! Pick another, please.')
                else:
                    await ctx.send ('I don\'t know that category. Format your message like this: ~bid puissance 4')
            else:
                await ctx.send('Format your message like this: ~bid puissance 4')
        else:
            await ctx.send('I don\'t need a bid from you right now.')
    else:
        await ctx.send('Now\'s not the time for bidding.')
'''
Allows players to bid on draft slots.
'''

async def check_bids():
    if not None in memory['bids'].values():
        memory['bidsin'].set()

async def check_clash_choices():
    if not None in memory['clash choices'].values():
        memory['clashesin'].set()

@b.command()
async def stay(ctx, *args):
    if not type(ctx.channel) == discord.DMChannel:
        await ctx.send('This command only works in DMs.')
        return
    if memory['clashing']:
        if str(ctx.author) in memory['clashes'][0]:
            await ctx.send('OK!')
            memory['clash choices'][str(ctx.author)] = 'stay'
            await check_clash_choices()
        else:
            await ctx.send('I don\'t need a choice from you right now.')
    else:
        await ctx.send('Now\'s not the time to submit a clash choice.')
'''
The command to refuse to budge during a clash.
'''

@b.command()
async def concede(ctx, *args):
    if not type(ctx.channel) == discord.DMChannel:
        await ctx.send('This command only works in DMs.')
        return
    if memory['clashing']:
        if str(ctx.author) in memory['clashes'][0]:
            await ctx.send('OK!')
            memory['clash choices'][str(ctx.author)] = 'concede'
            await check_clash_choices()
        else:
            await ctx.send('I don\'t need a choice from you right now.')
    else:
        await ctx.send('Now\'s not the time to submit a clash choice.')
'''
The command to cede during a clash.
'''

@b.command()
async def table(ctx, *args):
    if memory['phase'] == 'the draft':
        show_cats()
    else:
        await ctx.send('There\'s no draft going on.')
'''
Shows the current draft progress
'''

@b.command()
async def offer(ctx, *args):
    lower_args = [arg.lower() for arg in args]
    if memory['phase'] == 'the draft':
        if str(ctx.author) in memory['players']:
            if not str(ctx.author) in memory['pending trades']:
                args = lower_args
                if len(args) >= 6:
                    recipient = args[0].lower()
                    if recipient in memory['players']:
                        if not recipient in memory['pending trades']:
                            offered = []
                            wanted = []
                            past_offered = False
                            i = 1
                            while i < len(args):
                                if args[i] == 'for':
                                    past_offered = True
                                    i += 1
                                if past_offered:
                                    wanted.append((args[i].lower(), args[i + 1]))
                                    i += 1
                                else:
                                    offered.append((args[i].lower(), args[i + 1]))
                                    i += 1
                                i += 1
                            if past_offered:
                                valid = True
                                for item in offered:
                                    if not (item[0] in memory['cats'] or item[0] == 'bmark' or item[0] == 'wmark'):
                                        valid = False
                                for item in wanted:
                                    if not (item[0] in memory['cats'] or item[0] == 'bmark' or item[0] == 'wmark'):
                                        valid = False
                                if valid:
                                    offered_owned = True
                                    for item in offered:
                                        if not ((item[0] in memory['cats'] and memory[item[0]][int(item[1]) - 1] == str(ctx.author)) \
                                                or (item[0] == 'bmark' and memory['black marks'][str(ctx.author)] >= int(item[1]))   \
                                                or (item[0] == 'wmark' and memory['white marks'][str(ctx.author)] >= int(item[1]))):
                                            await ctx.send(str(ctx.author))
                                            await ctx.send(item[0])
                                            await ctx.send(item[1])
                                            offered_owned = False
                                    if offered_owned:
                                        wanted_owned = True
                                        for item in wanted:
                                            if not ((item[0] in memory['cats'] and memory[item[0]][int(item[1]) - 1] == recipient) \
                                                    or (item[0] == 'bmark' and memory['black marks'][recipient] >= int(item[1]))   \
                                                    or (item[0] == 'wmark' and memory['white marks'][recipient] >= int(item[1]))):
                                                wanted_owned = False
                                        if wanted_owned:
                                            # Make sure people can't offer a category unless they
                                            # request the same one or there's a free slot
                                            # in that category.
                                            all_cats_ok = True
                                            cat_ok = {}
                                            for item in offered:
                                                if item[0] in memory['cats']:
                                                    cat_ok[item[0]] = False
                                                    for req_item in wanted:
                                                        if item[0] == req_item[0]:
                                                            cat_ok[item[0]] = True
                                                    if not cat_ok[item[0]]:
                                                        for rung in range(len(memory[item[0]])):
                                                            if memory[item[0]][rung] == '' and rung <= len(memory['players']):
                                                                cat_ok[item[0]] = True
                                                else:
                                                    cat_ok[item[0]] = True
                                            for i in cat_ok:
                                                if not i:
                                                    all_cats_ok = False
                                            if all_cats_ok:
                                                # Make sure people can't request a category unless they
                                                # offer the same one or there's a free slot
                                                # in that category.
                                                cat_ok = {}
                                                for item in wanted:
                                                    if item[0] in memory['cats']:
                                                        cat_ok[item[0]] = False
                                                        for off_item in offered:
                                                            if item[0] == off_item[0]:
                                                                cat_ok[item[0]] = True
                                                        if not cat_ok[item[0]]:
                                                            for rung in range(len(memory[item[0]])):
                                                                if memory[item[0]][rung] == '' and rung <= len(memory['players']):
                                                                    cat_ok[item[0]] = True
                                                    else:
                                                        cat_ok[item[0]] = True
                                                for i in cat_ok:
                                                    if not i:
                                                        all_cats_ok = False
                                                if all_cats_ok:
                                                    # Make sure people can't offer a category the recipient
                                                    # has if they aren't requesting one in return.
                                                    cat_ok = {}
                                                    for item in offered:
                                                        if item[0] in memory['cats']:
                                                            cat_ok[item[0]] = False
                                                            if recipient in memory[item[0]]:
                                                                for req_item in wanted:
                                                                    if req_item[0] == item[0]:
                                                                        cat_ok[item[0]] = True
                                                        else:
                                                            cat_ok[item[0]] = True
                                                    for i in cat_ok:
                                                        if not i:
                                                            all_cats_ok = False
                                                    if all_cats_ok:
                                                        # Make sure people can't request a category they
                                                        # have if they aren't offering one in return.
                                                        cat_ok = {}
                                                        for item in wanted:
                                                            if item[0] in memory['cats']:
                                                                cat_ok[item[0]] = False
                                                                if str(ctx.author) in memory[item[0]]:
                                                                    for off_item in wanted:
                                                                        if off_item[0] == item[0]:
                                                                            cat_ok[item[0]] = True
                                                            else:
                                                                cat_ok[item[0]] = True
                                                        for i in cat_ok:
                                                            if not i:
                                                                all_cats_ok = False
                                                        if all_cats_ok:
                                                            # Save the pending trade and send a confirmation
                                                            # message to the recipient.

                                                            memory['pending trades'].append(str(ctx.author))
                                                            memory['pending trades'].append(recipient)

                                                            to_say = 'You have a trade offer from ' + ctx.author.display_name + '! They want to trade their '
                                                            for item in offered:
                                                                if item[0] in memory['cats']:
                                                                    to_say += item[0].capitalize() + ' ' + item[1] + ', '
                                                                elif item[0] == 'wmark' and item[1] == '1':
                                                                    to_say += 'white mark, '
                                                                elif item[0] == 'wmark':
                                                                    to_say += item[1] + ' white marks, '
                                                                elif item[0] == 'bmark' and item[1] == '1':
                                                                    to_say += 'black mark, '
                                                                elif item[0] == 'bmark':
                                                                    to_say += item[1] + ' black marks, '
                                                            to_say = to_say[:-2] + ' for your '
                                                            for item in wanted:
                                                                if item[0] in memory['cats']:
                                                                    to_say += item[0].capitalize() + ' ' + item[1] + ', '
                                                                elif item[0] == 'wmark' and item[1] == '1':
                                                                    to_say += ' white mark, '
                                                                elif item[0] == 'wmark':
                                                                    to_say += item[1] + ' white marks, '
                                                                elif item[0] == 'bmark' and item[1] == '1':
                                                                    to_say += ' black mark, '
                                                                elif item[0] == 'bmark':
                                                                    to_say += item[1] + ' black marks, '
                                                            to_say = to_say[:-2] + '! Reply with ~confirmtrade ' + ctx.author.display_name + ' to confirm, or ~denytrade ' + ctx.author.display_name + ' to deny.'

                                                            h_players = [str(ctx.author),recipient]
                                                            h_players.sort()
                                                            h_players = '&'.join(h_players)

                                                            memory['trade contents'][h_players] = (offered, wanted)
                                                            await ctx.send(to_say, recipient)
                                                            await ctx.send('Trade offer sent!', ctx.author.display_name)
                                                        else:
                                                            await ctx.send('You can\'t request a category you already have unless you offer the same one in return!')
                                                    else:
                                                        await ctx.send('You can\'t offer a category the recipient of the trade already has unless you request the same one in return!')
                                                else:
                                                    await ctx.send('You can\'t request a category unless you offer the same one or there\'s a free slot in that category!')
                                            else:
                                                await ctx.send('You can\'t offer a category unless you request the same one or there\'s a free slot in that category!')
                                        else:
                                            await ctx.send('You can only request things that the recipient of the offer has!')
                                    else:
                                        await ctx.send('You can only offer things that you have!')
                                else:
                                    await ctx.send('You can offer a category, like puissance, with the category\'s name or black or white marks with \'bmark\' or \'wmark\'')
                                    await ctx.send('Format your message like this: ~offer nick puissance 1 wmark 1 for access 1 executions 3 bmark 1')
                            else:
                                await ctx.send('Don\'t forget the \'for\'! Format your message like this: ~offer nick puissance 1 wmark 1 for access 1 executions 3 bmark 1')
                        else:
                            await ctx.send('Your recipient already has a trade pending! To avoid shenanigans, a player can only have one trade pending at a time.')
                    else:
                        await ctx.send('That recipient isn\'t in the draft! Format your message like this: ~offer nick puissance 1 wmark 1 for access 1 executions 3 bmark 1')
                else:
                    await ctx.send('Format your message like this: ~offer nick puissance 1 wmark 1 for access 1 executions 3 bmark 1')
            else:
                await ctx.send('You already have a trade pending! To avoid shenanigans, you can only have one trade pending at once.')
        else:
            await ctx.send('You\'re not in the draft!')
    else:
        await ctx.send('There\'s no draft going on.')
'''
Allows players to offer trades to other players.
'''

@b.command()
async def deny(ctx, *args):
    lower_args = [arg.lower() for arg in args]
    if memory['phase'] == 'the draft':
        if str(ctx.author) in memory['players']:
            if str(ctx.author) in memory['pending trades']:
                offerer = lower_args[0]
                if offerer.lower() in memory['players']:
                    h_players = [offerer.lower(), str(ctx.author)]
                    h_players.sort()
                    h_players = '&'.join(h_players)
                    if h_players in memory['trade contents']:
                        await ctx.send('Trade denied!')
                        await ctx.send(ctx.author.display_name + ' denied your trade.', offerer)
                        del memory['trade contents'][h_players]
                        memory['pending trades'].remove(str(ctx.author))
                        memory['pending trades'].remove(offerer.lower())
                    else:
                        await ctx.send('You don\'t have a pending trade with ' + offerer + '!')
                else:
                    await ctx.send(offerer + ' isn\'t a player in this draft!')
            else:
                await ctx.send('You don\'t have any pending trades!')
        else:
            await ctx.send('You\'re not in the draft!')
    else:
        await ctx.send('There\'s no draft going on.')
'''
Lets players deny trades offered them.
'''

@b.command()
async def roll(ctx, *, arg='1d6 1d6'):
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


# - - - - Absolute mess of code below. Mostly channel stuff. Tread at your own risk. - - - -
@b.command()
async def campaigns(ctx, *args):
    await ctx.send("Campaign list: https://docs.google.com/spreadsheets/d/1Foxb_C_zKvLuSMOB4HN5tRMpVwtPrkq6tdlokKSgEqY")

@b.command()
async def addgame(ctx, *args):
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

async def debug(ctx, message):
    await ctx.send(message)

@b.command()
async def enter(ctx, *args):
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
    gameName = ''
    gameID = None
    archiveID = None
    PDID = None
    WDID = None

    for arg in args:
        gameName = gameName + str(arg)

    namecheck = (await sheets.gamecheck(ctx.author.display_name,gameName))

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
    elif namecheck == False:
        await ctx.send("No.")
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

    for discord.Guild.TextChannel in ctx.message.guild.channels:
        if discord.Guild.TextChannel.name == gameName:
            gameID = discord.Guild.TextChannel.category

    if gameName == '':
        await ctx.send("Please write out the game you wish to unarchive after the command (i.e. ~unarchive New York)")
    elif gameID == PDID or gameID == WDID:
        await ctx.send("That game is already active.")
    elif namecheck == False:
        await ctx.send("No.")
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
    link = ''

    for arg in args:
        link = link + str(arg)

    await sheets.addlink(ctx.author.display_name,link)


# - - - - End of Disaster Area - - - -


b.loop.create_task(setup())
with fopen('secret') as s:
    token = s.read()[:-1]
b.run(token)
