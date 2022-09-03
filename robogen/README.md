robogen — modular code generation tool
======================================

*robogen* is a command-line tool which allows the generation of code from
templates. It is based around a powerful plugin architecture, and most aspects
of the tool can be extended through it: grammars, artifact descriptions,
generation templates and file populators are reachable from plugins.

This tool aims to provide a replacement for _RoboCompDSL_ for component
generation, and a straightforward development framework for future code
generation needs.

Installation
------------

The tool is distributed as a Python package, so `pip` can take care of the
installation. The following commands will install both the command-line tool and
the Python modules for plugins to import, and then check whether the
installation succeeded by running the tool:

```sh
pip install .
robogen --help
```

Some plugins are bundled in the `extras/plugins` directory. These can be
installed to the default plugin directory by running:

```sh
mkdir -fp /opt/robocomp/robogen/plugins
cp -r extras/plugins/* /opt/robocomp/robogen/plugins
```

Usage
-----

The tool can be invoked as follows:

```
robogen [OPTIONS] INPUT_FILE OUTPUT_PATH
```

The `INPUT_FILE` leads to the input artifact description to be processed.
`OUTPUT_PATH` points to the directory where files will be generated. `OPTIONS`
is an optional list of the following command-line flags.

<table>
 <tr>
  <td><code>--plugin-dir <i>path</i></code><br/><code>-P <i>path</i></code></td>
  <td>Add <i>path</i> to the list of paths where <i>robogen</i> will look for
  plugins at initialization.</td>
 </tr>
 <tr>
  <td><code>--import-dir <i>path</i></code><br/><code>-I <i>path</i></code></td>
  <td>Add <i>path</i> to the list of paths where <i>robogen</i> will look for
  files when an include sentence is processed.</td>
 </tr>
</table>

Alternatively, `RG_PLUGIN_DIR` and `RG_IMPORT_DIR` can be set to provide a
plugin and import path respectively.

Status
------

This tool is currently a functional prototype. It delivers all the features
advertised, but there are still some rough edges.

Extras
------

Under the *extras* directory of this repository, development material and
examples can be found. The contents of this directory may change at any time
and without prior notice, and are included only for testing and completeness
purposes.

