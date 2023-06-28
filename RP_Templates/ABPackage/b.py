import  utils

B = 20  # Global variable specific to b.py

def b_func():
    print("Executing b_func() in b.py")
    print("B =", B)

def b_method():
    print("Executing b_method() in b.py")

def main():
    print("Executing main() in b.py")
    b_func()
    b_method()

if __name__ == '__main__':
    parser = utils.argparse.ArgumentParser()
    # Add arguments to the parser
    args = parser.parse_args()
    main()
