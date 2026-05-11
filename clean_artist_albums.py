import sys
from pathlib import Path
from song_dedupe import deduplicate_songs

AUDIO_EXTENSIONS = {".mp3", ".m4a", ".wma"}
IGNORED_NON_SONG_FILENAMES = {".DS_Store", "Thumbs.db", "desktop.ini"}


def _is_ignorable_non_song_file(file_path):
  """Return True for metadata files that should not trigger an Other folder."""
  name = file_path.name
  return name in IGNORED_NON_SONG_FILENAMES or name.startswith("._")

def move_songs_to_unknown_album(root_directory, recursive=False):
  """Move audio files into a root-level "Unknown" folder.

  Only files directly inside root_directory are considered.
  This prevents moving songs out of nested artist/album subfolders.
  """
  root = Path(root_directory)
  if not root.exists():
    raise FileNotFoundError(f"Directory does not exist: {root}")
  if not root.is_dir():
    raise NotADirectoryError(f"Path is not a directory: {root}")

  unknown_album_folder = root / "Unknown"
  moved_count = 0
  iterator = root.iterdir()

  for file_path in iterator:
    if file_path.is_file() and file_path.suffix.lower() in AUDIO_EXTENSIONS:
      if unknown_album_folder in file_path.parents:
        continue
      if not unknown_album_folder.exists():
        unknown_album_folder.mkdir(exist_ok=True)
      target_path = unknown_album_folder / file_path.name
      file_path.rename(target_path)
      moved_count += 1

  # Remove Unknown when it has no meaningful files (or only ignorable metadata files).
  if unknown_album_folder.exists() and unknown_album_folder.is_dir():
    remaining_entries = list(unknown_album_folder.iterdir())
    meaningful_entries = [
      entry for entry in remaining_entries
      if not (entry.is_file() and _is_ignorable_non_song_file(entry))
    ]

    if not meaningful_entries:
      for entry in remaining_entries:
        if entry.is_file() and _is_ignorable_non_song_file(entry):
          entry.unlink()
      unknown_album_folder.rmdir()

  return f"Moved {moved_count} song(s) to '{unknown_album_folder.name}'."


def move_non_song_files_to_other(root_directory, recursive=False):
  """Move non-music files into a root-level "Other" folder.

  Only files directly inside root_directory are considered.
  This prevents moving non-music files out of nested artist/album subfolders.
  """
  root = Path(root_directory)
  if not root.exists():
    raise FileNotFoundError(f"Directory does not exist: {root}")
  if not root.is_dir():
    raise NotADirectoryError(f"Path is not a directory: {root}")

  other_folder = root / "Other"
  moved_count = 0
  iterator = root.iterdir()

  for file_path in iterator:
    if file_path.is_file() and file_path.suffix.lower() not in AUDIO_EXTENSIONS:
      if _is_ignorable_non_song_file(file_path):
        continue
      if other_folder in file_path.parents:
        continue
      if not other_folder.exists():
        other_folder.mkdir(exist_ok=True)
      target_path = other_folder / file_path.name
      file_path.rename(target_path)
      moved_count += 1

  # Remove Other when it has no meaningful files (or only ignorable metadata files).
  if other_folder.exists() and other_folder.is_dir():
    remaining_entries = list(other_folder.iterdir())
    meaningful_entries = [
      entry for entry in remaining_entries
      if not (entry.is_file() and _is_ignorable_non_song_file(entry))
    ]

    if not meaningful_entries:
      for entry in remaining_entries:
        if entry.is_file() and _is_ignorable_non_song_file(entry):
          entry.unlink()
      other_folder.rmdir()

  return f"Moved {moved_count} other file(s) to '{other_folder.name}'."


def clean_artist_albums(root_directory, delete_duplicates=True):
  """Move all songs into a root-level "Unknown" folder and non-music files into "Other".
  Iterate over album folders and deduplicate songs within each album."""
  songs_message = move_songs_to_unknown_album(root_directory, recursive=False)
  other_message = move_non_song_files_to_other(root_directory, recursive=False)

  print(songs_message)
  print(other_message)
  # Deduplicate songs within each album
  root = Path(root_directory)
  total_removed = 0
  remove_song_list = ""
  for album_folder in root.iterdir():
    if album_folder.is_dir():
      removed_songs = deduplicate_songs(album_folder, recursive=False, delete_duplicates=delete_duplicates)
      if removed_songs:
        total_removed += len(removed_songs)
        remove_song_list += f"{', '.join(removed_songs)} "

  if delete_duplicates:
    print(f"Removed {total_removed} duplicate song(s): {remove_song_list}")
  else:
    print(f"Found {total_removed} duplicate song(s): {remove_song_list} (no files were deleted)")


def main():
  """Main entry point for command-line usage."""
  if len(sys.argv) < 2:
    print("Usage: python3 clean_artist_albums.py <directory> [--no-delete]")
    print()
    print("Arguments:")
    print("  <directory>  Path to the artist album directory")
    print("  --no-delete  Preview changes without deleting files (optional)")
    sys.exit(1)

  directory = sys.argv[1]
  delete_duplicates = "--no-delete" not in sys.argv

  try:
    clean_artist_albums(directory, delete_duplicates=delete_duplicates)
  except FileNotFoundError as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
  except NotADirectoryError as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
  main()