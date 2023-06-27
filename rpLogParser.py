import os,re

##global variables
#globals, general variables
LOG_NAME = "mrdc.log"#"mrdc.log_SMALL" #log file name
LOG = "" #log file content
#BAD_LINES_TO_DEBUG = []
CMDS = [] #row commands, including prefixes
CTL_CMDS = []
ENV_CMDS = []
PROBLEM_CMDS = []
MAX_LINES_IN_COMMAND = 300 #already met scenario with almost 300 lines.

LOG_PREFIX_D = {#dictionary of prefixes
    'orig'   : r'^[a-zA-Z0-9]{0,5}\*\*> ',
    'ctl'    : r'^\*\*> ',
    'env'    : r'^env\*\*> '
}

#output files
ALL_CMDS_F_NAME     = "ri_all_orig.cmd" #include prefixes
ALL_CTL_CMDS_F_NAME = "ri_ctl.cmd" 
ALL_ENV_CMDS_F_NAME = "ri_env.cmd" 
ALL_PROBLEM_CMDS_F_NAME= 'ri_to_debug.cmd'

#global variables, for each command 

#COLOR PRINTING
RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"


def open_log():
    filepath = os.path.dirname(os.path.realpath(__file__))
    f_p = filepath + '/' + LOG_NAME
    print("working on log file: ", f_p)

    #open text file in read mode
    with open(f_p) as log_file:
        #print file size
        print("file size: ", os.path.getsize(f_p))
        global LOG
        LOG = log_file.read()
    print ("open_log finished")


def find_commands_in_log():
    print("find_commands_in_log()")
    
    import datetime
    log_lines = LOG.splitlines()  # Store the log lines in a variable
    print("num of lines in the log: ", len(log_lines))
    
    # Loop through each line in the log
    for id, line in enumerate(log_lines):
        if not line:
            continue
        if line.startswith(LOG_PREFIX_D['orig']):
            if line.startswith('**> exit '):
                continue
            #print(id, datetime.datetime.now(), ", line: ", line)
            if id + 1 < len(log_lines):
                next_line = log_lines[id + 1]
                if not (next_line.startswith("  INFO ") or
                        next_line.startswith("  WARN ") or
                        #re.sub(r"\s+", "", next_line) or
                        not next_line or
                        next_line == "Finalizing block DB data..." or
                        next_line == "################################################################################" or
                        next_line.startswith("Setting ")):

                    print(RED +"line #", id," ERROR, need debug: " + RESET, next_line)
                    BAD_LINES_TO_DEBUG.append(("on line id: ", id , ". line: ",next_line))
                    '''if len(BAD_LINES_TO_DEBUG) > 10:
                        break;
                    # Take appropriate error handling action instead of abrupt termination'''
            #print("next line: ", next_line)
    #print(RED + "\n\nBAD_LINES_TO_DEBUG: " + RESET, BAD_LINES_TO_DEBUG)
    print(RED + "in total {} lines to debug".format(len(BAD_LINES_TO_DEBUG))+ RESET)

'''
def find_commands_in_log():
    print("find_commands_in_log")
    print("len of the LOG: ", len(LOG))
    
    import datetime
    #foreach line in the log file, if it starts with one from CMDS_LIST,
    #  print the line and index.
    for id,line in enumerate(LOG.splitlines()):
        if len(line) == 0:
            continue
        if line[0] =="*":
            if line.startswith('**> exit '):
                continue
            print(id, datetime.datetime.now(),", line: ", line)
            next_line =  LOG.splitlines()[LOG.splitlines().index(line)+1]
            if not (next_line.startswith("  INFO ") or 
                    next_line.startswith("  WARN ") or 
                    next_line =="" or 
                    next_line == "Finalizing block DB data..." or
                    next_line == "################################################################################" or
                    next_line.startswith("Setting ")):
                print("next line ERROR, need debug: ", next_line)
                exit(0)
            print("next line: ", LOG.splitlines()[LOG.splitlines().index(line)+1])
'''        
'''   #loop print LOG lines with index prefix
    for index, line in enumerate(LOG.splitlines()):
        print("index: ", index, " line: ", line)
'''


# Check for "{" balance
def check_tcl_syntax(cmd, cont):
    open_braces = cmd.count('{')
    close_braces = cmd.count('}')
    return 0 if open_braces == close_braces else cont + 1

def find_commands_in_log_chatGTM_from_perl():
    import sys
    pos = 0
    cmd = ""
    cont = 0

    log_lines = LOG.splitlines()
    print("find_commands_in_log_chatGTM_from_perl() \nnum of lines in the log: ", len(log_lines))
    for id, line in enumerate(log_lines):
        pos += 1
        line = line.rstrip('\n') # Remove newline character
        if cont > MAX_LINES_IN_COMMAND:
            sys.stderr.write(f"long TCL command at line {pos}\n")
        if cont:
            cmd += line
            cont = check_tcl_syntax(cmd, cont)
        else:
            #if re.match(r'^.{0,5}\*\*>', line): #if line.startswith('FEWCHARS**> '):
            if re.match(LOG_PREFIX_D['orig'], line): 
                cmd = line
                cont = check_tcl_syntax(cmd, cont)
        if cont == 0 and cmd != "":
            #print(cmd)
            CMDS.append(cmd)
            cmd = ""

    print(BLUE + "num of CMDS: " + RESET, len(CMDS))   
    #print('\n'.join(f'{index}: {item}' for index, item in enumerate(CMDS))) 

def generate_CTL_and_ENV_from_CMDS():
    global CTL_CMDS, ENV_CMDS, PROBLEM_CMDS
    for cmd in CMDS:
        if re.match(LOG_PREFIX_D['env'], cmd):
            ENV_CMDS.append(cmd)
        elif re.match(LOG_PREFIX_D['ctl'], cmd):
            CTL_CMDS.append(cmd)
        else:
            PROBLEM_CMDS.append(cmd)
 
def generate_files():
    print("generate_files")
    print(BLUE+"len of the CMDS: " +RESET, len(CMDS))

    #generate ALL_CMDS_F_NAME file
    with open(ALL_CMDS_F_NAME, 'w') as f:
        for item in CMDS:
            f.write("%s\n" % item)
    
    generate_CTL_and_ENV_from_CMDS()
    print(BLUE+"len of the CTL_CMDS: "+RESET, len(CTL_CMDS))
    print(BLUE+"len of the ENV_CMDS: "+RESET, len(ENV_CMDS))
    print(RED +"len of the PROBLEM_CMDS: "+RESET, len(PROBLEM_CMDS))
    
    with open(ALL_CTL_CMDS_F_NAME, 'w') as f:
        for item in CTL_CMDS:
            f.write("%s\n" % item)
    with open(ALL_ENV_CMDS_F_NAME, 'w') as f:
        for item in ENV_CMDS:
            f.write("%s\n" % item)
    with open(ALL_PROBLEM_CMDS_F_NAME, 'w') as f:
        for item in PROBLEM_CMDS:
            f.write("%s\n" % item)


    print("generate_files finished")

def main():
    print("main function")
    open_log()
    #find_commands_in_log()
    find_commands_in_log_chatGTM_from_perl()
    generate_files()
    print("main function finished")

if __name__ == "__main__":
    main()