# Group laboratory photographs

These photographs were supplied by HWSec-CSIC for use on this website. The repository retains the six selected source photographs in `inputs/` needed to reproduce the published WebP assets.

The source files remain unchanged. WebP derivatives preserve the full composition and colour, with downsampling and compression for delivery. There is no retouching, compositing or generated content. Display crops use CSS only.

The photographs describe visible equipment. They are contextual images and do not establish that a pictured device is a particular publication’s prototype, a 65-nm RO-PUF, or a chiplet implementation. Published figures with their own attribution remain in `assets/images/research/`.

Reproduce these derivatives with `python3 scripts/prepare_photos.py` after installing Pillow in a virtual environment. The normal site build does not require Pillow. `photos.json` records original file hashes, dimensions and the selection.

Photographer names, optional affiliations and optional HTTPS profile links are maintained once per collection in `assets/docs/photo-credits.json`. Blank photographer fields omit public credits. Rebuild with `python3 scripts/build.py` after editing them. These credits are separate from the technical metadata in `photos.json` and from scientific figure attribution.

| Website asset | Original file | Delivery dimensions | Use |
| --- | --- | --- | --- |
| `packaged-chip.webp` | `inputs/Fotos_SPIRS/A60A1685.jpg` | 1920 × 1080 | Wire-bonded chip package; homepage hero. |
| `spirs-evaluation.webp` | `inputs/Fotos_SPIRS/A60A1673.jpg` | 1200 × 675 | SPIRS evaluation board; secure SoCs research area. |
| `wire-bonded-die.webp` | `inputs/Fotos_SPIRS/A60A1681.jpg` | 960 × 944 | Exposed die and bond wires; physical security research area. |
| `fibre-alignment.webp` | `inputs/Mesa óptica - set up/DSC01395.JPG` | 1200 × 800 | Fibre alignment stages; integrated photonics research area. |
| `spirs-measurement.webp` | `inputs/Fotos_SPIRS/_60A9978.jpg` | 1440 × 810 | SPIRS hardware connected to probes and cables; evaluation context. |
| `optical-bench.webp` | `inputs/Mesa óptica - set up/DSC01384.JPG` | 1440 × 960 | Optical bench with microscope and alignment stages; photonics context. |
