from discord.ext import commands
from shutil import copyfile
import random, time, discord, json, asyncio, names, math, scipy.stats

TIME_LENGTH = 900
# Fifteen minutes

async def get_time():
    ''' Gets the current day from file.
    If nothing is found, sets the time to 0'''
    time = None
    with open('./tm/time', 'r+') as timefile:
        if len(timefile.read()):
            timefile.seek(0)
            time = int(timefile.read())
            return time
    if not time:
        await set_time(0)
        return 0

async def get_time_hours(type='ampm'):
    time = await get_time()
    hour_part = time % 24
    if type == 'ampm':
        ampm = 'AM' if hour_part < 12 else 'PM'
        if hour_part > 12:
            hour_part -= 12
        if hour_part == 0:
            hour_part = 12
        return hour_part, ampm
    else:
        return hour_part

async def get_time_days():
    time = await get_time()
    return int(time / 24)

async def get_time_string():
    time = await get_time()
    day_part = int(time / 24)
    hour_part = time % 24
    ampm = 'AM' if hour_part < 12 else 'PM'
    if hour_part > 12:
        hour_part -= 12
    if hour_part == 0:
        hour_part = 12
    return 'Day ' + str(day_part) + ', ' + str(hour_part) + ' ' + ampm

async def a_(string):
    if string[0] in 'aeiou':
        return 'an ' + string
    else:
        return 'a ' + string

async def ord(num):
    o = str(num)
    if o[-1] == '1':
        return o + 'st'
    elif o[-1] == '2':
        return o + 'nd'
    elif o[-1] == '3':
        return o + 'rd'
    else:
        return o + 'th'

async def argmax(l, key = lambda x: x):
    return max(range(len(l)), key = lambda i: key(l[i]))

async def set_time(time):
    '''Writes the parameter 'time' to the time file'''
    with open('./tm/time', 'w+') as timefile:
        timefile.write(str(time))

async def time_forward():
    '''Increases the time file by one'''
    await set_time(await get_time() + 1)

async def tm_loop(b):
    '''The main loop function for tiny mechs
    Executes tm_day() every TIME_LENGTH seconds'''
    global TIME_LENGTH
    await b.wait_until_ready()
    await get_time()
    while True:
        await asyncio.sleep(TIME_LENGTH)
        await tm_day()

async def tm_day():
    '''Forwards time and triggers events'''
    await time_forward()
    await time_the_healer()
    await resume_fights()
    charlist = (await loadchars()).items()
    if len(charlist):
        for chartup in charlist:
            if await get_time_hours('24') > 6 and await get_time_hours('24') < 22:
                chance = 0.2
            else:
                chance = 0.05
            if random.random() < chance:
                char = await Pilot.async_init(chartup[0], dict = chartup[1])
                if not await is_fighting(char):
                    await tm_event(char)

async def time_the_healer():
    '''Has a chance to heal each pilot'''
    chars = await loadchars()
    for id, char in chars.items():
        pilot = await Pilot.async_init(id, dict = char)
        if pilot.health == 'Wounded' and random.random() < 0.1 and not await is_fighting(pilot):
            pilot.health = 'Healthy'
            await pilot.add_history('Rested and healed.')
            await updatechar(pilot)

async def is_fighting(char=None,id=None):
    if char:
        id = char.id
    fights = await loadfights()
    duels = await loadduels()
    raid = await loadraid()
    in_duel = False
    for duelids in duels.keys():
        if id in duelids and duels[duelids]['state'] == 'paused':
            in_duel = True
            break
    in_raid = False
    if len(raid):
        in_raid = id in raid['members']
    return id in fights or in_duel or in_raid

async def tm_event(char):
    '''Chooses what type of event to occur'''
    event = random.choices((tm_battle, tm_find, tm_chat, tm_tinker),weights=(0.4,0.2,0.2,0.2))[0]
    await event(char)

async def tm_find(char):
    loot = int((random.randint(20,30) + random.randint(5,40)) * (1.02 ** char.record))
    char.money += loot
    await char.add_history('Found some salvage worth ' + str(loot) + ' credits!', True)
    await updatechar(char)

async def tm_chat(char):
    charlist = list((await loadchars()).items())
    if len(charlist) > 1:
        ochartup = random.choice(charlist)
        partner = await Pilot.async_init(ochartup[0], dict = ochartup[1])
        tries = 0
        while await is_fighting(partner) or partner.id == char.id:
            tries += 1
            if tries > len(charlist):
                return
            ochartup = random.choice(charlist)
            partner = await Pilot.async_init(ochartup[0], dict = ochartup[1])
    else:
        return
    await partner.add_history('Chatted with ' + char.name + ' for a while. Learned something!', True)
    await char.add_history('Chatted with ' + partner.name + ' for a while. Learned something!', True)
    for c in (char, partner):
        learned = random.randint(0,3)
        c.stats[learned] += 1
        await updatechar(c)

async def tm_tinker(char):
    improvement = random.randint(10,25)
    min_stat = 0 if char.mech.stats[0] < char.mech.stats[1] else 1
    stat = random.choices((0, 1, min_stat),weights=(0.2,0.2,0.6))[0]
    char.mech.stats[stat] += improvement
    if stat == 0:
        await char.add_history('Tinkered on ' + await char.pronoun(type='his/her') + ' mech, improved Spark!', True)
    else:
        await char.add_history('Tinkered on ' + await char.pronoun(type='his/her') + ' mech, improved Steel!', True)
    await updatechar(char)

