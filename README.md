# semiconductors_catalogue

A collection of semiconductor parameters in JSON format
and a Python script to export them in `CSV`,
`Excel` and `LaTeX` form. It should be available
at <>.

## Installation

### With Git

Open a terminal, navigate to the directory where
you want to place the `semiconductors_catalogue` folder
and type

        git clone 

After that, you can get the newest version by
entering the `semiconductors_catalogue` folder and
typing

        git pull

### Without Git


## Requirements

A somewhat recent version of `LaTeX` is likely needed. I have only tested
with a 2025 `MiKTeX` version (25.4), but any relatively recent
installation should do the trick.
Both `LuaLaTeX` and `biber` are needed, though.
The necessary packages are listed in the preamble of
`table_summary.tex`.

A recent `Python` installation with the packages `pandas` and
`xlsxwriter` is likely needed (tested with `Python 3.12.4`, `pandas 3.0.0`
and `xlsxwriter 3.2.9`).

## Usage

The material data are stored in `material_data.json`.
New entries can be added straightforwardly by mirroring those already in place.
The new entries can have new names, but any new keys within them
will be disregarded. `field_names.json` contains the labels that will be used
in the `Excel` and `LaTeX` files for the material
parameters. `filenames.json` contains the file names
(*without file formats*) for the output of the `Python` script.

After modifying `material_data.json`, run the Python script,

        python json_to_csv.py

to update the `CSV` and `Excel` files and produce
new tables for `LaTeX`. `table_summary.tex` takes
those tables, stored in a separate `.tex` file,
and typesets them. To compile the document, open a terminal
in the `semiconductors_catalogue` folder and type

        lualatex table_summary.tex
        biber table_summary
        lualatex table_summary.tex

`sources.bib` contains `BibLatex` entries for the sources
from which material data was taken.
