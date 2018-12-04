import requests
import shelve
from time import sleep
from collections import defaultdict
from collections import OrderedDict
from bs4 import BeautifulSoup
from static import *

shelf = shelve.open("cache")

def get_champ(name):
    if name not in CHAMP_NAMES:
        return "Unable to find {}".format(name)
    
#    if shelf.has_key(name):
#        print "Already cached: " + name
#        return shelf[name]

    sleep(0.5)
    url = "http://champion.gg/champion/" + name
    r = requests.get(url + "?league=silver")
    page = BeautifulSoup(r.content)
    
    #print "Got this page {}".format(url)
    #print "Got this URL from request {}".format(r.url)
    #print page.text
    
    roles = []
    for roleText in page.select(".champion-profile ul li a h3"):
        roles.append(roleText.string.strip())
    
    if len(roles) < 1:
        print "--- Couldn't find {}".format(name)
        return
    
    data = defaultdict(dict)
    #print "Parsing {}".format(name)
    #data[roles[0]] = get_role(page)
    #print "Parsed {} {}".format(name, roles[0])
    
    #if len(roles) > :
    for role in roles[0:]:
        print "Parsing {} {}".format(name, role)
        page = BeautifulSoup(requests.get(url + "/" + role + "?league=silver").content)
        data[role] = get_role(page)
        print "Parsed {} {} {}".format(name, role, data[role])

    shelf[name] = dict(data)


    return dict(data)

def get_role(page):
    data = {}
    
    skills_columns = page.select(".champion-area") # .counter-column")
    if len(skills_columns) < 2:
        return data
        
    data['skills'] = get_skills(skills_columns[1]) # 0])
    
    data['starters'] = get_starters(page) # build_columns[1])
    data['build'] = get_build(page) # build_columns[0])
    
    return data

def get_skills(column):
    data = {}
    
    #print "get_skills {}".format(column)
    skill_orders = column.select(".skill-order")
    if len(skill_orders) < 1:
        return data
    
    mf_skills = parse_skill_order(skill_orders[0])
    mf_winrate = column.select(".build-text")[0].stripped_strings.next()
    data['frequent'] = {'order': mf_skills, 'win_rate': mf_winrate}
    
    hw_skills = parse_skill_order(column.select(".skill-order")[1])
    hw_winrate = column.select(".build-text")[1].stripped_strings.next()
    data['highest'] = {'order': hw_skills, 'win_rate': hw_winrate}

    return data

def parse_skill_order(el):
    selections = el.select(".skill-selections")
    row_labels = ["", "Q", "W", "E", "R"]
    
    data = {}
    for row_num in range(1, len(selections)):
        row = selections[row_num]
        label = row_labels[row_num]
        i = 1
        for div in row.find_all('div'):
            if 'selected' in div['class']:
                data[i] = label
            i += 1
    return "".join([str(x) for x in data.values()])

def get_starters(column):
    data = {}

    item_divs = column.select(".build-wrapper")

    # check how many item rows we have - if there are only two, just use those (better than nothing...)
    itemRows = len(item_divs)
    rowIndex = 2
    
    if itemRows == 2:
        rowIndex = 0

    mf_starters = parse_starters(item_divs[rowIndex])
    rowIndex = rowIndex + 1
    mf_winrate = column.select(".build-text")[0].stripped_strings.next()

    hw_starters = parse_starters(item_divs[rowIndex])
    hw_winrate = column.select(".build-text")[1].stripped_strings.next()

    #only add them both if they're not the same
    mf_str = str(mf_starters)
    hw_str = str(hw_starters)
    
    if mf_str != hw_str:
        data['frequent'] = {'items': mf_starters, 'win_rate': mf_winrate}
        
    data['highest'] = {'items': hw_starters, 'win_rate': hw_winrate}

    return data

def parse_starters(el):
    # use OrderedDict so the items come back in the correct order
    items = OrderedDict()
    for img in el.find_all('img'):
        src = img['src']
        src = src[src.rindex('/') + 1:]
        item_id = int(src[:src.index('.')])
        
        # always use potion instead of biscuit - the game will show the right thing based on masteries
        if item_id == 2010: # biscuit
            item_id = 2003  # health pot
        
        current = items.get(item_id, 0)
        items[item_id] = current + 1
    return items

def get_build(column):
    data = {}
    mf_build = parse_build(column.select(".build-wrapper")[0])
    mf_winrate = column.select(".build-text")[0].stripped_strings.next()
    data['frequent'] = {'items': mf_build, 'win_rate': mf_winrate}

    hw_build = parse_build(column.select(".build-wrapper")[1])
    hw_winrate = column.select(".build-text")[1].stripped_strings.next()
    data['highest'] = {'items': hw_build, 'win_rate': hw_winrate}
    
    return data

def parse_build(el):
    return [int(x) for x in parse_starters(el).keys()]

if __name__ == "__main__":
    
    getAll = True
    oneChamp = 'Lissandra'
    
    for champ in CHAMP_NAMES:
        if (getAll or (champ == oneChamp)):
            get_champ(champ)
    shelf.close()