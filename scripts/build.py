#!/usr/bin/env python3
"""Build the GitHub Pages site from JSON and templates. Python 3.10+, no packages."""

from __future__ import annotations

import argparse
from collections import defaultdict
from functools import lru_cache
import hashlib
from html import escape
import json
from pathlib import Path
import re
from string import Template
import sys
import unicodedata
from urllib.parse import urlparse
from xml.etree import ElementTree

from project_dates import STATUS_LABELS, project_duration, project_period, project_status, validate_project_dates
from publication_authors import authored_names, team_member_ids
from photo_credits import PhotoCreditError, credit_for_image, load_photo_credits

ROOT = Path(__file__).resolve().parents[1]
ARROW = '<span class="link-arrow" aria-hidden="true">→</span>'
SEARCH_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/></svg>'
MARK = '<svg class="brand-mark" viewBox="0 0 40 40" aria-hidden="true"><rect width="40" height="40" rx="2" fill="currentColor"/><path d="M11 8v24M29 8v24M11 20h18M8 12h6M26 12h6M8 28h6M26 28h6" stroke="var(--navy)" stroke-width="2"/><rect x="17" y="17" width="6" height="6" fill="var(--cyan)"/></svg>'


class ContentError(ValueError):
    """An actionable error in developer-maintained content."""


def e(value: object) -> str:
    return escape(str(value), quote=True)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContentError(message)


def fields(record: dict, required: tuple[str, ...], location: str) -> None:
    require(isinstance(record, dict), f'{location}: expected an object.')
    for field in required:
        require(isinstance(record.get(field), str) and bool(record[field].strip()),
                f'{location}.{field}: expected a non-empty string.')


