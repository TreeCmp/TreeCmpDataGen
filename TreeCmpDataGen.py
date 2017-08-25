#!/usr/bin/env python

import sys
import subprocess
import csv
import os

IT_NUM = 1
UNROOTED = 5
ROOTED = 4
MIN_N = min(ROOTED, UNROOTED)
END = 1000

rooted = 'r'

refTreePath = "newicks/reference_tree.newick"
outFilePath = "data/out.txt"
dataFilePath = "data/data.csv"


def print_distances():
    print("""Specify correct distance (only 1 of 11 available):
    Metrics for unrooted trees:
    ms - the Matching Split metric,
    rf - the Robinson-Foulds metric,
    pd - the Path Difference metric,
    qt - the Quartet metric,
    um - the UMAST metric,
    Metrics for rooted trees:
    mc - the Matching Cluster metric,
    rc - the Robinson-Foulds metric based on clusters,
    ns - the Nodal Splitted metric with L2 norm,
    tt - the Triples metric,
    mp - the Matching Pair metric.
    mt - the RMAST metric.""")

###############################
# read args from command line #
###############################

if len(sys.argv) <= 1:
    print_distances()
    exit(1)
else:
    distance = sys.argv[1]

if distance == 'ms' or distance == 'rf' or distance == 'pd' or distance == 'qt' or distance == 'um':
        rooted = 'u'
elif distance == 'mc' or distance == 'rc' or distance == 'ns' or distance == 'tt' or distance == 'mp' or distance == 'mt':
        rooted = 'r'
else:
    print_distances()
    exit(1)

if distance == 'ms' or distance == 'rf' or distance == 'qt' or distance == 'um' or distance == 'mc' or distance == 'rc' or distance == 'tt' or distance == 'mp' or distance == 'mt':
    resultType = 'int'
elif distance == 'pd' or distance == 'ns':
    resultType = 'float'
else:
    print_distances()
    exit(1)

if len(sys.argv) <= 2:
    print("""Specify correct generated trees type:
        e - uniform trees,
        y - Yule trees""")
    exit(1)
else:
    treesType = sys.argv[2]

if len(sys.argv) > 3:
    beg = int(sys.argv[3])
else:
    if rooted == "r":
        beg = ROOTED
    elif rooted == "u":
        beg = UNROOTED
    else:
        print("Undefined that tree is rooted or not")
        exit(1)

if len(sys.argv) > 4:
    end = int(sys.argv[4])
else:
    end = END

if len(sys.argv) > 5:
    itNum = int(sys.argv[5])
else:
    itNum = IT_NUM

##############################################
# creating trees database files if not exist #
##############################################

if not os.path.exists("data"):
    os.makedirs("data")
if not os.path.exists("newicks"):
    os.makedirs("newicks")

for n in range(beg, end+1):
    inputTreesPath = "newicks/n" + str(n) + "_" + treesType + "_trees.newick"
    if not os.path.exists(inputTreesPath):
        subprocess.check_call(["exe/PRTGen.exe", "-n", str(n), "-" + treesType, "1", "-" + rooted, "-f", inputTreesPath])

###################
# load data files #
###################

data = [[] for i in range(end-MIN_N+1)]
newData = []

if os.path.exists(dataFilePath):
    with open(dataFilePath, 'r') as csvFile:
        reader = csv.reader(csvFile, lineterminator='\n')
        if resultType == "int":
            data = [[int(e) for e in r] for r in reader]
        elif resultType == "float":
            data = [[float(e) for e in r] for r in reader]

n = beg
it = 1

#########################################################
# generate new tree and compute distance to each others #
#########################################################

while True:

    inputTreesPath = "newicks/n" + str(n) + "_" + treesType + "_trees.newick"
    subprocess.check_call(["exe/PRTGen.exe", "-n", str(n), "-" + treesType, "1", "-" + rooted, "-f", refTreePath])
    subprocess.check_call(["java", "-jar", "exe/treeCmp.jar", "-r", refTreePath, "-d", distance, "-i", inputTreesPath, "-o", outFilePath])

    outFile = open(outFilePath, 'r')
    outFileLines = outFile.readlines()
    newData.clear()

    for i in range(1, len(outFileLines)):
        res = outFileLines[i].split("\t")
        if resultType == "int":
            newData.append(int(float(res[3].replace('\n', ''))))
        elif resultType == "float":
            newData.append(float(res[3].replace('\n', '')))
        else:
            print("Undefined result type")
            exit(1)

    if 0 not in newData:
        data[n-MIN_N].extend(newData)
        inputTreesFile = open(inputTreesPath, "a")
        refTreeFile = open(refTreePath, "r")
        inputTreesFile.write(refTreeFile.read())
        inputTreesFile.close()
        refTreeFile.close()

    if n == end:
        if it == itNum:
            break;
        it += 1
        n = beg
    else:
        n += 1

    outFile.close()

with open(dataFilePath, 'w') as csvFile:
    writer = csv.writer(csvFile, lineterminator='\n')
    [writer.writerow(r) for r in data]
