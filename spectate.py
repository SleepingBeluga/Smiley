import discord, asyncio, datetime, traceback

async def spectate_topics(b):
    await b.wait_until_ready()
    while(True):
    # Forever
        try:
            #Set vars
            wdGames = []
            pdGames = []
            wdSpec = []
            pdSpec = []
            wdActive = []
            pdActive = []

            #Collect channels
            for server in b.guilds:
                for channel in server.channels:
                    if channel.category != None:
                        if channel.category.name in ('WeaverDice Games', 'WeaverDice Games 2'):
                            wdGames.append(channel)
                        elif channel.category.name in ('PactDice Games', 'PactDice Games 2'):
                            pdGames.append(channel)
                        elif channel.name == 'wd-spectating':
                            wdSpec.append(channel)
                        elif channel.name == 'pd-spectating':
                            pdSpec.append(channel)

            for chan in wdGames:
                async for message in chan.history(limit=1):
                    if (datetime.datetime.utcnow() - message.created_at).total_seconds() < 1800:
                        wdActive.append(chan)

            for chan in pdGames:
                async for message in chan.history(limit=1):
                    if (datetime.datetime.utcnow() - message.created_at).total_seconds() < 1800:
                        pdActive.append(chan)

            if len(wdSpec) == 1:
                top = "For active session commentary."
                if len(wdActive) != 0:
                    top += " Active channels: #"
                    for chan in wdActive:
                        top += chan.name
                        top += ", #"
                    top = top[:-3]

                await wdSpec[0].edit(topic=top)

            if len(pdSpec) == 1:
                top = "For active session commentary."
                if len(pdActive) != 0:
                    top += " Active channels: #"
                    for chan in pdActive:
                        top += chan.name
                        top += ", #"
                    top = top[:-3]

                await pdSpec[0].edit(topic=top)
        except Exception as e:
            server = b.guilds[0]
            log_chan_cat = [cat for cat in server.categories if cat.name.lower() == 'moderation'][0]
            log_chan = [chan for chan in log_chan_cat.channels if chan.name.lower() == 'botlog'][0]
            tb = ''.join(traceback.format_tb(e.__traceback__))
            error = discord.utils.escape_markdown(f'{repr(e)}')
            await log_chan.send(f'{error} in trimhistory loop:\n```{tb}```')
        await asyncio.sleep(900)
