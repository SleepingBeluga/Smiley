from discord.ext import commands
from shutil import copyfile
import random, time, discord, json, asyncio

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

async def tm_loop(b):
    await b.wait_until_ready()
    await get_time()
    while True:
        await time_forward()
        await asyncio.sleep(10)
        if random.random() < 0.8:
            await tm_event()

async def tm_event():
    await tm_battle()

async def tm_battle():
    chars = await loadchars()
    options = list(chars.items())
    id, fighter_d = random.choice(options)
    fighter = Pilot(id, dict = fighter_d)
    opponent = Enemy('Monster','aggressive',[50,20,100,75])
    result = await tm_fight(fighter, opponent)
    if result >= 0:
        fighter.history.append('Day ' + str(await get_time()) + ': Won a battle vs ' + opponent.name + '! ' + str(result))
    else:
        fighter.history.append('Day ' + str(await get_time()) + ': Lost a battle vs ' + opponent.name + '. ' + str(result))
        fighter.health = 'Wounded'
    await updatechar(fighter)

async def tm_fight(fighter,opponent):
    hows_it_going = 0
    rr = (-10,10) if fighter.health == 'Healthy' else (-10,5)
    for i, stat in enumerate(fighter.stats):
        hows_it_going += stat - opponent.stats[(i-1) % 4] + random.randint(rr[0],rr[1])
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
    new_pilot = Pilot(id, owner)
    char = await new_pilot.get_dict_for_json()
    chars[id] = char
    with open('./tm/chars.json', 'w+') as charsfile:
        json.dump(chars, charsfile)
    await ctx.send('Pilot created! Check up on them with `%tm check`')

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
        char = Pilot(id, dict = chars[id])
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
        char = Pilot(id, dict = chars[id])
        await ctx.send('```' + await char.get_history() + '```')
    else:
        await ctx.send("You don't seem to have a pilot yet.")

class Enemy():
    def __init__(self, name, strategy, stats):
        self.name = name
        self.strategy = strategy
        self.stats = stats

class Pilot():
    def __init__(self, id, owner = None, dict = None):
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
        elif owner:
            self.id = id
            self.owner = owner
            self.name = ''
            self.strategy = ''
            self.age = ''
            self.gender = ''
            self.stats = [60,60,60,60]
            self.mech = ''
            self.health = 'Healthy'
            self.history = []
        else:
            raise ArgumentError('To create a Pilot either an owner name or a dictionary must be passed')

    async def get_dict_for_json(self):
        return {'owner': self.owner, 'name': self.name,
                'strategy': self.strategy, 'age': self.age,
                'gender': self.gender, 'stats': self.stats,
                'mech': self.mech, 'health': self.health,
                'history': self.history}

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
