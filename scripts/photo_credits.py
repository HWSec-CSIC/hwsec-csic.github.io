"""Photographer attribution shared by image datasets, without rendering HTML."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
import re
from urllib.parse import urlparse


class PhotoCreditError(ValueError):
    """An actionable error in developer-maintained photo attribution."""


def _relative_path(value: object, location: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PhotoCreditError(f'{location}: expected a non-empty relative image path.')
    try:
        parsed = urlparse(value)
    except ValueError as error:
        raise PhotoCreditError(f'{location}: use a relative path inside assets/images.') from error
    path = PurePosixPath(value)
    if (parsed.scheme or parsed.netloc or parsed.query or parsed.fragment
            or path.is_absolute() or '..' in path.parts or '\\' in value
            or path.parts[:2] != ('assets', 'images')):
        raise PhotoCreditError(f'{location}: use a relative path inside assets/images, without traversal.')
    return path.as_posix()


def load_photo_credits(root: Path) -> list[dict]:
    """Load editable datasets and validate their image files/directories.

    A private ``_directoryPaths`` list records which paths are directories so
    matching does not depend on a working directory or further filesystem I/O.
    """
    root = root.resolve()
    source = root / 'assets' / 'docs' / 'photo-credits.json'
    try:
        data = json.loads(source.read_text(encoding='utf-8'))
    except json.JSONDecodeError as error:
        raise PhotoCreditError(f'photo-credits.json:{error.lineno}:{error.colno}: {error.msg}') from error
    except (OSError, UnicodeError) as error:
        raise PhotoCreditError(f'photo-credits.json: cannot read {source}: {error}') from error
    if not isinstance(data, dict) or not isinstance(data.get('datasets'), list):
        raise PhotoCreditError('photo-credits.json.datasets: expected an array.')

    image_root = (root / 'assets' / 'images').resolve()
    if not image_root.is_relative_to(root):
        raise PhotoCreditError('photo-credits.json: assets/images must stay inside the repository.')
    datasets = []
    ids = set()
    mapped_paths: list[tuple[Path, bool, str]] = []
    for index, record in enumerate(data['datasets']):
        location = f'photo-credits.json.datasets[{index}]'
        if not isinstance(record, dict):
            raise PhotoCreditError(f'{location}: expected an object.')
        dataset = dict(record)
        dataset_id = dataset.get('id')
        if not isinstance(dataset_id, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', dataset_id):
            raise PhotoCreditError(f'{location}.id: use a lowercase ID such as "lab-photos".')
        if dataset_id in ids:
            raise PhotoCreditError(f'{location}.id: duplicate dataset ID "{dataset_id}".')
        ids.add(dataset_id)
        if not isinstance(dataset.get('label'), str) or not dataset['label'].strip():
            raise PhotoCreditError(f'{location}.label: expected a non-empty string.')
        dataset.setdefault('url', '')
        for field in ('photographer', 'url'):
            if not isinstance(dataset.get(field), str):
                raise PhotoCreditError(f'{location}.{field}: expected a string; use "" when unknown.')
            dataset[field] = dataset[field].strip()
        if 'affiliation' in dataset:
            if not isinstance(dataset['affiliation'], str):
                raise PhotoCreditError(f'{location}.affiliation: expected a string; use "" when unknown.')
            dataset['affiliation'] = dataset['affiliation'].strip()
        if dataset['url']:
            try:
                parsed = urlparse(dataset['url'])
                hostname = parsed.hostname
                parsed.port
            except ValueError as error:
                raise PhotoCreditError(f'{location}.url: use a full HTTPS URL or "".') from error
            if (parsed.scheme != 'https' or not parsed.netloc or not hostname
                    or parsed.username is not None or parsed.password is not None
                    or any(character.isspace() for character in dataset['url'])):
                raise PhotoCreditError(f'{location}.url: use a full HTTPS URL or "".')
        if not isinstance(dataset.get('paths'), list) or not dataset['paths']:
            raise PhotoCreditError(f'{location}.paths: expected a non-empty array of image files or directories.')

        paths = []
        directories = []
        for path_index, value in enumerate(dataset['paths']):
            path_location = f'{location}.paths[{path_index}]'
            relative = _relative_path(value, path_location)
            resolved = (root / relative).resolve()
            if not resolved.is_relative_to(image_root):
                raise PhotoCreditError(f'{path_location}: image path or symlink escapes assets/images.')
            if not resolved.is_file() and not resolved.is_dir():
                raise PhotoCreditError(f'{path_location}: image file or directory does not exist: {relative}')
            if relative in paths:
                raise PhotoCreditError(f'{path_location}: duplicate path "{relative}".')
            is_directory = resolved.is_dir()
            for previous, previous_directory, previous_id in mapped_paths:
                overlaps = (resolved == previous
                            or (previous_directory and resolved.is_relative_to(previous))
                            or (is_directory and previous.is_relative_to(resolved)))
                if overlaps and previous_id != dataset_id:
                    raise PhotoCreditError(f'{path_location}: overlaps dataset "{previous_id}"; each image must have one dataset.')
            if is_directory:
                for child in resolved.rglob('*'):
                    if not child.resolve().is_relative_to(image_root):
                        raise PhotoCreditError(f'{path_location}: a directory symlink escapes assets/images: {child.name}')
                directories.append(relative)
            paths.append(relative)
            mapped_paths.append((resolved, is_directory, dataset_id))
        dataset['paths'] = paths
        dataset['_directoryPaths'] = directories
        datasets.append(dataset)
    return datasets


def credit_for_image(image: str, datasets: list[dict]) -> dict | None:
    """Return the matching named dataset; unknown/external images have no credit."""
    try:
        relative = _relative_path(image, 'image')
    except PhotoCreditError:
        return None
    for dataset in datasets:
        if not dataset.get('photographer', '').strip():
            continue
        directories = dataset.get('_directoryPaths', [])
        if ((relative in dataset['paths'] and relative not in directories)
                or any(relative.startswith(path + '/') for path in directories)):
            return dataset
    return None
