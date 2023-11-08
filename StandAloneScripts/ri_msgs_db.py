# Description:  CDC-12436, also spec captured in https://docs.google.com/spreadsheets/d/107WNTw6a6cG7oU_nFOJvpX8Gi_lwRLj4Q8LViUosq1s/edit#gid=305334017
#               This script is used to analyze RI logs and build a database of opcodes in use in our Testsuite
#               The script is using regular expressions to find the opcodes in the logs and build a database
#               of opcodes, severities and related log files.
# 

import os
#import sys
import re 

# Color escape codes
RESET = "\x1b[0m"
RED = "\x1b[31m"
GREEN = "\x1b[32m"
YELLOW = "\x1b[33m"
 

# Define the regular expression pattern using `re.VERBOSE`

#LOG_PATTERN = r'''(INFO|WARNING|ERROR)\s+\[#\s+(\d){3,7}\]\s+.*'''
LOG_PATTERN = r'''(INFO|WARN|ERR)\s*\[#\s*(\d+)\]\s+.*'''

MAX_LOG_SIZE_TO_ANALYZE_IN_MB = (1024**2)*5 #in MB
LOG_PART_NAME_TO_RM = ["old", "2016","2017","2018","2019", "rpt"] #["sma"]#

import socket
machine_name = socket.gethostname()
print("Machine Name:", machine_name)
if ("Romans-MacBook-Air.local" in machine_name):
    print("local MAC machine, working on local files")
    LOG_FILES_ROOT_TREE = "/Users/romanpaleria/Documents/Scripts/RI logs/tmp logs for script debug/tmp"
    DIR_LIST_FILE_PATH = "/Users/romanpaleria/Documents/Scripts/RI logs/dir_list.txt"
    IS_WORK_FROM_FILE = False 
else:
    print(f"working on RI server machine: {machine_name}")
    LOG_FILES_ROOT_TREE = "/home/roman/Testcases/Scripts/RiMessagesOpcodes/TOOL_LOGs/RI_REGR/log_dirs_list_11_tests"
    DIR_LIST_FILE_PATH= "/home/roman/Testcases/Scripts/RiMessagesOpcodes/TOOL_LOGs/RI_REGR/log_dirs_list_10k"
    IS_WORK_FROM_FILE = True 


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
        print ("add_log_entry() opcode: {}, severity: {}, log_file: {}".format(opcode,severity,log_file))

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
                    count += 1
        return count

    def print_statistics(self):
        print(GREEN + "\nLogDatabase::print_statistics()" + RESET)
        num_opcodes = self.num_opcodes()
        opcodes_multiple_severities = self.opcodes_with_multiple_severities()
        biggest_counter_opcode = self.opcode_with_biggest_counter()
        total_messages  = self.total_messages()
        count_info      = self.count_severity("INFO")
        count_warning   = self.count_severity("WARN")
        count_error     = self.count_severity("ERR")

        print(f"Number of opcodes:                  {num_opcodes}")
        print("Opcodes with multiple severities:    ", opcodes_multiple_severities)
        if opcodes_multiple_severities != []:
            print(RED + "ERROR: opcodes_multiple_severities != []" + RESET)
            for opcode in opcodes_multiple_severities:
                print(f"opcode: {opcode}  severities: {self.LOG_DICT[opcode]['severities']}  log_files: {self.LOG_DICT[opcode]['log_files']}")  

        print(f"Opcode with the biggest counter:    {biggest_counter_opcode}  (opcode/counter)")
        print(f"Total counted messages in the db:   {total_messages}")
        print(f"Total counted INFO    messages:     {count_info}")
        print(f"Total counted WARNING messages:     {count_warning}")
        print(f"Total counted ERROR messages:       {count_error}")

        if total_messages != count_info + count_warning + count_error:
            print(RED + "ERROR: total_messages != count_info + count_warning + count_error" + RESET)
    def is_numeric(self, value):
        return isinstance(value, (int, float, complex))
    
    def print_opcodes_inorder(self):
        print(GREEN + "\nLogDatabase::print_opcodes_inorder()" + RESET)
        #Convert opcode keys to integers, sort them, and print
        sorted_opcodes = sorted(map(int, self.LOG_DICT.keys()))
        for opcode in sorted_opcodes:
            print(f"Opcode: {opcode}") #, Value: {self.LOG_DICT[str(opcode)]}")

