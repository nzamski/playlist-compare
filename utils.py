import logging
from pathlib import Path
from typing import Dict

from pandas import DataFrame, read_csv

from constants import DATE_COLUMNS

logger = logging.getLogger(__name__)


def load_playlist(file_path: Path) -> DataFrame:
    df = read_csv(
        file_path,
        sep='\t',
        parse_dates=DATE_COLUMNS,
        dayfirst=True
    )
    logger.info(f"Loaded {len(df)} tracks from {file_path.name}")

    return df


def save_results(results: Dict[str, DataFrame], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    for key, df in results.items():
        csv_path = output_dir / f"{key}.csv"
        df.to_csv(csv_path, index=False)
        logger.info(f"Wrote CSV: {csv_path}")
