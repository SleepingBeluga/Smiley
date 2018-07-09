#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from sopel.module import commands, thread, require_privmsg, require_chanmsg
import time, random

'''
My (Smiley's) Main Module

I'm friendly, and I can do Pact Dice Drafts!
'''

def setup(bot):
    import sys
    reload(sys)
    sys.setdefaultencoding("utf-8")
    
    bot.memory['phase'] = 'none'
    bot.memory['round'] = None
    bot.memory['bidding'] = False
    bot.memory['clashing'] = False

    bot.memory['players'] = []
    bot.memory['to resolve'] = []
    
    bot.memory['pending trades'] = []
    bot.memory['trade contents'] = {}

    bot.memory['proper names'] = {}
    bot.memory['bids'] = {}
    bot.memory['clash choices'] = {}
    bot.memory['black marks'] = {}
    bot.memory['white marks'] = {}
    bot.memory['limits'] = {}
    
    bot.memory['rows to show'] = 0
    
    bot.memory['clash'] = False
    
    bot.memory['quitconfirm'] = False
    
    bot.memory['cats'] = ('puissance', 'longevity', 'access', 'executions', 'research', \
                          'schools',   'priority',  'family')
    bot.memory['puissance']  = ['', '', '', '', '',    '', '', '']
    bot.memory['longevity']  = ['', '', '', '', '',    '', '', '']
    bot.memory['access']     = ['', '', '', '', '',    '', '', '']
    bot.memory['executions'] = ['', '', '', '', '',    '', '', '']
    bot.memory['research']   = ['', '', '', '', '',    '', '', '']
    bot.memory['schools']    = ['', '', '', '', '',    '', '', '']
    bot.memory['priority']   = ['', '', '', '', '',    '', '', '']
    bot.memory['family']     = ['', '', '', '', '',    '', '', '']
    
    bot.memory['clashes'] = [[],[],[]]
'''
My initializing function.
'''

def subround(bot, clash):
    if not clash:
        bot.say('It\'s the beginning of round ' + str(bot.memory['round']) + '! (Submit your bids by PMing me with e.x. ~bid Executions 2)')
    else:
        to_say = 'We need to finish resolving the clashes! '
        for player in bot.memory['to resolve']:
            to_say = to_say + bot.memory['proper names'][player] + ', '
        if len(bot.memory['to resolve']) > 1:
            to_say = to_say + 'please submit your bids by PMing me with e.x. ~bid Executions 2'
        else:
            to_say = to_say + 'please submit your bid by PMing me with e.x. ~bid Executions 2'
        bot.say(to_say)
        bot.say('Remember, bids are restricted by the results of the clashes.')
    get_bids(bot)
    if bot.memory['phase'] == 'none':
        return
    calc_clashes(bot)
    while bot.memory['clash']:
        do_clash(bot, False)
        if bot.memory['phase'] == 'none':
            return
    show_cats(bot)
    if len(bot.memory['to resolve']) > 0:
        subround(bot, True)
    elif bot.memory['round'] == 8:
        bot.say('That\'s the end of the draft! Thanks for playing!')
        setup(bot)
    else:
        bot.memory['to resolve'] = bot.memory['players']
        bot.memory['round'] += 1
        subround(bot, False)
'''
My main loop. Executes subrounds and resolves clashes.
'''

def show_cats(bot):
    for cat in bot.memory['cats']:
        to_say = cat.capitalize()
        for i in range(11 - len(cat)):
            to_say += ' '
        to_say += '| '
        for i in range(bot.memory['rows to show']):
            if bot.memory[cat][i] == '':
                for j in range(14):
                    to_say += ' '
            else:
                to_say += ' ' + bot.memory['proper names'][bot.memory[cat][i]][:-1] + '​' + bot.memory['proper names'][bot.memory[cat][i]][-1]
                for j in range(13 - len(bot.memory[cat][i])):
                    to_say += ' '
            to_say += '|'
        bot.say(to_say)
        
    for player in bot.memory['players']:
        to_say = bot.memory['proper names'][player][:-1] + '​' + bot.memory['proper names'][player][-1] + ': '
        for i in range(bot.memory['white marks'][player]):
            to_say += '☆'
        to_say += ' | '
        for i in range(bot.memory['black marks'][player]):
            to_say += '★'
        bot.say(to_say)
