# Music Collection Cleaner

A Python utility to organize and clean up music collections by removing duplicates, organizing untagged songs, and moving non-music files.

## Features

- **Duplicate Detection**: Identifies and removes duplicate songs based on normalized filenames
- **Unknown Album Organization**: Moves songs without album folders to an "Unknown" folder
- **Non-Music File Handling**: Organizes non-music files into an "Other" folder
- **Flexible File Formats**: Supports MP3, M4A, and WMA audio files

## Requirements

- Python 3.6+
- No external dependencies

## Installation

Clone or download this repository to your local machine.

## Usage

The script assumes your directories are structured Artist/Album/Song

### Running from command line

To execute the cleaner, open a terminal and run the script directly:

```bash
python3 clean_artist_albums.py /path/to/music/directory
```

Replace `/path/to/music/directory` with the actual path to your music collection.

### Options

#### Delete duplicates (default behavior)
```bash
python3 clean_artist_albums.py /path/to/music/directory
```

#### Find duplicates without deleting
To preview changes without actually deleting files, use the `--no-delete` flag:
```bash
python3 clean_artist_albums.py /path/to/music/directory --no-delete
```

### Running from Python

You can also import and use the function directly in Python:

```python
from clean_artist_albums import clean_artist_albums

# Delete duplicates
clean_artist_albums('/path/to/music/directory')

# Preview without deleting
clean_artist_albums('/path/to/music/directory', delete_duplicates=False)
```

## What the script does

1. **Moves orphan songs**: All songs found in the root directory (not in an album folder) are moved to a `Unknown` folder
2. **Moves non-music files**: Any files with extensions other than `.mp3`, `.m4a`, or `.wma` are moved to an `Other` folder
3. **Deduplicates albums**: Within each album folder, duplicate songs are identified and removed based on:
   - Normalized song name (ignoring numbered copy suffixes like " (1)")
   - File type priority: MP3 > M4A > WMA (keeps the highest priority format)

## Output

The script will display messages indicating:
- Number of songs moved to "Unknown" folder
- Number of non-music files moved to "Other" folder
- Duplicate songs removed (or found, if running in preview mode)

## Example

```
Moved 5 song(s) to 'Unknown'.
Moved 2 other file(s) to 'Other'.
Removed 3 duplicate song(s) in 'Album Name': song1.m4a, song2.mp3
```
