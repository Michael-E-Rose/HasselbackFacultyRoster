#!/usr/bin/env python3
# Author:   Michael E. Rose <michael.ernst.rose@gmail.com>
"""Combines faculty information for faculty members
with Scopus IDs and PHD.
"""

from collections import Counter
from glob import glob
from math import log10
from os.path import basename, splitext

import pandas as pd
from numpy import nan

SOURCE_FOLDER = "./source_files/"
SCOPUS_FILE = "./mapping_files/persons.csv"
MAPPING_FILE = "./mapping_files/institutions.csv"
TARGET_FILE = "./hasselback.csv"


def complete_year(y):
    """Complete a year by adding missing century digits."""
    # Keep the following try-except until all numbers are correct
    try:
        y = int(y)
    except ValueError:
        return None
    try:
        digits = int(log10(y)) + 1
    except ValueError:  # y is 0
        return str(2000)
    if digits == 2:
        return str(1900 + y)
    elif digits == 1:
        return str(2000 + y)
    elif digits == 3:
        return str(1000 + y)
    else:
        return str(y)


def read_hasselback_file(fname, scopus, aff_map, degrees=('PHD',)):
    """Read and compile file, subsetted to relevant degress only."""
    year = splitext(basename(fname))[0].split("-")[0]
    df = pd.read_csv(fname).dropna(subset=["dep"])
    df = df[df['degree'].isin(degrees)]
    # Aggregate entries
    df['grad_year'] = df['grad_year'].apply(complete_year)
    df['school'] = df['school'].apply(lambda x: aff_map.get(x, x))
    id_cols = ['name', 'school', 'grad_year']
    df['ID'] = df[id_cols].fillna("").apply(lambda l: ";".join(l), axis=1)
    df['ID'] = df['ID'].str.replace(";;", ";").str.replace("nan", "").str.strip(";")
    # Aggregate departments
    df['dep'] = df['dep'].apply(lambda x: aff_map.get(x))
    before = df.shape[0]
    df = df.dropna(subset=["dep"]).set_index('ID').drop('grad_year', axis=1)
    after = df.shape[0]
    print(f">>> {year}: Dropping {before-after} names because of missing "
          "department and graduation year data")
    # Merge with Scopus
    df = df.merge(scopus, "left", left_index=True, right_index=True)
    identified = df[~df['scopus_id'].isnull()].copy()
    identified = identified.set_index("scopus_id").add_prefix(year + "_")
    unidentified = df[df['scopus_id'].isnull()][["dep"]].copy()
    return identified, unidentified


def main():
    # Read in
    scopus = pd.read_csv(SCOPUS_FILE, index_col=0)
    mapping = pd.read_csv(MAPPING_FILE, index_col=0).dropna(subset=['our_name'])
    mapping = mapping["our_name"].to_dict()
    files = glob(SOURCE_FOLDER + "*.csv")
    df, unidentified = read_hasselback_file(files[0], scopus[["scopus_id"]], mapping)
    for file in files[1:]:
        new, new_un = read_hasselback_file(file, scopus[["scopus_id"]], mapping)
        df = df.merge(new, "outer", left_index=True, right_index=True)
        unidentified = unidentified.append(new_un)

    # Add time-invariant information
    scopus = scopus.drop_duplicates(subset="scopus_id")
    scopus = scopus.set_index("scopus_id")
    df = df.merge(scopus[["scopus_name", 'grad_year']], "left",
                  left_index=True, right_index=True)

    # Maintenance file
    unidentified = unidentified[~unidentified.index.duplicated()]
    unidentified.to_csv("./mapping_files/unmapped.csv", index_label="faculty")
    print(f">>> {unidentified.shape[0]:,} individuals from "
          f"{unidentified['dep'].nunique():,} different universities without ID")

    # Write out
    df.index = df.index.astype(int)
    df.to_csv(TARGET_FILE, index_label="scopus_id")

    # Statistics
    dep = set()
    dep_cols = [c for c in df.columns if c.endswith("dep")]
    for dep_col in dep_cols:
        dep.update(set(df[dep_col]))
    print(f">>> {df.shape[0]:,} individuals from {len(dep):,} different "
          "universities with ID")
    all_deps = dep.union(set(unidentified["dep"]))
    stats = {"N_of_Hasselback_fac_scopus": f"{df.shape[0]:,}",
             "N_of_Hasselback_dep_scopus": len(dep),
             "N_of_Hasselback_fac": f"{df.shape[0] + unidentified.shape[0]:,}",
             "N_of_Hasselback_dep": len(all_deps)}
    print(stats)


if __name__ == '__main__':
    main()