async def tm_battle(char):
    '''Battles char vs a random enemy and saves the result'''
    fighter = char
    hc = fighter.record
    exp_stats = [5,50,100,150]
    random.shuffle(exp_stats)
    enemies = [Enemy('Enemy Drone','Aggressive',[50,20,100,75],[1000,1000]),
               Enemy('Rogue Mech Pilot','Cautious',[80,75,75,75],[750,1250]),
               Enemy('Enemy Soldier','Confident',[90,15,80,60],[1250,700]),
               Enemy('Enemy Soldier','Aggressive',[100,50,80,40],[750,1250]),
               Enemy('Berzerk Mech','Lucky',[20,90,90,20],[500,2000]),
               Enemy('Pirate','Clever',[40,40,75,100],[1500,500]),
               Enemy('Bandit','Lucky',[40,30,85,100],[1500,500]),
               Enemy('Emplacement','Defensive',[75,10,75,10],[1500,1700]),
               Enemy('Belligerents','Aggressive',[50,100,75,50],[1000,800]),
               Enemy('Guerilla Fighters','Clever',[55,90,75,60],[900,1000]),
               Enemy('Pack of Wild Animals','Aggressive',[10,20,80,70],[800,1900]),
               Enemy('Air Combatant','Confident',[50,80,60,95],[1000,1100]),
               Enemy('Enemy General','Clever',[110,80,80,75],[1400,1400]),
               Enemy('Deserter','Defensive',[65,100,80,90],[800,1400]),
               Enemy('Prototype Drone','Lucky',[55,15,105,70],[1200,1000]),
               Enemy('Cyborg','Defensive',[70,20,80,70],[1000,1000]),
               Enemy('Broken Experiment','Lucky',exp_stats,[1500,1700])
               ]
    opponent = random.choice(enemies)
    opponent.stats = [s + hc*1 for s in opponent.stats]
    opponent.stats2 = [s + hc*10 for s in opponent.stats2]
    await tm_start_fight(False, fighter, opponent)

async def tm_start_fight(is_duel, fighter, opponent):
    fstat = await fighter.choose_stat(opponent)
    ostat = await opponent.choose_stat(fighter)
    effectiveness = 1
    if not type(fstat) == int:
        fstat = 2
    if not type(ostat) == int:
        ostat = 2
    if fstat == ostat - 1:
        effectiveness = 2
    elif fstat == ostat + 1:
        effectiveness = 0.5
    statdiff = fighter.stats[fstat] * effectiveness - opponent.stats[ostat]
    advantage = 2.1/(1 + math.exp(-.07 * statdiff)) + 0.4
    rr = (0.8,1.2)
    fdam = fighter.mech.stats[0] / 5
    fdam *= 1 if fighter.health == 'Healthy' else 0.8
    odam = opponent.stats2[0] / 5 if not is_duel else opponent.mech.stats[0] / 5
    if is_duel:
        odam *= 1 if opponent.health == 'Healthy' else 0.8
    fhealth = fighter.mech.stats[1]
    ohealth = opponent.stats2[1] if not is_duel else opponent.mech.stats[1]
    if is_duel:
        await fighter.add_history('Started a duel vs ' + opponent.name + '. ' + await Pilot.statname(fstat) + ' vs. ' + await Pilot.statname(ostat))
        await opponent.add_history('Started a duel vs ' + fighter.name + '. ' + await Pilot.statname(ostat) + ' vs. ' + await Pilot.statname(fstat))
        await updatechar(opponent)
    else:
        await fighter.add_history('Started a fight vs ' + opponent.name + '. ' + await Pilot.statname(fstat) + ' vs. ' + await Pilot.statname(ostat))
    await updatechar(fighter)
    await tm_continue_fight(is_duel, fighter, opponent, advantage, fhealth, ohealth, fdam, odam, rr)

async def tm_start_raid(boss_d, member_ids):
    chars = await loadchars()
    members = [await Pilot.async_init(id, dict=chars[id]) for id in member_ids]
    boss = RaidBoss(dict = boss_d)
    member_stats = [await m.choose_stat(boss) for m in members]
    memberhealths = [m.mech.stats[1] for m in members]
    boss_stat = (int(scipy.stats.mode(member_stats)[0][0]) - 1) % 4
    boss.health *= len(members) ** 0.75
    await tm_continue_raid(boss, boss_stat, members, member_stats, memberhealths)

async def tm_continue_fight(is_duel, fighter, opponent, advantage, fhealth, ohealth, fdam, odam, rr):
    '''Decides who wins'''
    chars = await loadchars()
    fighter = await Pilot.async_init(fighter.id, dict=chars[fighter.id])
    if is_duel:
        opponent = await Pilot.async_init(opponent.id, dict=chars[opponent.id])
    fattack = max(1,int(fdam * advantage * (random.random() * (rr[1] - rr[0]) + rr[0])))
    oattack = max(1,int(odam / advantage * (random.random() * (rr[1] - rr[0]) + rr[0])))
    fhealth -= oattack
    ohealth -= fattack
    await fighter.add_history('Hit ' + opponent.name + ' for ' + str(fattack) + ' damage but got hit for ' + str(oattack) + ' in return.')
    await updatechar(fighter)
    if is_duel:
        await opponent.add_history('Hit ' + fighter.name + ' for ' + str(oattack) + ' damage but got hit for ' + str(fattack) + ' in return.')
        await updatechar(opponent)
    if fhealth <= 0 or ohealth <= 0:
        await tm_finish_fight(is_duel, fighter, opponent, fhealth - ohealth)
    else:
        await tm_pause_fight(is_duel, fighter, opponent, advantage, fhealth, ohealth, fdam, odam, rr)

