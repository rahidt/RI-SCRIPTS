A = 10  # Global variable

def a_func():
    print("Executing a_func() in a.py")
    print("A =", A)

def a_method():
    print("Executing a_method() in a.py")

def main():
    print("Executing main() in a.py")
    a_func()
    a_method()

if __name__ == '__main__':
    main()
