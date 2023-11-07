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
LOG_PATTERN = r'''(INFO|WARNING|ERROR)\s+\[#\s+(\d+)\]\s+.*'''

LOG_FILES_ROOT_TREE = "/Users/romanpaleria/Documents/Scripts/RI logs for analyze/tmp logs for script debug/"
LOG_FILES_ROOT_TREE = "/Users/romanpaleria/Documents/Scripts/RI logs for analyze/"


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
        return max(self.LOG_DICT, key=lambda opcode: self.LOG_DICT[opcode]['counter'])

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
        count_warning   = self.count_severity("WARNING")
        count_error     = self.count_severity("ERROR")

        print(f"Number of opcodes:                  {num_opcodes}")
        print("Opcodes with multiple severities:    ", opcodes_multiple_severities)
        print(f"Opcode with the biggest counter:    {biggest_counter_opcode}")
        print(f"Total counted messages in the db:   {total_messages}")
        print(f"Total counted INFO    messages:     {count_info}")
        print(f"Total counted WARNING messages:     {count_warning}")
        print(f"Total counted ERROR messages:       {count_error}")

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

    for file in log_files:
        with open(file) as f:
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

def print_dir_size_stats(dir_path):
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

if __name__ == "__main__":
    print_dir_size_stats(LOG_FILES_ROOT_TREE)
    files = get_log_files(LOG_FILES_ROOT_TREE)
    log_db = LogDatabase()

    grep_in_log_files(files, log_db)


    log_db.print_statistics()

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