async def tm_continue_raid(boss, boss_stat, members, member_stats, memberhealths):
    for i, m in enumerate(members):
        if memberhealths[i] > 0:
            if boss_stat == member_stats[i] + 1:
                effectiveness = 2
            elif boss_stat == member_stats[i] - 1:
                effectiveness = 0.5
            else:
                effectiveness = 1
            statdiff = m.stats[member_stats[i]] * effectiveness - boss.stats[boss_stat]
            advantage = 2.1/(1 + math.exp(-.07 * statdiff)) + 0.4
            mdam = max(1,int((m.mech.stats[0] / 5) * advantage * (random.random() * (1.2 - 0.8) + 0.8)))
            bdam = max(1,int((boss.stats2[0] / 5) / advantage * (random.random() * (1.2 - 0.8) + 0.8)))
            boss.health -= mdam
            memberhealths[i] -= bdam
            await m.add_history('Hit ' + boss.name + ' for ' + str(mdam) + ' damage but got hit for ' + str(bdam) + ' in return.')
            await updatechar(m)
            if boss.health <= 0:
                await tm_raid_victory(boss, members)
                return
            elif memberhealths[i] <= 0:
                await m.add_history('Was forced to retreat from the raid!')
                await updatechar(m)
    live_members = list(filter(lambda i: memberhealths[i] > 0, range(len(members))))
    if len(live_members) == 0:
        await tm_raid_loss(boss, members)
        return
    await tm_pause_raid(boss, boss_stat, members, member_stats, memberhealths)

async def tm_pause_fight(is_duel, fighter, opponent, advantage, fhealth, ohealth, fdam, odam, rr):
    if is_duel:
        dueldict = {'state': 'paused',
                    'fighter': await fighter.get_dict_for_json(),
                    'opponent': await opponent.get_dict_for_json(),
                    'advantage': advantage,
                    'fhealth': fhealth, 'ohealth': ohealth,
                    'fdam': fdam, 'odam': odam, 'rr': rr}
        duels = await loadduels()
        key = ';'.join(sorted([fighter.id,opponent.id]))
        duels[key] = dueldict
        with open('./tm/duels.json','w+') as duelsfile:
            json.dump(duels, duelsfile)
    else:
        fightdict = {'fighter': await fighter.get_dict_for_json(),
                     'opponent': await opponent.get_dict_for_json(),
                     'advantage': advantage,
                     'fhealth': fhealth, 'ohealth': ohealth,
                     'fdam': fdam, 'odam': odam, 'rr': rr}
        fights = await loadfights()
        fights[fighter.id] = fightdict
        with open('./tm/fights.json','w+') as fightsfile:
            json.dump(fights, fightsfile)

async def tm_pause_raid(boss, boss_stat, members, member_stats, memberhealths):
    members_ids = [m.id for m in members]
    boss_d = await boss.get_dict_for_json()
    raiddict = {'boss': boss_d, 'boss_stat': boss_stat,
                'members': members_ids, 'member_stats': member_stats,
                'memberhealths': memberhealths, 'state': 'paused'}
    with open('./tm/raid.json','w+') as raidfile:
        json.dump(raiddict, raidfile)

async def resume_fights():
    fights = await loadfights()
    open('./tm/fights.json','w').close()
    duels = await loadduels()
    open('./tm/duels.json','w').close()
    raid = await loadraid()
    open('./tm/raid.json','w').close()
    while len(fights):
        id, fight = fights.popitem()
        try:
            await tm_continue_fight(False,
                                    await Pilot.async_init(id, dict = fight['fighter']),
                                    Enemy(dict = fight['opponent']),
                                    fight['advantage'],
                                    fight['fhealth'], fight['ohealth'],
                                    fight['fdam'], fight['odam'],
                                    fight['rr'])
        except:
            print('Unknown pilot ID')
    while len(duels):
        ids, duel = duels.popitem()
        ids = ids.split(';')
        if duel['state'] == 'paused':
            try:
                await tm_continue_fight(True,
                                        await Pilot.async_init(ids[0], dict = duel['fighter']),
                                        await Pilot.async_init(ids[1], dict = duel['opponent']),
                                        duel['advantage'],
                                        duel['fhealth'], duel['ohealth'],
                                        duel['fdam'], duel['odam'],
                                        duel['rr'])
            except:
                print('Unknown pilot ID')
    if len(raid) and raid['state'] == 'paused':
        chars = await loadchars()
        members = []
        for id in raid['members']:
            try:
                members.append(await Pilot.async_init(id, dict=chars[id]))
            except:
                print('Unknown pilot ID')
        await tm_continue_raid(RaidBoss(dict=raid['boss']), raid['boss_stat'], members,
                               raid['member_stats'], raid['memberhealths'])

async def tm_finish_fight(is_duel, fighter, opponent, result):
    chars = await loadchars()
    fighter = await Pilot.async_init(fighter.id, dict=chars[fighter.id])
    if is_duel:
        opponent = await Pilot.async_init(opponent.id, dict=chars[opponent.id])
    if result >= 0:
        if is_duel:
            await opponent.add_history('Lost the duel vs ' + fighter.name + '.', True)
            await fighter.add_history('Won the duel vs ' + opponent.name + '!', True)
        else:
            topstat = max(fighter.stats)
            if 200 - topstat * random.randint(1,5) > 0:
                fighter.stats[random.randint(0,3)] += 1
            winnings = random.randint(10,50) + random.randint(5,50)
            winnings = int(winnings * (1.04 ** max(fighter.record, 0)))
            fighter.record += 1
            fighter.money += winnings
            await fighter.add_history('Won the battle vs ' + opponent.name + ', got ' + str(winnings) + ' credits!', True)
    else:
        if is_duel:
            await opponent.add_history('Won the duel vs ' + fighter.name + '!', True)
            await fighter.add_history('Lost the duel vs ' + opponent.name + '.', True)
        else:
            fighter.record -= 1
            fighter.health = 'Wounded'
            await fighter.add_history('Lost the battle vs ' + opponent.name + '.', True)
    await updatechar(fighter)
    if is_duel:
        await updatechar(opponent)

