# Encounter class for a fight
import random, re
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


async def talk(cape1, cape2):
    update = ''
    mod = random.randint(-2,2)
    past = cape1.history()
    if cape1.personality.plus1 == cape2.personality.plus1:
        mod += 3
    if cape1.personality.plus2 == cape2.personality.plus2:
        mod += 3
    if cape1.personality.plus1 == cape2.personality.plus2:
        mod += 2
    if cape1.personality.plus2 == cape2.personality.plus1:
        mod += 2
    if cape1.personality.archetype == cape2.personality.archetype:
        mod += 5
    if cape1.personality.personality == cape2.personality.personality:
        mod -= 3
    attacks = 'against ' + str(cape2.alias)
    talks = 'with ' + str(cape2.alias)
    count1 = past.count(attacks)
    count2 = past.count(talks)
    while count1 > 0:
        mod -= 2
        print('check1')
        count1 -= 1
    while count2 > 0:
        mod += 2
        print('check2')
        count2 -= 1
    await cape1.talkswith(cape2,mod)
    await cape2.talkswith(cape1,mod)
    update += str(cape1.alias) + " talked with " + str(cape2.alias) + " - "
    if mod >= 5:
        update += "It was great!\n"
    elif mod >= 3:
        update += "It was nice.\n"
    elif mod > 0:
        update += "It went okay.\n"
    elif mod > -2:
        update += "It was a little awkward.\n"
    elif mod < -5:
        update += "It was awful.\n"
    elif mod < -2:
        update += "It was very awkward.\n"
    update += str(mod)
    return update