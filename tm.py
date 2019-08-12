from discord.ext import commands
from shutil import copyfile
import random, time, discord, json, asyncio

async def tm_loop():
    await b.wait_until_ready()
    time = 0
    while True:
        time += 1
        asyncio.sleep(10)
        if random.random() < 0.3:
            await tm_event(time)

async def tm_event(time):
    await tm_battle(time)

async def tm_battle(time):
    chars = await loadchars()

async def loadchars():
    with open('./tm/chars.json', 'r+') as charsfile:
        if len(charsfile.read()):
            charsfile.seek(0)
            chars = json.load(charsfile)
        else:
            chars = {}
    return chars

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
    with open('./tm/chars.json', 'w+') as charsfile:
        chars[id] = char
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
    with open('./tm/chars.json', 'w+') as charsfile:
        del chars[id]
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
            self.history = dict['history']
        elif owner:
            self.id = id
            self.owner = owner
            self.name = ''
            self.strategy = ''
            self.age = ''
            self.gender = ''
            self.stats = ['','','','']
            self.mech = ''
            self.history = []
        else:
            raise ArgumentError('To create a Pilot either an owner name or a dictionary must be passed')

    async def get_dict_for_json(self):
        return {'owner': self.owner, 'name': self.name,
                'strategy': self.strategy, 'age': self.age,
                'gender': self.gender, 'stats': self.stats,
                'mech': self.mech, 'history': self.history}

    async def summary(self):
        return self.name + ', piloting the ' + self.mech + '\n' + \
               'Player: '      + self.owner    + '\n' + \
               'Age: '         + self.age      + '\n' + \
               'Gender: '      + self.gender   + '\n' + \
               'Strategy: '    + self.strategy + '\n' + \
               'Stats: '                       + '\n' + \
               '   Head: '     + self.stats[0] + '\n' + \
               '   Heart: '    + self.stats[1] + '\n' + \
               '   Strength: ' + self.stats[2] + '\n' + \
               '   Speed: '    + self.stats[3] + '\n'

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
