import argparse
import sys
from pathlib import Path

AUDIO_EXTENSIONS = {".mp3", ".m4a", ".wma"}


def _sanitize_path_part(value, fallback):
  cleaned = (value or "").strip().replace("/", "_")
  cleaned = cleaned.replace("\\", "_").replace(":", "_")
  cleaned = cleaned.strip(".")
  return cleaned or fallback


def _load_mutagen_file(file_path):
  try:
    from mutagen import File as MutagenFile
  except ImportError:
    return None, "mutagen-not-installed"

  try:
    return MutagenFile(file_path, easy=True), None
  except Exception:
    return None, "mutagen-read-error"


def _extract_artist_album(file_path):
  metadata, error = _load_mutagen_file(file_path)
  if metadata is None:
    if error == "mutagen-not-installed":
      return "Unknown Artist", "Unknown Album", "mutagen-not-installed"
    return "Unknown Artist", "Unknown Album", "missing-or-invalid-tags"

  artist = None
  album = None

  for key in ("albumartist", "artist"):
    values = metadata.get(key)
    if values:
      artist = values[0]
      break

  album_values = metadata.get("album")
  if album_values:
    album = album_values[0]

  artist = _sanitize_path_part(artist, "Unknown Artist")
  album = _sanitize_path_part(album, "Unknown Album")
  return artist, album, None


def _find_unique_destination(path):
  if not path.exists():
    return path

  stem = path.stem
  suffix = path.suffix
  parent = path.parent

  counter = 1
  while True:
    candidate = parent / f"{stem} ({counter}){suffix}"
    if not candidate.exists():
      return candidate
    counter += 1


def recover_unknown_songs(music_root, unknown_folder_name="Unknown", dry_run=True, recursive=True):
  root = Path(music_root)
  if not root.exists():
    raise FileNotFoundError(f"Directory does not exist: {root}")
  if not root.is_dir():
    raise NotADirectoryError(f"Path is not a directory: {root}")

  unknown_folder = root / unknown_folder_name
  if not unknown_folder.exists() or not unknown_folder.is_dir():
    raise FileNotFoundError(f"Unknown folder does not exist: {unknown_folder}")

  iterator = unknown_folder.rglob("*") if recursive else unknown_folder.iterdir()

  planned_moves = []
  mutagen_missing_count = 0
  unreadable_tag_count = 0

  for source_file in iterator:
    if not source_file.is_file():
      continue
    if source_file.suffix.lower() not in AUDIO_EXTENSIONS:
      continue

    artist, album, tag_error = _extract_artist_album(source_file)
    if tag_error == "mutagen-not-installed":
      mutagen_missing_count += 1
    elif tag_error is not None:
      unreadable_tag_count += 1

    destination_dir = root / artist / album
    destination_file = _find_unique_destination(destination_dir / source_file.name)
    planned_moves.append((source_file, destination_file))

  if dry_run:
    print(f"[DRY RUN] Planned moves: {len(planned_moves)}")
    if mutagen_missing_count:
      print("[DRY RUN] mutagen is not installed; all files will use fallback folders.")
      print("[DRY RUN] Install mutagen for better recovery: pip3 install mutagen")
    if unreadable_tag_count:
      print(f"[DRY RUN] Files with missing/invalid tags: {unreadable_tag_count}")

    preview_limit = 100
    for source_file, destination_file in planned_moves[:preview_limit]:
      print(f"{source_file} -> {destination_file}")
    if len(planned_moves) > preview_limit:
      print(f"... and {len(planned_moves) - preview_limit} more")

    return len(planned_moves)

  moved_count = 0
  for source_file, destination_file in planned_moves:
    destination_file.parent.mkdir(parents=True, exist_ok=True)
    source_file.rename(destination_file)
    moved_count += 1

  print(f"Moved {moved_count} file(s) out of {unknown_folder}")
  if mutagen_missing_count:
    print("Warning: mutagen is not installed; files were routed to fallback folders.")
  if unreadable_tag_count:
    print(f"Warning: {unreadable_tag_count} file(s) had missing/invalid tags.")

  return moved_count


def main():
  parser = argparse.ArgumentParser(
    description=(
      "Recover songs from a root Unknown folder back into Artist/Album folders "
      "using file metadata tags."
    )
  )
  parser.add_argument("music_root", help="Path to the root music directory")
  parser.add_argument(
    "--unknown-folder",
    default="Unknown",
    help="Name of the unknown folder inside music_root (default: Unknown)",
  )
  parser.add_argument(
    "--apply",
    action="store_true",
    help="Execute moves. Without this flag, runs in dry-run mode.",
  )
  parser.add_argument(
    "--non-recursive",
    action="store_true",
    help="Only inspect files directly inside Unknown (no nested scanning).",
  )

  args = parser.parse_args()

  try:
    recover_unknown_songs(
      args.music_root,
      unknown_folder_name=args.unknown_folder,
      dry_run=not args.apply,
      recursive=not args.non_recursive,
    )
  except (FileNotFoundError, NotADirectoryError) as exc:
    print(f"Error: {exc}", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
  main()