async def tm_raid_loss(boss, members):
    for m in members:
        await m.add_history('The raid vs. ' + boss.name + ' was unsuccessful.', True)
        await updatechar(m)
        m.record -= 1

async def tm_raid_victory(boss, members):
    for m in members:
        winnings = random.randint(100,500) + random.randint(5,500)
        winnings = int(winnings * (1.07 ** min(m.record, 0)))
        m.record += 1
        m.money += winnings
        await m.add_history('The raid vs. ' + boss.name + ' was successful! Got ' + str(winnings) + ' credits for participating!', True)
        await updatechar(m)

async def loadchars():
    '''Returns a dictionary of pilots as dicts'''
    with open('./tm/chars.json', 'r+') as charsfile:
        if len(charsfile.read()):
            charsfile.seek(0)
            chars = json.load(charsfile)
        else:
            chars = {}
    return chars

async def loadfights():
    '''Returns a dictionary of fights as dicts'''
    with open('./tm/fights.json', 'r+') as fightsfile:
        if len(fightsfile.read()):
            fightsfile.seek(0)
            fights = json.load(fightsfile)
        else:
            fights = {}
    return fights

async def loadduels():
    '''Returns a dictionary of duels as dicts'''
    with open('./tm/duels.json', 'r+') as duelsfile:
        if len(duelsfile.read()):
            duelsfile.seek(0)
            duels = json.load(duelsfile)
        else:
            duels = {}
    return duels

async def loadraid():
    with open('./tm/raid.json', 'r+') as raidfile:
        if len(raidfile.read()):
            raidfile.seek(0)
            raid = json.load(raidfile)
        else:
            raid = {}
    return raid

async def updatechar(char):
    '''Overwrites the old data for a character'''
    chars = await loadchars()
    chars[char.id] = await char.get_dict_for_json()
    with open('./tm/chars.json', 'w+') as charsfile:
        json.dump(chars, charsfile)

async def deletefight(id):
    fights = await loadfights()
    if id in fights:
        del fights[id]
    with open('./tm/fights.json', 'w+') as fightsfile:
        json.dump(fights, fightsfile)

async def parse_gen(pattern):
    '''Recursively randomly fills out a pattern template'''
    pwords = pattern.split(' ')
    result = []
    for word in pwords:
        if not word[0] == '$':
            result.append(word)
        else:
            with open('./tm/gen/' + word[1:]) as lpfile:
                lowerpattern = random.choice(lpfile.read().splitlines())
            result.append(await parse_gen(lowerpattern))
    return ' '.join(result)

async def join(ctx, *args):
    '''Allows a player to hire a Tiny Mech pilot'''
    if args:
        id = args[0]
    else:
        id = str(ctx.author.id)
    chars = await loadchars()
    if id in chars:
        await ctx.send('You already have a pilot!')
        return
    owner = ctx.author.display_name
    new_pilot = await Pilot.async_init(id, owner)
    await new_pilot.add_history('Pilot hired.', True)
    char = await new_pilot.get_dict_for_json()
    chars[id] = char
    with open('./tm/chars.json', 'w+') as charsfile:
        json.dump(chars, charsfile)
    await ctx.send('Pilot created! Check up on them with `%tm check`')
    await check(ctx, id)

async def delete(ctx, *args):
    '''Dismisses a player's pilot'''
    if args:
        id = args[0]
    else:
        id = str(ctx.author.id)
    chars = await loadchars()
    if not id in chars:
        await ctx.send('You don\'t have a pilot!')
        return
    await deletefight(id)
    del chars[id]
    with open('./tm/chars.json', 'w+') as charsfile:
        json.dump(chars, charsfile)
    await ctx.send('Pilot deleted.')

async def check(ctx, *args):
    '''Displays current info about your pilot and their mech'''
    if args:
        id = args[0]
    else:
        id = str(ctx.author.id)
    chars = await loadchars()
    if id in chars:
        char = await Pilot.async_init(id, dict = chars[id])
        await ctx.send('```' + await char.summary() + \
                       '``````' + await char.mech.summary() + '```')
    else:
        await ctx.send("You don't seem to have a pilot yet. Use `%tm join` to hire one!")

async def get_record(ctx, *args):
    '''Displays current net wins of your pilot'''
    if args:
        id = args[0]
    else:
        id = str(ctx.author.id)
    chars = await loadchars()
    if id in chars:
        char = await Pilot.async_init(id, dict = chars[id])
        await ctx.send(char.name + ' has ' + str(char.record) + ' net wins.')
    else:
        await ctx.send("You don't seem to have a pilot yet. Use `%tm join` to hire one!")

async def history(ctx, *args):
    '''Displays the eight most recent events involving your pilot'''
    if args:
        id = args[0]
    else:
        id = str(ctx.author.id)
    chars = await loadchars()
    if id in chars:
        char = await Pilot.async_init(id, dict = chars[id])
        await ctx.send('```' + await char.get_history() + '```')
    else:
        await ctx.send("You don't seem to have a pilot yet. Use `%tm join` to hire one!")

