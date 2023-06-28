###ways to run this file:
# 1. python path/r.py a
# 2. python -m   RI_Package.r  a
# 3. python -m   RI_Package.r  

import utils as u
#import a, b 

if __name__ == '__main__': ####if runing the file directly, need to append the package to path, so imports would work.
    script_dir = u.os.path.dirname(u.os.path.abspath(__file__))

    u.sys.path.append(u.os.path.join(script_dir, 'RI_Package'))
    #In the context of your example, if you have a file p.py located inside the RI_Package directory, using from . import a, b is the correct syntax because you are importing modules from within the same package. The dot (.) represents the current package (RI_Package).
    #On the other hand, from RI_Package import a, b would be used if you were importing modules from the RI_Package package from a different package or module outside of the RI_Package package.
    #from . import a, b




if __name__ == '__main__':
    print ("p.py is being run directly, file: ", __file__)
    u.print_color ("p.py is being run directly, RED", "RED")
    try: 
        if u.sys.argv[1] == 'a':
            a.a_func()
        elif sys.argv[1] == 'b':
            b.b_func()
        else:
            print("Invalid argument. Please specify 'a' or 'b'.")
    except IndexError:
        print("No argument provided. Please specify 'a' or 'b'.")