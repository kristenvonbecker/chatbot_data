import re
from nltk.tokenize import sent_tokenize


# parse the aliases field into a list
def parse_aliases(text):
    list = text.split(",")
    while "" in list:
        list.remove("")
    return list


# Define exhibit location codes
def get_location_code(location):
    if location == 'This exhibit is not currently on view.':
        return 'NOT ON VIEW'
    elif 'Gallery' in location:
        for n in range(6):
            code = str(n)
            if 'Gallery ' + code in location:
                if 'Mezzanine' in location:
                    return 'Gallery ' + code + ' (Mezzanine)'
                elif 'Black Box' in location:
                    return 'Gallery ' + code + ' (Black Box)'
                elif 'Wattis Studio' in location:
                    return 'Gallery ' + code + ' (Studio)'
                else:
                    return 'Gallery ' + code
    elif 'Entrance' in location:
        return 'Entrance'
    elif 'Crossroads' in location:
        return 'Crossroads'
    elif 'Plaza' in location:
        return 'Plaza'
    elif 'Atrium' in location:
        return 'Atrium'
    elif 'Bay Walk' in location:
        return 'Bay Walk'
    elif 'jetty' in location.lower():
        return 'Jetty'


# Regex pattern for CSS? language drop-down element in description field
has_lang_settings = r"\.btn-language(.+)Language(\s+Español)?(\s+繁體中文)?(\s+Filipino)?"


def remove_lang_settings(text):
    lang_settings = re.match(has_lang_settings, text, flags=re.DOTALL)
    if lang_settings:
        proc_text = re.sub(lang_settings.group(0), "", text).strip()
    else:
        proc_text = text
    return proc_text


# Define regex patterns for parsing OpenAI completion responses

# text begins with a fragment (what appears to be a text completion?)
frag_start = r"^([a-z][^\n]*)"

# pattern for an itemization which has -hash marks, - spaced hash marks, 3. enumeration
# ending in a newline or EOF
item_pattern = r"(- *|\d. )?(.*?)(\n)*(?:$|\n)"

# pattern for non-alphanumeric tokens
non_alphanum = r"\W+"


# Check whether a token is composed of only non-alphanum chars
def is_non_alphanum(text):
    match = re.match(non_alphanum, text)
    if match:
        return True if match.group(0) == text else False
    else:
        return False


# Remove fragment start from a response
def remove_frag_start(text):
    proc_text = re.sub(frag_start, "", text).strip()
    return proc_text


# Find items in a response which forms a list or collection
def find_items(text, short=True):
    if short:
        item_list = text.split(",")
    else:
        item_list = [text]
    item_list = [item.strip() for item in item_list if item and not is_non_alphanum(item)]
    item_list_rev = []
    for item in item_list:
        sub_items = re.findall(item_pattern, item)
        sents = sent_tokenize(item)
        if sub_items:
            item_list_rev += [sub_item[1].strip() for sub_item in sub_items]
        elif len(sents) > 1:
            item_list_rev += [sent for sent in sents]
        else:
            item_list_rev.append(item)
    item_list = [item.strip() for item in item_list_rev if item]
    item_list = [item for item in item_list if not is_non_alphanum(item)]
    if short:
        item_list = [item for item in item_list if len(item) < 30]
    return item_list


# Process exhibit keywords
def process_keywords(existing_list, new_list):
    proc_list = existing_list + new_list
    unique_list = []
    unique_list = [x.lower() for x in proc_list if x.lower() not in unique_list]
    proc_list = unique_list
    return proc_list


# Parse byline entities into creators and years
def get_creators(entities):
    creators = [entity["name"] for entity in entities if entity["type"] == "PERSON"]
    return creators


def get_year(entities):
    years = [entity["name"] for entity in entities if entity["type"] in ["DATE", "NUMBER"]]
    year = int(years[0]) if years else None
    return year
