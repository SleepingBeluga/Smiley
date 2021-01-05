#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
path_here = os.path.dirname(os.path.realpath(__file__))
os.chdir(path_here)
# Lets us not care where smiley runs from
import discord, git
from discord.ext import commands
import time, random, asyncio, sys, traceback
import sheets, draft, dice, gamechannels, wounds, trigger, trimhistory, spectate, channelorder
import autologs, capes, snack, liveread, messagemin, tokens
from wounds import WoundOption, Wound

class myHelp(commands.DefaultHelpCommand):
    def get_ending_note(self):
        return '```Type `%help <command>` for more info on a command.\nYou can also type `%help <category>` for more info on a category.\nFor more thorough documentation, go to https://smileybot.gitlab.io (WIP)```'

b = commands.Bot(command_prefix=('%'), case_insensitive=True, help_command=myHelp(dm_help=None))

@b.command()
async def hi(ctx, *args):
    '''The hi command. I'll greet the user.
    '''
    await ctx.send('Hi, <@' + str(ctx.author.id) + '>!')

@b.command()
async def updatebot(ctx, *args):
    '''Updates the bot. Mods only.'''
    if 'Mod Team' in (str(role) for role in ctx.author.roles):
        repo = git.Repo('.')
        repo.remotes.origin.fetch()
        repo.git.reset('--hard','origin/master')
        master = repo.head.reference
        message = master.commit.message.split("\n")[0]
        await ctx.send(f'Updated to commit *{message}*. Restarting!')
        await ctx.bot.logout()
        sys.exit(1)

@b.event
async def on_command_error(ctx, error):
    if ctx.message.guild and type(error) == discord.ext.commands.errors.CommandInvokeError:
        log_chan_cat = [cat for cat in ctx.message.guild.categories if cat.name.lower() == "moderation"][0]
        log_chan = [chan for chan in log_chan_cat.channels if chan.name.lower() == "botlog"][0]
        escaped_message = ctx.message.content.replace("`","<backtick>")
        cmd = f'<#{ctx.message.channel.id}> **{ctx.author.display_name}**: `{escaped_message}`'
        tb = ''.join(traceback.format_tb(error.original.__traceback__))
        error = discord.utils.escape_markdown(f'{repr(error.original)}')
        await log_chan.send(f'{error} in command:\n{cmd}\n```{tb}```')


b.add_cog(capes.Capes())
b.add_cog(draft.Draft())
b.add_cog(gamechannels.Game_Channels(b))
b.add_cog(dice.Rolls())
b.add_cog(wounds.Wounds())
b.add_cog(trigger.Triggers_And_More())
# b.add_cog(srpg.SRPG())
# b.add_cog(ac.Autocape())
# b.add_cog(tm.TinyMech())
b.add_cog(autologs.Auto_Logs())
b.add_cog(snack.Snacks())
b.add_cog(liveread.Liveread())
b.add_cog(messagemin.MessageMin(b))
b.add_cog(channelorder.ChanOrder(b))
b.add_cog(tokens.Tokens())
# Add all the command cogs

# b.loop.create_task(draft.setup())
# # Run the draft setup function before doing anything!

b.loop.create_task(trimhistory.channel_cleanup(b))
# Start the channel cleanup task on a loop.

# b.loop.create_task(tm.tm_loop(b))
# # Start running Tiny Mechs in the background.

# b.loop.create_task(ac.ac_loop(b))
# # Run the autocape loop too!

b.loop.create_task(spectate.spectate_topics(b))
# Run the loop to update spectating channels' topics.

with open('secret') as s:
    token = s.read()[:-1]
# Read the Discord bot token from a secret file

b.run(token)
# Start the bot, finally!