'''
Displays the categories so you can see who has what.
'''

@thread(True)
def get_bids(bot):
    for player in bot.memory['players']:
        if player not in bot.memory['to resolve']:
            bot.memory['bids'][player] = 0
        else:
            bot.memory['bids'][player] = None
    bot.memory['bidding'] = True
    start = time.time()
    while None in bot.memory['bids'].values():
        if (time.time() - start) > 240:
            to_say = 'Still waiting for '
            for player in bot.memory['to resolve']:
                if bot.memory['bids'][player] == None:
                    to_say = to_say + bot.memory['proper names'][player] + ', '
            if to_say[-2:] == ', ':
                to_say = to_say[:-2]
            bot.say(to_say)
            start = time.time()
        if bot.memory['phase'] == 'none':
            return
    bot.memory['bidding'] = False
    for player in bot.memory['players']:
        bot.memory['limits'][player] = 0
'''
Tells players to submit bids, and waits until all bids are done.
'''

def calc_clashes(bot):
    bid = None
    bid_player = None
    clashes_so_far = 0
    found_clash = False
    for player in bot.memory['to resolve']:
        if not (player in bot.memory['clashes'][0] or \
                player in bot.memory['clashes'][1] or \
                player in bot.memory['clashes'][2]):
            bid = bot.memory['bids'][player]
            for player2 in bot.memory['to resolve']:
                if not (player2 in bot.memory['clashes'][0] or \
                        player2 in bot.memory['clashes'][1] or \
                        player2 in bot.memory['clashes'][2]):
                    if bid == bot.memory['bids'][player2] and not player == player2:
                        bot.memory['clashes'][clashes_so_far].append(player2)
                        if not player in bot.memory['clashes'][clashes_so_far]:
                            bot.memory['clashes'][clashes_so_far].append(player)
                            found_clash = True
        if found_clash:
            clashes_so_far += 1
            found_clash = False
    if clashes_so_far == 0:
        bot.say('There are no clashes.')
    elif clashes_so_far == 1:
        bot.say('There\'s a clash!')
    else:
        bot.say('There are ' + str(clashes_so_far) + ' clashes!')
    
    for player in bot.memory['to resolve']:
        if not (player in bot.memory['clashes'][0] or \
                player in bot.memory['clashes'][1] or \
                player in bot.memory['clashes'][2]):
            bot.memory[bot.memory['bids'][player][0]][bot.memory['bids'][player][1] - 1] = player
    
    if clashes_so_far > 0:
        bot.memory['clash'] = True
    bot.memory['to resolve'] = []
'''
Figures out if there are clashes and who's in each.
'''

