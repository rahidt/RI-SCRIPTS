import utils
A = 10  # Global variable

def a_func():
    global gvar
    print("Executing a_func() in a.py. gvar =", utils.gvar)
    print("A =", A)

def a_method():
    print("Executing a_method() in a.py, :")

def main():
    print("Executing main() in a.py, gvar =", gvar) 
    a_func()
    a_method()