#############class end#####################

def get_log_files_from_cfg_file(file_path):
    '''Get all log files from the root tree'''
    dir_cntr  = 0
    dir_path_l = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith('#'):
                continue
            dir_path_l.append(line)
            dir_cntr += 1
            #print ("file: {}, path: {}".format(filename,file_path))                
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
                #print ("file: {}, path: {}".format(filename,file_path))
    print("get_log_files_from_cfg_file() found {} files in the CFG file".format(len(file_path_l)))
    return file_path_l

def get_log_files(dir_tree):
    '''Get all log files from the root tree'''
    dir_cntr  = 0
    file_cntr = 0
    file_path_l = []
    for root, dirs, files in os.walk(dir_tree):
        dir_cntr += 1
        for filename in files:
            file_path = os.path.join(root, filename)
            file_path_l.append(file_path)
            #with open(file_path, 'r', errors='replace') as file:
            file_cntr += 1
            #print ("file: {}, path: {}".format(filename,file_path))
                
    print(GREEN + "get_log_files() found {} dirs, {} files. worked on dirtree: {}".format(dir_cntr,file_cntr,dir_tree) + RESET)

    return file_path_l


def grep_in_log_files(log_files, db):
    #compile the regexp pattern
    regex = re.compile(LOG_PATTERN)

    for index, file in enumerate(log_files):
        print(f"Processing file {index+1}/{len(log_files)}: {file}")
        # Check the size of the file, skip if it's too large
        file_size = os.path.getsize(file)
        with open(file) as f:
            print( "openning: {}  file".format(file))
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

def filter_files(file_list):
    orig_len = len(file_list)
    print(GREEN + f"filter_files() found {orig_len} files. MAX_LOG_SIZE_TO_ANALYZE_IN_MB: {MAX_LOG_SIZE_TO_ANALYZE_IN_MB}" + RESET)
    for file in file_list:
        if os.path.getsize(file) > MAX_LOG_SIZE_TO_ANALYZE_IN_MB:
            print(f"Skipping {file} due to large size")
            file_list.remove(file)
    print(YELLOW + f"filter_files() removed {orig_len - len(file_list)} files due to large size" + RESET)

    #removing not relevant log files
    # Iterate through the list and remove files that match the specified strings
    files_to_keep = []
    for file_path in files:
        # Extract the file name from the path
        file_name = os.path.basename(file_path)
        
        # Check if the file name contains any of the strings to remove
        if not any(remove_str in file_name for remove_str in LOG_PART_NAME_TO_RM):
            files_to_keep.append(file_path)
    print(YELLOW + f"filter_files() removing {len(file_list) - len(files_to_keep)} files due to file names" + RESET)
    file_list = files_to_keep   

    print(f"filter_files() finished with {len(file_list)} files")
    return file_list


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

    if IS_WORK_FROM_FILE == False:
        #print_dir_size_stats(LOG_FILES_ROOT_TREE)
        files = get_log_files(LOG_FILES_ROOT_TREE)
    else:
        files = get_log_files_from_cfg_file(DIR_LIST_FILE_PATH)
    
    if len(files) == 0:
        print(RED + "No log files found. Exiting" + RESET)
        exit(1)

    log_db = LogDatabase()

    print_total_file_size(files, "before filtering")
    files = filter_files(files)
    print_total_file_size(files, "after filtering")
    grep_in_log_files(files, log_db)

    log_db.print_statistics()
    log_db.print_opcodes_inorder()

    if ENABLE_PROFILER == True:
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

