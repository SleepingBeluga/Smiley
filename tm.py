from discord.ext import commands
from shutil import copyfile
import random, time, discord, json, asyncio

DAY_LENGTH = 3600
# One hour

async def get_time():
    time = None
    with open('./tm/time', 'r+') as timefile:
        if len(timefile.read()):
            timefile.seek(0)
            time = int(timefile.read())
            return time
    if not time:
        await set_time(0)

async def set_time(time):
    with open('./tm/time', 'w+') as timefile:
        timefile.write(str(time))

async def time_forward():
    await set_time(await get_time() + 1)
    await time_the_healer()

async def tm_loop(b):
    global DAY_LENGTH
    await b.wait_until_ready()
    await get_time()
    while True:
        await asyncio.sleep(DAY_LENGTH)
        await tm_day()

async def tm_day():
    await time_forward()
    charlist = (await loadchars()).items()
    if len(charlist):
        for chartup in charlist:
            if random.random() < 0.2:
                char = await Pilot.async_init(chartup[0], dict = chartup[1])
                await tm_event(char)

async def time_the_healer():
    chars = await loadchars()
    for id, char in chars.items():
        pilot = await Pilot.async_init(id, dict = char)
        if pilot.health == 'Wounded' and random.random() < 0.2:
            pilot.health = 'Healthy'
            pilot.history.append('Day ' + str(await get_time()) + ': Rested and healed.')
            await updatechar(pilot)

async def tm_event(char):
    await tm_battle(char)

async def tm_battle(char):
    fighter = char
    hc = fighter.record
    mstats = [s + hc*10 for s in [50,20,100,75]]
    opponent = Enemy('Monster','Aggressive',mstats)
    result = await tm_fight(fighter, opponent)
    if result >= 0:
        fighter.record += 1
        fighter.history.append('Day ' + str(await get_time()) + ': Won a battle vs ' + opponent.name + '!')
    else:
        fighter.record -= 1
        fighter.history.append('Day ' + str(await get_time()) + ': Lost a battle vs ' + opponent.name + '.')
        fighter.health = 'Wounded'
    await updatechar(fighter)

async def tm_fight(fighter,opponent):
    fstat = await fighter.choose_stat(opponent)
    ostat = await opponent.choose_stat(fighter)
    advantage = 0
    if fstat == ostat - 1:
        advantage = 1.5
    elif fstat == ostat + 1:
        advantage = 0.66
    hows_it_going = 0
    rr = (-10,10) if fighter.health == 'Healthy' else (-10,5)
    for round in range(3):
        hows_it_going += fighter.stats[fstat] * advantage - \
                         opponent.stats[ostat] + random.randint(rr[0],rr[1])
    return hows_it_going

async def loadchars():
    with open('./tm/chars.json', 'r+') as charsfile:
        if len(charsfile.read()):
            charsfile.seek(0)
            chars = json.load(charsfile)
        else:
            chars = {}
    return chars

async def updatechar(char):
    chars = await loadchars()
    chars[char.id] = await char.get_dict_for_json()
    with open('./tm/chars.json', 'w+') as charsfile:
        json.dump(chars, charsfile)

async def parse_gen(pattern):
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
    if args:
        id = args[0]
    else:
        id = str(ctx.author.id)
    chars = await loadchars()
    if id in chars:
        char = await Pilot.async_init(id, dict = chars[id])
        await ctx.send('```' + await char.summary() + '```')
    else:
        await ctx.send("You don't seem to have a pilot yet.")

async def history(ctx, *args):
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

async def set_strategy(ctx, *args):
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
    await ctx.send('The ' + await parse_gen('$TopLevelPatterns'))

class Fight_Thing():
    def __init__(self, name, strategy, stats):
        self.name = name
        self.strategy = strategy
        self.stats = stats

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
        else:
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
            self.mech = dict['mech']
            self.health = dict['health']
            self.history = dict['history']
            self.record = dict['record']
        elif owner:
            self.id = id
            self.owner = owner
            if random.random() < 0.02:
                self.gender = 'Non-Binary'
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
            self.mech = await parse_gen('$TopLevelPatterns')
            self.health = 'Healthy'
            self.history = []
            self.record = 0
        else:
            raise ArgumentError('To create a Pilot either an owner name or a dictionary must be passed')
        return self

    def __init__(self):
        pass

    async def get_dict_for_json(self):
        return {'owner': self.owner, 'name': self.name,
                'strategy': self.strategy, 'age': self.age,
                'gender': self.gender, 'stats': self.stats,
                'mech': self.mech, 'health': self.health,
                'history': self.history, 'record': self.record}

    async def summary(self):
        return self.name + ', piloting the ' + self.mech + '\n' + \
               'Player: '   + self.owner    + '\n' + \
               'Age: '      + str(self.age) + '\n' + \
               'Gender: '   + self.gender   + '\n' + \
               'Strategy: ' + self.strategy + '\n' + \
               'Health: '   + self.health   + '\n' + \
               'Stats: '                    + '\n' + \
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

class TinyMech(commands.Cog):
    def __init__ (self):
        copyfile('./tm/chars.json','./tm/chars.json.old')

    @commands.command()
    async def tm(self, ctx, cmd, *args):
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
        elif cmd == 'forcedays':
            try:
                numdays = int(args[0])
            except:
                numdays = 1
            for day in range(numdays):
                await tm_day()
