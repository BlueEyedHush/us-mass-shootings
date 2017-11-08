from bs4 import BeautifulSoup
from datetime import datetime
from GunInfo import GunInfo
from Participant import Participant
import requests

testSet = set()

class GVAIncident:
    note = None
    characteristics = None
    participants = []

    def __init__(self, iid, date, state, city, no_k, no_i, event_url):
        print("http://gunviolencearchive.org/incident/" + iid)
        self.participants = []
        self.guns = []
        self.iid = iid
        self.date = self.format_date(date)
        self.state = str(state)
        self.city = str(city)
        self.no_k = int(no_k)
        self.no_i = int(no_i)
        self.incident_url = "http://gunviolencearchive.org/incident/" + iid
        result = requests.get(self.incident_url)
        self.event_url = str(event_url)
        self.lat, self.long = self.locate(result=result)
        self.scrapDetails(result=result)


    @staticmethod
    def title():
        return "id^date^state^city^killed^injured^incident_url^event_url^lat^long^note^guns^incident_characteristics^participants"

    def __repr__(self):
        return "%r^%r^%r^%r^%r^%r^%r^%r^%r^%r^%r^%r^%r^%r" % (
        self.iid, self.date, self.state, self.city, self.no_k, self.no_i, self.incident_url, self.event_url, self.lat,
        self.long, self.note, self.guns, self.characteristics, self.participants)

    def format_date(self, date):
        d = datetime.strptime(date, "%B %d, %Y")
        return datetime.strftime(d, "%Y-%m-%d")

    def scrapDetails(self, result):
        c = result.content
        soup = BeautifulSoup(c)

        incidentData = soup.find(class_="block block-system")

        if incidentData is None:
            print("Error - Incident data is None")

        if incidentData is not None:
            for paragraphTitle in incidentData.find_all("h2"):
                if paragraphTitle.string == "District":
                    continue
                elif paragraphTitle.string == "Sources":
                    continue
                elif paragraphTitle.string == "Guns Involved":
                    gunsList = paragraphTitle.parent.find_all("ul")
                    for gun in gunsList:
                        type = None
                        stolen = None

                        gunsData = gun.find_all("li")
                        for row in gunsData:
                            if row.string.startswith("Type:"):
                                type = row.string[6:]
                            elif row.string.startswith("Stolen:"):
                                stolen = row.string[8:]
                            else:
                                print("Error - Unhandled Gun Type: " + row.string)
                                continue
                        self.guns.append(GunInfo(type=type, stolen=stolen))
                elif paragraphTitle.string == "Participants":
                    people = paragraphTitle.parent.find_all("ul")
                    for person in people:
                        info = person.find_all("li")

                        status = None
                        ageGroup = None
                        name = None
                        relationship = None
                        gender = None
                        age = None
                        type = None

                        for row in info:
                            if row.string.startswith("Status:"):
                                status = row.string[8:]
                            elif row.string.startswith("Age Group:"):
                                ageGroup = row.string[11:]
                            elif "Name:" in str(row):
                                name = str(row)[4: -5]
                            elif row.string.startswith("Relationship:"):
                                relationship = row.string[14:]
                            elif row.string.startswith("Gender:"):
                                gender = row.string[8:]
                            elif row.string.startswith("Age:"):
                                age = row.string[5:]
                            elif row.string.startswith("Type:"):
                                type = row.string[6:]
                            else:
                                print("Error - Unhandled Participant Type: " + row.string)
                                continue
                        self.participants.append(Participant(status=status, ageGroup=ageGroup, name=name, relationship=relationship, gender=gender, age=age, type=type))
                elif paragraphTitle.string == "Location":
                    continue
                elif paragraphTitle.string == "Incident Characteristics":
                    characteristics = paragraphTitle.parent.find("ul").find_all("li")
                    self.characteristics = []
                    for row in characteristics:
                        self.characteristics.append(str(row.string))
                elif paragraphTitle.string == "Notes":
                    note = paragraphTitle.parent.find("p")
                    if note is not None:
                        self.note = str(note)[3:-4]
                    continue
                else:
                    print("Error - Unhandled Patagraph Title: " + paragraphTitle.string)


    def locate(self, result):
        c = result.content
        soup = BeautifulSoup(c)

        span = soup.find_all("span")
        spans = []
        for x in span:
            spans.append(x.string)

        found = False
        for y in spans:
            if y and y.startswith('Geolocation'):
                found = True
                latlong = y[13:]
                return [float(z.strip()) for z in latlong.split(',')]
        if not found:
            return [0, 0]
