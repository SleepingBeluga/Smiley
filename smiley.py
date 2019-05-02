#!/usr/bin/env python
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import time, random, asyncio
import sheets, draft, dice, gamechannels

'''My (Smiley's) Main Script

I'm friendly, and I can do Pact Dice drafts and dice rolls!
'''

b = commands.Bot(command_prefix=('~'))
memory = {}
fopen = open # I'm sorry God, this is the hackiest shit ever

async def setup():
    '''My initializing function.
    '''

    memory['channel'] = None
    memory['phase'] = 'none'
    memory['round'] = None
    memory['bidding'] = False
    memory['clashing'] = False
    # Set all the 'state' indicators to defaults

    memory['players'] = []
    memory['to resolve'] = []
    memory['player colors'] = []

    memory['pending trades'] = []
    memory['trade contents'] = {}

    memory['proper names'] = {}
    memory['bids'] = {}
    memory['clash choices'] = {}
    memory['black marks'] = {}
    memory['white marks'] = {}
    memory['limits'] = {}
    # Make empty arrays for all the player things

    memory['rows to show'] = 0

    memory['clash'] = False

    memory['quitconfirm'] = False

    memory['cats'] = ('puissance', 'longevity', 'access', 'executions', 'research', \
                          'schools',   'priority',  'family')
    memory['puissance']  = ['', '', '', '', '',    '', '', '']
    memory['longevity']  = ['', '', '', '', '',    '', '', '']
    memory['access']     = ['', '', '', '', '',    '', '', '']
    memory['executions'] = ['', '', '', '', '',    '', '', '']
    memory['research']   = ['', '', '', '', '',    '', '', '']
    memory['schools']    = ['', '', '', '', '',    '', '', '']
    memory['priority']   = ['', '', '', '', '',    '', '', '']
    memory['family']     = ['', '', '', '', '',    '', '', '']

    memory['clashes'] = [[],[],[]]
    # More empty things

    memory['colors'] = {"purple": (0.2,0.1,0.5),
                        "blue":   (0.1,0.3,0.8),
                        "green":  (0.2,0.5,0.1),
                        "yellow": (0.7,0.6,0.0), # Leave out first
                        "orange": (0.7,0.4,0.0), # Leave out second
                        "red":    (0.6,0.0,0.0)
                        }
    # Define colors

    memory['clashesin'] = asyncio.Event()
    memory['bidsin'] = asyncio.Event()
    # Events for the end of clash and bids

@b.command()
async def hi(ctx, *args):
    '''The hi command. I'll greet the user.
    '''
    await ctx.send('Hi, ' + ctx.author.display_name + '!')

@b.command()
async def reset(ctx, *args):
    '''Resets me, stopping any drafts in progress.
    '''
    if not memory['quitconfirm']:
        await ctx.send('Are you sure? This will reset any drafts in progress. (Use ~reset again to confirm)')
        memory['quitconfirm'] = True
        await asyncio.sleep(60)
        memory['quitconfirm'] = False
    else:
        await ctx.send('OK, I\'ve reset.')
        await setup()

b.add_cog(draft.Draft())
b.add_cog(gamechannels.Game_Channels())
b.add_cog(dice.Rolls())
b.add_cog(wounds.WoundCog())
# Add the cogs to the bot

b.loop.create_task(setup())
# Run the setup function before doing anything!

with fopen('secret') as s:
    token = s.read()[:-1]
# Read the Discord bot token from a soup or secret file

b.run(token)
# Start the bot
