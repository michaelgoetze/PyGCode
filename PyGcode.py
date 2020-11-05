#!/usr/bin/env python
'''A script that introduces python functionalities into Slic3r and PrusaSlicer gcodes. 
The script exepects a .gcode file as input and runs the embedded python code to generate a new
gcode file. run python PyGcode.py -h for help.'''

__author__ = "Michael Götze"
__copyright__ = "Copyright 2020, Michael Götze"
__credits__ = ["Michael Götze"]
__license__ = "GPLv3"
__version__ = "0.1"
__maintainer__ = "Michael Götze"
__email__ = "logdogdeveloper@gmail.com"

import sys
import os
import argparse
import shutil
import re
import tempfile

# List of Program arguments
parser = argparse.ArgumentParser(
    description='''A script that introduces python functionalities into Slic3r and PrusaSlicer gcodes.

##########################################################################

Pattern recognition:

    A pattern (;Python), followed by ':' indicates a single line command. e.g.
    e.g.:

        ;Python: print('M106 S255 ;Turn fan on to max') # this comment will not end up in the gcode but the comment after ';' will

    The pattern, followed by '<' will open a code-block, while the string, 
    followed by '>' will close the code block. 
    e.g.:

        ;Python< Any code/text written in this line will be ignored!!!
        ;for i in range(200,1000, 50):
        ;    print("G1 E0.5 F"+i) #Extrude 0.5 mm with increasing speed
        ;Python> Any code/text written in this line will also be ignored!!!

##########################################################################
############################ IMPORTANT ###################################
##########################################################################

Special characters:

    Square and Curly brackets cannot be used in any of the code blocks! They have to be replaced by the following

    Square brackets e.g. [AnyCode] must be replaced by <(AnyCode)>
    Curly brackets e.g. {AnyOtherCode} must be replaced by <~(AnyOtherCode)~>

##########################################################################

Macro Values 
    It is possible to save PrusaSlicer or Slic3R makro values to python variables.
    See https://help.prusa3d.com/en/article/makros_6261 for more details on macros.
    e.g.:

    ;Python: t = {temperature[0]} # retrieves the extruder temperature for the first filament slot

##########################################################################

Uncommenting
    All lines of code can also be g-code uncommented without semicolon. The original file might not be prinatble then!!

        ;Python<
        ;for i in range(200,1000, 50):
        ;    print("G1 E0.5 F"+str(i)) #Extrude 0.5 mm with increasing speed
        ;Python>

''', formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('input', type=str, help='relative path to gcode file that should be modified')
parser.add_argument('-o', '--override', action='store_true', help = 'Override original Gcode file, without creating a copy of the original')
parser.add_argument('-ext', '--extension', 
                    required=False,
                    default = '.gcode',
                    help='replace .gcode extension by this extension (e.g. _py.gcode)')
parser.add_argument('-p', '--pattern', 
                    required=False,
                    default = ';Python',
                    help='''Pattern of the String that is used to identify python lines. default: ';Python' ''')

##################################
###         Functions          ###
##################################

''' Function that copies a file and renames it to the selected name'''
def copy_rename(old_file_name, new_file_name):
    src_dir= os.getcwd()
    try:
        os.mkdir('temp')
    except FileExistsError:
        pass
    os.listdir()
    temp_dir = src_dir+'/temp'
    src_file = os.path.join(src_dir, old_file_name)
    shutil.copy(src_file,temp_dir) #copy the file to destination dir

    src_copy_file = os.path.join(temp_dir,old_file_name)
    temp_file_name = os.path.join(temp_dir, new_file_name)
    os.rename(src_copy_file, temp_file_name)#rename
    dst_file_name = os.path.join(src_dir, new_file_name)
    shutil.move(temp_file_name, dst_file_name)
    os.rmdir('temp')
    
##################################
###   Command Line Arguments   ###
##################################
    
args = parser.parse_args()

# Check, if input is a valid gcode file by its extension
if not args.input.lower().endswith('.gcode'):
    exit('please provide a gcode file as 1st argument. Run python PyGcode.py -h for help. Ending without processing. Provided input: ' + args.input)
    
print('\nProcessing GCODE file ['+args.input+']')

# If the file should not be overriden (default) then copy the original 
if not args.override:
    original = re.sub('\.gcode', '_original.gcode', args.input, flags=re.IGNORECASE)
    print('\tBacking up original file ['+ original+']')
    copy_rename(args.input, original)
else:
    print('\t-override option: No backup of the original is created')

# Change the extension of the outputFile    
outfile = args.input
if args.extension != '.gcode':
    outfile = re.sub('\.gcode', args.extension, args.input, flags=re.IGNORECASE)
    print('\t-ext option: changing output file from "' + args.input + '" to "'+outfile+'"')
    
# Pattern to detect source code snippets
pattern = args.pattern
if pattern != ';Python':
    print('\t-Pattern option. Code-recognition pattern is changed from ;Python to '+pattern)

    
##################################
# Gcode extraction, script prep  #
##################################

# Variable that records whether the current line is within a code-block or not.
code = False

# Define regex for brackets of the two following types [] and {}. These cannot be used directly as they would be interpreted by the Slicer as a 
# command before finishing the initial gcode file that this script will process.

# Load the Gcode and in parallel write out the python script that will generate the final gcode. Any gcode will just be put in a multiline string.
# Any python code will be saved as is to script.py. This script will then be run and print the output to the new .gcode file

tmp = tempfile.NamedTemporaryFile(delete=False)
tmp.close()
with open(tmp.name,'w') as fout:
    fout.write("print('''")

    with open(args.input) as fin:
        for s in fin:
            if s.lstrip().startswith(pattern + ':'):
                fout.write("''')\n")
                line = s.replace(pattern+':','').strip() +'\n'
                
                line = re.sub('<~\(', '{', line)
                line = re.sub('\)~>', '}', line)
                line = re.sub('<\(', '[', line)
                line = re.sub('\)>', ']', line)
                fout.write(line) 
                fout.write("print('''")              
            elif s.lstrip().startswith(pattern+'<'):
                fout.write("''')\n")
                code = True
            elif s.lstrip().startswith(pattern+'>'):
                fout.write("print('''")
                code = False
            else:
                line = s.rstrip()+ '\n'
                if code:
                    line = re.sub('^;', '', line)
                
                line = re.sub('<~\(', '{', line)
                line = re.sub('\)~>', '}', line)
                line = re.sub('<\(', '[', line)
                line = re.sub('\)>', ']', line)
                fout.write(line)

    if(code==False):
        fout.write("''')")


##################################
###      Gcode generation      ###
##################################

# Run the script to generate the modified gcode file.
print('\nGenerating New Gcode file')
print('> python', tmp.name, args.input,'>'+outfile)
os.system('python '+tmp.name + ' ' + args.input + ' >'+outfile)
os.unlink(tmp.name)
print('\nDone')