async def importanthistory(ctx, *args):
    '''Displays the eight most recent important events involving your pilot'''
    if args:
        id = args[0]
    else:
        id = str(ctx.author.id)
    chars = await loadchars()
    if id in chars:
        char = await Pilot.async_init(id, dict = chars[id])
        await ctx.send('```' + await char.get_history(True) + '```')
    else:
        await ctx.send("You don't seem to have a pilot yet. Use `%tm join` to hire one!")

async def do_upgrade(char):
    avgstat = (char.mech.stats[0] * char.mech.stats[0])**0.5
    cost = int((avgstat*(1.5**(avgstat/1000)))/100)*(10)
    if char.money >= cost:
        char.money -= cost
        stat = random.randint(0,1)
        char.mech.stats[stat] += random.randint(150,175)
        await char.add_history('Upgraded mech for ' + str(cost) + ' credits.', True)
        await updatechar(char)
        avgstat = (char.mech.stats[0] * char.mech.stats[0])**0.5
        cost = int((avgstat*(1.5**(avgstat/1000)))/100)*(10)
        return True, cost
    else:
        return False, cost

async def upgrade(ctx, *args):
    '''Try to purchase a mech upgrade'''
    if args:
        id = args[0]
    else:
        id = str(ctx.author.id)
    chars = await loadchars()
    if id in chars:
        char = await Pilot.async_init(id, dict = chars[id])
        res, cost = await do_upgrade(char)
        if res:
            await ctx.send('Upgrade purchased!```' + await char.mech.summary() + '```')
        else:
            await ctx.send('Your next upgrade costs ' + str(cost) + ' but you only have ' + str(char.money) + ' credits.')
    else:
        await ctx.send("You don't seem to have a pilot yet. Use `%tm join` to hire one!")

async def full_upgrade(ctx, *args):
    '''Try to purchase a mech upgrade'''
    if args:
        id = args[0]
    else:
        id = str(ctx.author.id)
    chars = await loadchars()
    if id in chars:
        char = await Pilot.async_init(id, dict = chars[id])
        res = True
        while res:
            res, cost = await do_upgrade(char)
        await ctx.send('Fully upgraded! Your next upgrade costs ' + str(cost) + \
                       '.```' + await char.summary() + '``````' + \
                       await char.mech.summary() + '```')
    else:
        await ctx.send("You don't seem to have a pilot yet. Use `%tm join` to hire one!")

async def disengage(ctx, *args):
    '''Try to purchase a mech upgrade'''
    if args:
        id = args[0]
    else:
        id = str(ctx.author.id)
    chars = await loadchars()
    if id in chars:
        char = await Pilot.async_init(id, dict = chars[id])
        if await is_fighting(char):
            await deletefight(char.id)
            await char.add_history('Disengaged from the fight.')
            await updatechar(char)
            await ctx.send('Disengaged successfully!')
        else:
            await ctx.send('You can\'t disengage either since you\'re not in a fight or since you\'re dueling.')
    else:
        await ctx.send("You don't seem to have a pilot yet. Use `%tm join` to hire one!")

async def buypet(ctx, *args):
    '''Try to purchase a pet. Your current pet will go live on a farm if successful'''
    if args:
        id = args[0]
    else:
        id = str(ctx.author.id)
    chars = await loadchars()
    if id in chars:
        char = await Pilot.async_init(id, dict = chars[id])
        avgstat = (char.mech.stats[0] * char.mech.stats[1])**0.5
        cost = int((avgstat*(1.4**(avgstat/1000)))/300)*(20)
        if char.money >= cost:
            char.money -= cost
            rarity = min(random.choices(range(5), k = 3)) + 1
            if char.pet.rarity == rarity:
                rarity += 1
            char.pet = Pet(await parse_gen('$Animals'), names.get_first_name(), rarity)
            await char.add_history('Bought a pet for ' + str(cost) + ' credits.', True)
            await updatechar(char)
            await ctx.send('Companion purchased!```' + await char.summary() + '```')
        else:
            await ctx.send('Buying a pet costs ' + str(cost) + ' right now but you only have ' + str(char.money) + ' credits.')
    else:
        await ctx.send("You don't seem to have a pilot yet. Use `%tm join` to hire one!")

async def set_strategy(ctx, *args):
    '''Set a strategy for your pilot to use in battle'''
    id = str(ctx.author.id)
    chars = await loadchars()
    if id in chars:
        validstrats = ('Aggressive','Defensive','Lucky','Cautious','Confident','Clever')
        char = await Pilot.async_init(id, dict = chars[id])
        if args:
            strat = args[0].capitalize()
        else:
            await ctx.send('You must choose a strategy. Valid strategies are: `' + ', '.join(validstrats) + '`')
        if not strat in validstrats:
            await ctx.send('Valid strategies are: `' + ', '.join(validstrats) + '`')
        else:
            char.strategy = strat
            await updatechar(char)
            await ctx.send('Strategy set.')
    else:
        await ctx.send("You don't seem to have a pilot yet. Use `%tm join` to hire one!")

async def setpetname(ctx, *args):
    '''Give your companion a name'''
    id = str(ctx.author.id)
    if args:
        name = args[0]
    else:
        await ctx.send('No name provided!')
        return
    if args and len(args) > 1:
        id = args[1]
    chars = await loadchars()
    if id in chars:
        char = await Pilot.async_init(id, dict = chars[id])
        if char.pet.type != None:
            char.pet.name = name
            await updatechar(char)
            await ctx.send("Pet renamed!")
        else:
            await ctx.send("You don't seem to have a pet. Buy one with `%tm buypet`")
    else:
        await ctx.send("You don't seem to have a pilot yet. Use `%tm join` to hire one!")

