import discord, asyncio, datetime, traceback

async def channel_cleanup(b):
    await b.wait_until_ready()
    while(True):
    # Forever
        try:
            for server in b.guilds:
                channel_list=dict( (channel.name,channel) for channel in server.channels)
            # Build a list of the server's channels
            for to_clear in ('relationships', 'lgbt-plus'):
            # For each channel we want to trim
                mlist=[]
                async for message in channel_list[to_clear].history(limit=None):
                    delta = (datetime.datetime.utcnow()-message.created_at)
                    tdiff= delta.days*86400 +delta.seconds
                    if tdiff >= 172800 and tdiff < 1209600:
                        mlist.append(message)
                        with open('output.txt','a+') as out:
                            out.write(f'#{to_clear} {str(message.created_at)} {message.author}: {message.clean_content}\n')
                    elif tdiff >= 1209600:
                        with open('output.txt','a+') as out:
                            out.write(f'#{to_clear} (old) {str(message.created_at)} {message.author}: {message.clean_content}\n')
                        await message.delete()
                for batch_i in range((len(mlist)//100) + 1):
                    batch = mlist[batch_i:batch_i+99]
                    await channel_list[to_clear].delete_messages(batch)
        except Exception as e:
            server = b.guilds[0]
            log_chan_cat = [cat for cat in server.categories if cat.name.lower() == 'moderation'][0]
            log_chan = [chan for chan in log_chan_cat.channels if chan.name.lower() == 'botlog'][0]
            tb = ''.join(traceback.format_tb(e.__traceback__))
            error = discord.utils.escape_markdown(f'{repr(e)}')
            await log_chan.send(f'{error} in trimhistory loop:\n```{tb}```')
        await asyncio.sleep(3600)
