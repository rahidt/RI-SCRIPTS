# Description:  CDC-12436, also spec captured in https://docs.google.com/spreadsheets/d/107WNTw6a6cG7oU_nFOJvpX8Gi_lwRLj4Q8LViUosq1s/edit#gid=305334017
#               This script is used to analyze RI logs and build a database of opcodes in use in our Testsuite
#               The script is using regular expressions to find the opcodes in the logs and build a database
#               of opcodes, severities and related log files.
# 

import os
#import sys
import re 
import shutil
from datetime import datetime
TIMESTAMP = datetime.now().strftime('%Y%m%d%H%M%S')

# Color escape codes
RESET = "\x1b[0m"
RED = "\x1b[31m"
GREEN = "\x1b[32m"
YELLOW = "\x1b[33m"
 

# Define the regular expression pattern using `re.VERBOSE`

#LOG_PATTERN = r'''(INFO|WARNING|ERROR)\s+\[#\s+(\d){3,7}\]\s+.*'''
LOG_PATTERN = r'''(INFO|WARN|ERR)\s*\[#\s*(\d+)\]\s+.*'''

#MAX_LOG_SIZE_TO_ANALYZE_IN_MB = (1024**2)*0.005 #in MB
MAX_LOG_SIZE_TO_ANALYZE_IN_MB       = .005
MAX_LOG_SIZE_TO_ANALYZE_IN_BYTES    = (1024**2)*MAX_LOG_SIZE_TO_ANALYZE_IN_MB #in MB

LOG_PART_NAME_TO_RM = ["old", "2016","2017","2018","2019", "rpt"] #["sma"]#
REMOVE_FILES_NOT_UNDER_GOLD_DIR = True
GOLD_DIR_NAMES_LIST = ["gold"]
MAX_FILES_TO_GREP = 12345678
CREATE_TESTSUITE_FILES = True
FIND_TESTSUITE_FILES   = False 
COMMENT_LINE = "#"

import socket
machine_name = socket.gethostname()
print("Machine Name:", machine_name)
if ("Romans-MacBook-Air.local" in machine_name):
    print("local MAC machine, working on local files")
    LOG_FILES_ROOT_TREE = "/Users/romanpaleria/Documents/Scripts/RI logs/tmp logs for script debug/"
    DIR_LIST_FILE_PATH = "/Users/romanpaleria/Documents/Scripts/RI logs/dir_list.txt"
    REMOVE_FILES_NOT_UNDER_GOLD_DIR = True
    GOLD_DIR_NAMES_LIST = ["gold",'tmp',"tmp logs for script debug"]

else:
    print(f"working on RI server machine: {machine_name}")
    LOG_FILES_ROOT_TREE = "/home/rgr/trunk/regress/TestSuite/jira/"
    LOG_FILES_ROOT_TREE = "/home/rgr/trunk/regress/TestSuite/"
    DIR_LIST_FILE_PATH= "/home/roman/Testcases/Scripts/RiMessagesOpcodes/TOOL_LOGs/RI_REGR/LOG_DIR_LISTS/log_dirs_list_1k"
    DIR_LIST_FILE_PATH= "/home/roman/Testcases/Scripts/RiMessagesOpcodes/TOOL_LOGs/RI_REGR/LOG_DIR_LISTS/log_dirs_list_11_tests"
    DIR_LIST_FILE_PATH= "/home/roman/Testcases/Scripts/RiMessagesOpcodes/TOOL_LOGs/RI_REGR/TestSuiteFileLists/files_for_grep.all"

ENABLE_PROFILER = False 
if ENABLE_PROFILER == True:
    #This code creates a profiler object, enables it, runs the code you want to profile, disables the profiler, and prints the statistics.
    #For more advanced profiling and visualization, you can also use third-party tools like line_profiler, memory_profiler, or Pyflame. These tools provide additional insights into code performance and memory usage.
    import cProfile


