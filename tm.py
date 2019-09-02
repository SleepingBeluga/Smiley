from discord.ext import commands
from shutil import copyfile
import random, time, discord, json, asyncio, math

DAY_LENGTH = 3600
# One hour

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

async def set_time(time):
    '''Writes the parameter 'time' to the time file'''
    with open('./tm/time', 'w+') as timefile:
        timefile.write(str(time))

async def time_forward():
    '''Increases the time file by one and heals'''
    await set_time(await get_time() + 1)
    await time_the_healer()

async def tm_loop(b):
    '''The main loop function for tiny mechs
    Executes tm_day() every DAY_LENGTH seconds'''
    global DAY_LENGTH
    await b.wait_until_ready()
    await get_time()
    while True:
        await asyncio.sleep(DAY_LENGTH)
        await tm_day()

async def tm_day():
    '''Forwards time and triggers events'''
    await time_forward()
    charlist = (await loadchars()).items()
    if len(charlist):
        for chartup in charlist:
            if random.random() < 0.2:
                char = await Pilot.async_init(chartup[0], dict = chartup[1])
                await tm_event(char)

async def time_the_healer():
    '''Has a chance to heal all pilots'''
    chars = await loadchars()
    for id, char in chars.items():
        pilot = await Pilot.async_init(id, dict = char)
        if pilot.health == 'Wounded' and random.random() < 0.2:
            pilot.health = 'Healthy'
            pilot.history.append('Day ' + str(await get_time()) + ': Rested and healed.')
            await updatechar(pilot)

async def tm_event(char):
    '''Chooses what type of event to occur'''
    await tm_battle(char)

async def tm_battle(char):
    '''Battles char vs a random enemy and saves the result'''
    fighter = char
    hc = fighter.record
    enemies = [Enemy('Monster','Aggressive',[50,20,100,75],[1000,1000]),
               Enemy('Rogue Mech Pilot','Defensive',[80,75,75,75],[750,1250]),
               Enemy('Enemy Soldier','Aggressive',[90,15,80,60],[1250,700]),
               Enemy('Carnivorous Plant','Lucky',[20,90,90,20],[500,2000]),
               Enemy('Pirate','Lucky',[40,40,75,100],[1500,500])]
    opponent = random.choice(enemies)
    opponent.stats = [s + hc*10 for s in opponent.stats]
    result = await tm_fight(fighter, opponent)
    if result >= 0:
        topstat = max(fighter.stats)
        if 200 - topstat * random.randint(1,5) > 0:
            fighter.stats[random.randint(0,3)] += 1
        winnings = random.randint(1,50) + random.randint(0,50)
        winnings = int(winnings * (1.05 ** fighter.record))
        fighter.record += 1
        fighter.money += winnings
        fighter.history.append('Day ' + str(await get_time()) + ': Won a battle vs ' + opponent.name + ', got ' + str(winnings) + ' credits!')
    else:
        fighter.record -= 1
        fighter.history.append('Day ' + str(await get_time()) + ': Lost a battle vs ' + opponent.name + '.')
        fighter.health = 'Wounded'
    await updatechar(fighter)

async def tm_fight(fighter,opponent):
    '''Decides who wins'''
    fstat = await fighter.choose_stat(opponent)
    ostat = await opponent.choose_stat(fighter)
    effectiveness = 0
    if not type(fstat) == int:
        fstat = 2
    if fstat == ostat - 1:
        effectiveness = 2
    elif fstat == ostat + 1:
        effectiveness = 0.5
    statdiff = fighter.stats[fstat] * effectiveness - opponent.stats[ostat]
    advantage = 2.1/(1 + math.exp(-.07 * statdiff)) + 0.4
    rr = (-50,50) if fighter.health == 'Healthy' else (-50,30)
    fdam = fighter.mech.stats[0] / 5
    odam = opponent.stats2[0] / 5
    fhealth = fighter.mech.stats[1]
    ohealth = opponent.stats2[1]
    while fhealth > 0 and ohealth > 0:
        fhealth -= int(odam / advantage) + random.randint(rr[0],rr[1])
        ohealth -= fdam * advantage + random.randint(rr[0],rr[1])
    return fhealth - ohealth

async def loadchars():
    '''Returns a dictionary of pilots'''
    with open('./tm/chars.json', 'r+') as charsfile:
        if len(charsfile.read()):
            charsfile.seek(0)
            chars = json.load(charsfile)
        else:
            chars = {}
    return chars

async def updatechar(char):
    '''Overwrites the old data for a character'''
    chars = await loadchars()
    chars[char.id] = await char.get_dict_for_json()
    with open('./tm/chars.json', 'w+') as charsfile:
        json.dump(chars, charsfile)

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
    new_pilot.history.append('Day ' + str(await get_time()) + ': Pilot hired.')
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
        await ctx.send("You don't seem to have a pilot yet.")

async def history(ctx, *args):
    '''Displays the five most recent events involving your pilot'''
    if args:
        id = args[0]
    else:
        id = str(ctx.author.id)
    chars = await loadchars()
    if id in chars:
        char = await Pilot.async_init(id, dict = chars[id])
        await ctx.send('```' + await char.get_history() + '```')
    else:
        await ctx.send("You don't seem to have a pilot yet.")

