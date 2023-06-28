# ABPackage/utils.py

import sys, os, argparse

tmp=1 
print("Importing utils module. f.p: ", __file__, ". tmp:", tmp)
tmp = tmp +1
# Global variable
gvar = 10

# Utility function
def utility_function():
    print("This is a utility function. gvar:", gvar)

color_codes = {
    "RESET": "\033[0m",
    "RED": "\033[31m",
    "GREEN": "\033[32m",
    "YELLOW": "\033[33m",
    "BLUE": "\033[34m",
    "MAGENTA": "\033[35m",
    "CYAN": "\033[36m"
}
def print_color(message, color):

    if color in color_codes:
        print(color_codes[color] + message + color_codes["RESET"])
    else:
        print("Invalid color specified")