#Gentry Atkinson
#gatkinso@stedwards.edu
#17 July, 2023

CAT_LIST_URL = 'http://www.wikicfp.com/cfp/allcat'
BASE_URL = 'http://www.wikicfp.com/cfp/call?conference='

from bs4 import BeautifulSoup
import urllib
import pandas as pd
import time

class Conference:
    def __init__(self, name: str, dates : str, location : str, deadline : str) -> None:
        self.name = name
        self.dates = dates
        self.location = location
        self.deadline = deadline


    def __str__(self) -> str:
        return f"{self.name}, {self.dates}, {self.location}, {self.deadline}\n"

if __name__ == '__main__':
    cat_page = urllib.request.urlopen(CAT_LIST_URL)
    cat_doc = BeautifulSoup(cat_page, 'html.parser')

    #print(cat_doc.prettify())

    links = cat_doc.find_all(['a'])

    categories = [l.text for l in links if 'conference' in str(l)]

    with open('categories.txt', 'w') as file:
        file.write('\n'.join(categories))
    
    conf_df = pd.DataFrame(columns=['Category', 'Acronym', 'Name', 'Location', 'Dates', 'Deadline'])
    idx = 0
    for cat in categories:
        #Get the number of pages in the category
        first_url = (BASE_URL+cat).replace(' ', '%20')
        first_page = urllib.request.urlopen(first_url)
        first_doc = BeautifulSoup(first_page, 'html.parser')
        last = first_doc.find('a', text='last')
        last = str(last).split('=')[-1][:-10]
        last = int(last)
        print(f"The {cat} category has {last} pages.")

        #For every page in category
        reached_expired = False
        for i in range(1, last+1):
            print(f"Page {i} of the {cat} category")
            list_url = (BASE_URL+cat+"&page=" + str(i)).replace(' ', '%20')
            list_page = urllib.request.urlopen(list_url)
            list_doc = BeautifulSoup(list_page, 'html.parser')
            table = list_doc.find('div', {'class':'contsec'})
            table = table.find('table')
            confs = table.find_all('tr')[6]
            rows = confs.find_all('tr')[1:]
            for j in range(0, len(rows)-1, 2):
                if rows[j].find('td').text == "Expired CFPs":
                    reached_expired = True 
                    break
                name = rows[j].find('td', {'colspan':'3'}).text
                acronym = rows[j].find('a').text
                data = rows[j+1].find_all('td')
                dates = data[0].text
                location = data[1].text
                deadline = data[2].text
                if acronym not in conf_df['Acronym']:
                    conf_df.loc[idx] = [cat, acronym, name, location, dates, deadline]
                    idx += 1
            if reached_expired:
                break
            time.sleep(0.1)
        
        
    conf_df.to_csv('conference_list.csv')
                
            
