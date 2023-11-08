import os

def has_gold_subdir_up(path):
    # Split the path into components
    components = os.path.normpath(path).split(os.path.sep)

    # Check if "gold" is in the parent directory
    if "gold" in components:
        gold_index = components.index("gold")
        print ("index of gold is: ", gold_index)
        if gold_index > 0:
            return True

    return False

# Example usage:
file_path = "/path/to/parent/gold/subdir/file.txt"
parent_directory = os.path.dirname(file_path)
print ("dir: ",os.path.basename(parent_directory))
       

if has_gold_subdir_up(file_path):
    print("The file path contains a 'gold' subdirectory one level up.")
else:
    print("The file path does not contain a 'gold' subdirectory one level up.")