async def duel(ctx, *args):
    '''Challenge someone to a duel, or accept a challenge.'''
    id = str(ctx.author.id)
    chars = await loadchars()
    if args and len(args) > 1:
        id = args[1]
    if ctx.message.mentions:
        opp_id = str(ctx.message.mentions[0].id)
    elif args:
        try:
            _ = int(args[0])
            opp_id = args[0]
        except:
            await ctx.send('Please @ the person you want to duel!')
            return
    else:
        await ctx.send('Please @ the person you want to duel!')
        return
    if id == opp_id:
        await ctx.send("You can't duel yourself!")
        return
    if not opp_id in chars:
        await ctx.send("That person doesn't have a mech!")
        return
    f = await Pilot.async_init(id, dict=chars[id])
    o = await Pilot.async_init(opp_id, dict=chars[opp_id])
    if await is_fighting(f):
        await ctx.send("You're already in a fight! You can use `%tm disengage` to leave the fight, unless it's a duel or a raid.")
        return
    if await is_fighting(o):
        await ctx.send("They're already in a fight!")
        return
    duels = await loadduels()
    f, o = sorted([f, o], key = lambda p: p.id)
    key = ';'.join([f.id,o.id])
    if key in duels:
        if duels[key]['state'] == 'challenge':
            await ctx.send('Challenge accepted. The duel has begun!')
            await tm_start_fight(True, f, o)
    else:
        duels[key] = {'state': 'challenge'}
        with open('./tm/duels.json','w+') as duelsfile:
            json.dump(duels, duelsfile)
        await ctx.send('Challenge sent!')
        await f.add_history('Challenged ' + o.name + ' to a duel!')
        await o.add_history('Got challenged to a duel by ' + f.name + '!')
        await updatechar(f)
        await updatechar(o)

async def mechname(ctx, *args):
    '''Generate a random mech name'''
    await ctx.send('The ' + await parse_gen('$TopLevelPatterns'))

async def openraid(ctx, *args):
    raid = await loadraid()
    if len(raid):
        await ctx.send("There's already a raid!")
    else:
        boss = RaidBoss('Amalgam','Aggressive',[200,10,10,10],[2000,2000], 2000)
        raid = {'state': 'open',
                'members': [],
                'boss': await boss.get_dict_for_json()}
        with open('./tm/raid.json','w+') as raidfile:
            json.dump(raid, raidfile)
        await ctx.send('RAID OPEN! Use `%tm joinraid` to participate!')

async def joinraid(ctx, *args):
    raid = await loadraid()
    if len(raid):
        if raid['state'] == 'open':
            if not await is_fighting(id=str(ctx.author.id)):
                raid['members'].append(str(ctx.author.id))
                with open('./tm/raid.json','w+') as raidfile:
                    json.dump(raid, raidfile)
                await ctx.send("Joined the raid!")
            else:
                await ctx.send("You're already in a fight! You can use `%tm disengage` to leave the fight, unless it's a duel or a raid.")
        else:
            await ctx.send("The raid already started.")
    else:
        await ctx.send("There's no raid to join.")

async def startraid(ctx, *args):
    raid = await loadraid()
    if len(raid):
        if raid['state'] == 'open':
            await tm_start_raid(raid['boss'],raid['members'])

async def checkraid(ctx, *args):
    raid = await loadraid()
    chars = await loadchars()
    if len(raid):
        to_send = '```State: ' + raid['state'] + '\nMembers:\n'
        for id in raid['members']:
            to_send += '   ' + chars[id]['name'] + '\n'
        to_send += '```'
    await ctx.send(to_send)

class Fight():
    pass

class Duel(Fight):
    pass

class Raid(Fight):
    pass

class Fight_Thing():
    def __init__(self, name='', strategy='', stats=[], stats2=[], dict = None):
        if dict:
            self.name = dict['name']
            self.strategy = dict['strategy']
            self.stats = dict['stats']
            self.stats2 = dict['stats2']
        else:
            self.name = name
            self.strategy = strategy
            self.stats = stats
            self.stats2 = stats2

    async def get_dict_for_json(self):
        return {'name': self.name, 'strategy': self.strategy,
                'stats': self.stats, 'stats2': self.stats2}

    async def choose_stat(self, opponent):
        if self.strategy == 'Aggressive':
            return await argmax(self.stats)
        elif self.strategy == 'Defensive':
            return (await argmax(opponent.stats) - 1) % 4
        elif self.strategy == 'Lucky':
            return random.randint(0,3)
        elif self.strategy == 'Cautious':
            max = 0
            max2 = 0
            for i, stat in enumerate(opponent.stats):
                if stat > max:
                    max2 = max
                    max2ind = i
                    max = stat
                elif stat > max2:
                    max2 = stat
                    max2ind = i
            return (max2ind - 1) % 4
        elif self.strategy == 'Confident':
            max = 0
            max2 = 0
            for i, stat in enumerate(self.stats):
                if stat > max:
                    max2 = max
                    max2ind = i
                    max = stat
                elif stat > max2:
                    max2 = stat
                    max2ind = i
            return max2ind
        elif self.strategy == 'Clever':
            if opponent.strategy == 'Clever':
                return random.randint(0,3)
            else:
                return await opponent.choose_stat(self)
        return 2

class Enemy(Fight_Thing):
    pass

