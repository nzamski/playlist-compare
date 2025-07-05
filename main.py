import logging
import time
from pathlib import Path

from constants import PLAYLIST_DIR, RESULTS_DIR
from logger import setup_logger
from utils import save_results

logger = logging.getLogger(__name__)

from playlist_comparer import PlaylistComparer


def main():
    setup_logger()

    start = time.perf_counter()
    logger.info("Starting playlist comparison process")

    playlist_dir = Path(PLAYLIST_DIR)
    files = sorted([p for p in playlist_dir.iterdir() if p.is_file()])
    if len(files) != 2:
        logger.error(
            f"Expected exactly 2 files in {playlist_dir!r}, found {len(files)}."
        )
        raise SystemExit(1)

    comparer = PlaylistComparer(files[0], files[1])
    results = comparer.compare()
    save_results(results, Path(RESULTS_DIR))

    duration = time.perf_counter() - start
    logger.info(f"Completed in {duration:.2f} seconds")


if __name__ == '__main__':
    main()
