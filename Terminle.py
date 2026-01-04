# Terminle.py V1.1
# A script to play wordle in the terminal
# Interfaces with nytimes.com to fetch today's word
# Colour support with guess history and letter information
# Allowed words are loaded from a file (words.xz)

import lzma, os, json
import requests
from datetime import datetime

TODAY = datetime.today().strftime('%Y-%m-%d')
HUMAN_DATE = datetime.today().strftime('%d/%m/%Y')

API_URL = f"https://www.nytimes.com/svc/wordle/v2/{TODAY}.json"

WORDS_FILE = "words.xz"
SAVE_FILE = "save.json"

BLANK_SAVE = {
    "completed": "1970-01-01",
    "played": 0,
    "won": 0,
    "lost": 0,
    "winTurn": {
        "1": 0,
        "2": 0,
        "3": 0,
        "4": 0,
        "5": 0,
        "6": 0
    }
}

# Colours
DEFAULT = "\033[0m"
GREY = "\033[100m\033[37m"
YELLOW = "\033[43m\033[30m"
GREEN = "\033[102m\033[30m"

solution = ""
puzzleId = 0
stats = None

validWords = set()

guessHistory = []

letterStatus = {
    "A": -1, "B": -1, "C": -1, "D": -1, "E": -1, "F": -1,
    "G": -1, "H": -1, "I": -1, "J": -1, "K": -1, "L": -1,
    "M": -1, "N": -1, "O": -1, "P": -1, "Q": -1, "R": -1,
    "S": -1, "T": -1, "U": -1, "V": -1, "W": -1, "X": -1,
    "Y": -1, "Z": -1
    }

# Title Screen
startMenu = r"""
########################################################################################################################
#                                                                                                                      #
#                                         ______                    _       __                                         #
#                                        /_  __/__  _________ ___  (_)___  / /__                                       #
#                                         / / / _ \/ ___/ __ `__ \/ / __ \/ / _ \                                      #
#                                        / / /  __/ /  / / / / / / / / / / /  __/                                      #
#                                       /_/  \___/_/  /_/ /_/ /_/_/_/ /_/_/\___/                                       #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                        Get 6 Chances To Guess A 5-Letter Word                                        #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                 Press ENTER To Start                                                 #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                  © 2025- Oliver2081                                                  #
#                                                                                                                      #
########################################################################################################################
"""

# Function
def fetchData():
    response = requests.get(API_URL)
    data = response.json()

    word = data.get("solution").upper()
    puzzleId = data.get("days_since_launch")

    return word, puzzleId

def loadValidWords():
    with open(WORDS_FILE, "rb") as f:
        data = lzma.decompress(f.read())
    
    words = data.decode().splitlines()
    words = {w.upper() for w in words}

    return words

def checkGuess(guess, solution):
    guess = guess.upper()
    wordStatus = [None] * 5

    for pos, letter in enumerate(guess):
        # Letter is not in word
        if letter not in solution:
            letterStatus[letter] = 0
            wordStatus[pos] = 0

        # Letter is in word, but in wrong place
        elif (letter in solution) and (solution[pos] != letter):
            letterStatus[letter] = 1
            wordStatus[pos] = 1
        
        # Letter is in correct place
        elif (letter in solution) and (solution[pos] == letter):
            letterStatus[letter] = 2
            wordStatus[pos] = 2
    
    return wordStatus

def printLetters(letterStatus):
    outString = ""
    for i, letter in enumerate(letterStatus.keys()):
        if letterStatus[letter] == 0:
            outString += f"{GREY}{letter}{DEFAULT} "
        elif letterStatus[letter] == 1:
            outString += f"{YELLOW}{letter}{DEFAULT} "
        elif letterStatus[letter] == 2:
            outString += f"{GREEN}{letter}{DEFAULT} "
        else:
            outString += f"{letter} "
    
    print(outString + "\n")

def printGuessHistory(guessHistory):
    outString = ""
    
    for entry in guessHistory:
        word = entry[0]
        colours = entry[1]

        for letter in range(5):
            if colours[letter] == 0:
                outString += f"{GREY}{word[letter]}{DEFAULT}"
            elif colours[letter] == 1:
                outString += f"{YELLOW}{word[letter]}{DEFAULT}"
            elif colours[letter] == 2:
                outString += f"{GREEN}{word[letter]}{DEFAULT}"
            else:
                outString += f"{word[letter]}"

        outString += "\n"

    print(outString + "\n")


def getStats():
    # Create file if it does not exist
    if not os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "w") as f:
            json.dump(BLANK_SAVE, f, indent=4)

    # Else read it from the file
    else:
        with open(SAVE_FILE, "r") as f:
            return json.load(f)

def saveStats(stats):
        with open(SAVE_FILE, "w") as f:
            json.dump(stats, f, indent=4)
    

def printStats(stats):
    print("\nStats:")
    print(f"    Total Games Played:    {stats["played"]}")
    print(f"    Win %:                 {round((stats["won"] / stats["played"]) * 100)}%")
    print(f"    Games Won:             {stats["won"]}")
    print(f"    Games Lost:            {stats["lost"]}")
    print(f"\n    Guess Distribution:")
    for turn in range(6):
        print(f"        {turn + 1}: {stats["winTurn"][str(turn + 1)]}")


def clearScreen():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

# Main App
solution, puzzleId = fetchData()
validWords = loadValidWords()
stats = getStats()

# Title Screen
clearScreen()
input(startMenu)

clearScreen()
print("\nTerminle\n")

printLetters(letterStatus)


for turn in range(6):
    while True:
        guess = input(f"Guess {turn + 1}: ").upper()

        if len(guess) != 5:
            print("Word Must Be 5 Letters Long")

        elif not guess.isalpha():
            print("Word Must Only Contain Letters")

        elif guess not in validWords:
            print("Word Not Recognised")
        else:
            break
    
    wordStatus = checkGuess(guess, solution)
    guessHistory.append([guess, wordStatus])

    
                
    clearScreen()
    print("\nTerminle\n")
    printLetters(letterStatus)
    printGuessHistory(guessHistory)

    # Check if game is won
    if wordStatus == [2, 2, 2, 2, 2]:
        print("Congratulations!")
        print(f"You have beaten today's terminle in {turn + 1} guesses")

        # Update stats
        if stats["completed"] != TODAY:

            stats["completed"] = TODAY
            stats["played"] += 1
            stats["won"] += 1
            stats["winTurn"][str(turn + 1)] += 1
        
        saveStats(stats)
        printStats(stats)

        input()
        exit(0)


print(f"Today's answer was: {solution}")
print("Better luck next time")

# Update Stats
if stats["completed"] != TODAY:
    
    stats["completed"] = TODAY
    stats["played"] += 1
    stats["lost"] += 1

saveStats(stats)
printStats(stats)

input()
