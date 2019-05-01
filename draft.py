from discord.ext import commands

async def subround(clash):
    '''My main loop. Executes subrounds and resolves clashes.
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
    '''Displays the categories so you can see who has what.
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
    '''Makes a new sheet for a PD Draft.
    Parameters: none
    Return: None
    '''
    num_players = len(memory["players"])
    memory["sheetID"] = await sheets.new_blank_sheet(memory, num_players)
    await memory['channel'].send('Click here to follow: https://docs.google.com/spreadsheets/d/' + memory["sheetID"])

async def update_sheet():
    '''Goes through my memory and copies current draft results
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
    '''Tells players to submit bids, and waits until all bids are done.
    '''
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
    '''Figures out if there are clashes and who's in each.
    '''
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

async def do_clash(continued):
    '''Performs clashes and adds players who need to rebid to 'to resolve'.
    '''
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

async def get_clash_choices():
    '''Tells players to submit clash choices, and waits until all clash choices are done.
    '''
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

async def all_resolved():
    '''Not used because it doesn't work yet. Ideally should calculate when future rounds can be autofilled, but with insigs/abysmal that's not an easy check.
    '''
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

async def check_bids():
    if not None in memory['bids'].values():
        memory['bidsin'].set()

async def check_clash_choices():
    if not None in memory['clash choices'].values():
        memory['clashesin'].set()

class Draft:
    '''Commands for Pact Dice drafts
    '''
    @commands.command()
    async def open(self, ctx, *args):
        '''Begins a draft so people can join.
        '''
        if memory['phase'] == 'none':
            memory['phase'] = 'setup'
            await ctx.send('Opening a draft! (Use ~join to join, and then ~start to begin)')
        else:
            await ctx.send('A draft is already ongoing! Finish it before trying again.')

    @commands.command()
    async def join(self, ctx, *args):
        '''Lets you join a draft.
        '''
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

    @commands.command()
    async def start(self, ctx, *args):
        '''Starts the draft after players join.
        '''
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

    @commands.command()
    async def bid(self, ctx, *args):
        '''Allows players to bid on draft slots.
        '''
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

    @commands.command()
    async def stay(self, ctx, *args):
        '''The command to refuse to budge during a clash.
        '''
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

    @commands.command()
    async def concede(self, ctx, *args):
        '''The command to cede during a clash.
        '''
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


    @commands.command()
    async def table(self, ctx, *args):
        '''Shows the current draft progress
        '''
        if memory['phase'] == 'the draft':
            show_cats()
        else:
            await ctx.send('There\'s no draft going on.')

    @commands.command()
    async def offer(self, ctx, *args):
        '''Allows players to offer trades to other players.
        '''
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

    @commands.command()
    async def deny(self, ctx, *args):
        '''Lets players deny trades offered them.
        '''
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