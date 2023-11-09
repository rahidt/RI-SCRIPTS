# Read opcodes from the catalog file
with open('catalog_opcodes.txt', 'r') as catalog_file:
    catalog_opcodes = catalog_file.read().splitlines()
    catalog_opcodes = [item.strip() for item in catalog_opcodes]
# Read opcodes from the testsute file
with open('log_opcodes.txt', 'r') as testsute_file:
    testsute_opcodes = testsute_file.read().splitlines()
    testsute_opcodes = [item.strip() for item in testsute_opcodes]

# Find opcodes in catalog but not in testsute
catalog_not_in_testsute = set(catalog_opcodes) - set(testsute_opcodes)

# Find opcodes in testsute but not in catalog
testsute_not_in_catalog = set(testsute_opcodes) - set(catalog_opcodes)

# Find opcodes common to both lists
common_opcodes = set(catalog_opcodes) & set(testsute_opcodes)

import sys 
with open('testsute_not_in_catalog.txt', 'w') as file:
    old_stdout = sys.stdout
    sys.stdout = file
    # Print the results
    print(f"Number of opcodes in the catalog but not in testsute: {len(catalog_not_in_testsute)}")
    print(f"Number of opcodes in testsute but not in the catalog: {len(testsute_not_in_catalog)}")
    print(f"Number of common opcodes in both lists: {len(common_opcodes)}")

    print ("\n---opcodes in testsute but not in the catalog: ", len(testsute_not_in_catalog))
    for item in testsute_not_in_catalog:
        print (item)
sys.stdout = old_stdout
import os
print (f"...{sys.argv[0].split(os.path.sep)[-1]} done")


'''catalog_f = open('catalog_opcodes.txt', 'r')
log_f = open('log_opcodes.txt', 'r')

catalog_lines = catalog_f.readlines()
log_lines = log_f.readlines()

catalog_f.close()
log_f.close()

catalog_lines = [x.strip() for x in catalog_lines]
log_lines = [x.strip() for x in log_lines]
#print ("catalog_lines: ", catalog_lines)

log_uniq_lines = []
catalog_uniq_lines = []
common_lines = []
for line in catalog_lines:
    if line not in log_lines:
        catalog_uniq_lines.append(line)
    else:
        common_lines.append(line)

for line in log_lines:
    if line not in catalog_lines:
        log_uniq_lines.append(line)



print ("num of log_uniq_lines: ", len(log_uniq_lines))  
print ("num of catalog_uniq_lines: ", len(catalog_uniq_lines))
print ("num of common_lines: ", len(common_lines))

log_uniq_f = open('log_uniq_opcodes.txt', 'w')
for line in log_uniq_lines:
    log_uniq_f.write(line + '\n')
log_uniq_f.close()'''


####