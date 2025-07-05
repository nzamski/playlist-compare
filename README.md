# Playlist Compare

A Python tool to compare two Apple Music playlist files (TSV format) and identify common and unique tracks.

## Features

- Loads two playlist files from the `playlists/` directory.
- Compares tracks using normalized names and artist sets.
- Outputs CSV files with common tracks and tracks unique to each playlist in the `results/` directory.
- Logs progress and summary information.

## Requirements

- Python 3.8+
- pandas

## Usage

1. Place exactly two TSV playlist files in the `playlists/` directory.
2. Each file should have columns: `Name`, `Artist`, `Date Modified`, `Date Added`, `Last Played`, `Last Skipped`.
3. Run the script:

   ```bash
   python main.py
   ```

4. Results will be saved as `common.csv`, `only_in_1.csv`, and `only_in_2.csv` in the `results/` directory.

## Example

```
playlists/
  ├── playlist1.tsv
  └── playlist2.tsv
results/
  ├── common.csv
  ├── only_in_1.csv
  └── only_in_2.csv
```
