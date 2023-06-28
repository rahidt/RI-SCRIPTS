#project located at: https://github.com/rahidt/RI-SCRIPTS
version = "18, vscode"

import os,re

##global variables
#globals, general variables
LOG_NAME = "../mrdc.log_SMALL"#"mrdc.log_SMALL" #log file name
LOG = "" #log file content
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
ALL_RI_STATS_SUMMARY_F_NAME = "ri_stats_summary.txt"

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


# Check for "{" balance
def check_tcl_syntax(cmd, cont):
    open_braces = cmd.count('{')
    close_braces = cmd.count('}')
    return 0 if open_braces == close_braces else cont + 1

def find_commands_in_log():
    import sys
    pos = 0
    cmd = ""
    cont = 0

    log_lines = LOG.splitlines()
    print("find_commands_in_log() \nnum of lines in the log: ", len(log_lines))
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




def generate_CTL_per_read_design_db_flow():
    global CTL_CMDS
    print("generate_CTL_per_read_design_db_flow() orig num of commands: ", len(CTL_CMDS))
    #removing all irelevant commands as replacing with read_design_db
    #0. initializing list and dict {cmd:cmd_count}
    skip_commands_list = ["read_liberty ", "analyze", "create_scenario ", "current_scenario ", "read_sdc ", "read_env ", "analyze_intent ", "exit "]
    skip_commands_dict = {cmd: 0 for cmd in skip_commands_list} 
    for cmd in CTL_CMDS[:]:  # Iterate over a copy of the list to safely remove items
        for skip_cmd in skip_commands_dict:
            if skip_cmd in cmd:
                CTL_CMDS.remove(cmd)
                skip_commands_dict[skip_cmd] += 1
                break
    print(YELLOW + "removed following commands as using read_design_db flow" + RESET)
    for key, value in skip_commands_dict.items():
        print(YELLOW + "removed command: " + RESET, key, "\t num of occurences: ", value)  
    #1. get partition_name from elaborate command, and removing it from the list.
    elab_partitions_list = [cmd for cmd in CTL_CMDS if cmd.startswith("elaborate ")]
    print("elab_partitions_list : ",elab_partitions_list )
    if len(elab_partitions_list) == 0 : 
        print ("Error - no elaborate commands found in the log" )
        exit(2)
    elif len(elab_partitions_list)  > 1 : 
        print ("Error - currently supporting only flow with single elaborate command. what to do if there is none/multiple elab commands in the log?..." )
        exit(2)
    
    elab_cmd = elab_partitions_list[0]
    pattern = r'elaborate '
    partition_name = re.sub(pattern, '', elab_cmd)
    print("partition name will be extracted from elab command:", partition_name)
    
    pattern = r'\-ivision '
    partition_name = re.sub(pattern, '', partition_name )
    #print(partition_name)
    
    pattern = r'-black_box\s*\w+ '
    partition_name = re.sub(pattern, '', partition_name ) 
    #print(partition_name)
    
    pattern = r'-black_box\s*\{[^}]+\}'
    partition_name = re.sub(pattern, '', partition_name ) 
    #print(partition_name)
    
    pattern = r'-auto_black_box'
    partition_name = re.sub(pattern, '', partition_name ) 
    print("final parition name: ",partition_name)

    ##finding all set_user_reset_synchronizer commands, and placing them before the analyze_intent 
    set_user_reset_synchronizer_cmds = [] 
    for cmd in CTL_CMDS[:]:  # Iterate over a copy of the list to safely remove items
        if cmd.startswith("set_user_reset_synchronizer ") :
            CTL_CMDS.remove(cmd)
            set_user_reset_synchronizer_cmds.append(cmd)
    #print("set_user_reset_synchronizer_cmds", set_user_reset_synchronizer_cmds )
    
    ##finding all read_rdc_db commands, and placing them before the read_env
    read_rdc_db_cmds = [] 
    for cmd in CTL_CMDS[:]:  # Iterate over a copy of the list to safely remove items
        if cmd.startswith("read_rdc_db ") :
            CTL_CMDS.remove(cmd)
            read_rdc_db_cmds.append(cmd)
    #print("read_rdc_db_cmds", read_rdc_db_cmds )

    #remove elaborate commands: commands = [cmd for cmd in commands if not cmd.startswith("elaborate ")]
    #replacing the elaborate command with next multiple commands: read_design_db, read_env, and analyze_intent
    new_cmds = ["read_design_db " + partition_name + " -project ./meridian_project"] + \
               read_rdc_db_cmds + \
               ["read_env " + ALL_ENV_CMDS_F_NAME ] + \
               set_user_reset_synchronizer_cmds + \
               ["analyze_intent -disable_auto_intent_generation"]
    for index, element in enumerate(CTL_CMDS):
        if element.startswith('elaborate'):
            #print("Index:", index)
            break
    CTL_CMDS[index:index+1] = new_cmds 
    #2. generate read_design_db command.
    #3. rm commands that read_design_db replaces, like: read_liberty, full list: #print "Skipped $read_liberty_cnt read_liberty commands\nSkipped $analyze_cnt analyze commands\nSkipped $scenario_cnt scenario related commands\nSkipped $read_sdc_cnt read_sdc commands\nSkipped $read_env_cnt read_env commands\nSkipped $analyze_intent_cnt analyze_intent commands\n";
    print("generate_CTL_per_read_design_db_flow() finished, cur num of commands: ", len(CTL_CMDS))




