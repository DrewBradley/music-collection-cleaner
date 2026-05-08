from pathlib import Path
from song_dedupe import deduplicate_songs

AUDIO_EXTENSIONS = {".mp3", ".m4a", ".wma"}

def move_songs_to_unknown_album(root_directory):
  """Move mp3/m4a/wma files into a root-level "Unknown" folder."""
  root = Path(root_directory)
  if not root.exists():
    raise FileNotFoundError(f"Directory does not exist: {root}")
  if not root.is_dir():
    raise NotADirectoryError(f"Path is not a directory: {root}")

  unknown_album_folder = root / "Unknown"
  unknown_album_folder.mkdir(exist_ok=True)

  moved_count = 0

  for file_path in root.rglob("*"):
    if file_path.is_file() and file_path.suffix.lower() in AUDIO_EXTENSIONS:
      if unknown_album_folder in file_path.parents:
        continue
      target_path = unknown_album_folder / file_path.name
      file_path.rename(target_path)
      moved_count += 1

  return f"Moved {moved_count} song(s) to '{unknown_album_folder.name}'."


def move_non_song_files_to_other(root_directory):
  """Move non-music files into a root-level "Other" folder."""
  root = Path(root_directory)
  if not root.exists():
    raise FileNotFoundError(f"Directory does not exist: {root}")
  if not root.is_dir():
    raise NotADirectoryError(f"Path is not a directory: {root}")

  other_folder = root / "Other"
  other_folder.mkdir(exist_ok=True)

  moved_count = 0

  for file_path in root.rglob("*"):
    if file_path.is_file() and file_path.suffix.lower() not in AUDIO_EXTENSIONS:
      if other_folder in file_path.parents:
        continue
      target_path = other_folder / file_path.name
      file_path.rename(target_path)
      moved_count += 1

  return f"Moved {moved_count} other file(s) to '{other_folder.name}'."


def clean_artist_albums(root_directory, delete_duplicates=True):
  """Move all songs into a root-level "Unknown" folder and non-music files into "Other".
  Iterate over album folders and deduplicate songs within each album."""
  songs_message = move_songs_to_unknown_album(root_directory)
  other_message = move_non_song_files_to_other(root_directory)

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
  print(f"Removed {total_removed} duplicate song(s) in '{album_folder.name}': {remove_song_list}")
 else:
  print(f"Found {total_removed} duplicate song(s) in '{album_folder.name}': {remove_song_list} (no files were deleted)")