async def upgrade(ctx, *args):
    '''Try to purchase a mech upgrade'''
    if args:
        id = args[0]
    else:
        id = str(ctx.author.id)
    chars = await loadchars()
    if id in chars:
        char = await Pilot.async_init(id, dict = chars[id])
        topstat = max(char.mech.stats)
        cost = int((topstat*(1.5**(topstat/1000)))/100)*(10)
        if char.money > cost:
            char.money -= cost
            stat = random.randint(0,1)
            char.mech.stats[stat] += random.randint(100,200)
            char.history.append('Day ' + str(await get_time()) + ': Upgraded mech for ' + str(cost) + ' credits.')
            await updatechar(char)
            await ctx.send('Upgrade purchased!```' + await char.mech.summary() + '```')
        else:
            await ctx.send('Your next upgrade costs ' + str(cost) + ' but you only have ' + str(char.money) + ' credits.')
    else:
        await ctx.send("You don't seem to have a pilot yet.")

async def set_strategy(ctx, *args):
    '''Set a strategy for your pilot to use in battle'''
    id = str(ctx.author.id)
    chars = await loadchars()
    if id in chars:
        validstrats = ('Aggressive','Defensive','Lucky')
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
        await ctx.send("You don't seem to have a pilot yet.")

async def mechname(ctx, *args):
    '''Generate a random mech name'''
    await ctx.send('The ' + await parse_gen('$TopLevelPatterns'))

class Fight_Thing():
    def __init__(self, name, strategy, stats, stats2):
        self.name = name
        self.strategy = strategy
        self.stats = stats
        self.stats2 = stats2

    async def choose_stat(self, opponent):
        if self.strategy == 'Aggressive':
            max = 0
            maxind = None
            for ind, stat in enumerate(self.stats):
                if stat > max:
                    max = stat
                    maxind = ind
            return maxind
        elif self.strategy == 'Defensive':
            max = 0
            maxind = None
            for ind, stat in enumerate(opponent.stats):
                if stat > max:
                    max = stat
                    maxind = ind
            return (maxind - 1) % 4
        elif self.strategy == 'Lucky':
            return random.randint(0,3)
        return 2

class Enemy(Fight_Thing):
    pass

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
            self.history = dict['history']
            self.record = dict['record']
            if 'money' in dict:
                self.money = dict['money']
            else:
                self.money = 0
        elif owner:
            self.id = id
            self.owner = owner
            if random.random() < 0.02:
                self.gender = random.choice(['Non-Binary','Agender','Genderfluid'])
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
            self.record = 0
            self.money = 0
        else:
            raise ArgumentError('To create a Pilot either an owner name or a dictionary must be passed')
        return self

    def __init__(self):
        pass

    async def get_dict_for_json(self):
        return {'owner': self.owner, 'name': self.name,
                'strategy': self.strategy, 'age': self.age,
                'gender': self.gender, 'stats': self.stats,
                'mech': await self.mech.get_dict_for_json(),
                'health': self.health, 'history': self.history,
                'record': self.record, 'money': self.money}

    async def summary(self):
        return 'Pilot:\n' + self.name + ', piloting the ' + self.mech.name + '\n' + \
               'Player: '   + self.owner       + '\n' + \
               'Age: '      + str(self.age)    + '\n' + \
               'Gender: '   + self.gender      + '\n' + \
               'Strategy: ' + self.strategy    + '\n' + \
               'Health: '   + self.health      + '\n' + \
               'Money: '    + str(self.money) + '\n' + \
               'Stats: '                       + '\n' + \
               '   Head: '     + str(self.stats[0]) + '\n' + \
               '   Heart: '    + str(self.stats[1]) + '\n' + \
               '   Strength: ' + str(self.stats[2]) + '\n' + \
               '   Speed: '    + str(self.stats[3])

    async def get_history(self):
        to_ret = 'Recent history for ' + self.name + \
                 ' as of day ' + str(await get_time()) + ':'
        for event in self.history[-5:]:
            to_ret += '\n' + event
        return to_ret

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



class TinyMech(commands.Cog):
    def __init__ (self):
        copyfile('./tm/chars.json','./tm/chars.json.old')

    @commands.command()
    async def tm(self, ctx, cmd, *args):
        '''Use the tm commands.
        Options include %tm join, %tm delete, %tm check, %tm history, %tm upgrade, %tm strategy <strategy>'''
        if cmd == 'join':
            await join(ctx, *args)
        elif cmd == 'check':
            await check(ctx, *args)
        elif cmd == 'delete':
            await delete(ctx, *args)
        elif cmd == 'history':
            await history(ctx, *args)
        elif cmd == 'strategy':
            await set_strategy(ctx, *args)
        elif cmd == 'mechname':
            await mechname(ctx, *args)
        elif cmd == 'forceevent':
            await tm_event()
        elif cmd == 'upgrade':
            await upgrade(ctx, *args)
        elif cmd == 'forcedays':
            try:
                numdays = int(args[0])
            except:
                numdays = 1
            for day in range(numdays):
                await tm_day()
