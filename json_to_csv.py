import json
import pandas as pd
import collections.abc


def check_coeff(string, entry):
    if string in entry:
        coeff = str(entry[string])
    else:
        coeff = str(0.0)
    return coeff


def read_entry(entry):
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


with open("material_data.json", encoding="utf-8") as f:
    d = json.load(f)

with open("field_names.json", encoding="utf-8") as f:
    names = json.load(f)

with open("filenames.json", encoding="utf-8") as f:
    files = json.load(f)

index_list = []
index_names = []
for material, data in d.items():
    for field, contents in data.items():
        if field not in index_list and field != "full_name":
            index_list.append(field)
            if field in names:
                index_names.append(names[field])
            else:
                index_names.append(field)

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

    dict_value[material_name] = pd.Series(data=value_list, index=index_names)
    dict_units[material_name] = pd.Series(data=units_list, index=index_names)
    dict_citekey[material_name] = pd.Series(data=citekey_list, index=index_names)
    dict_notes[material_name] = pd.Series(data=notes_list, index=index_names)

df_values = pd.DataFrame(dict_value)
df_units = pd.DataFrame(dict_units)
df_citekey = pd.DataFrame(dict_citekey)
df_notes = pd.DataFrame(dict_notes)

df_values.to_csv(files["values_csv"] + ".csv")
df_units.to_csv(files["units_csv"] + ".csv")
df_citekey.to_csv(files["citekey_csv"] + ".csv")
df_notes.to_csv(files["notes_csv"] + ".csv")

with pd.ExcelWriter(files["excel"] + ".xlsx") as writer:
    df_values.to_excel(writer, sheet_name="Values")
    df_units.to_excel(writer, sheet_name="Units")
    df_citekey.to_excel(writer, sheet_name="References")
    df_notes.to_excel(writer, sheet_name="Notes")
    for name, sheet in writer.sheets.items():
        sheet.autofit()

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
