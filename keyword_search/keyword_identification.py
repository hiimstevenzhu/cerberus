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
        splitKeyword = keyword.split()
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
    return

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
    splitText = text.upper().split()
    for keyword in keywords:
        for word in splitText:
            if keyword == word:
                numMatch += 1
                matchedKeywords.append(keyword)
                if keyword in matchDict:
                    matchDict[keyword] += 1
                else:
                    matchDict[keyword] = 1
    return (numMatch, matchedKeywords, matchDict)

# 
# @description: the Booyer-Moore string matching algorithm
# @input: STR text, STR keyword
# @output: BOOL whether the keyword is found in the text
#
def BooyerMoore(text: str, kw: str) -> bool:
    # for consideration
    return


