from sopel.module import commands, thread, require_privmsg, require_chanmsg
import time, random

'''
My (Smiley's) Main Module

I'm friendly, but that's about it!
'''

def setup(bot):
    bot.memory['phase'] = 'none'
    bot.memory['players'] = []
    bot.memory['to resolve'] = []
    bot.memory['bids'] = {}
    bot.memory['clash choices'] = {}
    bot.memory['black marks'] = {}
    bot.memory['white marks'] = {}
    bot.memory['limits'] = {}
    bot.memory['rows to show'] = 0
    bot.memory['round'] = None
    
    bot.memory['bidding'] = False
    bot.memory['clashing'] = False
    
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
            to_say = to_say + player + ', '
        to_say = to_say + 'please submit your bids by PMing me with e.x. ~bid Executions 2'
        bot.say(to_say)
        bot.say('Remember your bids are restricted by the results of the clashes.')
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
                to_say += ' ' + bot.memory[cat][i][:-1] + '​' + bot.memory[cat][i][-1]
                for j in range(13 - len(bot.memory[cat][i])):
                    to_say += ' '
            to_say += '|'
        bot.say(to_say)
        
    for player in bot.memory['players']:
        to_say = player[:-1] + '​' + player[-1] + ': '
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
                    to_say = to_say + player + ', '
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
            to_say = to_say + player + ', '
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
                coin0 = random.choice(('heads','tails'))
                coin1 = random.choice(('heads','tails'))
                # Thal, stay away.
                
                to_say = 'Flipping a coin for ' + player0 + ': ' + coin0.capitalize() + '! '
                if coin0 == 'heads':
                    to_say = to_say + player0 + ' loses the spot and will have to rebid at least two rungs lower.'
                    bot.memory['to resolve'].append(player0)
                    bot.memory['limits'][player0] = bot.memory['bids'][bot.memory['clashes'][0][0]][1] + 2
                    if bot.memory['bids'][bot.memory['clashes'][0][0]][1] + 2 > bot.memory['rows to show']:
                        bot.memory['rows to show'] = bot.memory['bids'][bot.memory['clashes'][0][0]][1] + 2

                else:
                    to_say = to_say + player0 + ' gets a black mark.'
                    bot.memory['black marks'][player0] += 1
                bot.say(to_say)    
                to_say = 'Flipping a coin for ' + player1 + ': ' + coin1.capitalize() + '! '
                if coin1 == 'heads':
                    to_say = to_say + player1 + ' loses the spot and will have to rebid at least two rungs lower.'
                    bot.memory['to resolve'].append(player1)
                    bot.memory['limits'][player1] = bot.memory['bids'][bot.memory['clashes'][0][0]][1] + 2
                    if bot.memory['bids'][bot.memory['clashes'][0][0]][1] + 2 > bot.memory['rows to show']:
                        bot.memory['rows to show'] = bot.memory['bids'][bot.memory['clashes'][0][0]][1] + 2

                else:
                    to_say = to_say + player1 + ' gets a black mark.'
                    bot.memory['black marks'][player1] += 1
                bot.say(to_say)
                
                if coin0 == 'tails' and coin1 == 'tails':
                    bot.say('The clash continues! Please choose either ~stay or ~concede again.')
                    do_clash(bot, True)
                elif coin0 == 'tails':
                    bot.memory[bot.memory['bids'][bot.memory['clashes'][0][0]][0]][bot.memory['bids'][bot.memory['clashes'][0][0]][1] - 1] \
                        = player0
                elif coin1 == 'tails':
                    bot.memory[bot.memory['bids'][bot.memory['clashes'][0][0]][0]][bot.memory['bids'][bot.memory['clashes'][0][0]][1] - 1] \
                        = player1
                        
            if bot.memory['clash choices'][player1] == 'concede':
                coin = random.choice(('heads','tails'))
                # Thal, get out
                to_say = player0 + ' stayed. ' + player1 + ' conceded. Flipping a coin: ' + coin + '! '
                if coin == 'heads':
                    to_say += player1 + ' gets a white mark and chooses a category at a lower rung. ' + \
                              player0 + ' gets the spot.'
                    bot.memory['white marks'][player1] += 1
                else:
                    to_say += player1 + ' loses the spot and will have to choose a category at a lower rung. ' + \
                              player0 + ' gets the spot and a black mark.'
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
                coin = random.choice(('heads','tails'))
                # I'm serious, Thal. This code is witch-proof
                to_say = player1 + ' stayed. ' + player0 + ' conceded. Flipping a coin: ' + coin + '! '
                if coin == 'heads':
                    to_say += player0 + ' gets a white mark and chooses a category at a lower rung. ' + \
                              player1 + ' gets the spot.'
                    bot.memory['white marks'][player0] += 1
                else:
                    to_say += player0 + ' loses the spot and will have to choose a category at a lower rung. ' + \
                              player1 + ' gets the spot and a black mark.'
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
                bot.say(player + ' conceded, and will have to rebid for a lower rung.')
            elif bot.memory['clash choices'][player] == 'stay':
                coin = random.choice(('heads','tails'))
                # HECATE INTERFERUM NIHILUS
                to_say = player + ' stayed. Flipping a coin: ' + coin + '! '
                if coin == 'heads':
                    to_say += player + ' loses the spot, and will have to choose a rung at least two lower.' 
                    bot.memory['limits'][player] = bot.memory['bids'][bot.memory['clashes'][0][0]][1] + 2
                    if bot.memory['bids'][bot.memory['clashes'][0][0]][1] + 2 > bot.memory['rows to show']:
                        bot.memory['rows to show'] = bot.memory['bids'][bot.memory['clashes'][0][0]][1] + 2
                    bot.memory['to resolve'].append(player)
                    number_of_clashers -= 1
                    bot.memory['clashes'][0].remove(player)
                elif coin == 'tails':
                    to_say += player + ' remains.'
                    to_mark.append(player)
                    remaining.append(player)
                bot.say(to_say)
        if number_of_clashers <= 2 and number_of_clashers > 0:
            to_say = 'Since there are 2 or less clashers remaining, black marks will be doled out to '
            for player in to_mark:
                to_say += player + ', '
                bot.memory['black marks'][player] += 1
            to_say = to_say[:-2] + '!'
            bot.say(to_say)
        if number_of_clashers > 1:
            bot.say('There\'s more than one clasher remaining! PM me with ~stay or ~concede again!')
            do_clash(bot, True)
        elif number_of_clashers == 1:
            player = remaining[0]
            bot.say('There\'s only ' + player + ' left! They get the spot!')
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
                    to_say = to_say + player + ', '
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

