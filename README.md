# HWSec-CSIC Website

A minimal, Apple‑inspired static site for the HWSec‑CSIC group. Built with plain HTML/CSS/JS for easy hosting on GitHub Pages.

## Structure
- `index.html` — Home page with sections: Hero, About, Research, People, Publications, Projects, Contact
- `styles.css` — Design system: system font, responsive grid, translucent header, glass cards, dark mode preference
- `script.js` — Mobile nav, reveal‑on‑scroll, smooth scrolling, back‑to‑top button
- `script.js` — Mobile nav, reveal‑on‑scroll, smooth scrolling, back‑to‑top button, team filters/list view, animated details, and publications renderer with search/sort/copy DOI
- `img/` — Images and logos
- `robots.txt`, `sitemap.xml` — Basic SEO plumbing

## Local preview
```bash
python3 -m http.server 8080
```
Open http://localhost:8080

## Notes
- All assets are local; no external dependencies.
- Images are set to `loading="lazy"` where appropriate and using `decoding="async"`.
- The site honors `prefers-reduced-motion` and `prefers-color-scheme: dark`.

## Publications: how to add or edit
- Source of truth is `data/publications.json` (array of objects). Required fields: `title`, `authors` (array of strings), `journal`, `year`, `doi`. Optional: `volume`, `issue`, `pages`, `article`.
- The list on the home page is rendered client‑side. If JSON fails to load (e.g. on very old browsers), a server‑rendered fallback list in `index.html` is shown.
- The Publications section includes a search box (title/authors/DOI) and a toggle to sort by year (descending/ascending). Each entry has a "Copy DOI" button.

Example entry in `data/publications.json`:
```
{
	"title": "Timing‑Optimized Hardware Implementation to Accelerate Polynomial Multiplication in the NTRU Algorithm",
	"authors": ["E. Camacho‑Ruiz", "S. Sánchez‑Solano", "P. Brox", "M.C. Martínez‑Rodríguez"],
	"journal": "ACM Journal on Emerging Technologies in Computing Systems",
	"volume": "17",
	"issue": "3",
	"article": "35",
	"year": 2021,
	"doi": "10.1145/3445979"
}
```

## Customization
- Replace `img/logo.jpeg` with an SVG for sharper rendering.
- Tune colors in `:root` variables inside `styles.css`.
- Add or edit content directly in `index.html`.
