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
* how to map names like first:John middle: Alexander, III, last: McMillan
* JoAnn Emerson vs. Jo Ann Emerson
* known issue with removing '-': Hon. Jackson-Lee, returns Jesse L. Jackson Jr. as top

https://raw.githubusercontent.com/unitedstates/congress-legislators/master/legislators-current.yaml
https://raw.githubusercontent.com/unitedstates/congress-legislators/master/legislators-historical.yaml
? https://raw.githubusercontent.com/unitedstates/congress-legislators/master/executive.yaml

TODO
use python-levenshtein package
filter by initials
consecutive parts of names
"""

import yaml
import re
from itertools import permutations
import unicodedata
# import Levenshtein

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
        middlename = True, \
        lastname = True, \
        suffix = True, \
        nickname = True):
    """ don't use this, replace accents with ascii instead """
    ret = set()
    for mb in members_list:
        for b,name in zip(\
                [firstname, middlename, lastname, suffix, nickname], \
                ['first', 'middle', 'last', 'suffix', 'nickname']):
            if (b) and (name in mb['name']):
                ret = ret.union(set(lower_name(mb['name'][name])))
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
        nickname = name_dict['nickname']
    return firstname, middlename, lastname, suffix, nickname 

def generate_bioguide_dict(members_list):
    ret = {}
    for member in members_list:
        bioguide = member['id']['bioguide']
        ret[bioguide] = member
    return ret

