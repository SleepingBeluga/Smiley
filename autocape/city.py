# The city is the highest level of the autocape, handling the iterative step
# process
from autocape.cape import Cape
import random

class City():

    def __init__(self, name, population, districtNum):
        self.name = name
        self.population = population
        self.districtNum = districtNum
        self.districts = []
        self.capes = []
        for x in range(0,districtNum):
            self.districts.append(District(x))
        self.teams = []
        capeNum = int(population / 8000)
        for z in range(0,5):
            self.addTeam(z)
        for y in range(0,capeNum):
            self.addCape(0)


    def addCape(self, newbie):
        if newbie == 0:
            cape = Cape(random.randint(0,10000),None)
        else:
            cape = newbie
        r = random.randint(0,(len(self.teams) - 1))
        x = self.teams[r]
        x.capes.append(cape)
        if x.indep == False:
            x.place.addCape(cape)
        else:
            num = random.randint(0, len(self.districts) - 1)
            self.districts[num].addCape(cape)
        self.capes.append(cape.alias)

    def addTeam(self,team):
        self.teams.append(Team(team,self))

    def info(self):
        layout = ""
        people = ""
        for x in range(0,self.districtNum):
            layout += "\t" + self.districts[x].name + "\n"
        for group in self.teams:
            people += "\t" + group.name + ":\n"
            for person in group.capes:
                people += "\t\t" + person.alias + "\n"
        return "```Name: " + self.name + \
                "\nPopulation: " + str(self.population) + \
                "\nDistricts: " + str(self.districtNum) + \
                "\n" + layout + \
                "Capes:" + "\n" + people + "```"

    def search(self, name):
        for team in self.teams:
            for cape in team.capes:
                if cape.alias == name:
                    return cape


class District:
    def __init__(self, num):
        if num == 0:
            self.ecoLevel = 1  # Rich
            self.name = 'Downtown'
        elif num == 1:
            self.ecoLevel = 2  # Medium
            self.name = 'Suburbs'
        elif num == 2:
            self.ecoLevel = 3  # Poor
            self.name = 'Outskirts'
        else:
            self.ecoLevel = random.randint(1,3)
            self.name = 'Random' + str(num)
        self.bases = []
        self.capes = []

    def info(self):
        desc = "```Name: " + self.name + "\n" + "Base(s): "
        if len(self.bases) != 0:
            for team in self.bases:
                desc += str(team.name) + ", "
            desc = desc[:-2]
        else:
            desc += "None"
        desc += "\n" + "Cape(s): "
        if len(self.capes) != 0:
            for cape in self.capes:
                desc += str(cape.alias) + ", "
            desc = desc[:-2]
        else:
            desc += "None"
        desc += "```"
        return desc


    def addTeam(self,team):
        self.bases.append(team)
        for cape in team.capes:
            self.addCape(cape)

    def addCape(self,cape):
        self.capes.append(cape)
        cape.locate(self)

    def removeCape(self,cape):
        check = False
        for capes in self.capes:
            if capes == cape:
                self.capes.remove(cape)
                check = True
        return check


class Team:
    def __init__(self,num,city):
        self.capes = []
        self.indep = False
        if num == 0:
            self.indep = True
            self.name = "Independents"
            self.place = None
        elif num == 1:
            self.name = "Protectorate"
            for district in city.districts:
                if district.name == "Downtown":
                    self.place = district
                    district.addTeam(self)
        elif num == 2:
            self.name = "Wards"
            for district in city.districts:
                if district.name == "Downtown":
                    self.place = district
                    district.addTeam(self)
        elif num == 3:
            self.name = "Villains"
            pick = random.randint(0,len(city.districts) - 1)
            self.place = city.districts[pick]
            city.districts[pick].addTeam(self)
        else:
            self.name = "Team" + str(num)
            pick = random.randint(0,len(city.districts) - 1)
            self.place = city.districts[pick]
            city.districts[pick].addTeam(self)

    def addcape(self, cape):
        self.capes.append(cape)
        if self.place != None:
            self.place.addCape(cape)

    def info(self):
        people = '```'
        people += "" + self.name + ":\n"
        for person in self.capes:
            people += "\t" + person.alias + "\n"
        people += '```'
        return people