class RaidBoss(Fight_Thing):
    def __init__(self, name='', strategy='', stats=[], stats2=[], health=0, dict = None):
        if dict:
            self.name = dict['name']
            self.strategy = dict['strategy']
            self.stats = dict['stats']
            self.stats2 = dict['stats2']
            self.health = dict['health']
        else:
            self.name = name
            self.strategy = strategy
            self.stats = stats
            self.stats2 = stats2
            self.health = health

    async def get_dict_for_json(self):
        return {'name': self.name, 'strategy': self.strategy,
                'stats': self.stats, 'stats2': self.stats2,
                'health': self.health}

class Pilot(Fight_Thing):
    @classmethod
    async def async_init(cls, id, owner = None, dict = None):
        self = Pilot()
        if dict:
            self.id = id
            self.owner = dict['owner']
            self.name = dict['name']
            self.strategy = dict['strategy']
            self.age = dict['age']
            self.gender = dict['gender']
            self.stats = dict['stats']
            self.mech = await Mech.async_init(dict = dict['mech'])
            self.health = dict['health']
            self.history = dict['history'][-100:]
            self.record = dict['record']
            if 'money' in dict:
                self.money = dict['money']
            else:
                self.money = 0
            if 'pet' in dict:
                try:
                    self.pet = Pet(dict['pet']['type'],
                                   dict['pet']['name'],
                                   dict['pet']['rarity'])
                except:
                    self.pet = Pet(dict['pet']['type'],
                                   dict['pet']['name'],
                                   1)
            else:
                self.pet = Pet(None)
            if 'bday' in dict:
                self.bday = dict['bday']
            else:
                self.bday = await get_time_days() + random.randint(0,366)
            if 'importanthistory' in dict:
                self.importanthistory = dict['importanthistory'][-100:]
            else:
                self.importanthistory = []
            if 'rank' in dict:
                self.rank = dict['rank']
            else:
                self.rank = 0
            if self.bday <= await get_time_days():
                self.age += 1
                self.bday += 366
                await self.add_history('Celebrated ' + await self.pronoun(type='his/her') + ' ' + await ord(self.age) + ' birthday!', True)
                await updatechar(self)
            if self.record >= 6*(self.rank + 1)*(1.11**self.rank):
                await self.promote()
                await self.add_history('Pilot promoted!', True)
                await updatechar(self)
        elif owner:
            self.id = id
            self.owner = owner
            if random.random() < 0.02:
                if random.random() < 0.5:
                    self.gender = 'Non-Binary'
                else:
                    self.gender = 'Agender'
                self.name = names.get_full_name()
            elif random.random() < 0.5:
                self.gender = 'Male'
                self.name = names.get_full_name(gender='male')
            else:
                self.gender = 'Female'
                self.name = names.get_full_name(gender='female')
            self.strategy = 'Defensive'
            self.age = int(max(5,random.lognormvariate(3.5,0.4)))
            self.stats = [60,60,60,60]
            strengths = [random.randint(0,3) for _ in range(2)]
            for s in strengths:
                self.stats[s] += 15
            weaknesses = [random.randint(0,3) for _ in range(2)]
            for w in weaknesses:
                self.stats[w] -= 15
            for i in range(4):
                self.stats[i] += random.randint(-5,5)
            self.mech = await Mech.async_init()
            self.health = 'Healthy'
            self.history = []
            self.importanthistory = []
            self.record = 0
            self.money = 0
            self.pet = Pet(None)
            self.bday = await get_time_days() + random.randint(0,366)
            self.rank = 0
        else:
            raise ArgumentError('To create a Pilot either an owner name or a dictionary must be passed')
        return self

    def __init__(self):
        pass

    @classmethod
    async def statname(cls, stat):
        return {0: 'Head',
                1: 'Heart',
                2: 'Strength',
                3: 'Speed'}[stat]

    async def get_dict_for_json(self):
        return {'owner': self.owner, 'name': self.name,
                'strategy': self.strategy, 'age': self.age,
                'gender': self.gender, 'stats': self.stats,
                'mech': await self.mech.get_dict_for_json(),
                'health': self.health, 'history': self.history,
                'record': self.record, 'money': self.money,
                'pet': await self.pet.get_dict_for_json(),
                'bday': self.bday, 'rank': self.rank,
                'importanthistory': self.importanthistory}

    async def summary(self):
        ranks = ['Recruit','Pilot','Pilot First Class',
                 'Senior Pilot','Petty Sergeant','Sergeant',
                 'Master Sergeant', 'Master Sergeant First Class',
                 'Ensign', 'Lieutenant', 'Captain', 'Major',
                 'Lieutenant Colonel', 'Colonel', 'Lieutenant Commander',
                 'Commander', 'Brigadier General', 'Major General',
                 'Lieutenant General', 'General, 1 Star']
        if self.rank < len(ranks):
            rank = ranks[self.rank]
        else:
            stars = self.rank - len(ranks) + 1
            rank = 'General, ' + str(stars) + ' Stars'
        return 'Pilot:\n' + self.name + ', piloting the ' + self.mech.name + '\n' + \
               'Player: '    + self.owner             + '\n' + \
               'Age: '       + str(self.age)          + '\n' + \
               'Gender: '    + self.gender            + '\n' + \
               'Rank: '      + rank                   + '\n' + \
               'Strategy: '  + self.strategy          + '\n' + \
               'Health: '    + self.health            + '\n' + \
               'Money: '     + str(self.money)        + '\n' + \
               'Companion: ' + await self.pet.print() + '\n' + \
               'Stats: '                              + '\n' + \
               '   Head: '     + str(self.stats[0])   + '\n' + \
               '   Heart: '    + str(self.stats[1])   + '\n' + \
               '   Strength: ' + str(self.stats[2])   + '\n' + \
               '   Speed: '    + str(self.stats[3])

    async def pronoun(self, type):
        if type == 'he/she':
            if self.gender == 'Male':
                return 'he'
            elif self.gender == 'Female':
                return 'she'
            else:
                return 'they'
        elif type == 'him/her':
            if self.gender == 'Male':
                return 'him'
            elif self.gender == 'Female':
                return 'her'
            else:
                return 'them'
        elif type == 'his/her':
            if self.gender == 'Male':
                return 'his'
            elif self.gender == 'Female':
                return 'her'
            else:
                return 'their'
        elif type == 'his/hers':
            if self.gender == 'Male':
                return 'his'
            elif self.gender == 'Female':
                return 'hers'
            else:
                return 'theirs'
        else:
            return ''

    async def add_history(self, text, is_important=False):
        if is_important:
            self.importanthistory.append(await get_time_string() + ': ' + text)
        self.history.append(await get_time_string() + ': ' + text)

    async def get_history(self, is_important=False):
        if is_important:
            to_ret = 'Recent important history for ' + self.name + \
                     ' as of ' + (await get_time_string()).lower() + ':'
            for event in self.importanthistory[-8:]:
                to_ret += '\n' + event
        else:
            to_ret = 'Recent history for ' + self.name + \
                     ' as of ' + (await get_time_string()).lower() + ':'
            for event in self.history[-8:]:
                to_ret += '\n' + event
        return to_ret

    async def promote(self):
        prom_stats = random.choices(range(4), k=3)
        for i, s in enumerate(prom_stats):
            self.stats[s] += 10*(i+1)
        self.rank += 1

