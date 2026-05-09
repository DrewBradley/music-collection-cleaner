import sys
from pathlib import Path
from clean_artist_albums import move_songs_to_unknown_album, move_non_song_files_to_other, clean_artist_albums

def clean_root_music_folder(root_directory, delete_duplicates=True):
  """Move all songs into a root-level "Unknown" folder and non-music files into "Other".
  Iterate over artist folders and clean each artist's albums."""
  root = Path(root_directory)
  if not root.exists():
    raise FileNotFoundError(f"Directory does not exist: {root}")
  if not root.is_dir():
    raise NotADirectoryError(f"Path is not a directory: {root}")

  songs_message = move_songs_to_unknown_album(root_directory)
  other_message = move_non_song_files_to_other(root_directory)

  processed_artists = []
  for artist_folder in root.iterdir():
    if not artist_folder.is_dir():
      continue
    if artist_folder.name in {"Unknown", "Other"}:
      continue

    clean_artist_albums(artist_folder, delete_duplicates=delete_duplicates)
    processed_artists.append(artist_folder.name)

  artist_message = f"Processed {len(processed_artists)} artist folder(s): {', '.join(processed_artists)}"
  return f"{songs_message}\n{other_message}\n{artist_message}"


def main():
  """Main entry point for command-line usage."""
  if len(sys.argv) < 2:
    print("Usage: python3 clean_root_music_folder.py <directory> [--no-delete]")
    print()
    print("Arguments:")
    print("  <directory>  Path to the root music directory")
    print("  --no-delete  Preview changes without deleting files (optional)")
    sys.exit(1)

  directory = sys.argv[1]
  delete_duplicates = "--no-delete" not in sys.argv

  try:
    result = clean_root_music_folder(directory, delete_duplicates=delete_duplicates)
    print(result)
  except FileNotFoundError as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
  except NotADirectoryError as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
  main()