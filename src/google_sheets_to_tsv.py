#!/usr/bin/env python3
from pathlib import Path
import pandas as pd

SHEET_ID = "1LkeHNxWd5eltpbbYzH2aocMpnZjpIS7PpwXFk9d5ggg"

# Map tab names -> gids (fill in the real gid values)
TABS = {
    "WMBT_annotation": "0",
}

OUTDIR = Path(__file__).resolve().parents[1] / "curation_tables"
OUTDIR.mkdir(parents=True, exist_ok=True)


def strip_prefix(name: str, prefix: str) -> str:
    pref = prefix + "_"
    return name[len(pref) :] if name.startswith(pref) else name


for tab_name, gid in TABS.items():
    url = (
        f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=tsv&gid={gid}"
    )

    # Read TSV via pandas
    df = pd.read_csv(url, sep="\t")

    # Sort by the first column
    if not df.empty:
        first_col = df.columns[0]
        df = df.sort_values(by=first_col, kind="mergesort", na_position="last")

    # Output file name (strip "WMBT_" prefix)
    out_name = strip_prefix(tab_name, "WMBT") or "sheet"
    out_file = OUTDIR / f"{out_name}.tsv"

    # Write TSV with LF endings
    df.to_csv(out_file, sep="\t", index=False, lineterminator="\n")
    print(f"Saved {out_file}")