class LogDatabase:
    def __init__(self):
        self.LOG_DICT = {}
        

    def add_log_entry(self, opcode, severity, log_file):
        if opcode not in self.LOG_DICT:
            self.LOG_DICT[opcode] = {
                'severities': [],
                'log_files': [],
                'counter': 0
            }
        ##appending only new severity and related logfile for first match
        if (severity not in self.LOG_DICT[opcode]['severities']):
            self.LOG_DICT[opcode]['severities'].append(severity)
            self.LOG_DICT[opcode]['log_files'].append(log_file)
        self.LOG_DICT[opcode]['counter'] += 1
        #print ("add_log_entry() opcode: {}, severity: {}, log_file: {}".format(opcode,severity,log_file))

    def get_entry(self, opcode):
        if opcode in self.LOG_DICT:
            return self.LOG_DICT[opcode]
        else:
            return None

    def get_all_entries(self):
        return self.LOG_DICT
    
    def print_database(self):
        for opcode, data in self.LOG_DICT.items():
            print(f"Opcode: {opcode}")
            print(f"Count: {data['counter']}")
            print("Severities:")
            for severity in data['severities']:
                print(f"  - {severity}")
            print("Log Files:")
            for log_file in data['log_files']:
                print(f"  - {log_file}")
            print()  # Empty line to separate entries
    
    def num_opcodes(self):
        return len(self.LOG_DICT)

    def opcodes_with_multiple_severities(self):
        return [opcode for opcode, data in self.LOG_DICT.items() if len(data['severities']) > 1]

    def opcode_with_biggest_counter(self):
        if not self.LOG_DICT:
            return None
        opcode = max(self.LOG_DICT, key=lambda opcode: self.LOG_DICT[opcode]['counter'])
        counter = self.LOG_DICT[opcode]['counter']
        return opcode, counter

    def total_messages(self):
        return sum(data['counter'] for data in self.LOG_DICT.values())
    
    def count_severity(self, severity_type):
        count = 0
        for opcode, data in self.LOG_DICT.items():
            #severities, _, _ = data
            for severity in data['severities']:
                if severity == severity_type:
                    count += data['counter']
        return count


    def print_statistics(self):
        print(GREEN + "\n---LogDatabase::print_statistics()" + RESET)
        self.print_opcodes_inorder()
        self.print_db_summary_stats()
        
    def print_db_summary_stats(self):
        print(GREEN + "--LogDatabase::print_db_summary_stats()" + RESET)
        num_opcodes = self.num_opcodes()
        opcodes_multiple_severities = self.opcodes_with_multiple_severities()
        biggest_counter_opcode = self.opcode_with_biggest_counter()
        total_messages  = self.total_messages()
        count_info      = self.count_severity("INFO")
        count_warning   = self.count_severity("WARN")
        count_error     = self.count_severity("ERR")

        print(f"Number of opcodes:                  {num_opcodes}")
        if opcodes_multiple_severities != []:
            print(RED + "ERROR: opcodes_multiple_severities != []" + RESET)
            print("Opcodes with multiple severities:    ", opcodes_multiple_severities)
            for opcode in opcodes_multiple_severities:
                print(f"opcode: {opcode}  severities: {self.LOG_DICT[opcode]['severities']}  log_files: {self.LOG_DICT[opcode]['log_files']}")  

        print(f"Opcode with the biggest counter:    {biggest_counter_opcode}  (opcode/counter)")
        print(f"Total counted messages in the db:   {total_messages}")
        print(f"Total counted INFO    messages:     {count_info}")
        print(f"Total counted WARNING messages:     {count_warning}")
        print(f"Total counted ERROR messages:       {count_error}")

        if total_messages != count_info + count_warning + count_error:
            print(RED + f"ERROR: {total_messages} != {count_info + count_warning + count_error} ---> total_messages != count_info + count_warning + count_error " + RESET)
        
    
    def is_numeric(self, value):
        return isinstance(value, (int, float, complex))
    
    def print_opcodes_inorder(self):
        print(GREEN + "\nLogDatabase::print_opcodes_inorder()" + RESET)
        #Convert opcode keys to integers, sort them, and print
        print(f"----Opcode:  \t\t ----Severityies: \t ----Log Files:")
        for key in sorted(self.LOG_DICT, key=lambda k: int(k)):
            severities_l = self.LOG_DICT[key]['severities']
            severities_str = ", ".join(severities_l)
            logs_l = self.LOG_DICT[key]['log_files']
            logs_str = ", ".join(logs_l)
            print(f"{key} \t\t {severities_str} \t {logs_str}")
####################################################
#############class end##############################
####################################################

