# This file deals with parsing text and removing semblances of non-alphanumeric characters.

def cleanText(text:str) -> str:
    cleanedText = ""
    for char in text:
        if char.isalnum() or char.isspace():
            cleanedText += char
    return cleanedText