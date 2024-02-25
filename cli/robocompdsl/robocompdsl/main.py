#!/usr/bin/env python3

# TODO
#
# Read ports from component-ports.txt for the files in etc.
#
#
from typing import Optional, List
from pathlib import Path
import typer
import os
import sys
import pyparsing
import rich
from rich.console import Console

from robocompdsl.common.filesgenerator import FilesGenerator

DESCRIPTION_STR = """\
This application create components files from cdsl files or .ice from idsl
    a) to generate code from a CDSL file:\t{name}    INPUT_FILE.CDSL    OUTPUT_PATH
    b) to generate a new CDSL file:\t\t{name}    NEW_COMPONENT_DESCRIPTOR.CDSL
    c) to generate .ice from a IDSL file:\t{name}    INPUT_FILE.idsl    OUTPUT_FILE_PATH.ice
"""

app = typer.Typer(help=DESCRIPTION_STR)

console = Console()

DIFF_TOOLS = ["meld", "kdiff3", "diff"]

DUMMY_CDSL_STRING = """import "import1.idsl";
import "import2.idsl";

Component <CHANGETHECOMPONENTNAME>
{
    Communications
    {
        implements interfaceName;
        requires otherName;
        subscribesTo topicToSubscribeTo;
        publishes topicToPublish;
    };
    language Cpp//Cpp11//python;
    gui Qt(QWidget//QDialog//QMainWindow);
    //options dsr, agmagent, InnerModelViewer;
    statemachine "statemachine.smdsl";
};\n\n"""

DUMMY_SMDSL_STRING = """
/* CHANGE THE NAME OF THE MACHINE IF YOU MAKE
   ANY CHANGE TO THE DEFAULT STATES OR TRANSITIONS */

defaultMachine{
    states compute;
    initial_state initialize;
    end_state finalize;
    transitions{
        initialize => compute;
        compute => compute;
        compute => finalize;
    };
};


/* --------------------------------------------------------------
   This is the accepted syntax for the State Machine definition 

name_machine{
    [states name_state *[, name_state];]
    [initial_state name_state;]
    [end_state name_state;]
    [transitions{
        name_state => name_state *[, name_state];
        *[name_state => name_state *[, name_state];]
    };]
};

[:parent_state [parallel]{
    states name_state *[, name_state];
    [initial_state name_state;]
    [end_state name_state;]
    [transitions{
        name_state => name_state *[, name_state];
        *[name_state => name_state *[, name_state];]
    };]
};]

------------------------------------------------------------------ */\n"""


def generate_dummy_CDSL(path):
    """
    This function takes a path as an input parameter and checks if the file at
    that path exists. If it does exist already then its just print a warning to
    console and exits from function otherwise  if file does not exist ,then generate
    and write contents of the string called 'DUMMY_CDSL_STRING' with name derived
    from path name and writes to a file specified by path.

    Args:
        path (str): The `path` input parameter is a file path where the generated
            CDSL will be saved to disk. It determines the output file name and
            location based on its directory path and file name.

    """
    if os.path.exists(path):
        console.print(f"File {path} already exists.\nNot overwritting.", style='yellow')
    else:
        console.print(f"Generating dummy CDSL file: {path}")

        name = path.split('/')[-1].split('.')[0]
        string = DUMMY_CDSL_STRING.replace('<CHANGETHECOMPONENTNAME>', name)
        open(path, "w").write(string)


def generate_dummy_SMDSL(path):
    """
    This function checks if a given file path exists. If it does exist and if the
    user runs this command again then the function only displays a message stating
    that the file exists (in yellow color).  If the file does not exist however
    it creates the dummy SMDSL file at the given path. The text contained within
    DUMMY_SMDSL_STRING gets written to the new file.

    Args:
        path (list): The `path` input parameter is the file path where the generated
            dummy SMDSL file will be saved. It determines the location of the
            output file and checks if the file already exists before generating it.

    """
    if os.path.exists(path):
        console.print(f"File {path} already exists.\nNot overwritting.", style='yellow')
    else:
        console.print(f"Generating dummy SMDSL file: {path}", style='green')

        open(path, "w").write(DUMMY_SMDSL_STRING)


