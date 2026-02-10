"""
Convert `JSON` to `CSV`, `Excel` and `LaTeX`.

This script reads `material_data.json`, puts
the data in pandas dataframes and then saves
them in four `.csv` files, one `.xlsx` file
and one `.tex` file (using `longtable` environments).
The four `.csv`, the `.xlsx` and the `.tex` files
contain the same information. Two other `JSON`
files, `field_names.json` and `filenames.json`,
are accessed. They contain proper names
for the material parameter names
and the output file names respectively.
"""

import json
import pandas as pd
import collections.abc


def check_coeff(string, entry):
    """Read key *string* of dictionary *entry*, and if non-existent, default to 0."""
    if string in entry:
        coeff = str(entry[string])
    else:
        coeff = str(0.0)
    return coeff


def read_entry(entry):
    """
    Read dictionary *entry* and parse (some of) its keywords.

    Reads the contents of keys:
        - "a0", "ax", "ay", "axx", "axy", "ayy", "axxx",
          "axxy", "axyy" and "ayyy" if "quaternary" is `True`,
          and a string representing a polynomial with those
          coefficients is saved as *value*
          (if the keys do not exist, 0 is returned for each)
        - "a0", "ax" and "axx" if the above does not hold
          and "ternary" is `True`, and a string representing
          a polynomial with those coefficients is saved as *value*
          (if the keys do not exist, 0 is returned for each)
        - "value" if none of the above holds, which is saved in *value*
          (if the key does not exist, "N/A" is returned)
        - "units", "sources" and "notes" in any case,
          stored in *units*, *citekey* (if an iterable,
          the entries are glued together in a string
          using commas) and *notes* respectively
          (if the keys do not exist, "N/A" is returned for each)

    Parameters
    ----------
    entry : dictionary

    Returns
    -------

    value : *Any (expected array of numbers)*
    units : *Any (expected string)*
    citekey : *Any (expected string with no whitespace)*
    notes : *Any (expected string)*
    """
    if "quaternary" in entry and entry["quaternary"] is True:
        a0 = check_coeff("a0", entry)
        ax = check_coeff("ax", entry)
        ay = check_coeff("ay", entry)
        axx = check_coeff("axx", entry)
        axy = check_coeff("axy", entry)
        ayy = check_coeff("ayy", entry)
        axxx = check_coeff("axxx", entry)
        axxy = check_coeff("axxy", entry)
        axyy = check_coeff("axyy", entry)
        ayyy = check_coeff("ayyy", entry)
        value = (
            a0
            + " + "
            + ax
            + "x + "
            + ay
            + "y + "
            + axx
            + "x^{2} + "
            + axy
            + "xy + "
            + ayy
            + "yy + "
            + axxx
            + "x^{3} + "
            + axxy
            + "x^{2}y + "
            + axyy
            + "xy^{2} + "
            + ayyy
            + "y^{3}"
        )
    elif "ternary" in entry and entry["ternary"] is True:
        a0 = check_coeff("a0", entry)
        ax = check_coeff("ax", entry)
        axx = check_coeff("axx", entry)
        value = a0 + " + " + ax + "x + " + axx + "x^{2}"
    elif "value" in entry:
        value = entry["value"]
    else:
        value = "N/A"

    if "units" in entry:
        units = entry["units"]
    else:
        units = "N/A"

    if "sources" in entry:
        temp = entry["sources"]
        if isinstance(temp, collections.abc.Sequence) and not isinstance(temp, str):
            citekey = ""
            for i, citation in enumerate(entry["sources"]):
                if i != 0:
                    citekey = citekey + ","
                citekey = citekey + citation
        else:
            citekey = temp
    else:
        citekey = "N/A"

    if "notes" in entry:
        notes = entry["notes"]
    else:
        notes = "N/A"

    return value, units, citekey, notes


# open all the `JSON`
with open("material_data.json", encoding="utf-8") as f:
    d = json.load(f)

with open("field_names.json", encoding="utf-8") as f:
    names = json.load(f)

with open("filenames.json", encoding="utf-8") as f:
    files = json.load(f)

# run through all the materials once, and
# save all the different parameter keys
index_list = []
index_names = []
for material, data in d.items():
    for field, contents in data.items():
        if field not in index_list and field != "full_name":
            index_list.append(field)
            if field in names:
                # use the names provided in "field_names.json"
                # for the parameter fields, if they exist
                index_names.append(names[field])
            else:
                # else, use the key itself
                index_names.append(field)

# run through the materials again,
# and extract the data for all the parameters
dict_value = {}
dict_units = {}
dict_citekey = {}
dict_notes = {}
for material, data in d.items():
    if "full_name" in data:
        material_name = data["full_name"]
    else:
        material_name = material
    value_list = []
    units_list = []
    citekey_list = []
    notes_list = []
    for index in index_list:
        if index not in data:
            value = "N/A"
            units = "N/A"
            citekey = "N/A"
            notes = "N/A"
        else:
            value, units, citekey, notes = read_entry(data[index])
        value_list.append(value)
        units_list.append(units)
        citekey_list.append(citekey)
        notes_list.append(notes)

    # save the data in a list of `pd.Series`
    dict_value[material_name] = pd.Series(data=value_list, index=index_names)
    dict_units[material_name] = pd.Series(data=units_list, index=index_names)
    dict_citekey[material_name] = pd.Series(data=citekey_list, index=index_names)
    dict_notes[material_name] = pd.Series(data=notes_list, index=index_names)

df_values = pd.DataFrame(dict_value)
df_units = pd.DataFrame(dict_units)
df_citekey = pd.DataFrame(dict_citekey)
df_notes = pd.DataFrame(dict_notes)

# save to `.csv`
df_values.to_csv(files["values_csv"] + ".csv")
df_units.to_csv(files["units_csv"] + ".csv")
df_citekey.to_csv(files["citekey_csv"] + ".csv")
df_notes.to_csv(files["notes_csv"] + ".csv")

# save to `.xlsx`
with pd.ExcelWriter(files["excel"] + ".xlsx") as writer:
    df_values.to_excel(writer, sheet_name="Values")
    df_units.to_excel(writer, sheet_name="Units")
    df_citekey.to_excel(writer, sheet_name="References")
    df_notes.to_excel(writer, sheet_name="Notes")
    for name, sheet in writer.sheets.items():
        sheet.autofit()

# save to `.tex`
with open(files["latex_tables"] + ".tex", "w", encoding="utf-8") as f:
    f.write(
        df_values.style.format("{}", escape="latex").to_latex(
            column_format=(len(dict_value) + 1) * "p{1.5 cm}", environment="longtable"
        )
    )
    f.write("\n")
    f.write(
        df_units.style.format("${}$").to_latex(
            column_format=(len(dict_value) + 1) * "p{1.5 cm}", environment="longtable"
        )
    )
    f.write("\n")
    f.write(
        df_citekey.style.format(r"\cite{{{}}}", escape="latex").to_latex(
            column_format=(len(dict_value) + 1) * "p{1.5 cm}", environment="longtable"
        )
    )
    f.write("\n")
    f.write(
        df_notes.style.format("{}", escape="latex").to_latex(
            column_format=(len(dict_value) + 1) * "p{1.5 cm}", environment="longtable"
        )
    )
