# Class to represent a cape
import random, json, ac
from autocape import sheets
from autocape.personality import Personality
from autocape.power import Power
from autocape.reputation import Reputation


class Cape:

    # This class can be inherited by different possible powers and the base
    # abilities overriden

    def __init__(self, id, dict):
        if dict == None:
            self.name = sheets.name()
            self.alias = sheets.capename()
            self.generateStatblock()
            # Start the game at basic morale level, can scale from 0.0 and up
            self.morale = 1.0
            self.generatePower()
            self.generatePersonality()
            self.reputation = Reputation(self.personality)
            self.state = random.randint(0, 2)
            self.location = None
            self.playerName = None
            self.pc = False
            self.id = id
            self.relations = {}
            self.bff = 'None'
            self.nemesis = 'None'
            self.logs = ''
            # There is extra stuff to consider, but we can worry about that later
        else:
            self.name = dict['name']
            self.alias = dict['alias']
            self.generateStatblock()
            self.morale = 1.0
            self.power = Power(dict['power'])
            self.personality = Personality(self.power,dict['personality'])
            self.reputation = Reputation(self.personality)
            self.state = random.randint(0,2)
            self.location = dict['location']
            self.playerName = dict['shard']
            self.pc = dict['pc']
            self.id = dict['id']
            self.relations = dict['relations']
            self.bff = dict['bff']
            self.nemesis = dict['nemesis']
            self.logs = dict['logs']

    def generateStatblock(self):
        # Initialize everything to default 3 value
        self.statblock = [
            3.0,  # Brawn
            3.0,  # Athletics
            3.0,  # Dexterity
            3.0,  # Wits
            3.0,  # Social
            3.0,  # Knowledge
            3.0  # Guts
        ]
        # Strengths can be doubled up on the same thing!
        strength1 = random.randrange(0, 6)
        strength2 = random.randrange(0, 5)
        if (strength2 >= strength1):
            strength2 += 1

        weakness = random.randrange(0, 4)
        if (weakness >= strength1):
            weakness += 1
        if (weakness >= strength2):
            weakness += 1

        # Now shift up and down the stats based on strength/weakness
        self.statblock[strength1] += 1.0
        self.statblock[strength2] += 1.0
        self.statblock[weakness] -= 1.0

    def generatePower(self):
        # We need to decide what the power is going to be, and how we represent
        # that information
        self.power = Power(None)

    def generatePersonality(self):
        # It is likely that the personality and power mesh in some way
        # There is likely to be some extraction of stats from the power that
        # go into the personality (or vice versa)
        self.personality = Personality(self.power,None)

    def status(self):
        status = "Name: " + str(self.name) + "\n"
        if self.pc == True:
            status += "Shard: " + self.playerName + "\n"
        status += "Alias: " + str(self.alias) + "\n" + \
               "Personality: " + str(self.personality.personality) + "\n" + \
                "Archetype: " + str(self.personality.archetype) + "\n" + \
               "Power: " + str(self.power.category.categoryName) + " power with " + \
               str(self.power.aspects[0].aspectName) + " and " + \
               str(self.power.aspects[1].aspectName) + " aspects"
        if self.location != None:
            status += "\nLocation: " + str(self.location.name)
        if self.bff != 'None':
            status += "\nBestie: " + self.bff
        if self.nemesis != 'None':
            status += "\nNemesis: " + self.nemesis
        return status

    def history(self):
        if self.logs == '':
            return "No history."
        else:
            return self.logs

    # This should not be accessible by the users, it is here for debugging
    def abilities(self):
        return "Hitpoints Max: " + str(self.hitpoints()) + "\n" + \
               "Dodge Ability: " + str(self.dodge()) + "\n" + \
               "Initiative Ability: " + str(self.initiative()) + "\n" + \
               "Tactics Ability: " + str(self.tactics()) + "\n" + \
               "Willpower Ability: " + str(self.willpower()) + "\n" + \
               "Accuracy Ability: " + str(self.accuracy())

    def hitpoints(self):
        return round((
                self.brawn() * 0.35 +
                self.athletics() * 0.15 +
                self.guts() * 0.5
        ), 2)

    def dodge(self):
        return round((
                self.athletics() * 0.5 +
                self.dexterity() * 0.35 +
                self.wits() * 0.15
        ), 2)

    def initiative(self):
        return round((
                self.athletics() * 0.15 +
                self.dexterity() * 0.35 +
                self.wits() * 0.5
        ), 2)

    def tactics(self):
        return round((
                self.wits() * 0.35 +
                self.social() * 0.15 +
                self.knowledge() * 0.5
        ), 2)

    def willpower(self):
        return round((
                self.social() * 0.15 +
                self.knowledge() * 0.35 +
                self.guts() * 0.5
        ), 2)

    def accuracy(self):
        return round((
                self.dexterity() * 0.75 +
                self.wits() * 0.25
        ), 2)

    # Stat values are decided by their integer value, with morale sliding the
    # probability of rounding up around
    def stat(self, index):
        intvalue = int(self.statblock[index])
        decimal = self.statblock[index] - intvalue
        if (decimal == 0.0):
            return intvalue
        elif (random.randrange(0, 99) * self.morale > decimal * 100):
            return intvalue + 1
        else:
            return intvalue

    def brawn(self):
        return self.stat(0)

    def athletics(self):
        return self.stat(1)

    def dexterity(self):
        return self.stat(2)

    def wits(self):
        return self.stat(3)

    def social(self):
        return self.stat(4)

    def knowledge(self):
        return self.stat(5)

    def guts(self):
        return self.stat(6)

    # Morale can be shifted by positive or negative
    def moraleShift(self, shift):
        if (shift < 0 and self.morale + shift < 0):
            self.morale = 0.0
        else:
            self.morale += shift

    def decide(self, fight):
        grabBag = [0,1,2]
        if self.personality.plus1 == "Brawn" or self.personality.plus1 == "Dexterity":
            grabBag.append(2)
        if self.personality.plus2 == "Brawn" or self.personality.plus2 == "Dexterity":
            grabBag.append(2)
        if self.personality.column == "Aggressive":
            grabBag.append(2)
        if self.personality.plus1 == "Guts" or self.personality.plus1 == "Athletics":
            grabBag.append(1)
        if self.personality.plus2 == "Guts" or self.personality.plus2 == "Athletics":
            grabBag.append(1)
        if self.personality.column == "Assertive":
            grabBag.append(1)
        if self.personality.plus1 == "Knowledge" or self.personality.plus1 == "Wits":
            grabBag.append(0)
        if self.personality.plus2 == "Knowledge" or self.personality.plus2 == "Wits":
            grabBag.append(0)
        if self.personality.column == "Indirect":
            grabBag.append(0)
        if fight == False:
            grabBag.append(3)
            if self.personality.plus1 == "Social":
                grabBag.append(3)
            if self.personality.plus2 == "Social":
                grabBag.append(3)
            if self.personality.column == "Passive":
                grabBag.append(3)
        num = random.randint(0,(len(grabBag) - 1))
        choice = grabBag[num]
        self.state = choice

    def locate(self, place):
        self.location = place

    def givePlayer(self, name):
        self.playerName = name

    def jsonDict(self):
        return {'id':self.id,'name':self.name, 'shard':self.playerName,
                'alias':self.alias,'personality':self.personality.perJsonDict(),
                'power':self.power.powJsonDict(),'location':self.location,'pc':self.pc,
                'relations':self.relations,'bff':self.bff,'nemesis':self.nemesis,'logs':self.logs}

    async def win(self, loser):
        if self.state == 0:
            self.logs += "Plotted against " + str(loser.alias) + " - Won.\n"
        elif self.state == 1:
            self.logs += "Defended against " + str(loser.alias) + " - Won.\n"
        elif self.state == 2:
            self.logs += "Fought against " + str(loser.alias) + " - Won.\n"
        await self.updateCape()

    async def lose(self, winner):
        if self.state == 0:
            self.logs += "Plotted against " + str(winner.alias) + " - Lost.\n"
        elif self.state == 1:
            self.logs += "Defended against " + str(winner.alias) + " - Lost.\n"
        elif self.state == 2:
            self.logs += "Fought against " + str(winner.alias) + " - Lost.\n"
        await self.updateCape()

    async def tie(self, other):
        if self.state == 0:
            self.logs += "Plotted against " + str(other.alias) + " - Tied.\n"
        elif self.state == 1:
            self.logs += "Defended against " + str(other.alias) + " - Tied.\n"
        elif self.state == 2:
            self.logs += "Fought against " + str(other.alias) + " - Tied.\n"
        await self.updateCape()

    async def updateCape(self):
        capes = await ac.loadcapes()
        entry = self.jsonDict()
        capes[self.id] = entry
        with open('autocape/capes.json', 'w+') as capefile:
            json.dump(capes, capefile)

    async def talkswith(self, cape, mod):
        if cape.name not in self.relations:
            self.relations[cape.name] = 0
        self.relations[cape.name] += mod
        self.logs += "Talked with " + str(cape.alias) + " - "
        if mod >= 5:
            self.logs += "It was great!\n"
        elif mod >= 3:
            self.logs += "It was nice.\n"
        elif mod > 0:
            self.logs += "It went okay.\n"
        elif mod > -2:
            self.logs += "It was a little awkward.\n"
        elif mod < -5:
            self.logs += "It was awful.\n"
        elif mod < -2:
            self.logs += "It was very awkward.\n"
        await self.updateCape()