@require_chanmsg
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
        if not trigger.nick in bot.memory['players']:
            bot.memory['players'].append(trigger.nick)
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
            bot.say('Starting the draft!')
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
        if trigger.nick in bot.memory['to resolve']
            if len(trigger.group(2).lower().split()) == 2:
                cat = trigger.group(2).lower().split()[0]
                rung = int(trigger.group(2).lower().split()[1])
                if cat in bot.memory['cats']:
                    if not trigger.nick in bot.memory[cat]:
                        if (rung <= len(bot.memory['players']) and rung >= bot.memory['limits'][trigger.nick]) or rung == bot.memory['limits'][trigger.nick]:
                            if bot.memory[cat][rung - 1] == '':
                                bot.say('Got it!')
                                bot.memory['bids'][trigger.nick] = (cat, rung)
                            else:
                                bot.say('That one\'s taken, please choose another.')
                        else:
                            to_say = 'Please choose a rung between '
                            if bot.memory['limits'][trigger.nick] == 0:
                                to_say += '1'
                            else:
                                to_say += str(bot.memory['limits'][trigger.nick])
                            to_say += ' and '
                            if bot.memory['limits'][trigger.nick] <= len(bot.memory['players']):
                                to_say += str(len(bot.memory['players']))
                            else:
                                to_say += str(bot.memory['limits'][trigger.nick])
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
        if trigger.nick in bot.memory['clashes'][0]:
            bot.say('OK!')
            bot.memory['clash choices'][trigger.nick] = 'stay'
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
        if trigger.nick in bot.memory['clashes'][0]:
            bot.say('OK!')
            bot.memory['clash choices'][trigger.nick] = 'concede'
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
        if trigger.nick in bot.memory['players']
            args = trigger.group(2).lower().split()
            if len(args) >= 5:
                recipient = args[0]
                offered = []
                wanted = []
                past_offered = False
                i = 0
                while i < len(args):
                    if args[i] == 'for':
                        past_offered = True
                    if past_offered:
                        offered.append((args[i], args i + 1))
                        i += 1
                    else:
                        wanted.append((args[i], args i + 1))
                        i += 1
                    i += 1
                valid = True
                for item in offered:
                    if not (item[0] in bot.memory['cats'] or item [0] == 'bmark' or item [0] == 'wmark'):
                        valid = False
                for item in wanted:
                    if not (item[0] in bot.memory['cats'] or item [0] == 'bmark' or item [0] == 'wmark'):
                        valid = False
                if valid:
                    offered_owned = True
                    for item in offered:
                        if not ((item[0] in bot.memory['cats'] and bot.memory[item[0]][item[1]] == trigger.nick) \
                                or (item[0] == 'bmark' and bot.memory['black marks'][trigger.nick] >= item[1])   \
                                or (item[0] == 'wmark' and bot.memory['white marks'][trigger.nick] >= item[1]):
                            offered_owned = False
                    if offered_owned:
                        wanted_owned = True
                        for item in wanted:
                            if not ((item[0] in bot.memory['cats'] and bot.memory[item[0]][item[1]] == recipient) \
                                    or (item[0] == 'bmark' and bot.memory['black marks'][recipient] >= item[1])   \
                                    or (item[0] == 'wmark' and bot.memory['white marks'][recipient] >= item[1]):
                                wanted_owned = False
                        if wanted_owned:
                            # Make sure people can't offer a category unless they
                            # request the same one or there's a free slot
                            # in that category.
                            all_cats_ok = True
                            cat_ok = {}
                            for item in offered:
                                cat_ok[item[0]] = False
                                for req_item in wanted:
                                    if item[0] == req_item[0]
                                        cat_ok[item[0]] = True
                                if not cat_ok[item[0]]:
                                    for rung in range(len(bot.memory[item[0]])):
                                        if bot.memory[item[0]][rung] = '' and rung <= len(bot.memory['players']):
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
                                    cat_ok[item[0]] = False
                                    for req_item in offered:
                                        if item[0] == req_item[0]
                                            cat_ok[item[0]] = True
                                    if not cat_ok[item[0]]:
                                        for rung in range(len(bot.memory[item[0]])):
                                            if bot.memory[item[0]][rung] = '' and rung <= len(bot.memory['players']):
                                                cat_ok[item[0]] = True
                                for i in cat_ok:
                                    if not i:
                                        all_cats_ok = False
                                if all_cats_ok:
                                    # TODO: Make sure people can't offer a category the recipient
                                    # has if they aren't requesting one in return.
                                    
                                    # TODO: Make sure people can't request a category they
                                    # have if they aren't offering one in return.
                                    
                                    # TODO: Save the pending trade and send a confirmation
                                    # message to the recipient.
                                    
                                    # TODO: If the player or recipient already has a trade
                                    # pending, give an error.
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
                bot.say('Format your message like this: ~offer nick puissance 1 wmark 1 for access 1 executions 3 bmark 1')
        else:
            bot.say('You\'re not in the draft!')
    else:
        bot.say('There\'s no draft going on.')

