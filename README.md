

# PyGcode - extend PrusaSlicer or Slic3r G-code with python

In PrusaSlicer/Slic3r it is possible to run specific gcode at the start (start G-code), at the end (end G-code), before/after layer change or during filament change. These custom G-codes can be set in the printer settings or also filament settings. It is possible to use a macros as a simple pseudo language in these fields. This already enables the use of some basic if/else logic and especially access to variables like the current layer, Z-position, temperatures and the selected filament...

With this postprocessing script, it is possible to run proper python scripts to generate more complex custom G-codes. This way you could just change a variable in the start-gcode and it can effect e.g. all tool changes, include for loops or make more complicated calculations than min() or max(). The options are wide open.

## Usage

You will need python 3 to run this script ([Python 3 Download](https://www.python.org/downloads/)). Simply run this postprocessing script with the generated .gcode-file:

`python PyGcode.py [-h -o -ext -p] <input.gcode>`

e.g.
`python PyGcode.py -ext _py.gcode -o benchy.gcode`

In PrusaSlicer the postprocessing script can be provided as a bat file where the created gcode is passed as an argument. In Windows you can use the batch file `RunPyGcode.bat` that contains the command.

    python "%~dp0\PyGcode.py" -ext _py.gcode -o %1`
    pause`

where `%~dp0` is the relative path to the PyGcode.py file and  `%1` is the path to the exported g-code file.

## Including python code

Python code can be included in any field that will put text into the G-code file. This includes Printer-Settings->Custom G-code and Filament Settings->Custom G-code.
It is possible to include single-line code or multiline code blocks. Anything that is output by python's `print(str)` will end up in the final G-code file. See also the example .gcode file in the example folder.

### Special characters 

**IMPORTANT**

Curly and square brackets cannot be used within the python code block as they would be interpreted by Slic3r or PrusaSlicer and lead to an error. They have to be replaced.

Square brackets e.g. ```[AnyCode]``` must be replaced by ```<(AnyCode)>```
Curly brackets e.g. ```{AnyOtherCode}``` must be replaced by ```<~(AnyOtherCode)~>```

### Single-line command

A single line code starts with the following pattern:

    ;Python:

followed by a python command ('<(' and ')>' replace square brackets)

	;Python: temperatures = <(a for a in range(195, 220, 5))>

### Multi-line code block

A multi-line code block is surrounded by the following pattern:

	;Python<
	python code goes here
	;Python>

Anything between those two lines will be considered as python code. Any text within those surrounding two lines will be ignored

	;Python< This text is ignored
	python code goes here
	;Python> This text as well

The code can be written as is or preceded by a semicolon
	
	;Python<
	for i in range(100,200,20):
	    print("G1 E0.5 F"+str(i))
	;Python>

gives the same output as:

    ;Python<
    ;for i in range(100,200,20):
    ;    print("G1 E0.5 F"+str(i))
    ;Python>
while the latter option will be regarded as comment by a 3D-printer, if the unprocessed gcode file is used.

## Program Arguments

PyGcode.py expects one positional argument that contains the input .gcode-file (see Usage)

### optional arguments
| short | long | function |
|--|--|--|
| `-h` | `--help` | show the help information |
| `-o` | <nobr>`--override`</nobr> | override the original file (do not create a backup<br> of the input file if in combination with -ext) |
| `-ext` | <nobr>`--extension`</nobr> | replace .gcode extension by this extension <br>(e.g. _py.gcode) |
| `-p` | `--pattern` | exchange the `;Python` pattern by a different string |
