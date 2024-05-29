# This python script contains keyword-searching algorithms, given a keyword set
# This will serve as a benchmark, using non-ml models to do this
from typing import List, Any, Dict
from keyword_search import parse_helper as ph

# 
# We will use a dictionary data structure to store and update the keyword cluster(s) 

clusters = {}

def insertCluster(keywords:List[str], clusterName:str) -> None:
    clusters[clusterName] = []
    for keyword in keywords:
        clusters[clusterName].append(keyword.upper())
            
def updateCluster(keywords:List[str], clusterName:str) -> None:
    for keyword in keywords:
        clusters[clusterName].append(keyword.upper())
        
def printCluster(clusterName:str) -> None:
    print(f"Keywords in cluster {clusterName}:")
    print(clusters[clusterName])
    
#
# @description: This function takes in a text block, as well as a list of keywords
# @input: STR text block, LIST list of keywords
# @output: None
#
def matchKeywords(text: str, clustername) -> None:
    numMatch, matchedKeywords, matchDict = matchHelper(text, clustername)
    if numMatch >= 1:
        print(f"Number of keywords matched: {numMatch}")
        print(f"Matched keywords: {matchedKeywords}")
        print(f"Number of matches: {matchDict}")
    else:
        print("No keywords matched")
    return numMatch, matchedKeywords, matchDict

#
# @description: The main helper function
# @input: STR text block, LIST list of keywords
# @output: INT number of keywords matched, LIST matched keywords, DICT number of matches
# 
def matchHelper(text: str, clustername) -> tuple[int, List[str]]:
    text = ph.cleanText(text)
    keywords = clusters[clustername]
    numMatch = 0
    matchedKeywords = []
    matchDict = {}
    text = text.upper()
    for keyword in keywords:
        '''
        In order to prevent the string matching algorithm from matching words that are short/possible substrings like I, am, etc
        We simply add spaces to the beginning and end of the keyword
        We do the same for text under parse_helper's cleanText function
        '''
        keyword = " " + keyword + " "
        count = BooyerMooreCount(text, keyword)
        if count > 0:
            numMatch += count
            matchedKeywords.append(keyword)
            matchDict[keyword] = count
    return (numMatch, matchedKeywords, matchDict)

# 
# @description: the Booyer-Moore string matching algorithm
# @input: STR text, STR keyword
# @output: BOOL whether the keyword is found in the text
#
def BooyerMoore(text: str, kw: str) -> bool:
    charJump = computeCharJump(kw)
    matchJump = computeMatchJump(kw)
    m = len(kw)-1
    n = len(text)-1
    j = k = m
    while (j <= n):
        if kw[k] == text[j]:
            if k == 0:
                return True
            else:
                j -= 1
                k -= 1
        else:
            j += max(charJump[text[j]], matchJump[k])
            k = m
    return False

def computeCharJump(kw: str) -> Dict[str, int]:
    charJump = {}
    m = len(kw)
    for i in range(27):
        if i == 26:
            charJump[" "] = m
        else:
            charJump[chr(i+65)] = m
    for i in range(m):
        charJump[kw[i]] = m - i - 1
    return charJump

def computeMatchJump(kw: str) -> List[int]:
    matchJump = [0] * len(kw)
    m = len(kw)
    suffix = [0] * m
    suffix[m-1] = m
    g = m-1
    f = 0
    for i in range(m-2, -1, -1):
        if i > g and suffix[i + m - 1 - f] < i - g:
            suffix[i] = suffix[i + m - 1 - f]
        else:
            if i < g:
                g = i
            f = i
            while (g >= 0 and kw[g] == kw[g + m - 1 - f]):
                g -= 1
            suffix[i] = f - g
    for i in range(m):
        matchJump[i] = m - suffix[m-1]
    for i in range(m-1):
        matchJump[m - suffix[i] - 1] = m - i - 1
    return matchJump

def BooyerMooreCount(text: str, kw: str) -> bool:
    charJump = computeCharJump(kw)
    # matchJump = computeMatchJump(kw)
    # DEBUG
    # print(charJump)
    # print(matchJump)
    # print(f"Matching for {kw} in {text}...")
    m = len(kw)-1
    n = len(text)-1
    j = k = m
    count = 0
    while (j <= n):
        # DEBUG
        # print(f"on {count} iteration, comparing {kw[k]} {k} with {text[j]} {j}")
        if kw[k] == text[j]:
            if k == 0:
                count += 1
                k = m
                j = j + m + 1
                # print(f"Match found, count is {count}, new k is {k}, new j is {j}")
            else:
                j -= 1
                k -= 1
        else:
            #jump = max(charJump[text[j]], matchJump[k]) # original code, but we realise that on duplicates with spacing, matchJump is wonky - we resort to simple Boyer-Moore.
            jump = max(charJump[text[j]], m-k+1)
            j += jump
            # print(f"j jumps by {jump}")
            k = m
    return count

