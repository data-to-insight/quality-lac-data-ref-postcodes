import re
import sys
from pathlib import Path
from zipfile import ZipFile

import brotli
import msgpack

import pandas as pd

column_mappings = {
    "pcd7": "pcd",
    "east1m": "oseast1m",
    "north1m": "osnrth1m",
    "lad25cd": "laua",
}


def find_postcode_files(data_dir: Path):
    return list(data_dir.glob("*.msgpack.br"))


def read_postcode_file(input_file: Path | str):
    ptn = re.compile(".*NSPD_.*_UK.csv")

    with ZipFile(input_file, "r") as zipObject:
        listOfFileNames = zipObject.namelist()
        for fileName in listOfFileNames:
            if ptn.match(fileName):
                with zipObject.open(fileName) as file:
                    print("Parsing", fileName)
                    df = pd.read_csv(
                        file, usecols=column_mappings.keys(), low_memory=False
                    )
                    df = df.rename(columns=column_mappings)
                    return df

    print("No postcode file found in Zip", flush=True)
    sys.exit(20)


def write_postcode_files(df: pd.DataFrame, output_dir: Path):
    df["first_letter"] = df["pcd"].str[0]
    total_size = 0
    for letter in df["first_letter"].unique():
        letter_codes = df[df.first_letter == letter]
        del letter_codes["first_letter"]
        print(
            f"Writing {letter_codes.shape[0]:6d} entries for the letter {letter}. ",
            end="",
            flush=True,
        )

        filename = output_dir / f"postcodes_{letter}.msgpack.br"
        # Convert dataframe to dict format for msgpack
        data = {
            "columns": list(letter_codes.columns),
            "data": letter_codes.to_dict(orient="list"),
        }
        # Serialize with msgpack and compress with brotli
        packed = msgpack.packb(data, use_bin_type=True)
        compressed = brotli.compress(packed)
        with open(filename, "wb") as f:
            f.write(compressed)
        size = filename.stat().st_size
        print(f"{size / 1024 / 1024:5.2f} MB \u2705", flush=True)
        total_size += size

    print()
    print(f"Total size: {total_size / 1024 / 1024:5.2f} MB 👍", flush=True)
