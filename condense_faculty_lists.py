#!/usr/bin/env python3
# Author:   Michael E. Rose <michael.ernst.rose@gmail.com>
"""Combines faculty information for faculty members
with Scopus IDs and PhD.
"""

from collections import Counter
from math import log10
from pathlib import Path

import pandas as pd
from numpy import nan

SOURCE_FOLDER = Path("./source_files/")
MAPPING_FOLDER = Path("./mapping_files/")
TARGET_FILE = Path("./hasselback.csv")


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


def read_hasselback_file(fname, scopus, aff_map, degree_incl=('PHD',),
                         rank_excl=('Retir', 'Emer', 'Deces', 'Visit')):
    """Read and compile file, subsetted to relevant degress only."""
    year = fname.stem.split("-")[0]
    df = pd.read_csv(fname).dropna(subset=["dep"])
    df = df[df['degree'].isin(degree_incl)]
    df = df[~df['rank'].isin(rank_excl)]
    df = df[~df["annotation"].fillna("").str.startswith("visiting from")]
    # Aggregate entries
    df['grad_year'] = df['grad_year'].apply(complete_year)
    df['school'] = df['school'].replace(aff_map)
    id_cols = ['name', 'school', 'grad_year']
    df['ID'] = df[id_cols].fillna("").apply(lambda l: ";".join(l), axis=1)
    df['ID'] = df['ID'].str.replace(";;", ";").str.strip(";")
    # Aggregate departments
    missing = []
    for dep in df["dep"].unique():
        if dep not in aff_map:
            missing.append(dep)
    df['dep'] = df['dep'].apply(lambda x: aff_map.get(x))
    before = df.shape[0]
    df = df.dropna(subset=["dep"]).set_index('ID').drop(columns='grad_year')
    after = df.shape[0]
    print(f">>> {year}: Dropping {before-after} names because of missing "
          "department data")
    # Merge with Scopus
    df = df.join(scopus)
    identified = df[~df['scopus_id'].isnull()].copy()
    identified = identified.set_index("scopus_id").add_prefix(year + "_")
    unidentified = df[df['scopus_id'].isnull()][["dep"]].copy()
    return identified, unidentified, missing


def main():
    # Read in
    scopus = pd.read_csv(MAPPING_FOLDER/"persons.csv", index_col=0)
    inst_map = pd.read_csv(MAPPING_FOLDER/"institutions.csv", index_col=0)
    inst_map = inst_map.dropna(subset=['our_name'])
    inst_map = inst_map["our_name"].to_dict()
    files = sorted(SOURCE_FOLDER.glob("*.csv"),
                   key=lambda s: f"{s.stem[1]}{s.stem[4]}{s.stem[0]}")
    df, unidentified, missing = read_hasselback_file(files[0], scopus[["scopus_id"]], inst_map)
    for file in files[1:]:
        new, new_un, new_miss = read_hasselback_file(file, scopus[["scopus_id"]], inst_map)
        df = df.join(new, how="outer")
        missing.extend(new_miss)
        unidentified = pd.concat([unidentified, new_un])

    # Add time-invariant information
    scopus = scopus.drop_duplicates(subset="scopus_id").set_index("scopus_id")
    df = df.join(scopus)

    # Maintenance file
    unidentified = unidentified[~unidentified.index.duplicated()]
    unidentified = unidentified.sort_index()
    unidentified.to_csv("./mapping_files/unmapped.csv", index_label="faculty")
    print(f">>> {unidentified.shape[0]:,} individuals from "
          f"{unidentified['dep'].nunique():,} different universities without ID")

    # Write out
    df.index = df.index.astype("uint64")
    df.to_csv(TARGET_FILE, index_label="scopus_id", float_format="%.0f")

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

    missing = Counter(missing)
    print(f">>> Found {len(missing):,} institutions w/o mapping:")
    print(missing)


if __name__ == '__main__':
    main()