class Mech():
    @classmethod
    async def async_init(cls, dict = None):
        self = Mech()
        if dict:
            if type(dict) == type(''):
                self.name = dict
                self.stats = [1000,1000]
                if random.random() < 0.67:
                    if random.random() < 0.5:
                        strength = 0
                    else:
                        strength = 1
                    self.stats[strength] += 500
                    self.stats[1 - strength] -= 500
                for i in range(2):
                    self.stats[i] += random.randint(-50,50)
            else:
                self.name = dict['name']
                self.stats = dict['stats']
        else:
            self.name = await parse_gen('$TopLevelPatterns')
            self.stats = [1000,1000]
            if random.random() < 0.67:
                if random.random() < 0.5:
                    strength = 0
                else:
                    strength = 1
                self.stats[strength] += 500
                self.stats[1 - strength] -= 500
            for i in range(2):
                self.stats[i] += random.randint(-50,50)
        return self

    def __init__(self):
        pass

    async def summary(self):
        return 'Mech:\nThe ' + self.name + '\n' + \
               'Stats:\n' + \
               '   Spark: '     + str(self.stats[0]) + '\n' + \
               '   Steel: '    + str(self.stats[1]) + '\n'

    async def get_dict_for_json(self):
        return {'name': self.name, 'stats': self.stats}

class Pet():
    def __init__(self, type=None, name=None, rarity = 0):
        self.type = type
        self.name = name
        self.rarity = rarity

    async def print(self):
        rarestr = ' ' + ('★' * self.rarity)
        if self.type == None:
            return 'None'
        elif self.name == None:
            return a_(self.type).capitalize() + rarestr
        else:
            return self.name + ' the ' + self.type + rarestr

    async def get_dict_for_json(self):
        return {'name': self.name, 'type': self.type,
                'rarity': self.rarity}

class TinyMech(commands.Cog):
    def __init__ (self):
        copyfile('./tm/chars.json','./tm/chars.json.old')

    @commands.command()
    async def tm(self, ctx, cmd, *args):
        '''Use the tm commands.
        Options include %tm join, %tm delete, %tm check, %tm history, %tm upgrade, %tm strategy <strategy>, %tm duel @<user>, %tm buypet'''
        if cmd == 'join':
            await join(ctx, *args)
        elif cmd == 'check':
            await check(ctx, *args)
        elif cmd == 'delete':
            await delete(ctx, *args)
        elif cmd == 'history':
            await history(ctx, *args)
        elif cmd == 'ihistory':
            await importanthistory(ctx, *args)
        elif cmd == 'strategy':
            await set_strategy(ctx, *args)
        elif cmd == 'getmechname':
            await mechname(ctx, *args)
        elif cmd == 'upgrade':
            await upgrade(ctx, *args)
        elif cmd == 'fupgrade':
            await full_upgrade(ctx, *args)
        elif cmd == 'duel':
            await duel(ctx, *args)
        elif cmd == 'buypet':
            await buypet(ctx, *args)
        elif cmd == 'petname':
            await setpetname(ctx, *args)
        elif cmd == 'time':
            await ctx.send(await get_time_string())
        elif cmd == 'record':
            await get_record(ctx, *args)
        elif cmd == 'disengage':
            await disengage(ctx, *args)
        elif cmd == 'joinraid':
            await joinraid(ctx, *args)
        elif cmd == 'checkraid':
            await checkraid(ctx, *args)
        elif ctx.author.id == 200669454848360448:
            if cmd == 'forcedays':
                try:
                    numdays = int(args[0])
                except:
                    numdays = 1
                for day in range(numdays):
                    await tm_day()
            elif cmd == 'forceevent':
                await tm_event()
            elif cmd == 'openraid':
                await openraid(ctx, *args)
            elif cmd == 'startraid':
                await startraid(ctx, *args)
            elif cmd == 'settime':
                try:
                    t = int(args[0])
                    await set_time(t)
                except:
                    return