def do_clash(bot, continued):
    if not continued:
        to_say = 'Clash: '
        for player in bot.memory['clashes'][0]:
            to_say = to_say + bot.memory['proper names'][player] + ', '
        to_say = to_say[:-2] + ' for ' + bot.memory['bids'][bot.memory['clashes'][0][0]][0].capitalize() \
                             + ' ' + str(bot.memory['bids'][bot.memory['clashes'][0][0]][1]) + '! ' \
                             + 'Please PM me with either ~stay or ~concede'
        bot.say(to_say)
    
    number_of_clashers = len(bot.memory['clashes'][0])
    
    if number_of_clashers == 2:
        player0 = bot.memory['clashes'][0][0]
        player1 = bot.memory['clashes'][0][1]
        get_clash_choices(bot)
        if bot.memory['clash choices'][player0] == 'stay':
            if bot.memory['clash choices'][player1] == 'stay':
                bot.say('They both stayed!')
                
                # Anti luck manipulation barriers around the random parts
                
                # MUSA DERELINQUAS ME SERMONIBUS          🐀
                coin0 = random.choice(('heads','tails')) #🐀
                coin1 = random.choice(('heads','tails')) #🐀
                # Thal, stay away.                        🐀
                
                to_say = 'Flipping a coin for ' + bot.memory['proper names'][player0] + ': ' + coin0.capitalize() + '! '
                if coin0 == 'heads':
                    to_say = to_say + bot.memory['proper names'][player0] + ' loses the spot and will have to rebid at least two rungs lower.'
                    bot.memory['to resolve'].append(player0)
                    bot.memory['limits'][player0] = bot.memory['bids'][bot.memory['clashes'][0][0]][1] + 2
                    if bot.memory['bids'][bot.memory['clashes'][0][0]][1] + 2 > bot.memory['rows to show']:
                        bot.memory['rows to show'] = bot.memory['bids'][bot.memory['clashes'][0][0]][1] + 2

                else:
                    to_say = to_say + bot.memory['proper names'][player0] + ' gets a black mark.'
                    bot.memory['black marks'][player0] += 1
                bot.say(to_say)    
                to_say = 'Flipping a coin for ' + bot.memory['proper names'][player1] + ': ' + coin1.capitalize() + '! '
                if coin1 == 'heads':
                    to_say = to_say + bot.memory['proper names'][player1] + ' loses the spot and will have to rebid at least two rungs lower.'
                    bot.memory['to resolve'].append(player1)
                    bot.memory['limits'][player1] = bot.memory['bids'][bot.memory['clashes'][0][0]][1] + 2
                    if bot.memory['bids'][bot.memory['clashes'][0][0]][1] + 2 > bot.memory['rows to show']:
                        bot.memory['rows to show'] = bot.memory['bids'][bot.memory['clashes'][0][0]][1] + 2

                else:
                    to_say = to_say + bot.memory['proper names'][player1] + ' gets a black mark.'
                    bot.memory['black marks'][player1] += 1
                bot.say(to_say)
                
                if coin0 == 'tails' and coin1 == 'tails':
                    bot.say('The clash continues! Please choose either ~stay or ~concede again.')
                    do_clash(bot, True)
                    return
                elif coin0 == 'tails':
                    bot.memory[bot.memory['bids'][bot.memory['clashes'][0][0]][0]][bot.memory['bids'][bot.memory['clashes'][0][0]][1] - 1] \
                        = player0
                elif coin1 == 'tails':
                    bot.memory[bot.memory['bids'][bot.memory['clashes'][0][0]][0]][bot.memory['bids'][bot.memory['clashes'][0][0]][1] - 1] \
                        = player1
                        
            if bot.memory['clash choices'][player1] == 'concede':
                # FORTUNA RERUM NATURALIUM               🐀
                coin = random.choice(('heads','tails')) #🐀
                # Thal, get out                          🐀
                to_say = bot.memory['proper names'][player0] + ' stayed. ' + bot.memory['proper names'][player1] + ' conceded. Flipping a coin: ' + coin + '! '
                if coin == 'heads':
                    to_say += bot.memory['proper names'][player1] + ' gets a white mark and chooses a category at a lower rung. ' + \
                              bot.memory['proper names'][player0] + ' gets the spot.'
                    bot.memory['white marks'][player1] += 1
                else:
                    to_say += bot.memory['proper names'][player1] + ' loses the spot and will have to choose a category at a lower rung. ' + \
                              bot.memory['proper names'][player0] + ' gets the spot and a black mark.'
                    bot.memory['black marks'][player0] += 1
                bot.say(to_say)
                bot.memory['limits'][player1] = bot.memory['bids'][bot.memory['clashes'][0][0]][1] + 1
                if bot.memory['bids'][bot.memory['clashes'][0][0]][1] + 1 > bot.memory['rows to show']:
                    bot.memory['rows to show'] = bot.memory['bids'][bot.memory['clashes'][0][0]][1] + 1
                bot.memory['to resolve'].append(player1)
                bot.memory[bot.memory['bids'][bot.memory['clashes'][0][0]][0]][bot.memory['bids'][bot.memory['clashes'][0][0]][1] - 1] \
                        = player0
                
        elif bot.memory['clash choices'][player0] == 'concede':
            if bot.memory['clash choices'][player1] == 'stay':
                # EX TALIS MAGA                                🐀
                coin = random.choice(('heads','tails'))       #🐀
                # I'm serious, Thal. This code is witch-proof  🐀
                to_say = player1 + ' stayed. ' + bot.memory['proper names'][player0] + ' conceded. Flipping a coin: ' + coin + '! '
                if coin == 'heads':
                    to_say += bot.memory['proper names'][player0] + ' gets a white mark and chooses a category at a lower rung. ' + \
                              bot.memory['proper names'][player1] + ' gets the spot.'
                    bot.memory['white marks'][player0] += 1
                else:
                    to_say += bot.memory['proper names'][player0] + ' loses the spot and will have to choose a category at a lower rung. ' + \
                              bot.memory['proper names'][player1] + ' gets the spot and a black mark.'
                    bot.memory['black marks'][player1] += 1
                bot.say(to_say)
                bot.memory['limits'][player0] = bot.memory['bids'][bot.memory['clashes'][0][0]][1] + 1
                if bot.memory['bids'][bot.memory['clashes'][0][0]][1] + 1 > bot.memory['rows to show']:
                    bot.memory['rows to show'] = bot.memory['bids'][bot.memory['clashes'][0][0]][1] + 1
                bot.memory['to resolve'].append(player0)
                bot.memory[bot.memory['bids'][bot.memory['clashes'][0][0]][0]][bot.memory['bids'][bot.memory['clashes'][0][0]][1] - 1] \
                        = player1
                        
            elif bot.memory['clash choices'][player1] == 'concede':
                bot.say('They both conceded, and will need to rebid for a lower rung.')
                bot.memory['limits'][player0] = bot.memory['bids'][bot.memory['clashes'][0][0]][1] + 1
                bot.memory['limits'][player1] = bot.memory['bids'][bot.memory['clashes'][0][0]][1] + 1
                if bot.memory['bids'][bot.memory['clashes'][0][0]][1] + 1 > bot.memory['rows to show']:
                    bot.memory['rows to show'] = bot.memory['bids'][bot.memory['clashes'][0][0]][1] + 1
                bot.memory['to resolve'].append(player0)
                bot.memory['to resolve'].append(player1)

    else:
        to_mark = []
        clashers = []
        remaining = []
        get_clash_choices(bot)
        for i in range(number_of_clashers):
            clashers.append(bot.memory['clashes'][0][i])
        for player in clashers:
            if bot.memory['clash choices'][player] == 'concede':
                bot.memory['to resolve'].append(player)
                bot.memory['limits'][player] = bot.memory['bids'][bot.memory['clashes'][0][0]][1] + 1
                if bot.memory['bids'][bot.memory['clashes'][0][0]][1] + 1 > bot.memory['rows to show']:
                    bot.memory['rows to show'] = bot.memory['bids'][bot.memory['clashes'][0][0]][1] + 1
                number_of_clashers -= 1
                bot.memory['clashes'][0].remove(player)
                bot.say(bot.memory['proper names'][player] + ' conceded, and will have to rebid for a lower rung.')
            elif bot.memory['clash choices'][player] == 'stay':
                # MAGICAE NON INTERMIXTI                                 🐀
                coin = random.choice(('heads','tails'))                 #🐀
                # Let's see you get around that foolproof magic barrier  🐀
                to_say = bot.memory['proper names'][player] + ' stayed. Flipping a coin: ' + coin + '! '
                if coin == 'heads':
                    to_say += bot.memory['proper names'][player] + ' loses the spot, and will have to choose a rung at least two lower.' 
                    bot.memory['limits'][player] = bot.memory['bids'][bot.memory['clashes'][0][0]][1] + 2
                    if bot.memory['bids'][bot.memory['clashes'][0][0]][1] + 2 > bot.memory['rows to show']:
                        bot.memory['rows to show'] = bot.memory['bids'][bot.memory['clashes'][0][0]][1] + 2
                    bot.memory['to resolve'].append(player)
                    number_of_clashers -= 1
                    bot.memory['clashes'][0].remove(player)
                elif coin == 'tails':
                    to_say += bot.memory['proper names'][player] + ' remains.'
                    to_mark.append(player)
                    remaining.append(player)
                bot.say(to_say)
        if number_of_clashers <= 2 and number_of_clashers > 0:
            to_say = 'Since there are 2 or less clashers remaining, black marks will be doled out to '
            for player in to_mark:
                to_say += bot.memory['proper names'][player] + ', '
                bot.memory['black marks'][player] += 1
            to_say = to_say[:-2] + '!'
            bot.say(to_say)
        if number_of_clashers > 1:
            bot.say('There\'s more than one clasher remaining! Remaining clashers, PM me with ~stay or ~concede again!')
            do_clash(bot, True)
            return
        elif number_of_clashers == 1:
            player = remaining[0]
            bot.say('There\'s only ' + bot.memory['proper names'][player] + ' left! They get the spot!')
            bot.memory[bot.memory['bids'][bot.memory['clashes'][0][0]][0]][bot.memory['bids'][bot.memory['clashes'][0][0]][1] - 1] \
                = player
        else:
            bot.say('No one gets the spot this round!')
    
    bot.memory['clashes'][0] = bot.memory['clashes'][1]
    bot.memory['clashes'][1] = bot.memory['clashes'][2]
    bot.memory['clashes'][2] = []
    
    if bot.memory['clashes'][0] == []:
        bot.memory['clash'] = False
