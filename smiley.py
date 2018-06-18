from sopel.module import commands, require_privmsg, require_chanmsg
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
    bot.memory['round'] = None
    
    bot.memory['bidding'] = False
    bot.memory['clash'] = False
    
    bot.memory['quitconfirm'] = False
    
    bot.memory['puissance']  = [None, None, None, None, None, None]
    bot.memory['longevity']  = [None, None, None, None, None, None]
    bot.memory['access']     = [None, None, None, None, None, None]
    bot.memory['executions'] = [None, None, None, None, None, None]
    bot.memory['research']   = [None, None, None, None, None, None]
    bot.memory['schools']    = [None, None, None, None, None, None]
    bot.memory['priority']   = [None, None, None, None, None, None]
    bot.memory['family']     = [None, None, None, None, None, None]
    
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
    calc_clashes(bot)
    if bot.memory['clash']:
        do_clash(bot)
    if len(bot.memory['to resolve']) > 0:
        subround(bot, True)
    elif all_resolved(bot):
        show_table(bot)
        bot.say('That\'s the end of the draft! Thanks for playing!')
        setup(bot) 
    else:
        bot.memory['to resolve'] = bot.memory['players']
        subround(bot, False)
'''
My main loop. Executes subrounds and resolves clashes.
'''

def get_bids(bot):
    for player in bot.memory['players']:
        bot.memory['bids'][player] = None
    for player in bot.memory['players']:
        if player not in bot.memory['to resolve']:
            bot.memory['bids'][player] = 0
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
    bot.memory['bidding'] = False
'''
Tells players to submit bids, and waits until all bids are done.
'''

def calc_clashes(bot):
    bid = None
    bid_player = None
    clashes_so_far = 0
    for player in bot.memory['to resolve']:
        if not (player in bot.memory['clashes'][0] or \
                player in bot.memory['clashes'][1] or \
                player in bot.memory['clashes'][2]):
            bid = bot.memory['bids'][player]
            bid_player = player
            for player2 in bot.memory['to resolve']:
                if bid == bot.memory['bids'][player] and not player == player2:
                    if not player in bot.memory['clashes'][clashes_so_far]:
                        bot.memory['clashes'][clashes_so_far].append(player)
                        clashes_so_far += 1
                    bot.memory['clashes'][clashes_so_far].append(player2)
    bot.say('There are ' + str(clashes_so_far) + ' clashes.')
    if clashes_so_far > 0:
        bot.memory['clash'] = True
'''
Figures out if there are clashes and who's in each.
'''

def do_clash(bot):
    bot.memory['to resolve'] = []
    #TODO: uh, everything
'''
Performs clashes and adds players who need to rebid to 'to resolve'.
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
        #TODO: Change to 4
        if len(bot.memory['players']) >= 1 and len(bot.memory['players']) <= 6:
            bot.say('Starting the draft!')
            bot.memory['phase'] = 'the draft'
            bot.memory['round'] = 1
            bot.memory['to resolve'] = bot.memory['players']
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

@require_chanmsg
@commands('reset')
def reset(bot, trigger):
    if not bot.memory['quitconfirm']:
        bot.say('Are you sure? This will reset any drafts in progress. (Use ~quit again to confirm)')
        bot.memory['quitconfirm'] = True
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
        if trigger.nick in bot.memory['to resolve']:
            cat = trigger.group(2).lower().split()[0]
            rung = int(trigger.group(2).lower().split()[1])
            if bot.memory.contains(cat):
                if rung <= len(bot.memory['players']):
                    if bot.memory[cat][rung - 1] == None:
                        bot.memory['bids'][trigger.nick] = (cat, rung)
                        bot.say('Got it!')
                    else:
                        bot.say('That one\'s taken, please choose another.')
                else:
                    bot.say('Please choose a rung between 1 and ' + str(len(bot.memory['players'])) + '. Format your message like this: ~bid puissance 4')
            else:
                bot.say ('I don\'t know that category. Format your message like this: ~bid puissance 4')
        else:
            bot.say('I don\'t need a bid from you right now.')
    else:
        bot.say('Now\'s not the time for bidding.')
