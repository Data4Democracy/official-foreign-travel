"""
* these are probably names with the most commas
  * Hon. John R. Kuhl, Jr., CODEL led by
  * Pearre, Robert H., Jr
* there are also nicknames in ``''
* 30579  Revised figures for Hon. George
* 44600                -Hon. Todd Tiahrt
* sometimes Hon, or Hon instead of Hon
df.loc[(df['name'].notnull()) & (df['name'].str.contains('Hon')) & (df['name'].str.startswith('Hon.')==0)]
* 36449              Hon C.W. Bill Young, the official name is first:C., mid:W. Bill, last: Young
* in official last names, max number of words seems to be 3
* currently some dates are not parsed correctly
pd.to_datetime(df['arrival_date'], errors='coerce').isnull()
1408                        Hon. Dave Reichert    2/29/2007       2/9/2007   
* how to deal with names with -?

https://raw.githubusercontent.com/unitedstates/congress-legislators/master/legislators-current.yaml
https://raw.githubusercontent.com/unitedstates/congress-legislators/master/legislators-historical.yaml
? https://raw.githubusercontent.com/unitedstates/congress-legislators/master/executive.yaml
"""

# TODO number of words in a name

import yaml
import re

def load_legislators(filename):
    with open(filename) as f:
        return yaml.load(f.read())

def check_bioguide(members_list):
    """ 
    check that all records has bioguide id 
    prints out those that don't
    """
    flag = True
    for x in members_list:
        try:
            _ = x['id']['bioguide']
        except KeyError:
            print(x)
            flag = False
    return flag

def get_charset(\
        members_list, \
        firstname = True, \
        middlename = False, \
        lastname = True, \
        suffix = True, \
        nickname = False):
    ret = set()
    for mb in members_list:
        for b,name in zip(\
                [firstname, middlename, lastname, suffix, nickname], \
                ['first', 'middle', 'last', 'suffix', 'nickname']):
            if (b) and (name in mb['name']):
                ret = ret.union(set(mb['name'][name]))
    return ret

def get_names(name_dict):
    firstname, middlename, lastname, suffix, nickname = '', '', '', '', ''
    if 'first' in name_dict:
        firstname = name_dict['first']
    if 'last' in name_dict:
        lastname = name_dict['last']
    if 'middle' in name_dict:
        middlename = name_dict['middle']
    if 'suffix' in name_dict:
        suffix = name_dict['suffix']
    if 'nickname' in name_dict:
        suffix = name_dict['nickname']
    return firstname, middlename, lastname, suffix, nickname 

def generate_bioguide_dict(members_list):
    ret = {}
    for member in members_list:
        bioguide = member['id']['bioguide']
        # assert(bioguide not in ret)
        ret[bioguide] = member
    return ret

def month_iterator(start_year, start_month, end_year, end_month):
    """ returns a (year,month) tuple, end inclusive """
    assert((1<=start_month) and (start_month<=12))
    year, month = start_year, start_month
    while (year<end_year) or ((year==end_year) and (month<=end_month)):
        yield (year,month)
        month += 1
        if month > 12:
            month = 1
            year += 1

def append_data(members_index, members_list):
    """
    members_index 
           key: (year, month)
         value: dict   key lastname_lower
                     value dict bioguide -> \
                             -> (first, mid, last, suffix, nickname, \
                             first_lower, mid_lower, last_lower, suffix_lower, nickname_lower)
    names converted to lower-case to make search easier
    """
    for member in members_list:
        firstname, middlename, lastname, suffix, nickname = get_names(member['name'])
        first_lower, mid_lower, last_lower, suf_lower, nick_lower = [\
                str.lower(nm) for nm in [firstname, middlename, lastname, suffix, nickname]]
        member_tuple = (firstname, middlename, lastname, suffix, nickname, \
                first_lower, mid_lower, last_lower, suf_lower, nick_lower)
        member_bioguide = member['id']['bioguide']
        for term in member['terms']:
            term_start = term['start'].split('-')
            term_end = term['end'].split('-')
            start_year, start_month = int(term_start[0]), int(term_start[1])
            end_year, end_month = int(term_end[0]), int(term_end[1])
            for year,month in month_iterator(start_year, start_month, end_year, end_month):
                if (year, month) not in members_index:
                    members_index[(year, month)] = {}
                if last_lower not in members_index[(year, month)]:
                    members_index[(year, month)][last_lower] = {}
                members_index[(year, month)][last_lower][member_bioguide] = member_tuple

def name_search(name, arrival_date, departure_date, members_index, charset = None, word_count = 3):
    """
    dates are assumed to be in m/d/yyyy format, and arrival<=departure
    the algorithm does the following preprocessing:
    1. convert name to lower case, same for charset if not None
    2. if charset is not None then first remove all char not in charset before the search
    then the algorithm checks every month between arrival and departure, and each consecutive
    sequence of up to word_count words to see if there is a matching last name
    returns a list of bioguide-id of all lastname in members_index that appears in name
    """
    name = name.lower()
    name = re.sub(r' +', ' ', name)
    if charset is not None:
        charset = set(c.lower() for c in charset)
        name = re.sub(r'[^{0}]'.format(''.join(c for c in charset)), '', name)
    name = name.split(' ')
    arr_month, _, arr_year = [int(x) for x in arrival_date.split('/')]
    dep_month, _, dep_year = [int(x) for x in arrival_date.split('/')]
    ret = []
    for year,month in month_iterator(arr_year, arr_month, dep_year, dep_month):
        if (year,month) in members_index:
            for wl in range(1, word_count+1):
                for i in range(0, len(name)-wl+1):
                    sn = ' '.join(name[i:i+wl])
                    if sn in members_index[(year,month)]:
                        for bio in members_index[(year,month)][sn]:
                            if bio not in ret:
                                ret.append(bio)
    return ret

