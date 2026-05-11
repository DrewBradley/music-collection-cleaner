# Music Collection Cleaner

A Python utility to organize and clean up music collections by removing duplicates, organizing untagged songs, and moving non-music files.

## Features

- **Duplicate Detection**: Identifies and removes duplicate songs based on normalized filenames
- **Unknown Album Organization**: Moves songs without album folders to an "Unknown" folder
- **Non-Music File Handling**: Organizes non-music files into an "Other" folder
- **Flexible File Formats**: Supports MP3, M4A, and WMA audio files
- **Safe Root Mode (default)**: Root cleaner only moves files from the immediate root directory
- **Recovery Utility**: Restore songs from a root `Unknown` folder into `Artist/Album` folders
- **Unsorted Sorter**: Sort files from an unsorted folder into `Music/Artist/Album`

## Requirements

- Python 3.6+
- No external dependencies

## Installation

Clone or download this repository to your local machine.

## Usage

The script assumes your directories are structured as:
- Root/Artist/Album/Song (for clean_root_music_folder)
- Artist/Album/Song (for clean_artist_albums)

### Option 1: Clean entire music collection (Root level)

To clean your entire music collection directory with multiple artist folders:

```bash
python3 clean_root_music_folder.py /path/to/music/directory
```

Replace `/path/to/music/directory` with the actual path to your root music directory.

By default, this runs in **safe mode**:
- Moves songs/non-music files only from the immediate root folder
- Does **not** recursively pull files out of artist/album folders

#### Preview changes without deleting:
```bash
python3 clean_root_music_folder.py /path/to/music/directory --no-delete
```

#### Unsafe recursive root scan (optional)
This restores old behavior and can pull files out of nested folders:
```bash
python3 clean_root_music_folder.py /path/to/music/directory --unsafe-recursive-root-scan
```

### Option 2: Clean individual artist albums

To clean a specific artist directory (without iterating subdirectories):

```bash
python3 clean_artist_albums.py /path/to/artist/directory
```

This will:
- Move orphan songs to "Unknown" folder
- Move non-music files to "Other" folder
- Deduplicate songs within each album folder

#### Preview changes without deleting:
```bash
python3 clean_artist_albums.py /path/to/artist/directory --no-delete
```

### Option 3: Recover songs from root Unknown folder

If files were previously moved into `Unknown`, use the recovery utility.

#### Dry run (recommended first)
```bash
python3 recover_unknown_songs.py /path/to/music/directory
```

#### Apply recovery moves
```bash
python3 recover_unknown_songs.py /path/to/music/directory --apply
```

#### Optional: install metadata parser for better tag recovery
```bash
pip3 install mutagen
```

Without `mutagen`, files are still recoverable but will fall back to `Unknown Artist/Unknown Album` when tags cannot be read.

### Option 4: Sort an unsorted folder into Music/Artist/Album

If you have a folder like `Music/Unsorted` with mixed files, you can sort it into
`Music/Artist/Album` using the same metadata-driven logic.

#### Dry run (recommended first)
```bash
python3 recover_unknown_songs.py /path/to/music/directory --unsorted-folder Unsorted
```

#### Apply sorting moves
```bash
python3 recover_unknown_songs.py /path/to/music/directory --unsorted-folder Unsorted --apply
```

### Running from Python

You can also import and use the functions directly in Python:

```python
from clean_root_music_folder import clean_root_music_folder
from clean_artist_albums import clean_artist_albums
from recover_unknown_songs import recover_unknown_songs, sort_unsorted_songs

# Clean entire collection
clean_root_music_folder('/path/to/music/directory')

# Clean specific artist
clean_artist_albums('/path/to/artist/directory')

# Preview without deleting
clean_root_music_folder('/path/to/music/directory', delete_duplicates=False)
clean_artist_albums('/path/to/artist/directory', delete_duplicates=False)

# Recover songs from Unknown (dry run)
recover_unknown_songs('/path/to/music/directory', dry_run=True)

# Recover songs from Unknown (apply moves)
recover_unknown_songs('/path/to/music/directory', dry_run=False)

# Sort from Music/Unsorted into Music/Artist/Album (dry run)
sort_unsorted_songs('/path/to/music/directory', unsorted_folder_name='Unsorted', dry_run=True)

# Sort from Music/Unsorted into Music/Artist/Album (apply moves)
sort_unsorted_songs('/path/to/music/directory', unsorted_folder_name='Unsorted', dry_run=False)
```

## What the script does

1. **Moves orphan songs**: Songs found directly in the selected directory are moved to an `Unknown` folder
2. **Moves non-music files**: Files found directly in the selected directory (that are not `.mp3`, `.m4a`, `.wma`) are moved to an `Other` folder
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
