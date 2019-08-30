# Class to represent reputation

class Reputation():

    def __init__(self, personality):
        # Reputation is broken down into various areas
        # Each can go into the negative
        self.aggression = 0.0
        self.heroic = 0.0
        self.sane = 0.0
        self.leader = 0.0
        # Some elements of personality can affect starting reputation
        # Check across the columns
        if (str(personality.column) == "Agressive"):
            self.aggression += 0.2
        elif (str(personality.column) == "Passive"):
            self.aggression -= 0.2
        elif (str(personality.column) == "Assertive"):
            self.leader += 0.2
        # Let's check across the rows
        if (str(personality.row) == "Reactive"):
            self.sane += 0.2
        elif (str(personality.row) == "Performance"):
            self.sane -= 0.2