def generate_CTL_and_ENV_from_CMDS():
    global CTL_CMDS, ENV_CMDS, PROBLEM_CMDS
    for cmd in CMDS:
        if re.match(LOG_PREFIX_D['env'], cmd):
            cmd_without_prefix = re.sub(r'^{}(.*)'.format(LOG_PREFIX_D['env']), r'\1', cmd)
            ENV_CMDS.append(cmd_without_prefix)
        elif re.match(LOG_PREFIX_D['ctl'], cmd):
            cmd_without_prefix = re.sub(r'^{}(.*)'.format(LOG_PREFIX_D['ctl']), r'\1', cmd)
            CTL_CMDS.append(cmd_without_prefix)
        else:
            PROBLEM_CMDS.append(cmd)

    generate_CTL_per_read_design_db_flow()
 
def generate_runtime_stats():
    print(BLUE+"generate_runtime_stats()"+RESET)
    lines = LOG.splitlines()
    # Regular expression patterns to extract relevant information
    self_time_pattern = r"self time \(s\): user (\d+)  sys (\d+)  real (\d+)"
    memory_pattern = r"memory \(MB\): curr (\d+)"

    # List to store parsed data
    parsed_data = []

    # Parse each line and extract the relevant information
    for line in lines:
        self_time_match = re.search(self_time_pattern, line)
        memory_match = re.search(memory_pattern, line)
        if self_time_match and memory_match:
            user_time, sys_time, real_time = self_time_match.groups()
            memory = memory_match.group(1)
            parsed_data.append((line, int(real_time), int(memory)))

    # Sort the parsed data by real self time and memory consumption
    sorted_data_time = sorted(parsed_data, key=lambda x: x[1], reverse=True)
    sorted_data_memory = sorted(parsed_data, key=lambda x: x[2], reverse=True)

    with open(ALL_RI_STATS_SUMMARY_F_NAME, 'w') as f:
        print("opened file: ", ALL_RI_STATS_SUMMARY_F_NAME)
        #f.write("%s\n" % item)

        # Print the lines with highest real self time
        f.write("\nLines sorted by real self time (descending order):\n")
        for item in sorted_data_time:
            f.write(f"{item[1]}s: {item[0]}\n")
            
        # Print the lines with highest memory consumption
        f.write("\nLines sorted by memory consumption (descending order):\n")
        for item in sorted_data_memory:
            f.write(f"{item[2]}MB: {item[0]}\n")


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

    generate_runtime_stats()
    print("generate_files finished")

def main():
    print("main function")
    open_log()
    find_commands_in_log()
    generate_files()
    print("main function finished, version:", version)

if __name__ == "__main__":
    main()


    
    
