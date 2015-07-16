import shelve
from static import *
import json
import os

shelf = shelve.open("cache")

patch = "5.13"

def parse_champ(name):
    if name not in CHAMP_NAMES:
        return "Unable to find {}".format(name)

    if not shelf.has_key(name):
        return "No data for {}".format(name)

    champ = shelf[name]
    if not os.path.exists("Champions/{}/Recommended".format(name)):
        os.makedirs("Champions/{}/Recommended/".format(name))

    for role in champ.keys():
        data = get_base(name, role)
        data['blocks'] += get_starters(champ[role]['starters'])
        data['blocks'] += get_build(champ[role]['skills'], champ[role]['build'])
        data['blocks'] += get_misc()
        print "Saving {} {}".format(name, role)
        with open("Champions/{}/Recommended/{}{}.json".format(name, role, patch.replace(".", "_")), "w+") as f:
            f.write(json.dumps(data))

    return True
        
def get_base(name, role):
    data = json.loads(BASE_ATTRS)
    data['title'] = "{} {} {}".format(name, role, patch)
    data['champion'] = name
    return data

def get_starters(s):
    res = []
    first = "true"

    for label in s.keys():
        d = s[label]

        block = {}
        block['type'] = "Start ({}) - {} win".format(label.title(), d['win_rate'])
        block['items'] = [{"count": v, "id": str(k)} for k,v in d['items'].iteritems()]

        # add the common items, but only to the first one
        if first == "true":
            first = "false"
            add_common_items(block['items'])
        
        res.append(block)

    return res

# add trinkets and wards for convenience
def add_common_items(items):
    maybe_append(items, "3340") # yellow
    maybe_append(items, "3341") # red
    maybe_append(items, "2044") # green
    maybe_append(items, "2043") # pink
    maybe_append(items, "2003") # health
    maybe_append(items, "2004") # mana
    return items

def maybe_append(items, item_id):
    found = False
    for item in items:
        if item['id'] == item_id:
            found = True
    
    if found == False:
        items.append({"count": 1, "id": item_id})

    return

def get_build(skills, s):

    freq_text = skills['frequent']['order']
    highest_text = skills['highest']['order']

    res = []

    for label in s.keys():
        d = s[label]

        block = {}
        
        if label == "frequent":
            text = freq_text
        else:
            text = highest_text
        
        block['type'] = "Build ({}) - {} win".format(label.title(), d['win_rate']) + " / Skills: " + text
        block['items'] = [{"count": 1, "id": str(k)} for k in d['items']]

        res.append(block)

    return res

def get_misc():
    first = {"type": "Trinkets and Consumables"}
    first['items'] = [
                      {"count": 1, "id": "3362"}, # upgrade yellow
                      {"count": 1, "id": "3364"}, # upgrade red
                      {"count": 1, "id": "3342"}, # blue
                      {"count": 1, "id": "3363"}, # upgrade blue
                      {"count": 1, "id": "2139"}, # Elixir of Sorcery
                      {"count": 1, "id": "2138"}, # Elixir of Iron
                      {"count": 1, "id": "2140"}  # Elixir of Wrath
                    ]

    return [first]

if __name__ == "__main__":
    for champ in CHAMP_NAMES:
        parse_champ(champ)
    shelf.close()