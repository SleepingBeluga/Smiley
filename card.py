class Card:
    def __init__(
        self,
        name,
        tier,
        civ,
        power,
        affiliation,
        alignment,
        classification,
        pc,
        campaign,
        submitter,
        tagline = ""
    ):
        self.name = name.strip()
        self.tier = tier.strip()
        self.civ = civ.strip()
        self.power = power.strip()
        self.affiliation = affiliation.strip()
        self.alignment = alignment.strip()
        self.classification = classification.strip()
        self.pc = pc.strip()
        self.campaign = campaign.strip()
        self.submitter = submitter.strip()
        self.tagline = tagline.strip()