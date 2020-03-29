import discord, asyncio, datetime

async def channel_cleanup(b):
    await b.wait_until_ready()
    while(True):
    # Forever
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
                elif tdiff > 1209600:
                    await message.delete()
            for batch_i in range((len(mlist)//100) + 1):
                batch = mlist[batch_i:batch_i+99]
                await channel_list[to_clear].delete_messages(batch)
        await asyncio.sleep(3600)
