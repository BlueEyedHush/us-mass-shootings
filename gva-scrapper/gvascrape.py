from bs4 import BeautifulSoup
from gvaincident import GVAIncident
import requests
import sys
import jsonpickle

output_file = sys.argv[1]

##################################
#   WARNING:
#   after scrapp last comna in file should be deleted
##################################

def scrape(results, soup):
    table = soup.find("table")
    for row in table.find_all('tr')[1:]:
        col = row.find_all('td')

        date = col[0].string
        state = col[1].string
        city = col[2].string
        killed = col[4].string
        injured = col[5].string
        incident_url = col[6].ul.li.a.get('href')
        incident_id = incident_url[-6:]
        event_url = col[6].ul.li.findNext('li').a.get('href')

        record = GVAIncident(incident_id, date, state, city, killed, injured, event_url)
        json_object = jsonpickle.encode(record)
        # print json_object
        results.append(record)



def write_csv(results):
    target = open(output_file, 'a')
    for r in results:
        json_object = jsonpickle.encode(r)
        target.write(json_object)
        target.write(",\n")
    #     target.write(repr(r))
    #     target.write("\n")
    target.close()

def write_sring(results):
    target = open(output_file, 'a')
    for r in results:
        json_object = jsonpickle.encode(results)
        target.write(json_object)
        target.write(",\n")
    # target.write(repr(r))
    #     target.write("\n")
    target.close()


def main():
    sys.setrecursionlimit(10000)
    results = []
    base_url = 'http://www.gunviolencearchive.org'
    next_url = ''
    for year in range(2014, 2017 + 1):
        next_url = base_url + "/reports/mass-shooting" + "?year=" + str(year) #+ "&page=5"
        while next_url:
            print base_url + next_url
            next_page = requests.get(next_url)
            c = next_page.content
            soup = BeautifulSoup(c, "lxml")
            scrape(results, soup)
            next_url = soup.find('a', {'title': 'Go to next page'})
            if next_url:
                next_url = base_url + next_url.get('href')
            write_csv(results)
            results = []


if __name__ == "__main__":
    main()
