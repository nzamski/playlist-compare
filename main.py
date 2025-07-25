import logging

from constants import PLAYLIST_DIR, RESULTS_DIR
from logger import setup_logger
from utils import save_results

logger = logging.getLogger(__name__)

from playlist_comparer import PlaylistComparer


def main():
    setup_logger()
    logger.info("Starting playlist comparison")

    files = sorted([p for p in PLAYLIST_DIR.iterdir() if p.is_file() and not p.name.startswith('.')])
    if len(files) != 2:
        logger.error(f"Expected exactly 2 files in {PLAYLIST_DIR.name} directory, found {len(files)}.")
        raise SystemExit(1)

    comparer = PlaylistComparer(files[0], files[1])
    results = comparer.compare()

    save_results(results, RESULTS_DIR)
    logger.info(f"Finished playlist comparison successfully (saved in {RESULTS_DIR.name} directory)")


if __name__ == '__main__':
    main()