'''def get_log_files_from_cfg_file(file_path):
    #Get all log files from the root tree
    dir_cntr  = 0
    dir_path_l = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith(COMMENT_LINE):
                continue
            dir_path_l.append(line)
            dir_cntr += 1
            #print ("file: {}, path: {}".format(file_path.split(os.path.sep)[-1],file_path))                
    print("get_log_files_from_cfg_file() found {} dirs. CFG file parsed : {}".format(dir_cntr,file_path))
    
    file_cntr = 0
    file_path_l = []
    for dir in dir_path_l:
        for root, dirs, files in os.walk(dir):
            for filename in files:
                file_path = os.path.join(root, filename)
                file_path_l.append(file_path)
                #with open(file_path, 'r', errors='replace') as file:
                file_cntr += 1
                print ("file: {}, path: {}".format(filename,file_path))
    print("get_log_files_from_cfg_file() found {} files in the CFG file".format(len(file_path_l)))
    return file_path_l'''

    
def get_log_files_from_cfg_file(file_path):
    '''Get all log files from the root tree'''
    file_cntr  = 0
    cmnt_cntr  = 0
    file_path_l = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith(COMMENT_LINE):
                cmnt_cntr += 1
                continue
            file_path_l.append(line)
            file_cntr += 1
            #print ("file: {}, path: {}".format(file_path.split(os.path.sep)[-1],file_path))                
    print("get_log_files_from_cfg_file() found {} files, {} comment lines. CFG file parsed : {}".format(file_cntr,cmnt_cntr,file_path))
    return file_path_l


def get_log_files(dir_tree):
    '''Get all log files from the root tree'''
    dir_cntr  = 0
    file_cntr = 0
    file_path_l = []
    for root, dirs, files in os.walk(dir_tree):
        dir_cntr += 1
        if file_cntr > MAX_FILES_TO_GREP:
            print(YELLOW + "get_log_files() reached MAX_FILES_TO_GREP: {}  -- skipping the rest of the files".format(MAX_FILES_TO_GREP) + RESET)
            break           
        for filename in files:
            file_path = os.path.join(root, filename)
            file_path_l.append(file_path)
            #with open(file_path, 'r', errors='replace') as file:
            file_cntr += 1

            #print ("file: {}, path: {}".format(filename,file_path))
    print(GREEN + "get_log_files() found {} dirs, {} files. worked on dirtree: {}".format(dir_cntr,file_cntr,dir_tree) + RESET)
    
    return file_path_l


from concurrent.futures import ThreadPoolExecutor
# ... (Previous code, imports, constants, and LogDatabase class)
def process_log_file(log_file, log_db):
    # Log file processing code here
    #compile the regexp pattern
    regex = re.compile(LOG_PATTERN)

    #print(GREEN + f"Processing file: {log_file}" + RESET)
    
    # Check the size of the file, skip if it's too large
    file_size = os.path.getsize(log_file)
    
    with open(log_file) as f:
        try:
            text = f.read()
        except UnicodeDecodeError:
            print(YELLOW + f"process_log_file(): UnicodeDecodeError: {log_file} -- skipping the file" + RESET)
            return

    # Find all matches in the text
    matches = regex.findall(text)

    # Add all matches to the database
    for match in matches:
        severity, opcode = match
        log_db.add_log_entry(opcode, severity, log_file)

def process_log_files(log_files, log_db):
    print(GREEN + f"\n---process_log_files(): {len(log_files)} files" + RESET)
    results = []
    num_of_logs = len(log_files)
    with ThreadPoolExecutor(max_workers=4) as executor:  # Adjust max_workers as needed
        for inx, log_file in enumerate(log_files):
            print(f"Processing log {inx+1}/{num_of_logs}: {log_file}")
            results.append(executor.submit(process_log_file, log_file, log_db))

    # Wait for all threads to finish
    for result in results:
        result.result()




'''
def process_log_files(log_files, db):
    #compile the regexp pattern
    regex = re.compile(LOG_PATTERN)
    
    print(GREEN + "\n---process_log_files: {} files".format(len(log_files)) + RESET)

    for index, file in enumerate(log_files):
        print(f"Processing file {index+1}/{len(log_files)}: {file}")
        # Check the size of the file, skip if it's too large
        file_size = os.path.getsize(file)
        with open(file) as f:
            #print( "openning: {}  file".format(file))
            try: 
                text = f.read()
            except UnicodeDecodeError:
                print(YELLOW + "UnicodeDecodeError: {}  -- skipping the file".format(file) + RESET)
                continue    
        # Find all matches in the text
        matches = regex.findall(text)

        # Add all matches to the database                                        
        for match in matches:
            severity, opcode = match
            log_db.add_log_entry(opcode, severity, file)
'''

