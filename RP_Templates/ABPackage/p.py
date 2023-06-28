###ways to run this file:
# 1. python path/p.py a
# 2. python -m   ABPackage.p  a
# 3. python -m   ABPackage.p  

import utils as u
import a, b 

if __name__ == '__main__': ####if runing the file directly, need to append the package to path, so imports would work.
    script_dir = u.os.path.dirname(u.os.path.abspath(__file__))

    u.sys.path.append(u.os.path.join(script_dir, 'ABPackage'))
    #In the context of your example, if you have a file p.py located inside the ABPackage directory, using from . import a, b is the correct syntax because you are importing modules from within the same package. The dot (.) represents the current package (ABPackage).
    #On the other hand, from ABPackage import a, b would be used if you were importing modules from the ABPackage package from a different package or module outside of the ABPackage package.
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