def identifier(value: str, location: str) -> None:
    require(isinstance(value, str) and bool(re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', value)),
            f'{location}: use a lowercase ID such as "phd-students".')


def url(value: str, location: str, *, local: bool = False) -> None:
    require(isinstance(value, str) and bool(value.strip()), f'{location}: expected a URL.')
    parsed = urlparse(value)
    if local and not parsed.scheme and not parsed.netloc:
        require(not value.startswith('/') and not parsed.query and not parsed.fragment,
                f'{location}: use a relative asset path.')
        path = (ROOT / value).resolve()
        require(path.is_relative_to(ROOT) and path.is_file(),
                f'{location}: local file does not exist: {value}')
    else:
        require(parsed.scheme == 'https' and bool(parsed.netloc),
                f'{location}: use a full HTTPS URL.')


def validate_links(links: list, location: str) -> None:
    require(isinstance(links, list), f'{location}: expected an array.')
    for index, link in enumerate(links):
        path = f'{location}[{index}]'
        fields(link, ('label', 'url'), path)
        url(link['url'], path + '.url')


def validate_groups(data: dict, key: str, location: str) -> set[str]:
    require(isinstance(data, dict), f'{location}: expected an object.')
    require(isinstance(data.get('groups'), list), f'{location}.groups: expected an array.')
    require(isinstance(data.get(key), list), f'{location}.{key}: expected an array.')
    ids: set[str] = set()
    for index, group in enumerate(data['groups']):
        path = f'{location}.groups[{index}]'
        fields(group, ('id', 'label'), path)
        identifier(group['id'], path + '.id')
        require(group['id'] not in ids, f'{path}: duplicate group ID "{group["id"]}".')
        ids.add(group['id'])
    return ids


def validate(site: dict, team: dict, publications: list, projects: dict) -> None:
    fields(site, ('name', 'url', 'institution', 'institutionShort', 'address', 'city', 'phone', 'contactFormKey'), 'site.json')
    if 'shortName' in site:
        fields(site, ('shortName',), 'site.json')
    url(site['url'], 'site.json.url')
    require(re.fullmatch(r'\+[\d ]+', site['phone']) is not None, 'site.json.phone: expected an international phone number.')
    require(type(site.get('copyrightYear')) is int, 'site.json.copyrightYear: expected an integer.')
    for name in ('institutions', 'socialLinks'):
        validate_links(site.get(name), 'site.json.' + name)

    groups = validate_groups(team, 'members', 'team.json')
    member_ids: set[str] = set()
    for index, member in enumerate(team['members']):
        path = f'team.json.members[{index}]'
        fields(member, ('id', 'name', 'role', 'group'), path)
        identifier(member['id'], path + '.id')
        require(member['id'] not in member_ids, f'{path}: duplicate member ID "{member["id"]}".')
        member_ids.add(member['id'])
        require(member['group'] in groups, f'{path}.group: unknown group "{member["group"]}".')
        if member.get('photo'):
            url(member['photo'], path + '.photo', local=True)
        if 'photoPosition' in member:
            require(isinstance(member['photoPosition'], str) and bool(re.fullmatch(r'(?:100|\d{1,2})% (?:100|\d{1,2})%', member['photoPosition'])),
                    f'{path}.photoPosition: use two percentages, e.g. "50% 30%".')
        for name in ('bio', 'affiliation', 'photo'):
            if name in member:
                require(isinstance(member[name], str), f'{path}.{name}: expected a string.')
        if 'tags' in member:
            require(isinstance(member['tags'], list) and all(isinstance(t, str) for t in member['tags']), f'{path}.tags: expected an array of strings.')
        if 'authorNames' in member:
            require(isinstance(member['authorNames'], list)
                    and all(isinstance(name, str) and bool(name.strip()) for name in member['authorNames']),
                    f'{path}.authorNames: expected an array of non-empty publication-name aliases.')
        for name in ('visible',):
            if name in member:
                require(type(member[name]) is bool, f'{path}.{name}: expected true or false.')
        validate_links(member.get('links', []), path + '.links')

    require(isinstance(publications, list), 'publications.json: expected an array.')
    dois: set[str] = set()
    publication_ids: set[str] = set()
    for index, publication in enumerate(publications):
        path = f'publications.json[{index}]'
        fields(publication, ('title', 'journal'), path)
        require(isinstance(publication.get('authors'), list) and bool(publication['authors'])
                and all(isinstance(a, str) and a.strip() for a in publication['authors']), f'{path}.authors: expected a non-empty array of names.')
        require(type(publication.get('year')) is int and 1900 <= publication['year'] <= 2200,
                f'{path}.year: expected a four-digit integer.')
        if 'doi' in publication:
            require(isinstance(publication['doi'], str), f'{path}.doi: expected a string.')
        if publication.get('doi'):
            require(re.fullmatch(r'10\.\d{4,9}/\S+', publication['doi']) is not None,
                    f'{path}.doi: use the DOI only, e.g. "10.1145/3445979".')
            require(publication['doi'].casefold() not in dois, f'{path}.doi: duplicate DOI "{publication["doi"]}".')
            dois.add(publication['doi'].casefold())
        else:
            fields(publication, ('id', 'url'), path)
        if 'id' in publication:
            identifier(publication['id'], path + '.id')
            require(publication['id'] not in publication_ids, f'{path}.id: duplicate publication ID "{publication["id"]}".')
            publication_ids.add(publication['id'])
        if 'url' in publication:
            url(publication['url'], path + '.url')
        require(publication.get('type', 'journal') in ('journal', 'conference'), f'{path}.type: use "journal" or "conference".')
        for name in ('volume', 'issue', 'pages', 'article'):
            if name in publication:
                require(isinstance(publication[name], (str, int)), f'{path}.{name}: expected a string or integer.')
        for name in ('pdf', 'code'):
            if publication.get(name):
                url(publication[name], path + '.' + name, local=name == 'pdf')
        if 'eligibilityException' in publication:
            fields(publication, ('eligibilityException',), path)
        members = team_member_ids(publication['authors'], team)
        require(len(members) >= 2 or bool(publication.get('eligibilityException')),
                f'{path}.authors: at least two distinct visible team members are required '
                f'(matched {len(members)}). Check authorNames in team.json for published name variants.')

    groups = validate_groups(projects, 'projects', 'projects.json')
    project_ids: set[str] = set()
    for index, project in enumerate(projects['projects']):
        path = f'projects.json.projects[{index}]'
        fields(project, ('id', 'name', 'title', 'group', 'abstract', 'funder'), path)
        identifier(project['id'], path + '.id')
        require(project['id'] not in project_ids, f'{path}: duplicate project ID "{project["id"]}".')
        project_ids.add(project['id'])
        require(project['group'] in groups, f'{path}.group: unknown group.')
        try:
            validate_project_dates(project, path)
        except ValueError as error:
            raise ContentError(str(error)) from error
        for name in ('programme', 'period'):
            if name in project:
                fields(project, (name,), path)
        require(isinstance(project.get('details'), list), f'{path}.details: expected an array.')
        for i, detail in enumerate(project['details']):
            fields(detail, ('label', 'value'), f'{path}.details[{i}]')
        if project.get('url'):
            url(project['url'], path + '.url')


def load_content() -> tuple[dict, dict, list, dict]:
    records = []
    for name in ('site', 'team', 'publications', 'projects'):
        path = ROOT / 'assets' / 'docs' / f'{name}.json'
        try:
            records.append(json.loads(path.read_text(encoding='utf-8')))
        except json.JSONDecodeError as error:
            raise ContentError(f'{path.name}:{error.lineno}:{error.colno}: {error.msg}') from error
    validate(*records)
    return tuple(records)


def template(name: str, values: dict) -> str:
    return Template((ROOT / 'templates' / name).read_text(encoding='utf-8')).substitute(values)


def external_link(label: str, href: str, css: str = '', accessible_label: str = '') -> str:
    aria = f' aria-label="{e(accessible_label)}"' if accessible_label else ''
    return f'<a class="{e(css)}" href="{e(href)}" target="_blank" rel="noopener noreferrer"{aria}>{e(label)} {ARROW}</a>'


@lru_cache(maxsize=5)
def link_icon(name: str) -> str:
    """Inline our five locally stored brand marks; no external icon service."""
    svg = ElementTree.fromstring((ROOT / 'assets' / 'icons' / (name + '.svg')).read_text(encoding='utf-8'))
    paths = ''.join(f'<path d="{e(path.attrib["d"])}"/>'
                    for path in svg if path.tag.rsplit('}', 1)[-1] == 'path')
    return f'<svg class="link-icon" viewBox="{e(svg.attrib["viewBox"])}" fill="currentColor" aria-hidden="true" focusable="false">{paths}</svg>'


def profile_link(label: str, href: str, accessible_label: str = '') -> str:
    host = (urlparse(href).hostname or '').casefold().removeprefix('www.')
    icon = {'github.com': 'github', 'gitlab.com': 'gitlab', 'linkedin.com': 'linkedin', 'orcid.org': 'orcid'}.get(host)
    if re.fullmatch(r'scholar\.google\.[a-z.]+', host):
        icon = 'googlescholar'
    if not icon:
        return external_link(label, href, accessible_label=accessible_label)
    description = accessible_label or label
    return f'<a class="icon-link" href="{e(href)}" target="_blank" rel="noopener noreferrer" aria-label="{e(description)}" title="{e(description)}">{link_icon(icon)}</a>'


def photographer_attribution(dataset: dict) -> str:
    name = e(dataset['photographer'].strip())
    href = dataset.get('url', '').strip()
    name = f'<a href="{e(href)}" target="_blank" rel="noopener noreferrer">{name}</a>' if href else name
    affiliation = dataset.get('affiliation', '').strip()
    return name + (f' ({e(affiliation)})' if affiliation else '')


def photo_credit(image: str, datasets: list | None = None) -> str:
    dataset = credit_for_image(image, datasets or [])
    return f'<span class="photo-credit">Photo: {photographer_attribution(dataset)}</span>' if dataset else ''


def collection_photo_credits(images: list[str], datasets: list) -> str:
    credits = {}
    for image in images:
        dataset = credit_for_image(image, datasets)
        if dataset:
            key = (dataset['photographer'].strip(), dataset.get('affiliation', '').strip(), dataset.get('url', '').strip())
            if key not in credits:
                credits[key] = {'dataset': dataset, 'labels': []}
            if dataset['label'] not in credits[key]['labels']:
                credits[key]['labels'].append(dataset['label'])
    if not credits:
        return ''
    names = []
    for credit in credits.values():
        label = e(' / '.join(credit['labels'])) + ': ' if len(credits) > 1 else ''
        names.append(label + photographer_attribution(credit['dataset']))
    return '<p class="photo-credits">Photography · ' + ' · '.join(names) + '</p>'


def options(groups: list) -> str:
    return ''.join(f'<option value="{e(g["id"])}">{e(g["label"])}</option>' for g in groups)


def team_sections(team: dict) -> str:
    sections = []
    for group in team['groups']:
        members = [m for m in team['members'] if m['group'] == group['id'] and m.get('visible', True)]
        if not members:
            continue
        cards = []
        for member in members:
            if member.get('photo'):
                position = member.get('photoPosition', '50% 30%')
                photo = f'<img src="{e(member["photo"])}" alt="{e(member["name"])}" loading="lazy" decoding="async" style="object-position: {e(position)}">'
            else:
                initials = ''.join(part[0] for part in member['name'].removeprefix('Dr. ').split()[:2])
                photo = f'<span class="initials" aria-hidden="true">{e(initials)}</span>'
            extras = ''
            for field, css in (('affiliation', 'person-affiliation'), ('bio', 'person-bio')):
                if member.get(field):
                    extras += f'<p class="{css}">{e(member[field])}</p>'
            if member.get('tags'):
                extras += '<ul class="person-tags" aria-label="Research interests">' + ''.join(f'<li>{e(tag)}</li>' for tag in member['tags']) + '</ul>'
            links = ''.join(profile_link(link['label'], link['url'], accessible_label=f'{link["label"]} — {member["name"]}') for link in member.get('links', []))
            haystack = ' '.join([member['name'], member['role'], member.get('bio', ''), member.get('affiliation', ''), *member.get('tags', [])])
            cards.append(f'''<article class="person" id="{e(member['id'])}" data-item data-group="{e(group['id'])}" data-search-text="{e(haystack)}">
  <div class="person-photo">{photo}</div>
  <div class="person-info"><h3>{e(member['name'])}</h3><p class="person-role">{e(member['role'])}</p>{extras}<div class="person-links">{links}</div></div>
</article>''')
        sections.append(f'''<section class="team-group" id="{e(group['id'])}" data-size="{len(members)}" data-section aria-labelledby="heading-{e(group['id'])}">
  <div class="group-heading"><h2 id="heading-{e(group['id'])}">{e(group['label'])}</h2><span class="group-count" data-section-count>{len(members)} people</span></div>
  <div class="team-grid">{''.join(cards)}</div>
</section>''')
    return '\n'.join(sections)


def publication_reference(publication: dict) -> str:
    """Source references use a DOI, or an explicit stable ID when none exists."""
    return publication.get('doi') or publication['id']


def publication_identity(publication: dict) -> str:
    """Namespace IDs and normalize DOIs for deduplication and citation keys."""
    return ('doi:' if publication.get('doi') else 'id:') + publication_reference(publication).casefold()


def publication_url(publication: dict) -> str:
    return 'https://doi.org/' + publication['doi'] if publication.get('doi') else publication['url']


def citation(publication: dict) -> str:
    source = [publication['journal']]
    for field, prefix in (('volume', 'vol. '), ('issue', 'no. '), ('pages', 'pp. '), ('article', 'article ')):
        if publication.get(field):
            source.append(prefix + str(publication[field]))
    return f'{", ".join(publication["authors"])}. {publication["title"]}. {", ".join(source)}, {publication["year"]}. {publication_url(publication)}'


def tex(value: object) -> str:
    replacements = {'\\': r'\textbackslash{}', '{': r'\{', '}': r'\}', '&': r'\&', '%': r'\%', '_': r'\_', '#': r'\#', '$': r'\$', '~': r'\textasciitilde{}', '^': r'\textasciicircum{}'}
    return ''.join(replacements.get(char, char) for char in str(value))


def bibtex(publication: dict) -> str:
    author = publication['authors'][0].split()[-1]
    key = re.sub(r'[^a-z0-9]', '', unicodedata.normalize('NFKD', author).encode('ascii', 'ignore').decode().lower())
    key += str(publication['year']) + hashlib.sha256(publication_identity(publication).encode()).hexdigest()[:6]
    conference = publication.get('type') == 'conference'
    entries = [('author', tex(' and '.join(publication['authors']))), ('title', '{' + tex(publication['title']) + '}'), ('booktitle' if conference else 'journal', tex(publication['journal'])), ('year', str(publication['year']))]
    for source, target in (('volume', 'volume'), ('issue', 'number'), ('pages', 'pages'), ('article', 'eid')):
        if publication.get(source):
            value = str(publication[source])
            if source == 'pages':
                value = re.sub(r'(?<=\d)[–-](?=\d)', '--', value)
            entries.append((target, tex(value)))
    if publication.get('doi'):
        entries.append(('doi', tex(publication['doi'])))
    else:
        entries.append(('url', tex(publication['url'])))
    return '@' + ('inproceedings' if conference else 'article') + '{' + key + ',\n' + ',\n'.join(f'  {field} = {{{value}}}' for field, value in entries) + '\n}'


def publication_card(publication: dict, number: int | None = None, team: dict | None = None) -> str:
    kind = publication.get('type', 'journal')
    haystack = ' '.join([publication['title'], *publication['authors'], publication['journal'], publication_reference(publication), publication_url(publication)])
    source = [publication['journal']]
    for field, label in (('volume', 'Vol. '), ('issue', 'No. '), ('pages', 'pp. '), ('article', 'Article ')):
        if publication.get(field):
            source.append(label + str(publication[field]))
    source_label = 'Read paper' if publication.get('doi') else 'View source'
    links = external_link(source_label, publication_url(publication), 'text-link', source_label + ': ' + publication['title'])
    if publication.get('doi') and publication.get('url') and publication['url'] != publication_url(publication):
        links += external_link('Repository', publication['url'], 'text-link', 'Repository: ' + publication['title'])
    for field, label in (('pdf', 'PDF'), ('code', 'Code')):
        if publication.get(field):
            links += (profile_link(label, publication[field], 'Source code: ' + publication['title'])
                      if field == 'code' else external_link(label, publication[field], 'text-link'))
    number_label = f'<span class="publication-number" aria-hidden="true">[{number:02d}]</span>' if number is not None else ''
    return f'''<article class="publication" data-item data-year="{publication['year']}" data-type="{kind}" data-search-text="{e(haystack)}">
  {number_label}
  <span class="publication-type eyebrow">{kind.title()}</span>
  <h3>{external_link(publication['title'], publication_url(publication))}</h3>
  <p class="publication-authors">{authored_names(publication['authors'], team or {})}</p>
  <p class="publication-source">{e(' · '.join(source))}</p>
  <div class="publication-actions">{links}
    <details class="citation-details"><summary>Cite <span aria-hidden="true">+</span></summary>
      <div class="citation-panel">
        <div class="citation-heading"><h4>Plain-text citation</h4><button class="copy-button" type="button" data-copy="citation" data-enhancement hidden aria-label="Copy citation: {e(publication['title'])}">Copy citation</button></div>
        <p data-citation>{e(citation(publication))}</p>
        <div class="citation-heading"><h4>BibTeX</h4><button class="copy-button" type="button" data-copy="bibtex" data-enhancement hidden aria-label="Copy BibTeX: {e(publication['title'])}">Copy BibTeX</button></div>
        <pre data-bibtex>{e(bibtex(publication))}</pre>
      </div>
    </details>
  </div>
</article>'''


def publication_sections(publications: list, team: dict | None = None) -> str:
    years = defaultdict(list)
    for publication in publications:
        years[publication['year']].append(publication)
    ordered = sorted(publications, key=lambda publication: publication['year'], reverse=True)
    numbers = {publication_identity(publication): index for index, publication in enumerate(ordered, 1)}
    return '\n'.join(f'''<section class="publication-year" data-section data-year="{year}" aria-labelledby="year-{year}">
  <div class="year-heading"><h2 id="year-{year}">{year}</h2><span data-section-count>{len(years[year])} publications</span></div>
  <div class="year-publications">{''.join(publication_card(p, numbers[publication_identity(p)], team) for p in years[year])}</div>
</section>''' for year in sorted(years, reverse=True))


def project_attributes(project: dict) -> str:
    """Expose the same date source to the browser and static HTML."""
    return f'data-project="{e(project["id"])}" data-start-date="{e(project.get("startDate", ""))}" data-end-date="{e(project.get("endDate", ""))}" data-status="{project_status(project)}"'


def current_projects(projects: dict, limit: int = 3) -> str:
    """Include future candidates so a loaded page can keep its preview current."""
    records = projects['projects']
    ongoing = [project for project in records if project_status(project) == 'ongoing']
    candidates = ongoing or [p for state in ('upcoming', 'completed') for p in records if project_status(p) == state]
    selected = {project['id'] for project in candidates[:limit]}
    return '\n'.join(f'''<article class="home-project" data-current-project-item {project_attributes(project)}{'' if project['id'] in selected else ' hidden'}>
  <div class="home-project-top"><h3><a href="projects.html#{e(project['id'])}">{e(project['name'])}</a></h3><span class="project-status status-{project_status(project)}" data-project-status>{STATUS_LABELS[project_status(project)]}</span></div>
  <p class="project-programme">{e(project.get('programme', project['funder']))}</p>
  <p class="project-period">{e(project_period(project))}</p>
  <p class="project-abstract">{e(project['abstract'])}</p>
</article>''' for project in records)


def latest_publication(publication: dict, team: dict | None = None) -> str:
    """A compact home entry with the same complete citation as the archive."""
    source = [publication['journal']]
    for field, label in (('volume', 'Vol. '), ('issue', 'No. '), ('pages', 'pp. '), ('article', 'Article ')):
        if publication.get(field):
            source.append(label + str(publication[field]))
    title = publication['title']
    link_label = ('Read paper: ' if publication.get('doi') else 'Publication source: ') + title
    return f'''<article class="latest-publication">
  <span class="latest-publication-year">{publication['year']}</span>
  <div class="latest-publication-copy"><h3>{external_link(title, publication_url(publication))}</h3><p class="publication-authors">{authored_names(publication['authors'], team or {})}</p><p class="publication-source">{e(' · '.join(source))}</p></div>
  <div class="latest-publication-actions">
    {external_link('Link', publication_url(publication), 'text-link', link_label)}
    <details class="citation-details"><summary>Citation</summary><div class="citation-panel"><div class="citation-heading"><h4>Plain-text citation</h4><button class="copy-button" type="button" data-copy="citation" data-enhancement hidden aria-label="Copy citation: {e(title)}">Copy citation</button></div><p data-citation>{e(citation(publication))}</p></div></details>
    <details class="citation-details"><summary>BibTeX</summary><div class="citation-panel"><div class="citation-heading"><h4>BibTeX</h4><button class="copy-button" type="button" data-copy="bibtex" data-enhancement hidden aria-label="Copy BibTeX: {e(title)}">Copy BibTeX</button></div><pre data-bibtex>{e(bibtex(publication))}</pre></div></details>
  </div>
</article>'''


def project_sections(projects: dict) -> str:
    sections = []
    for group in projects['groups']:
        cards = []
        for project in [p for p in projects['projects'] if p['group'] == group['id']]:
            duration = project_duration(project)
            details = (f'<div><dt>Duration</dt><dd>{e(duration)}</dd></div>' if duration else '')
            details += ''.join(f'<div><dt>{e(d["label"])}</dt><dd>{e(d["value"])}</dd></div>' for d in project['details'] if d['label'].casefold() != 'duration')
            link = external_link('Project website', project['url'], 'text-link') if project.get('url') else ''
            programme = project.get('programme', project['funder'])
            haystack = ' '.join([project['name'], project['title'], project['abstract'], project['funder'], programme, project_period(project), *(d['value'] for d in project['details'])])
            cards.append(f'''<article class="project" id="{e(project['id'])}" data-item data-group="{e(group['id'])}" {project_attributes(project)} data-search-text="{e(haystack)}">
  <div class="project-overview">
    <div class="project-top"><h3>{e(project['name'])}</h3><h4 class="project-title">{e(project['title'])}</h4></div>
    <p class="project-programme">{e(programme)}</p><p class="project-period">{e(project_period(project))}</p>
    <span class="project-status status-{project_status(project)}" data-project-status><span aria-hidden="true"></span>{STATUS_LABELS[project_status(project)]}</span>
  </div>
  <details class="project-details"><summary>About the project <span aria-hidden="true">+</span></summary><p class="project-abstract">{e(project['abstract'])}</p><dl>{details}<div><dt>Funded by</dt><dd>{e(project['funder'])}</dd></div></dl>{link}</details>
</article>''')
        if cards:
            sections.append(f'''<section class="project-group" id="{e(group['id'])}" data-section aria-labelledby="heading-{e(group['id'])}">
  <div class="project-group-heading"><h2 id="heading-{e(group['id'])}">{e(group['label'])}</h2><span class="group-count" data-section-count>{len(cards)} projects</span></div>
  <div class="project-index-labels" aria-hidden="true"><span>Project</span><span>Programme</span><span>Period</span><span>Status</span></div>
  <div class="project-index">{''.join(cards)}</div>
</section>''')
    return '\n'.join(sections)


def load_featured(publications: list, projects: dict) -> list:
    path = ROOT / 'assets' / 'docs' / 'featured.json'
    try:
        records = json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as error:
        raise ContentError(f'{path.name}:{error.lineno}:{error.colno}: {error.msg}') from error
    validate_featured(records, publications, projects)
    return records


def validate_featured(records: list, publications: list, projects: dict) -> None:
    require(isinstance(records, list), 'featured.json: expected an array.')
    references = {
        'publication': {publication_reference(p).casefold() for p in publications},
        'project': {p['id'] for p in projects['projects']},
    }
    ids = set()
    for index, record in enumerate(records):
        path = f'featured.json[{index}]'
        fields(record, ('id', 'kind', 'reference', 'heading', 'description'), path)
        identifier(record['id'], path + '.id')
        require(record['id'] not in ids, f'{path}.id: duplicate featured work ID.')
        ids.add(record['id'])
        require(record['kind'] in references, f'{path}.kind: use "publication" or "project".')
        reference = record['reference'].casefold() if record['kind'] == 'publication' else record['reference']
        require(reference in references[record['kind']], f'{path}.reference: no matching {record["kind"]} in the source data.')
        require(isinstance(record.get('topics', []), list) and all(isinstance(t, str) for t in record.get('topics', [])), f'{path}.topics: expected an array of strings.')
        if record.get('diagram'):
            require(record['diagram'] in ('mlkem', 'puf', 'photonics'), f'{path}.diagram: use "mlkem", "puf" or "photonics".')
        if 'cover' in record:
            cover = record['cover']
            fields(cover, ('image', 'alt', 'caption'), path + '.cover')
            url(cover['image'], path + '.cover.image', local=True)
            if 'width' in cover or 'height' in cover:
                for dimension in ('width', 'height'):
                    require(type(cover.get(dimension)) is int and cover[dimension] > 0, f'{path}.cover.{dimension}: expected a positive integer; set both width and height.')
        if 'figure' in record:
            figure = record['figure']
            fields(figure, ('image', 'alt', 'caption', 'credit', 'source', 'license', 'licenseLabel'), path + '.figure')
            url(figure['image'], path + '.figure.image', local=True)
            url(figure['source'], path + '.figure.source')
            url(figure['license'], path + '.figure.license')
            if 'width' in figure or 'height' in figure:
                for dimension in ('width', 'height'):
                    require(type(figure.get(dimension)) is int and figure[dimension] > 0, f'{path}.figure.{dimension}: expected a positive integer; set both width and height.')


def featured_work(records: list, publications: list, projects: dict, team: dict | None = None, photo_datasets: list | None = None) -> str:
    articles = []
    for index, record in enumerate(records):
        if record['kind'] == 'publication':
            source = next(p for p in publications if publication_reference(p).casefold() == record['reference'].casefold())
            href = publication_url(source)
            kind = f'{source["journal"]} · {source["year"]}'
            source_label = 'Read paper' if source.get('doi') else 'View source'
            links = external_link(source_label, href, 'text-link', source_label + ': ' + source['title'])
            if source.get('doi') and source.get('url') and source['url'] != href:
                links += external_link('Repository', source['url'], 'text-link', 'Repository: ' + source['title'])
            if source.get('code'):
                links += profile_link('Source code', source['code'], 'Source code: ' + record['heading'])
            heading_link = external_link(source['title'], href)
            metadata = f'<p class="feature-authors">{authored_names(source["authors"], team or {})}</p>'
        else:
            source = next(p for p in projects['projects'] if p['id'] == record['reference'])
            href = 'projects.html#' + source['id']
            kind = f'{source.get("programme", "Research project")} · {project_period(source)}'
            links = f'<a class="text-link" href="{e(href)}">Explore {e(source["name"])} {ARROW}</a>'
            heading_link = f'<a href="{e(href)}">{e(source["title"])} {ARROW}</a>'
            metadata = ''
        diagram = ''
        if record.get('diagram'):
            svg = (ROOT / 'templates' / (record['diagram'] + '.svg')).read_text(encoding='utf-8')
            # Scope IDs so the same diagram can illustrate several featured records.
            svg = re.sub(r'id="([^"]+)"', lambda m: f'id="feature-{record["id"]}-{m[1]}"', svg)
            svg = re.sub(r'aria-labelledby="([^"]+)"', lambda m: 'aria-labelledby="' + ' '.join(f'feature-{record["id"]}-{name}' for name in m[1].split()) + '"', svg)
            diagram = f'<div class="feature-diagram">{svg}</div>'
        research_figure = ''
        if record.get('figure'):
            figure = record['figure']
            dimensions = f' width="{figure["width"]}" height="{figure["height"]}"' if 'width' in figure and 'height' in figure else ''
            research_figure = f'''<figure class="research-figure"><a href="{e(figure['image'])}" target="_blank" rel="noopener noreferrer" aria-label="View full-size figure: {e(figure['caption'])}"><img src="{e(figure['image'])}" alt="{e(figure['alt'])}"{dimensions} loading="lazy" decoding="async"></a>
  <figcaption><span>{e(figure['caption'])}</span><span>{e(figure['credit'])}. <a href="{e(figure['source'])}" target="_blank" rel="noopener noreferrer">Original article</a> · <a href="{e(figure['license'])}" target="_blank" rel="noopener noreferrer">{e(figure['licenseLabel'])}</a> · <a href="{e(figure['image'])}" target="_blank" rel="noopener noreferrer">Full-size figure</a></span></figcaption>
</figure>'''
        if record.get('cover'):
            cover = record['cover']
            dimensions = f' width="{cover["width"]}" height="{cover["height"]}"' if 'width' in cover and 'height' in cover else ''
            visual = f'<figure class="feature-cover"><img src="{e(cover["image"])}" alt="{e(cover["alt"])}"{dimensions} loading="lazy" decoding="async"><figcaption>{e(cover["caption"])}{photo_credit(cover["image"], photo_datasets)}</figcaption></figure>'
            if research_figure:
                research_figure = '<details class="feature-figure-details"><summary>Research figure <span aria-hidden="true">+</span></summary>' + research_figure + '</details>'
        else:
            visual = research_figure or diagram
            research_figure = ''
        topics = '<div class="feature-topics">' + ''.join(f'<span>{e(topic)}</span>' for topic in record.get('topics', [])) + '</div>' if record.get('topics') else ''
        short_heading = f'<p class="feature-heading">{e(record["heading"])}</p>' if record['heading'] != source['title'] else ''
        heading_id = 'featured-title-' + record['id']
        body = f'<div class="feature-copy">{topics}<span class="feature-kind">{e(kind)}</span>{short_heading}<h3 id="{e(heading_id)}">{heading_link}</h3>{metadata}<p class="feature-description">{e(record["description"])}</p><div class="feature-links">{links}<a class="text-link" href="publications.html">View all publications {ARROW}</a></div>{research_figure}</div>'
        articles.append(f'<article class="featured-work feature-showcase {"feature-lead" if index == 0 else "feature-side"}" id="featured-{e(record["id"])}" aria-labelledby="{e(heading_id)}" data-featured-item data-featured-title="{e(source["title"])}"><div class="feature-visual">{visual}</div>{body}</article>')
    return '\n'.join(articles)


def build_site() -> dict[str, str]:
    site, team, publications, projects = load_content()
    try:
        photo_datasets = load_photo_credits(ROOT)
    except PhotoCreditError as error:
        raise ContentError(str(error)) from error
    short_name = site.get('shortName', site['name'])
    values = {key: e(value) for key, value in site.items() if not isinstance(value, list)}
    years = sorted({p['year'] for p in publications}, reverse=True)
    visible_members = [m for m in team['members'] if m.get('visible', True)]
    group_heading = ' '.join(f'<span class="group-term">{e(word)}</span>' if '-' in word else e(word) for word in site['name'].split(' '))
    values.update(group_name=e(site['name']), group_heading=group_heading, site_name=e(short_name), arrow=ARROW, search_icon=SEARCH_ICON,
                  people_count=len(visible_members), group_count=len({m['group'] for m in visible_members}),
                  publication_count=len(publications), project_count=len(projects['projects']),
                  active_project_count=sum(project_status(project) == 'ongoing' for project in projects['projects']),
                  year_range=f'{min(years)}–{max(years)}' if years else 'Archive',
                  group_options=options(team['groups']), project_group_options=options(projects['groups']), year_options=''.join(f'<option value="{year}">{year}</option>' for year in years),
                  team_sections=team_sections(team), publication_sections=publication_sections(publications, team), project_sections=project_sections(projects),
                  phone_raw=e(site['phone'].replace(' ', '')))
    latest = sorted(publications, key=lambda p: p['year'], reverse=True)[:3]
    values['latest_publications'] = '\n'.join(latest_publication(publication, team) for publication in latest)
    values['featured_work'] = featured_work(load_featured(publications, projects), publications, projects, team, photo_datasets)
    values['hero_photo_credit'] = photo_credit('assets/images/lab/packaged-chip.webp', photo_datasets)
    values['group_photo_credit'] = photo_credit('assets/images/grupo.jpeg', photo_datasets)
    values['research_photo_credits'] = collection_photo_credits([
        'assets/images/lab/spirs-evaluation.webp', 'assets/images/lab/wire-bonded-die.webp',
        'assets/images/lab/fibre-alignment.webp', 'assets/images/lab/spirs-measurement.webp',
    ], photo_datasets)
    values['team_photo_credits'] = collection_photo_credits([member['photo'] for member in visible_members if member.get('photo')], photo_datasets)
    values['current_projects'] = current_projects(projects)
    descriptions = {
        'index': (site['name'], f'{site["name"]} ({short_name}) researches secure RISC-V systems, cryptographic hardware and integrated photonics at IMSE-CNM in Sevilla, Spain.'),
        'team': ('People', f'Meet the researchers, engineers and collaborators in {site["name"]} ({short_name}).'),
        'publications': ('Publications', f'Explore journal articles and conference contributions from {site["name"]} ({short_name}).'),
        'projects': ('Research Projects', f'Discover European, national and agency-funded projects from {site["name"]} ({short_name}).'),
        'contact': ('Contact', f'Contact {site["name"]} ({short_name}) at the Instituto de Microelectrónica de Sevilla for research questions, collaboration or opportunities to join the group.'),
        '404': ('Page Not Found', f'The page you are looking for could not be found. Explore {site["name"]} ({short_name}).')
    }
    pages = {}
    nav = [('index', 'About'), ('team', 'Team'), ('publications', 'Publications'), ('projects', 'Projects'), ('contact', 'Contact')]
    for page, (title, description) in descriptions.items():
        navigation = ''.join(f'<a class="nav-link{" nav-contact" if name == "contact" else ""}" href="{name}.html{"#about" if name == "index" else ""}"' + (' aria-current="page"' if page == name else '') + f'>{label}</a>' for name, label in nav)
        content = template(page + '.html', values)
        base_values = dict(values, title=e(f'{title} | {short_name}'), description=e(description),
                           canonical=e(site['url'].rstrip('/') + ('/' if page == 'index' else '/' + page + '.html')),
                           extra_meta='<base href="/"><meta name="robots" content="noindex">' if page == '404' else '',
                           extra_scripts='<script src="https://web3forms.com/client/script.js" async defer></script>' if page == 'contact' else '',
                           site_url=e(site['url'].rstrip('/')), site_name=e(short_name), copyright_year=site['copyrightYear'],
                           brand_mark=MARK, navigation=navigation, page_class=f'page-{page}', content=content,
                           institution_links=''.join(external_link(link['label'], link['url']) for link in site['institutions']),
                           social_links=''.join(profile_link(link['label'], link['url']) for link in site['socialLinks']))
        pages[page + '.html'] = '\n'.join(line.rstrip() for line in template('base.html', base_values).splitlines()) + '\n'
    return pages


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Validate content and check generated HTML without modifying files.')
    args = parser.parse_args()
    try:
        pages = build_site()
    except (ContentError, OSError, KeyError) as error:
        print(f'Content error: {error}', file=sys.stderr)
        return 1
    changed = []
    for name, content in pages.items():
        path = ROOT / name
        if not path.exists() or path.read_text(encoding='utf-8') != content:
            changed.append(name)
            if not args.check:
                path.write_text(content, encoding='utf-8')
    if args.check and changed:
        print('Generated pages are out of date: ' + ', '.join(changed) + '. Run: python3 scripts/build.py', file=sys.stderr)
        return 1
    print('Content validated. ' + ('Generated pages are up to date.' if args.check else f'Built {len(pages)} pages ({len(changed)} changed).'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