def filter_files_by_accessability(file_list):
    return_list = []
    no_access_count = 0
    no_read_count = 0
    for file_path in file_list:
        if os.path.exists(file_path):
            if os.access(file_path, os.R_OK):
                return_list.append(file_path)
            else:
                no_read_count += 1
                print(RED + f"The file '{file_path}' is not readable. Skipping this file."+ RESET)
                # Handle the case where the file is not readable
        else:
            no_access_count += 1
            print(RED + f"The file '{file_path}' does not exist. Skipping this file." + RESET)
            # Handle the case where the file doesn't exist or take any other necessary actions.
    print(GREEN + f"---filter_files_by_accessability() found {len(file_list)} files. removed {no_access_count},{no_read_count} as not accesable,readable" + RESET)
    return return_list

def filter_files_by_size(file_list):
    orig_len = len(file_list)
    removed_file_list = []
    print(GREEN + f"---filter_files_by_size() found {orig_len} files. MAX_LOG_SIZE_TO_ANALYZE_IN_MB: {MAX_LOG_SIZE_TO_ANALYZE_IN_MB}" + RESET)
    for file in file_list:
        if os.path.getsize(file) > MAX_LOG_SIZE_TO_ANALYZE_IN_BYTES:
            print(f"Skipping {file} due to large size")
            file_list.remove(file)
            removed_file_list.append(file) 
    print(YELLOW + f"filter_files_by_size() removed {orig_len - len(file_list)} files due to large size" + RESET)
    return file_list, removed_file_list

def filter_files_by_log_part_name(file_list) :
    #removing not relevant log files
    # Iterate through the list and remove files that match the specified strings
    files_to_keep = []
    for file_path in file_list:
        # Extract the file name from the path
        file_name = os.path.basename(file_path)
        
        # Check if the file name contains any of the strings to remove
        if not any(remove_str in file_name for remove_str in LOG_PART_NAME_TO_RM):
            files_to_keep.append(file_path)
    print(YELLOW + f"filter_files_by_log_part_name() removing {len(file_list) - len(files_to_keep)} files due to file names" + RESET)
    file_list = files_to_keep   

    print(GREEN + f"---filter_files_by_log_part_name() finished with {len(file_list)} files" + RESET)
    return file_list

'''def filter_files_by_dir_name (file_list):
    return_file_list = []
    print(GREEN + "---filter_files_by_dir_name() found {} files".format(len(file_list)) + RESET)
    if REMOVE_FILES_NOT_UNDER_GOLD_DIR == True:
        print(GREEN + f"removing files that are not under gold dirs {GOLD_DIR_NAMES_LIST}" + RESET)
        logs_under_gold = 0
        for gold_dir in GOLD_DIR_NAMES_LIST:
            for file_path in return_file_list:
                dir_fullpath = os.path.dirname(file_path)
                uper_dir_name = os.path.basename(dir_fullpath)
                if uper_dir_name == gold_dir:
                    return_file_list.add(file_path)
                    #print(f"removed {file_path} due to not under gold dir, gold_dir: {gold_dir}\n")
                    logs_under_gold += 1
        print(YELLOW + "removed {} files due to not under gold dir\n".format(len(file_list) - logs_under_gold) + RESET)
    
    return return_file_list'''
def filter_files_by_dir_name_chatGPT(file_paths):
    relevant_file_paths = [
        path for path in file_paths
        if any(gold_dir in path.split(os.path.sep)[-2] for gold_dir in GOLD_DIR_NAMES_LIST)
    ]
    not_relevant_file_paths = set(file_paths) - set(relevant_file_paths)
    print(GREEN + f"---filter_files_by_dir_name_chatGPT() total {len(file_paths)} files. {len(relevant_file_paths)} files relevant. removed {len(not_relevant_file_paths)} files " + RESET)
    for i,path in enumerate(not_relevant_file_paths):
        print(f"removed {i}/{len(not_relevant_file_paths)}, path: {path}")
    
    return relevant_file_paths

def filter_files(file_list):
    print(GREEN + f"----filter_files() found {len(file_list)} files." + RESET)
    file_list = filter_files_by_accessability(file_list)
    #file_list = filter_files_by_dir_name(file_list)
    file_list = filter_files_by_dir_name_chatGPT(file_list)
    file_list = filter_files_by_log_part_name(file_list)
    file_list, oversized_files_list = filter_files_by_size(file_list)
    
    print(f"filter_files() finished with {len(file_list)} files")
    return file_list, oversized_files_list 


