class GunInfo:
    def __init__(self, type, stolen):
        self.type = str(type) if type is not None else None
        self.stolen = str(stolen) if stolen is not None else None

    def __repr__(self):
        return "{%r,%r}" % (self.type, self.stolen)