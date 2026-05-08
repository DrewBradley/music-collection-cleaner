import re
from pathlib import Path


_NUMBERED_COPY_RE = re.compile(r"^(?P<base>.+) \((?P<copy>[1-9])\)$")
_FILE_TYPE_WEIGHT = {
	".mp3": 0,
	".m4a": 1,
	".wma": 2,
}


def _normalized_song_name(file_path):
	"""Return normalized song name, ignoring numbered copy suffixes and extension."""
	stem = file_path.stem
	match = _NUMBERED_COPY_RE.match(stem)
	if match:
		stem = match.group("base")

	return stem


def _file_type_rank(file_path):
	"""Lower rank means higher priority when choosing which duplicate to keep."""
	return _FILE_TYPE_WEIGHT.get(file_path.suffix.lower(), len(_FILE_TYPE_WEIGHT))


def deduplicate_songs(directory, recursive=True, delete_duplicates=True):
	"""Deduplicate files that share the same song name.

	Files are grouped by name regardless of file type, and copy suffixes like
	" (1)" are treated as the same song. The kept file is chosen by type
	priority: mp3, then m4a, then wma, then any other type.

	Args:
		directory: Directory to scan.
		recursive: If True, scan subdirectories too.
		delete_duplicates: If True, remove duplicate files from disk.

	Returns:
		A list of duplicate song filenames that were removed or would be removed.
	"""
	root = Path(directory)
	if not root.exists():
		raise FileNotFoundError(f"Directory does not exist: {root}")
	if not root.is_dir():
		raise NotADirectoryError(f"Path is not a directory: {root}")

	iterator = root.rglob("*") if recursive else root.iterdir()
	seen_by_name = {}
	removed_song_names = []

	for file_path in iterator:
		if not file_path.is_file():
			continue

		key = _normalized_song_name(file_path)
		if key in seen_by_name:
			kept_file = seen_by_name[key]
			if _file_type_rank(file_path) < _file_type_rank(kept_file):
				seen_by_name[key] = file_path
				removed_song_names.append(kept_file.name)
				if delete_duplicates:
					kept_file.unlink()
			else:
				removed_song_names.append(file_path.name)
				if delete_duplicates:
					file_path.unlink()
		else:
			seen_by_name[key] = file_path

	return removed_song_names
