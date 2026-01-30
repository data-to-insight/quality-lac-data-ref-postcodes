from pathlib import Path
import pandas as pd
import click
from rich.console import Console
from rich.table import Table
from qlacref_postcodes import Postcodes
from qlacref_postcodes._generate import write_postcode_files, read_postcode_file

ROOT_DIR = Path(__file__).parent


@click.group()
def cli():
    pass


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.argument(
    "output_dir",
    type=click.Path(
        exists=True, writable=True, file_okay=False, dir_okay=True, resolve_path=True
    ),
    default=ROOT_DIR,
)
def generate(input_file: str, output_dir: str):
    input_file = Path(input_file)
    output_dir = Path(output_dir)
    df = read_postcode_file(input_file)
    write_postcode_files(df, output_dir)


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.argument(
    "output_file",
    type=click.Path(writable=True, file_okay=True, dir_okay=False, resolve_path=True),
    default=None,
)
def to_parquet(input_file: str, output_file: str | None = None):
    input_file = Path(input_file)
    if output_file is None:
        output_file = input_file.with_suffix(".parquet")
    output_file = Path(output_file)
    df = read_postcode_file(input_file)
    df.to_parquet(
        output_file,
        compression="brotli",
        index=False,
    )
    print(
        f"Written {output_file.stat().st_size / 1024 / 1024:5.2f} MB to {output_file}"
    )


@cli.command()
@click.argument("partial_postcode", type=str)
@click.option(
    "--data-dir",
    type=click.Path(
        exists=True, writable=True, file_okay=False, dir_okay=True, resolve_path=True
    ),
)
def search(partial_postcode: str, data_dir: str | None = None):
    console = Console()
    partial_postcode = partial_postcode.strip().upper().replace(" ", "")

    pc = Postcodes(data_dir=data_dir)
    pc.load_postcodes(partial_postcode[0])
    df = pc.dataframe

    result = df[df.pcd_abbr.str.startswith(partial_postcode)]
    if result.empty:
        console.print(f"No postcodes found for [yellow]{partial_postcode}[/yellow]")
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Postcode")
    table.add_column("Easting")
    table.add_column("Northing")
    table.add_column("Local Authority")

    # Add rows
    for _, row in result.iterrows():
        pcd = str(row.pcd)
        easting = f"{row.oseast1m:06.0f}" if not pd.isna(row.oseast1m) else ""
        northing = f"{row.osnrth1m:06.0f}" if not pd.isna(row.osnrth1m) else ""
        laua = str(row.laua) if not pd.isna(row.laua) else ""
        table.add_row(
            pcd,
            easting,
            northing,
            laua,
        )

    console.print(table)
    console.print(f"Found [green]{result.shape[0]:,}[/green] postcodes")


if __name__ == "__main__":
    cli()
