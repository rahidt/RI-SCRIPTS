###ways to run this file:
# 1. python path/r.py a
# 2. python -m   RI_Package.r  a
# 3. python -m   RI_Package.r  

import utils as u
import argparse

#import a, b 

if __name__ == '__main__': ####if runing the file directly, need to append the package to path, so imports would work.
    script_dir = u.os.path.dirname(u.os.path.abspath(__file__))

    u.sys.path.append(u.os.path.join(script_dir, 'RI_Package'))
    #In the context of your example, if you have a file p.py located inside the RI_Package directory, using from . import a, b is the correct syntax because you are importing modules from within the same package. The dot (.) represents the current package (RI_Package).
    #On the other hand, from RI_Package import a, b would be used if you were importing modules from the RI_Package package from a different package or module outside of the RI_Package package.
    #from . import a, b

run_dir = None
log_file = None
debug_level = 0

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--run_dir', help='Run directory')
    parser.add_argument('-l', '--log_file', help='Log file')
    parser.add_argument('-debug', type=int, help='Debug level')

    print("script activated, received next sys.argv: ", u.sys.argv)
    u.print_color("script activated, received next sys.argv" + str(u.sys.argv), "GREEN")
    args = parser.parse_args()

    if args.run_dir:
        run_dir = args.run_dir
        print("run_dir: ", run_dir)

    if args.log_file:
        log_file = args.log_file
        print("log_file: ", log_file)

    if args.debug is not None:
        debug_level = args.debug
        print("debug_level: ", debug_level)