'''
Performs clashes and adds players who need to rebid to 'to resolve'.
'''

@thread(True)
def get_clash_choices(bot):
    for player in bot.memory['players']:
        if player not in bot.memory['clashes'][0]:
            bot.memory['clash choices'][player] = ""
        else:
            bot.memory['clash choices'][player] = None
    bot.memory['clashing'] = True
    start = time.time()
    while None in bot.memory['clash choices'].values():
        if (time.time() - start) > 240:
            to_say = 'Still waiting for '
            for player in bot.memory['clashes'][0]:
                if bot.memory['clash choices'][player] == None:
                    to_say = to_say + bot.memory['proper names'][player] + ', '
            if to_say[-2:] == ', ':
                to_say = to_say[:-2]
            bot.say(to_say)
            start = time.time()
        if bot.memory['phase'] == 'none':
            return
    bot.memory['clashing'] = False
'''
Tells players to submit clash choices, and waits until all clash choices are done.
'''

def all_resolved(bot):
    if any(x == '' for x in bot.memory['puissance'][:len(bot.memory['players'])]):
        return False
    if any(x  == ''  for x in bot.memory['longevity'][:len(bot.memory['players'])]):
        return False
    if any(x  == ''  for x in bot.memory['access'][:len(bot.memory['players'])]):
        return False
    if any(x  == ''  for x in bot.memory['executions'][:len(bot.memory['players'])]):
        return False
    if any(x  == ''  for x in bot.memory['research'][:len(bot.memory['players'])]):
        return False
    if any(x  == ''  for x in bot.memory['schools'][:len(bot.memory['players'])]):
        return False
    if any(x  == ''  for x in bot.memory['priority'][:len(bot.memory['players'])]):
        return False
    if any(x  == ''  for x in bot.memory['family'][:len(bot.memory['players'])]):
        return False
    return True
