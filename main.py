import logging
import re
import sys
import time
from difflib import SequenceMatcher
from pathlib import Path
from typing import Set, Dict

from pandas import DataFrame, read_csv

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter(
    fmt='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
)
logger.addHandler(handler)

DATE_COLUMNS = ['Date Modified', 'Date Added', 'Last Played', 'Last Skipped']
NAME_SIM_THRESHOLD = 0.8
KEY_COLUMNS = ['Name', 'Artist']


def load_playlist(file_path: Path) -> DataFrame:
    """Load a playlist TSV file into a DataFrame."""
    df = read_csv(
        file_path,
        sep='\t',
        parse_dates=DATE_COLUMNS,
        dayfirst=True
    )
    logger.info(f"Loaded {len(df)} tracks from {file_path.name}")
    return df


def normalize_name(text: str) -> str:
    """Normalize track name for comparison, removing parentheticals and extra spaces."""
    t = text.lower().strip()
    t = re.sub(r"\(.*?\)", "", t)
    t = re.sub(r"(feat\.?|featuring)\s.*", "", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def is_similar(a: str, b: str, threshold: float) -> bool:
    """Check if two strings are similar above a threshold."""
    return SequenceMatcher(None, a, b).ratio() >= threshold


def normalize_artist(text: str) -> Set[str]:
    """Normalize the artist string into a set of names."""
    base = normalize_name(text)
    base = re.sub(r"(feat\.?|featuring)\s.*", "", base)
    tokens = re.split(r"\s*(?:&|,|and|/|;)\s*", base)
    return {tok.strip() for tok in tokens if tok.strip()}


def is_artist_subset(a: Set[str], b: Set[str]) -> bool:
    """Check if one artist set is a subset of the other."""
    return a.issubset(b) or b.issubset(a)


def compare_playlists(df1: DataFrame, df2: DataFrame) -> Dict[str, DataFrame]:
    """
    Compare two playlists and return dicts of common and unique tracks.
    Uses normalized name and artist subset logic.
    """
    df1_tmp = df1.copy()
    df2_tmp = df2.copy()
    df1_tmp['_norm_name'] = df1_tmp['Name'].apply(normalize_name)
    df1_tmp['_norm_artist'] = df1_tmp['Artist'].apply(normalize_artist)
    df2_tmp['_norm_name'] = df2_tmp['Name'].apply(normalize_name)
    df2_tmp['_norm_artist'] = df2_tmp['Artist'].apply(normalize_artist)

    # Build index for df2 for a faster lookup
    df2_index = {}
    for idx, row in df2_tmp.iterrows():
        df2_index.setdefault(row['_norm_name'], []).append((idx, row['_norm_artist']))

    common_pairs = set()
    for i1, row1 in df1_tmp.iterrows():
        name1 = row1['_norm_name']
        art1 = row1['_norm_artist']
        for i2, art2 in df2_index.get(name1, []):
            if is_artist_subset(art1, art2):
                common_pairs.add((i1, i2))

    idx1_common = [i for i, _ in common_pairs]
    idx2_common = [j for _, j in common_pairs]

    common = (
        df1
        .loc[idx1_common]
        .drop_duplicates(subset=KEY_COLUMNS)
        .sort_values(KEY_COLUMNS)
        .reset_index(drop=True)
    )
    only_in_1 = (
        df1
        .drop(idx1_common)
        .drop_duplicates(subset=KEY_COLUMNS)
        .sort_values(KEY_COLUMNS)
        .reset_index(drop=True)
    )
    only_in_2 = (
        df2
        .drop(idx2_common)
        .drop_duplicates(subset=KEY_COLUMNS)
        .sort_values(KEY_COLUMNS)
        .reset_index(drop=True)
    )

    logger.info(
        f"Found {len(common)} common tracks, "
        f"{len(only_in_1)} only in first, "
        f"{len(only_in_2)} only in second"
    )
    return {'common': common, 'only_in_1': only_in_1, 'only_in_2': only_in_2}


def save_results(results: Dict[str, DataFrame], output_dir: Path) -> None:
    """Save comparison results to CSV files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    for key, df in results.items():
        csv_path = output_dir / f"{key}.csv"
        df.to_csv(csv_path, index=False)
        logger.info(f"Wrote CSV: {csv_path}")


def main() -> None:
    start = time.perf_counter()
    logger.info("Starting playlist comparison process")

    playlist_dir = Path('playlists')
    files = sorted([p for p in playlist_dir.iterdir() if p.is_file()])
    if len(files) != 2:
        logger.error(
            f"Expected exactly 2 files in {playlist_dir!r}, found {len(files)}."
        )
        raise SystemExit(1)

    logger.info(f"Comparing playlists: {files[0].name} and {files[1].name}")
    df1 = load_playlist(files[0])
    df2 = load_playlist(files[1])

    results = compare_playlists(df1, df2)
    output_dir = Path('results')
    save_results(results, output_dir)

    duration = time.perf_counter() - start
    logger.info(f"Completed in {duration:.2f} seconds")


if __name__ == '__main__':
    main()