def month_iterator(start_year, start_month, end_year, end_month):
    """ returns a (year,month) tuple, end inclusive """
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
         value: dict key: bioguide \
                   value: (first, mid, last, suffix, nickname, \
                           first_lower, mid_lower, last_lower, suffix_lower, nickname_lower)
    names converted to lower-case, special symbol removed, to make search easier
    """
    for member in members_list:
        firstname, middlename, lastname, suffix, nickname = \
                get_names(member['name'])
        first_lower, mid_lower, last_lower, suf_lower, nick_lower = [\
                lower_name(nm) for nm in \
                [firstname, middlename, lastname, suffix, nickname]]
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
                members_index[(year, month)][member_bioguide] = member_tuple

def lower_name(s):
    t = str.lower(s)
    t = re.sub(r"[\-(),.`']", ' ', t)
    t = re.sub(r'  +', ' ', t)
    return unicodedata.normalize('NFKD',t.strip()).encode('ascii','ignore').decode()

def word_score(s1, s2):
    """
    if the first letter of s1 and s2 does not match, return 0
    otherwise calculate c --- the length of the longest common substring of
    s1[1:] and s2[1:], and return (1+c)/max(|s1|,|s2|) 
    """
    if s1[0] != s2[0]:
        return 0
    len_s1 = len(s1)
    len_s2 = len(s2)
    scores = [[0]*len_s2 for _ in range(len_s1)]
    # scores[i][j] is the best match of s1[1:i+1] and s2[1:j+1]
    for j in range(1,len_s2):
        for i in range(1,len_s1):
            scores[i][j] = 0
            if s1[i] == s2[j]: 
                scores[i][j] = max(scores[i][j], scores[i-1][j-1]+1)
            scores[i][j] = max(scores[i-1][j], scores[i][j-1], scores[i][j])
    return (1.0+scores[-1][-1]) / max(len_s1,len_s2)

def words_list_score(s1, s2):
    """
    if either s1 or s2 is empty return 0

    s1 and s2 are strings of words separated by single spaces
    returns s/max(|s1|,|s2|), where |s1| (and |s2|) are number
    of words in |s1| (and in |s2|, resp.), and s is the word matching
    that achieves the highest score
    """
    if (not s1.strip()) or (not s2.strip()):
        return 0
    ps = s1.strip().split(' ')
    lp = len(ps)
    ts = s2.strip().split(' ')
    lt = len(ts)
    scores = [[0.0]*(lt+1) for _ in range(lp+1)]
    # word_score = Levenshtein.jaro_winkler
    for i in range(1,lp+1):
        for j in range(1,lt+1):
            scores[i][j] = max(\
                    scores[i-1][j], \
                    scores[i][j-1], \
                    scores[i-1][j-1]+word_score(ps[i-1],ts[j-1]))
    return scores[-1][-1]/max(lt,lp)

def name_match(names, target, weights = (0.8,0.4,4,0.2,1)):
    """
    names is a tuple in the order first, middle, last, suffix, nickname
    target is a list of words
    """
    names_list = [(nm,w) for nm,w in zip(names,weights)]
    score = 0
    len_target = len(target)
    target_slices = [['']*(len_target+1) for _ in range(len_target)]
    for jp in range(len_target):
        for j in range(jp+1, len_target+1):
            if j == jp+1:
                target_slices[jp][j] = target[jp]
            else:
                target_slices[jp][j] = target_slices[jp][j-1] + ' ' + target[j-1]
    for perm in permutations(range(len(names_list))):
        scores = [[0]*(len_target+1) for _ in range(5+1)]
        for i in range(1,5+1):
            for j in range(1,len_target+1):
                tmp = [scores[i][j-1], scores[i-1][j]]
                for jp in range(j):
                    tmp.append(scores[i-1][jp] + \
                            names_list[perm[i-1]][1] * words_list_score(\
                            names_list[perm[i-1]][0],  target_slices[jp][j]))
                scores[i][j] = max(tmp)
        score = max(score, scores[-1][-1])
    return score

def search_by_name(name, arrival_date, departure_date, \
        members_index, charset = None, return_length = 5):
    """
    dates are assumed to be in m/d/yyyy format, and arrival<=departure
    the algorithm does the following preprocessing:
    1. convert name to lower case, same for charset if not None
    2. if charset is not None then first remove all char not in charset before the search
    then the algorithm checks every month between arrival and departure, and each consecutive
    sequence of up to word_count words to see if there is a matching last name
    returns a list of bioguide-id of all lastname in members_index that appears in name
    """
    name = unicodedata.normalize('NFKD',name.lower()).encode('ascii','ignore').decode()
    name = re.sub(r' +', ' ', name)
    if charset is not None:
        charset = set(c.lower() for c in charset)
        if '-' in charset:
            charset.remove('-')
            charset.add('\-')
        name = re.sub(r'[^{0}]'.format(''.join(c for c in charset)), ' ', name)
    else:
        name = re.sub(r'[^ a-zA-z]', ' ', name)
    name = re.sub(r'  +', ' ', name)
    name = name.strip()
    name = name.split(' ')
    arr_month, _, arr_year = [int(x) for x in arrival_date.split('/')]
    dep_month, _, dep_year = [int(x) for x in arrival_date.split('/')]
    ret = {}
    for year,month in month_iterator(arr_year, arr_month, dep_year, dep_month):
        if (year,month) in members_index:
            for bio, member_tuple in members_index[(year,month)].items():
                if bio not in ret:
                    initials = set()
                    for s in member_tuple[-5:]:
                        if s:
                            initials = initials.union(set([t[0] for t in s.split(' ')]))
                    name_f = [nm for nm in name if nm[0] in initials]
                    ret[bio] = name_match(member_tuple[-5:], name_f)
    retlist = [(k,v) for k,v in ret.items()]
    retlist = sorted(retlist, key=lambda x:-x[1])
    return retlist[:return_length]

def initialize():
    lcur = load_legislators('legislators-current.yaml')
    lhis = load_legislators('legislators-historical.yaml')
    members_list = lcur+lhis
    charset = get_charset(members_list)
    members_dict = generate_bioguide_dict(members_list)
    members_index = {}
    append_data(members_index, members_list)
    return charset, members_list, members_dict, members_index

def get_name_by_bioguide(bio, members_dict):
    try:
        if isinstance(bio, str):
            return members_dict[bio]['name']
        elif isinstance(bio, list):
            return [members_dict[b]['name'] for b in bio]
    except KeyError:
        return None