'''
Not used because it doesn't work yet. Ideally should calculate when future rounds can be autofilled, but with insigs/abysmal that's not an easy check. 
'''

@commands('hi')
def hi(bot, trigger):
    bot.reply('Hi!')
'''
The hi command. I'll greet the user.
'''

@require_chanmsg
@commands('open')
def open(bot, trigger):
    if bot.memory['phase'] == 'none':
        bot.memory['phase'] = 'setup'
        bot.say('Opening a draft! (Use ~join to join, and then ~start to begin)')
    else:
        bot.say('A draft is already ongoing! Finish it before trying again.')
'''
Begins a draft so people can join.
'''

@require_chanmsg
@commands('join')
def join(bot, trigger):
    if bot.memory['phase'] == 'setup':
        if not trigger.nick.lower() in bot.memory['players']:
            bot.memory['players'].append(trigger.nick.lower())
            bot.memory['proper names'][trigger.nick.lower()] = trigger.nick
            bot.say(trigger.nick + ' has joined!')
        else:
            bot.say('You\'ve already joined!')
    elif bot.memory['phase'] == 'none':
        bot.say('You can\'t join because there\'s no draft going on! (Use ~open to start one)')
    else:
        bot.say('You can\'t join right now, we\'re in ' + bot.memory['phase'] + '!')
'''
Lets you join a draft.
'''

