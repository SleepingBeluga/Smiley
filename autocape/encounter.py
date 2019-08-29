# Encounter class for a fight

# This is going to be complicated because of how many different factors go into
# it. Need a method to decide what AI's preference is going into a fight,
# then roll tactics to select which it wants the most!

async def fight(cape1, cape2):
    update = ''

    if cape1.state == 2:
        update += str(cape1.alias) + " attacked " + str(cape2.alias) + "!\n"
        if cape2.state == 0:
            update += str(cape1.alias) + " beat them up!\n"
            await cape1.win(cape2)
            await cape2.lose(cape1)
        elif cape2.state == 1:
            update += str(cape2.alias) + " beat them up!\n"
            await cape1.lose(cape2)
            await cape2.win(cape1)
        elif cape2.state == 2:
            update += str(cape2.alias) + " fought " + str(cape1.alias) + " off.\n"
            await cape1.tie(cape2)
            await cape2.tie(cape1)
    elif cape1.state == 0:
        update += str(cape1.alias) + " plotted against " + str(cape2.alias) + ".\n"
        if cape2.state == 0:
            update += str(cape2.alias) + " found " + str(cape1.alias) + " out!\n"
            await cape1.tie(cape2)
            await cape2.tie(cape1)
        elif cape2.state == 1:
            update += str(cape1.alias) + " has a plan...\n"
            await cape1.win(cape2)
            await cape2.lose(cape1)
        elif cape2.state == 2:
            update += str(cape2.alias) + " beat them up!\n"
            await cape1.lose(cape2)
            await cape2.win(cape1)
    elif cape1.state == 1:
        update += str(cape1.alias) + " taunted " + str(cape2.alias) + ".\n"
        if cape2.state == 0:
            update += str(cape2.alias) + " beat them up!\n"
            await cape1.lose(cape2)
            await cape2.win(cape1)
        elif cape2.state == 1:
            update += str(cape2.alias) + " ignored them.\n"
            await cape1.tie(cape2)
            await cape2.tie(cape1)
        elif cape2.state == 2:
            update += str(cape1.alias) + " beat them up!\n"
            await cape1.win(cape2)
            await cape2.lose(cape1)

    return update