def  create_testsuite_files(file_list, file_name, prefix = ""):

    if os.path.exists(file_name):
        new_file_name = f"{file_name}_{TIMESTAMP}"
        shutil.move(file_name, new_file_name)
    
    with open(file_name, 'w') as file:
        file.write(f"{COMMENT_LINE} {prefix}\n")
        file.write(f"{COMMENT_LINE} working on root tree {LOG_FILES_ROOT_TREE}\n")
        for file_path in file_list:
            file.write(file_path + '\n')
        file.close()
    print(GREEN + f"--create_testsuite_files() working on root tree {LOG_FILES_ROOT_TREE}" + RESET)
    print(f"create_testsuite_files() created file: {file_name}")

def print_total_file_size(file_list, prefix):
    total_size = 0
    for file_path in file_list:
        #print(GREEN + f"print_total_file_size() {file_path}" + RESET)
        if os.path.isfile(file_path):
            total_size += os.path.getsize(file_path)
    print(GREEN + f"\nprint_total_file_size() ---{prefix}---" + RESET)
    print(f"Total size of analyzed file size: {total_size / (1024**2):.2f} MB")
    print(f"Total files analyzed {len(file_list)} \n")

'''def print_dir_size_stats(dir_path):
    total_dir_size = 0
    total_files = 0
    for dirpath, dirnames, filenames in os.walk(dir_path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            total_dir_size += os.path.getsize(filepath)
            total_files += 1
   
    # Replace 'your_directory_path' with the path of the directory you want to check
    directory_path = 'your_directory_path'
    
    print(GREEN + "\nprint_dir_size_stats()" + RESET)
    #print(f"Total size of '{directory_path}': {total_dir_size} bytes")
    print(f"Total size of '{directory_path}': {total_dir_size / (1024**2):.2f} MB")
    print(f"Total files in dir structure {total_files} \n")
'''





if __name__ == "__main__":    
    if ENABLE_PROFILER == True:
        profiler = cProfile.Profile()
        profiler.enable()

    if FIND_TESTSUITE_FILES == True:
        #print_dir_size_stats(LOG_FILES_ROOT_TREE)
        files = get_log_files(LOG_FILES_ROOT_TREE)
    else:
        files = get_log_files_from_cfg_file(DIR_LIST_FILE_PATH)
    
    if len(files) == 0:
        print(RED + "No log files found. Exiting" + RESET)
        exit(1)

    log_db = LogDatabase()
    
    if FIND_TESTSUITE_FILES == True: #using CFG file, expecting only relevant files in it.
        print_total_file_size(files, "before filtering")
        files, oversized_files = filter_files(files)
        all_logs_in_golden_list = files + oversized_files 
        print_total_file_size(files, "after filtering")
        print_total_file_size(all_logs_in_golden_list , "after filtering, including oversized files")
        if CREATE_TESTSUITE_FILES == True:
            print(GREEN + "\nCreating testsuite files" + RESET)
            comment = f"This is autogenerated list of all files that has size < {MAX_LOG_SIZE_TO_ANALYZE_IN_MB} MB in Testsuite golden dir that could be relevant for grep"
            create_testsuite_files(files, "files_for_grep.all",comment)
            comment = f"This is autogenerated list of all files that has size > {MAX_LOG_SIZE_TO_ANALYZE_IN_MB} MB in Testsuite golden dir that could be relevant for grep"
            create_testsuite_files(oversized_files, "files_for_grep.oversized",comment)
            exit(0)
    
    process_log_files(files, log_db)

    log_db.print_statistics()

    if ENABLE_PROFILER == True:
        print(GREEN + "\nPrinting run profile stats" + RESET)
        profiler.disable()
        profiler.print_stats(sort='cumulative')  

    #log_db.print_database() 
    #add_data_to_db(line)

    '''# Example usage:
    log_db = LogDatabase()

    log_db.add_log_entry("opcode1", "INFO", "log_file1.log")
    log_db.add_log_entry("opcode1", "ERROR", "log_file2.log")
    log_db.add_log_entry("opcode2", "DEBUG", "log_file3.log")

    # Get an entry for a specific opcode
    entry = log_db.get_entry("opcode1")
    print(entry)

    # Get all entries in the database
    all_entries = log_db.get_all_entries()
    print(all_entries)'''