@require_chanmsg
@commands('start')
def start(bot, trigger):
    if bot.memory['phase'] == 'setup':
        if len(bot.memory['players']) >= 4 and len(bot.memory['players']) <= 6:
            bot.say('Starting the draft! Consider using a monospaced font for the duration of the draft to make my tables look better.')
            bot.memory['phase'] = 'the draft'
            bot.memory['round'] = 1
            bot.memory['to resolve'] = bot.memory['players']
            for player in bot.memory['players']:
                bot.memory['black marks'][player] = 0
                bot.memory['white marks'][player] = 0
            for player in bot.memory['players']:
                bot.memory['limits'][player] = 0
            bot.memory['rows to show'] = len(bot.memory['players'])
            subround(bot, False)
        else:
            bot.say('You must have between 4 and 6 players to start.')
    elif bot.memory['phase'] == 'none':
        bot.say('You can\'t start the draft yet, you need players first! (Use ~open to let players join)')
    else:
        bot.say('You can\'t start a draft right now, we\'re in ' + bot.memory['phase'] + '!')
'''
Starts the draft after players join.
'''

@thread(True)
@require_chanmsg
@commands('reset')
def reset(bot, trigger):
    if not bot.memory['quitconfirm']:
        bot.say('Are you sure? This will reset any drafts in progress. (Use ~reset again to confirm)')
        bot.memory['quitconfirm'] = True
        time.sleep(60)
        bot.memory['quitconfirm'] = False
    else:
        bot.say('OK, I\'ve reset.')
        setup(bot)
'''
Resets me, stopping any drafts in progress.
'''

@require_privmsg
@commands('bid')
def bid(bot, trigger):
    if bot.memory['bidding']:
        if trigger.nick.lower() in bot.memory['to resolve']:
            if len(trigger.group(2).lower().split()) == 2:
                cat = trigger.group(2).lower().split()[0]
                rung = int(trigger.group(2).lower().split()[1])
                if cat in bot.memory['cats']:
                    if not trigger.nick.lower() in bot.memory[cat]:
                        if (rung <= len(bot.memory['players']) and rung >= bot.memory['limits'][trigger.nick.lower()]) or rung == bot.memory['limits'][trigger.nick.lower()]:
                            if bot.memory[cat][rung - 1] == '':
                                bot.say('Got it!')
                                bot.memory['bids'][trigger.nick.lower()] = (cat, rung)
                            else:
                                bot.say('That one\'s taken, please choose another.')
                        else:
                            to_say = 'Please choose a rung between '
                            if bot.memory['limits'][trigger.nick.lower()] == 0:
                                to_say += '1'
                            else:
                                to_say += str(bot.memory['limits'][trigger.nick.lower()])
                            to_say += ' and '
                            if bot.memory['limits'][trigger.nick.lower()] <= len(bot.memory['players']):
                                to_say += str(len(bot.memory['players']))
                            else:
                                to_say += str(bot.memory['limits'][trigger.nick.lower()])
                            to_say += '. Format your message like this: ~bid puissance 4'
                            bot.say(to_say)
                    else:
                        bot.say('You already have a rung in that category! Pick another, please.')
                else:
                    bot.say ('I don\'t know that category. Format your message like this: ~bid puissance 4')
            else:
                bot.say('Format your message like this: ~bid puissance 4')
        else:
            bot.say('I don\'t need a bid from you right now.')
    else:
        bot.say('Now\'s not the time for bidding.')
'''
Allows players to bid on draft slots.
'''

@require_privmsg
@commands('stay')
def stay(bot, trigger):
    if bot.memory['clashing']:
        if trigger.nick.lower() in bot.memory['clashes'][0]:
            bot.say('OK!')
            bot.memory['clash choices'][trigger.nick.lower()] = 'stay'
        else:
            bot.say('I don\'t need a choice from you right now.')
    else:
        bot.say('Now\'s not the time to submit a clash choice.')
'''
The command to refuse to budge during a clash.
'''

@require_privmsg
@commands('concede')
def concede(bot, trigger):
    if bot.memory['clashing']:
        if trigger.nick.lower() in bot.memory['clashes'][0]:
            bot.say('OK!')
            bot.memory['clash choices'][trigger.nick.lower()] = 'concede'
        else:
            bot.say('I don\'t need a choice from you right now.')
    else:
        bot.say('Now\'s not the time to submit a clash choice.')
