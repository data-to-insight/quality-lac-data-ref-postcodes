import logging
import os
from typing import Iterable, Union

import pandas as pd
from pathlib import Path

import brotli
import msgpack

logger = logging.getLogger(__name__)

alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

_dtypes = {
    'pcd': 'str',
    'oseast1m': 'float64',
    'osnrth1m': 'float64',
    'laua': 'str',
    'pcd_abbr': 'str',
}
columns = list(_dtypes.keys())


class Postcodes:
    _read = set()
    _data_dir = Path(__file__).parent
    _df = pd.DataFrame({c: pd.Series(dtype=t) for c, t in _dtypes.items()})

    def __init__(self, data_dir: Union[Path, str] = None):
        if data_dir is not None:
            self._data_dir = Path(data_dir)
        elif os.getenv('QLACREF_DATA_DIR') is not None:
            self._data_dir = Path(os.environ['QLACREF_DATA_DIR'])

    def _get_filename(self, letter):
        return self._data_dir / f"postcodes_{letter}.msgpack.br"

    def _read_msgpack(self, letter):
        filename = self._get_filename(letter)
        logger.debug(f"Opening {filename}")
        with open(filename, 'rb') as file:
            compressed = file.read()
            unpacked = brotli.decompress(compressed)
            data = msgpack.unpackb(unpacked, raw=False)
            return pd.DataFrame(data["data"], columns=data["columns"])

    @property
    def dataframe(self):
        return self._df

    def load_postcodes(self, letters: Iterable[str]):
        if os.getenv("QLAC_DISABLE_PC"):
            return
        dataframes = [self._df]
        to_load = set([l.upper() for l in letters]) - self._read
        logger.info(f"Loading {to_load}")
        for letter in to_load:
            if letter in self._read:
                continue
            try:
                df = self._read_msgpack(letter)
                logger.debug(f"Read {df.shape[0]} postcodes from {letter}")
                dataframes.append(df)
            except (ValueError, FileNotFoundError):
                logger.debug(f"File not found for {letter}")
                pass

        if len(dataframes) > 1:
            logger.debug(f"Concateting {len(dataframes)} dataframes")
            self._df = pd.concat(dataframes)
            self._df.reset_index(drop=True, inplace=True)
            logger.debug(f"Creating abbreviations")
            self._df['pcd_abbr'] = self._df['pcd'].str.replace(' ', '')
            logger.debug(f"Done")
            self._read = self._read | to_load
