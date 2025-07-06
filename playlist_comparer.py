import logging
import re
from pathlib import Path

from pandas import DataFrame

from constants import KEY_COLUMNS
from utils import load_playlist

logger = logging.getLogger(__name__)


class PlaylistComparer:
    def __init__(self, path1: Path, path2: Path):
        self.path1 = path1
        self.path2 = path2
        self.name1 = self.path1.stem
        self.name2 = self.path2.stem
        self.df1 = load_playlist(self.path1)
        self.df2 = load_playlist(self.path2)

    def compare(self) -> dict[str, DataFrame]:
        df1_tmp = self.df1.copy()
        df2_tmp = self.df2.copy()
        df1_tmp['_norm_name'] = df1_tmp['Name'].apply(self.normalize_name)
        df1_tmp['_norm_artist'] = df1_tmp['Artist'].apply(self.normalize_artist)
        df2_tmp['_norm_name'] = df2_tmp['Name'].apply(self.normalize_name)
        df2_tmp['_norm_artist'] = df2_tmp['Artist'].apply(self.normalize_artist)

        df2_index = {}
        for idx, row in df2_tmp.iterrows():
            df2_index.setdefault(row['_norm_name'], []).append((idx, row['_norm_artist']))

        common_pairs = set()
        for i1, row1 in df1_tmp.iterrows():
            name1 = row1['_norm_name']
            art1 = row1['_norm_artist']
            for i2, art2 in df2_index.get(name1, []):
                if self.is_artist_subset(art1, art2):
                    common_pairs.add((i1, i2))

        idx1_common = [i for i, _ in common_pairs]
        idx2_common = [j for _, j in common_pairs]

        common = (
            self.df1
            .loc[idx1_common]
            .drop_duplicates(subset=KEY_COLUMNS)
            .sort_values(KEY_COLUMNS)
            .reset_index(drop=True)
        )
        only_in_1 = (
            self.df1
            .drop(idx1_common)
            .drop_duplicates(subset=KEY_COLUMNS)
            .sort_values(KEY_COLUMNS)
            .reset_index(drop=True)
        )
        only_in_2 = (
            self.df2
            .drop(idx2_common)
            .drop_duplicates(subset=KEY_COLUMNS)
            .sort_values(KEY_COLUMNS)
            .reset_index(drop=True)
        )

        logger.info(
            f"Found {len(common)} common tracks, "
            f"{len(only_in_1)} only in {self.name1}, "
            f"{len(only_in_2)} only in {self.name2}"
        )

        return {'common': common, f'{self.name1}_uniques': only_in_1, f'{self.name2}_uniques': only_in_2}

    @staticmethod
    def normalize_name(text: str) -> str:
        t = text.lower().strip()
        t = re.sub(r"\(.*?\)", "", t)
        t = re.sub(r"(feat\.?|featuring)\s.*", "", t)
        t = re.sub(r"\s+", " ", t)

        return t.strip()

    @staticmethod
    def normalize_artist(text: str) -> set[str]:
        base = PlaylistComparer.normalize_name(text)
        base = re.sub(r"(feat\.?|featuring)\s.*", "", base)
        tokens = re.split(r"\s*(?:&|,|and|/|;)\s*", base)

        return {tok.strip() for tok in tokens if tok.strip()}

    @staticmethod
    def is_artist_subset(a: set[str], b: set[str]) -> bool:
        return a.issubset(b) or b.issubset(a)