@app.command()
def generate(
        input_file: str = typer.Argument(..., help="The input dsl file"),
        output_path: Optional[str] = typer.Argument(None, help="The path to put the generated files"),
        include_dirs: List[Path] = typer.Option([],  "--include_dirs", "-I", help="List of directories to find includes."),
        diff: bool = typer.Option(False, "--diff", "-d", help="Show the diff of the old and new files"),
        test: bool = typer.Option(False, "--test", "-t",  help="Testing option")
):
    """
    This function takes a few inputs that define options and then execute a generator
    to process a DSL input file for a language based on the options selected (either
    CDSL or SMDSL) with options as follows:
    - 'output_path': if set will place output files there
    - 'include_dirs': option list of directories from where includes go (can be
    .idsl and others to be specified with flag)
    -'diff': whether it wants a difference between generated version of the original
    file.
    and based on input_file and whether includes and outputs options were found
    run corresponding generation routines. if inputs other than options passed to
    the program that end with '.idsl', warning is printed

    Args:
        input_file (typer.Argument(..., help="The input dsl file")): The input_file
            input parameter takes a string representing the name of an file to be
            processed by the generate() function.
        output_path (typer.Argument(None, help="The path to put the generated
            files")): The output path is optional parameter that the function takes
            to indicate where the generated files will go; if not specified an
            error will be raised unless input file has ".cdsl" extension
        include_dirs (typer.Option([],  "--include_dirs", "-I", help="List of
            directories to find includes.")): The include_dirs parameter is a list
            of directories that contains header files. The purpose of the header
            file directory list to the Generator program to find the includes while
            building the final file
        diff (typer.Option(False, "--diff", "-d", help="Show the diff of the old
            and new files")): Based on the provided function signature `diff`, is
            an input parameter that sets whether to display a diff between the
            previous version of the generated files and the current version if the
            generation procedure changes the contents of the file. In other terms
            ` diff` decides wether or not the generated output needs to be
            differentiated by color when displayed for better understanding while
            running test files and verification  of newly made outputs versus
            before ones with modifications included during generation
        test (typer.Option(False, "--test", "-t",  help="Testing option")): The
            'test' input parameter is an optional parameter of type Boolean which
            defaults to false (off).  When tested 'True' and executing generate
            function , then the program will only show messages if there are no
            errors . otherwise display the generated file.

    Returns:
        int: The function returns an integer value:
        
        0 - if input file has the correct format and output generation completed
        successfully
        -1 - If there is a parsing error while generating files

    """
    if output_path is None:
        if input_file.endswith(".cdsl"):
            generate_dummy_CDSL(input_file)
            generate_dummy_SMDSL("statemachine.smdsl")
            sys.exit(0)
        else:
            print(output_path, input_file)
            print("No output path with non .cdsl file")
            sys.exit(-1)
    if input_file.endswith(".idsl"):
        include_dirs.append(Path(input_file).absolute().parents[0])
    for i_dir in include_dirs:
        if not i_dir.is_dir():
            console.log(f"{i_dir} directory in -I option  not exists")
            return -1
    if input_file.endswith(".cdsl") or input_file.endswith(".jcdsl") or input_file.endswith(".idsl"):
        try:
            # print("To generate", input_file, output_path, include_dirs, diff, test)
            FilesGenerator().generate(input_file, output_path, include_dirs, diff, test)
        except pyparsing.ParseException as pe:
            console.log(f"Error generating files for {rich.Text(input_file, style='red')}")
            console.log(pe.line)
            console.log(' ' * (pe.col - 1) + '^')
            console.log(pe)
            exit(-1)
    else:
        console.print("Please check the Input file \n" + "Input File should be either .cdsl or .idsl")
        sys.exit(-1)


if __name__ == '__main__':
    app()
