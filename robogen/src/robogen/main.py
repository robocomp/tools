#!/bin/python3

import os
import typer

from typing import List

from robogen.artifact  import ImportManager
from robogen.generator import GeneratorManager
from robogen.plugin    import PluginManager

app = typer.Typer(help='''\
This application creates components from a component description file or .ice
files from interface description files.

usage: {name} [OPTIONS] COMPONENT PATH

Arguments:
  COMPONENT  Input file to drive the generation
  PATH       Destination for the generated files

Options:
  --plugin-dirs  Set list of directories to look for plugins
  --import-dirs  Set list of directories to look for import files
  --diff         Diff `.new' files against their old counterparts''')

@app.command()
def generate(
    input_file:  str       = typer.Argument(..., help='Input file to drive the generation'),
    output_path: str       = typer.Argument(..., help='Destination for the generated files'),
    plugin_dirs: List[str] = typer.Option([], '--plugin-dir', '-P', help='Add directory to look for plugins'),
    import_dirs: List[str] = typer.Option([], '--import-dir', '-I', help='Add directory to look for import files'),
    diff_tool:   str       = typer.Option(None, '--diff', '-d', help="Diff `.new' files against their old counterparts")
):
    '''Entry point for the application.'''

    for entry in plugin_dirs:
        PluginManager.add_path(entry)

    # Add plugin paths
    PluginManager.add_path('/opt/robocomp/robogen/plugins')
    if 'RG_PLUGIN_DIR' in os.environ:
      PluginManager.add_path(os.environ['RG_PLUGIN_DIR'])
    for plugin_dir in plugin_dirs:
      PluginManager.add_path(plugin_dir)

    # Add import paths
    ImportManager.add_path('/opt/robocomp/interfaces/IDSLs')
    if 'RG_IMPORT_DIR' in os.environ:
      ImportManager.add_path(os.environ['RG_IMPORT_DIR'])
    for import_dir in import_dirs:
      ImportManager.add_path(import_dir)

    # Run!
    PluginManager.load_plugins()
    GeneratorManager.set_diff_tool(diff_tool)
    GeneratorManager().generate_files(input_file, output_path)

if __name__ == '__main__':
    app()
