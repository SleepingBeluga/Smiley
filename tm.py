from discord.ext import commands
import random, time, discord, json

async def join(ctx, *args):
    char = {'owner': ctx.author.display_name, 'name': None,
            'strategy': None, 'age': None, 'gender': None, 'stats': None,
            'mech': None, 'history': None}
    with open('./tm/chars.json', 'a+') as charsfile:
        if len(read(charsfile)):
            chars = json.load(charsfile)
        else:
            chars = {}
        if str(ctx.author.id) in chars:
            await ctx.send('You already have a pilot!')
            return
        chars[str(ctx.author.id)] = char
        json.dump(chars, charsfile)
        await ctx.send('Pilot created! Check up on them with `%tm check`')

async def check(ctx, *args):
    with open('./tm/chars.json', 'r+') as charsfile:
        await ctx.send(json.load(charsfile)[str(ctx.author.id)])

class TinyMech(commands.Cog):
    @commands.command()
    async def tm(self, ctx, cmd, *args):
        if cmd == 'join':
            await join(ctx, *args)
        elif cmd == 'check':
            await check(ctx, *args)
