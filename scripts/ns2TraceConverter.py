# Script to convert TCL mobility traces and specify a new starting time
# The script reads the input file and produces a new TCL file in which the 
# time instants are equal to the previous values minus the time offset

import sys

if (len (sys.argv) != 3):
    print ("Pass two cmd line argument\n(1) path of the file to convert\n(2) time offset in seconds")
    exit ()
    
filename = sys.argv[1]
timeOffset = float (sys.argv[2])
file = open (filename, "r")

for l in file:
    tokens = l.split ()
    if ((tokens [0] == "$ns_") & (tokens [1] == "at")):
        tokens [2] = str (round (float (tokens [2]) - timeOffset, 2))
        newLine = ' '.join (tokens)
        print (newLine)
    else:
        print (l, end="")
    