'''
The command to cede during a clash.
'''

@require_privmsg
@commands('table')
def table(bot, trigger):
    if bot.memory['phase'] == 'the draft':
        show_cats(bot)
    else:
        bot.say('There\'s no draft going on.')
'''
Shows the current draft progress
'''

@commands('help')
def help(bot, trigger):
    bot.say('Use ~open to open up a draft for players to join, ~join to join an opened draft, ~start to start, and ~table in PM to see how the draft is going so far. I\'ll give you more instructions during the draft!')
'''
Gives basic help.
TODO: expand to give help on commands.
'''

@require_privmsg
@commands('offer')
def offer(bot, trigger):
    if bot.memory['phase'] == 'the draft':
        if trigger.nick.lower() in bot.memory['players']:
            if not trigger.nick.lower() in bot.memory['pending trades']:
                args = trigger.group(2).lower().split()
                if len(args) >= 6:
                    recipient = args[0].lower()
                    if recipient in bot.memory['players']:
                        if not recipient in bot.memory['pending trades']:
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
                                    if not (item[0] in bot.memory['cats'] or item[0] == 'bmark' or item[0] == 'wmark'):
                                        valid = False
                                for item in wanted:
                                    if not (item[0] in bot.memory['cats'] or item[0] == 'bmark' or item[0] == 'wmark'):
                                        valid = False
                                if valid:
                                    offered_owned = True
                                    for item in offered:
                                        if not ((item[0] in bot.memory['cats'] and bot.memory[item[0]][int(item[1]) - 1] == trigger.nick.lower()) \
                                                or (item[0] == 'bmark' and bot.memory['black marks'][trigger.nick.lower()] >= int(item[1]))   \
                                                or (item[0] == 'wmark' and bot.memory['white marks'][trigger.nick.lower()] >= int(item[1]))):
                                            bot.say(trigger.nick.lower())
                                            bot.say(item[0])
                                            bot.say(item[1])
                                            offered_owned = False
                                    if offered_owned:
                                        wanted_owned = True
                                        for item in wanted:
                                            if not ((item[0] in bot.memory['cats'] and bot.memory[item[0]][int(item[1]) - 1] == recipient) \
                                                    or (item[0] == 'bmark' and bot.memory['black marks'][recipient] >= int(item[1]))   \
                                                    or (item[0] == 'wmark' and bot.memory['white marks'][recipient] >= int(item[1]))):
                                                wanted_owned = False
                                        if wanted_owned:
                                            # Make sure people can't offer a category unless they
                                            # request the same one or there's a free slot
                                            # in that category.
                                            all_cats_ok = True
                                            cat_ok = {}
                                            for item in offered:
                                                if item[0] in bot.memory['cats']:
                                                    cat_ok[item[0]] = False
                                                    for req_item in wanted:
                                                        if item[0] == req_item[0]:
                                                            cat_ok[item[0]] = True
                                                    if not cat_ok[item[0]]:
                                                        for rung in range(len(bot.memory[item[0]])):
                                                            if bot.memory[item[0]][rung] == '' and rung <= len(bot.memory['players']):
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
                                                    if item[0] in bot.memory['cats']:
                                                        cat_ok[item[0]] = False
                                                        for off_item in offered:
                                                            if item[0] == off_item[0]:
                                                                cat_ok[item[0]] = True
                                                        if not cat_ok[item[0]]:
                                                            for rung in range(len(bot.memory[item[0]])):
                                                                if bot.memory[item[0]][rung] == '' and rung <= len(bot.memory['players']):
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
                                                        if item[0] in bot.memory['cats']:
                                                            cat_ok[item[0]] = False
                                                            if recipient in bot.memory[item[0]]:
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
                                                            if item[0] in bot.memory['cats']:
                                                                cat_ok[item[0]] = False
                                                                if trigger.nick.lower() in bot.memory[item[0]]:
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
                                                            
                                                            bot.memory['pending trades'].append(trigger.nick.lower())
                                                            bot.memory['pending trades'].append(recipient)
                                                            
                                                            to_say = 'You have a trade offer from ' + trigger.nick + '! They want to trade their '
                                                            for item in offered:
                                                                if item[0] in bot.memory['cats']:
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
                                                                if item[0] in bot.memory['cats']:
                                                                    to_say += item[0].capitalize() + ' ' + item[1] + ', '
                                                                elif item[0] == 'wmark' and item[1] == '1':
                                                                    to_say += ' white mark, '
                                                                elif item[0] == 'wmark':
                                                                    to_say += item[1] + ' white marks, '
                                                                elif item[0] == 'bmark' and item[1] == '1':
                                                                    to_say += ' black mark, '
                                                                elif item[0] == 'bmark':
                                                                    to_say += item[1] + ' black marks, '
                                                            to_say = to_say[:-2] + '! Reply with ~confirmtrade ' + trigger.nick + ' to confirm, or ~denytrade ' + trigger.nick + ' to deny.'
                                                            
                                                            both_players = [trigger.nick.lower(),recipient]
                                                            both_players.sort()
                                                            both_players = '&'.join(both_players)
                                                            
                                                            bot.memory['trade contents'][both_players] = (offered, wanted)
                                                            bot.say(to_say, recipient)
                                                            bot.say('Trade offer sent!', trigger.nick)
                                                        else:
                                                            bot.say('You can\'t request a category you already have unless you offer the same one in return!')
                                                    else:
                                                        bot.say('You can\'t offer a category the recipient of the trade already has unless you request the same one in return!')
                                                else:
                                                    bot.say('You can\'t request a category unless you offer the same one or there\'s a free slot in that category!')
                                            else:
                                                bot.say('You can\'t offer a category unless you request the same one or there\'s a free slot in that category!')
                                        else:
                                            bot.say('You can only request things that the recipient of the offer has!')
                                    else:
                                        bot.say('You can only offer things that you have!')
                                else:
                                    bot.say('You can offer a category, like puissance, with the category\'s name or black or white marks with \'bmark\' or \'wmark\'')
                                    bot.say('Format your message like this: ~offer nick puissance 1 wmark 1 for access 1 executions 3 bmark 1')
                            else:
                                bot.say('Don\'t forget the \'for\'! Format your message like this: ~offer nick puissance 1 wmark 1 for access 1 executions 3 bmark 1')
                        else:
                            bot.say('Your recipient already has a trade pending! To avoid shenanigans, a player can only have one trade pending at a time.')
                    else:
                        bot.say('That recipient isn\'t in the draft! Format your message like this: ~offer nick puissance 1 wmark 1 for access 1 executions 3 bmark 1')
                else:
                    bot.say('Format your message like this: ~offer nick puissance 1 wmark 1 for access 1 executions 3 bmark 1')
            else:
                bot.say('You already have a trade pending! To avoid shenanigans, you can only have one trade pending at once.')
        else:
            bot.say('You\'re not in the draft!')
    else:
        bot.say('There\'s no draft going on.')
'''
Allows players to offer trades to other players.
'''

@require_privmsg
@commands('tradedeny')
def tradedeny(bot, trigger):
    if bot.memory['phase'] == 'the draft':
        if trigger.nick.lower() in bot.memory['players']:
            if trigger.nick.lower() in bot.memory['pending trades']:
                offerer = trigger.group(2)
                if offerer.lower() in bot.memory['players']:
                    both_players = [offerer.lower(), trigger.nick.lower()]
                    both_players.sort()
                    both_players = '&'.join(both_players)
                    if both_players in bot.memory['trade contents']:
                        bot.say('Trade denied!')
                        bot.say(trigger.nick + ' denied your trade.', offerer)
                        del bot.memory['trade contents'][both_players]
                        bot.memory['pending trades'].remove(trigger.nick.lower())
                        bot.memory['pending trades'].remove(offerer.lower())
                    else:
                        bot.say('You don\'t have a pending trade with ' + offerer + '!')
                else:
                    bot.say(offerer + ' isn\'t a player in this draft!')
            else:
                bot.say('You don\'t have any pending trades!')
        else:
            bot.say('You\'re not in the draft!')
    else:
        bot.say('There\'s no draft going on.')
'''
Lets players deny trades offered them.
'''
