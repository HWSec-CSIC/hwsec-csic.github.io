#!/usr/bin/env python3
"""Prepare the selected group photographs for the web. Requires Pillow.

This optional asset-preparation step is separate from the dependency-free
site builder. Original photographs remain untouched in inputs/.
Edit photographer credits separately in assets/docs/photo-credits.json.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SELECTION = (
    ('packaged-chip', 'Fotos_SPIRS/A60A1685.jpg', 1920, 'Wire-bonded chip package; homepage hero.'),
    ('spirs-evaluation', 'Fotos_SPIRS/A60A1673.jpg', 1200, 'SPIRS evaluation board; secure SoCs research area.'),
    ('wire-bonded-die', 'Fotos_SPIRS/A60A1681.jpg', 960, 'Exposed die and bond wires; physical security research area.'),
    ('fibre-alignment', 'Mesa óptica - set up/DSC01395.JPG', 1200, 'Fibre alignment stages; integrated photonics research area.'),
    ('spirs-measurement', 'Fotos_SPIRS/_60A9978.jpg', 1440, 'SPIRS hardware connected to probes and cables; evaluation context.'),
    ('optical-bench', 'Mesa óptica - set up/DSC01384.JPG', 1440, 'Optical bench with microscope and alignment stages; photonics context.'),
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT / 'inputs', help='Directory containing the original photographs.')
    parser.add_argument('--output', type=Path, default=ROOT / 'assets/images/lab', help='Directory for WebP derivatives and provenance.')
    args = parser.parse_args()
    try:
        from PIL import Image, ImageOps
    except ImportError:
        parser.error('Pillow is needed only for photo preparation. Install it in a virtual environment: pip install Pillow')
    source_dir, output_dir = args.source.resolve(), args.output.resolve()
    if output_dir.is_relative_to(source_dir):
        parser.error('--output must be outside the originals directory.')
    paths = [source_dir / relative for _, relative, _, _ in SELECTION]
    for source in paths:
        if not source.is_file():
            parser.error(f'Missing selected photograph: {source}')
    output_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for name, relative, width, description in SELECTION:
        source = source_dir / relative
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        with Image.open(source) as original:
            original_size = original.size
            image = ImageOps.exif_transpose(original)
            image.thumbnail((width, width * 2), Image.Resampling.LANCZOS)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            target = output_dir / (name + '.webp')
            profile = original.info.get('icc_profile')
            options = {'icc_profile': profile} if profile else {}
            image.save(target, 'WEBP', quality=86, method=6, **options)
            records.append({
                'image': target.name,
                'source': 'inputs/' + relative,
                'sourceSHA256': digest,
                'sourceWidth': original_size[0], 'sourceHeight': original_size[1],
                'width': image.width, 'height': image.height,
                'description': description,
            })
        if hashlib.sha256(source.read_bytes()).hexdigest() != digest:
            raise RuntimeError(f'Original photograph changed: {source}')
        print(f'{target.name}: {records[-1]["width"]}×{records[-1]["height"]}, {target.stat().st_size:,} bytes')
    (output_dir / 'photos.json').write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    lines = [
        '# Group laboratory photographs', '',
        'These photographs were supplied by HWSec-CSIC for use on this website. The repository retains the six selected source photographs in `inputs/` needed to reproduce the published WebP assets.', '',
        'The source files remain unchanged. WebP derivatives preserve the full composition and colour, with downsampling and compression for delivery. There is no retouching, compositing or generated content. Display crops use CSS only.', '',
        'The photographs describe visible equipment. They are contextual images and do not establish that a pictured device is a particular publication’s prototype, a 65-nm RO-PUF, or a chiplet implementation. Published figures with their own attribution remain in `assets/images/research/`.', '',
        'Reproduce these derivatives with `python3 scripts/prepare_photos.py` after installing Pillow in a virtual environment. The normal site build does not require Pillow. `photos.json` records original file hashes, dimensions and the selection.', '',
        'Photographer names, optional affiliations and optional HTTPS profile links are maintained once per collection in `assets/docs/photo-credits.json`. Blank photographer fields omit public credits. Rebuild with `python3 scripts/build.py` after editing them. These credits are separate from the technical metadata in `photos.json` and from scientific figure attribution.', '',
        '| Website asset | Original file | Delivery dimensions | Use |',
        '| --- | --- | --- | --- |',
    ]
    lines.extend(f'| `{r["image"]}` | `{r["source"]}` | {r["width"]} × {r["height"]} | {r["description"]} |' for r in records)
    (output_dir / 'SOURCES.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
