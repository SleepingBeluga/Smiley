#!/usr/bin/env python
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import time, random, asyncio
import sheets, draft, dice, gamechannels, wounds, trigger, trimhistory, srpg, tm
import ac
from wounds import WoundOption, Wound

'''My (Smiley's) Main Script
I'm friendly, and I have commands to support playing PD and WD!
'''

b = commands.Bot(command_prefix=('%'))

@b.command()
async def hi(ctx, *args):
    '''The hi command. I'll greet the user.
    '''
    await ctx.send('Hi, <@' + str(ctx.author.id) + '>!')

@b.command()
async def reset(ctx, *args):
    '''Resets me, stopping any drafts in progress.
    '''
    if not draft.memory['quitconfirm']:
        await ctx.send('Are you sure? This will reset any drafts in progress. (Use %reset again to confirm)')
        draft.memory['quitconfirm'] = True
        await asyncio.sleep(60)
        draft.memory['quitconfirm'] = False
    else:
        await ctx.send('OK, I\'ve reset.')
        await draft.setup()

b.add_cog(draft.Draft())
b.add_cog(gamechannels.Game_Channels())
b.add_cog(dice.Rolls())
b.add_cog(wounds.Wounds())
b.add_cog(trigger.Trigger())
b.add_cog(srpg.SRPG())
b.add_cog(ac.Autocape())
b.add_cog(tm.TinyMech())

b.loop.create_task(draft.setup())
# Run the draft setup function before doing anything!

b.loop.create_task(trimhistory.channel_cleanup(b))
# Start the channel cleanup task on a loop.

b.loop.create_task(tm.tm_loop(b))
# Start running Tiny Mechs in the background.

b.loop.create_task(ac.ac_loop(b))

with open('secret') as s:
    token = s.read()[:-1]
# Read the Discord bot token from a soup or secret file

b.run(token)
# Start the bot
