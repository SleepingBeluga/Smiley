from discord.ext import commands
from shutil import copyfile
import random, time, discord, json

async def join(ctx, *args):
    if args:
        id = args[0]
    else:
        id = str(ctx.author.id)
    char = {'owner': ctx.author.display_name, 'name': None,
            'strategy': None, 'age': None, 'gender': None, 'stats': None,
            'mech': None, 'history': None}
    with open('./tm/chars.json', 'r+') as charsfile:
        if len(charsfile.read()):
            charsfile.seek(0)
            chars = json.load(charsfile)
        else:
            chars = {}
        if id in chars:
            await ctx.send('You already have a pilot!')
            return
    with open('./tm/chars.json', 'w+') as charsfile:
        chars[id] = char
        json.dump(chars, charsfile)
        await ctx.send('Pilot created! Check up on them with `%tm check`')

async def check(ctx, *args):
    if args:
        id = args[0]
    else:
        id = str(ctx.author.id)

    with open('./tm/chars.json', 'r+') as charsfile:
        await ctx.send(json.load(charsfile)[id])

class TinyMech(commands.Cog):
    def __init__ (self):
        copyfile('./tm/chars.json','./tm/chars.json.old')

    @commands.command()
    async def tm(self, ctx, cmd, *args):
        if cmd == 'join':
            await join(ctx, *args)
        elif cmd == 'check':
            await check(ctx, *args)
