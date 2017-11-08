class Participant:
    def __init__(self, status, ageGroup, name, relationship, gender, age, type):
        self.status = str(status) if status is not None else None
        self.ageGroup = str(ageGroup) if ageGroup is not None else None
        self.name = str(name) if name is not None else None
        self.relationship = str(relationship) if relationship is not None else None
        self.gender = str(gender) if gender is not None else None
        self.age = int(age) if age is not None else None
        self.type = str(type) if type is not None else None

    def __repr__(self):
        return "{%r,%r,%r,%r,%r,%r,%r}" % (self.status, self.ageGroup, self.name, self.relationship, self.gender, self.age, self.type)