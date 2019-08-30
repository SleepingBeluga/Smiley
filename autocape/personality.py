# Class to represent personality
import random

columns = ["Aggressive", "Assertive", "Passive", "Indirect"]

rows = [
  "Conflict", 
  "Course", 
  "Performance", 
  "Views", 
  "Feelings", 
  "Dream", 
  "Reactive"
]

personalities = [
  ["Angry",     "Brave",         "Cold",          "Vicious"],
  ["Wild",      "Adventurous",   "Detached",      "Distant"],
  ["Impulsive", "Creative",      "Ambitious",     "Unpredictable"],
  ["Critical",  "Stubborn",      "Diligent",      "Wary"],
  ["Harsh",     "Confident",     "Quiet",         "Joking"],
  ["Driven",    "Contemplative", "Introspective", "Devious"],
  ["Tough",     "Serious",       "Morose",        "Cagey"]
]

strengths = ['Brawn','Athletics','Dexterity','Wits','Social','Knowledge','Guts']

archetypes = [
    ['Champion','Lancer','Fury','Gladiator','Menace','Martial Artist','Titan'],
    ['Raider','Acrobat','Hunter','Stalker','Rider','Explorer','Interceptor'],
    ['Assassin','Rogue','Scoundrel','Marksman','Broker','Craftsman','Packrat'],
    ['Guard','Lookout','Hacker','Scout','Handler','Investigator','Sentinel'],
    ['Boss','Joker','Playboy','Psychologist','Politician','Manipulator','Believer'],
    ['Expert','Thwart','Knack','Schemer','Tactitian','Genius','Architect'],
    ['Juggernaut','Crusader','Support','Survivor','Stubborn','Dauntless','Indomitable']
]

class Personality():

    def __init__(self, power, dict):
        if dict == None:
            row = random.randrange(0,6)
            column = random.randrange(0,3)
            plus1 = random.randrange(0,6)
            plus2 = random.randrange(0,6)
            self.personality = personalities[row][column]
            self.row = rows[row]
            self.column = columns[column]
            self.archetype = archetypes[plus1][plus2]
            self.plus1 = strengths[plus1]
            self.plus2 = strengths[plus2]
        else:
            self.personality = dict['personality']
            self.row = dict['row']
            self.column = dict['col']
            self.archetype = dict['archetype']
            self.plus1 = dict['plus1']
            self.plus2 = dict['plus2']


    def perJsonDict(self):
        return {'personality':self.personality,'row':self.row,
                'col':self.column,'archetype':self.archetype,
                'plus1':self.plus1,'plus2':self.plus2}