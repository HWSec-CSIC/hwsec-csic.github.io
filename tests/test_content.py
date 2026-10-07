"""Regression checks for developer-edited content and static HTML output."""

from copy import deepcopy
from html.parser import HTMLParser
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from urllib.parse import unquote, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import build


class Document(HTMLParser):
    def __init__(self, content):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.references = []
        self.items = 0
        self.images = []
        self.featured = []
        self.projects = []
        self.details = []
        self.mains = 0
        self.headings = 0
        self.feed(content)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if 'data-item' in attrs:
            self.items += 1
        if 'data-featured-item' in attrs:
            self.featured.append(attrs)
        if 'data-project' in attrs:
            self.projects.append(attrs)
        if tag == 'details':
            self.details.append(attrs)
        if tag == 'main':
            self.mains += 1
        if tag == 'h1':
            self.headings += 1
        if tag == 'img':
            self.images.append(attrs)
        for field in ('href', 'src'):
            if attrs.get(field):
                self.references.append(attrs[field])


class ContentTests(unittest.TestCase):
    def setUp(self):
        self.site, self.team, self.pubs, self.projects = deepcopy(build.load_content())

    def validate(self):
        build.validate(self.site, self.team, self.pubs, self.projects)

    def test_all_source_records_reach_static_pages(self):
        pages = build.build_site()
        self.assertEqual(Document(pages['team.html']).items, sum(m.get('visible', True) for m in self.team['members']))
        self.assertEqual(Document(pages['publications.html']).items, len(self.pubs))
        self.assertEqual(Document(pages['projects.html']).items, len(self.projects['projects']))
        for paper in self.pubs:
            self.assertIn(build.e(paper['title']), pages['publications.html'])
        for person in self.team['members']:
            if person.get('visible', True):
                self.assertIn(build.e(person['name']), pages['team.html'])

    def test_local_links_assets_and_fragment_targets_exist(self):
        pages = build.build_site()
        documents = {name: Document(page) for name, page in pages.items()}
        for name, document in documents.items():
            self.assertEqual(len(document.ids), len(set(document.ids)), f'{name}: duplicate IDs')
            self.assertEqual(document.mains, 1, name)
            self.assertEqual(document.headings, 1, name)
            for image in document.images:
                self.assertTrue(image.get('alt'), f'{name}: missing image description')
            for reference in document.references:
                parsed = urlparse(reference)
                if parsed.scheme or parsed.netloc:
                    continue
                target = parsed.path or name
                self.assertTrue((build.ROOT / target).exists(), f'{name}: missing {target}')
                if parsed.fragment:
                    self.assertIn(unquote(parsed.fragment), documents[target].ids, f'{name}: broken fragment {reference}')

    def test_invalid_profile_fails_with_useful_location(self):
        self.team['members'][0]['group'] = 'misspelled-group'
        with self.assertRaisesRegex(build.ContentError, r'team.json.members\[0\].group'):
            self.validate()

    def test_missing_photo_and_duplicate_ids_are_rejected(self):
        self.team['members'][0]['photo'] = 'assets/images/missing.jpg'
        with self.assertRaisesRegex(build.ContentError, 'local file does not exist'):
            self.validate()
        del self.team['members'][0]['photo']
        self.team['members'][1]['id'] = self.team['members'][0]['id']
        with self.assertRaisesRegex(build.ContentError, 'duplicate member ID'):
            self.validate()

    def test_duplicate_doi_and_incomplete_author_list_are_rejected(self):
        self.pubs.append(deepcopy(self.pubs[0]))
        with self.assertRaisesRegex(build.ContentError, 'duplicate DOI'):
            self.validate()
        self.pubs.pop()
        self.pubs[0]['authors'] = []
        with self.assertRaisesRegex(build.ContentError, r'authors'):
            self.validate()

    def test_doi_deduplication_and_featured_references_ignore_case(self):
        paper = next(p for p in self.pubs if p.get('doi'))
        duplicate = deepcopy(paper)
        duplicate['doi'] = duplicate['doi'].swapcase()
        self.pubs.append(duplicate)
        with self.assertRaisesRegex(build.ContentError, 'duplicate DOI'):
            self.validate()
        self.pubs.pop()
        record = {'id': 'case-example', 'kind': 'publication', 'reference': paper['doi'].swapcase(),
                  'heading': paper['title'], 'description': 'Reference test'}
        build.validate_featured([record], self.pubs, self.projects)
        self.assertIn(build.e(paper['title']), build.featured_work([record], self.pubs, self.projects))
        self.assertEqual(build.publication_identity(paper), build.publication_identity(duplicate))

    def doi_less_fixture(self):
        return {'id': 'verified-conference-paper', 'title': 'Conference contribution & implementation',
                'authors': ['M. C. Martínez-Rodríguez', 'P. Brox'], 'journal': 'Research conference',
                'year': 2026, 'type': 'conference', 'url': 'https://example.org/papers/verified-contribution'}

    def test_doi_less_publications_require_unique_stable_id_and_safe_url(self):
        paper = self.doi_less_fixture()
        self.pubs.append(paper)
        self.validate()
        for name, value, error in [('id', '', r'\.id'), ('id', 'Not a slug', 'lowercase ID'),
                                   ('url', '', r'\.url'), ('url', 'javascript:alert(1)', 'HTTPS'),
                                   ('doi', None, r'\.doi'), ('doi', 'pending', 'use the DOI only')]:
            original = paper.get(name)
            paper[name] = value
            with self.subTest(field=name, value=value), self.assertRaisesRegex(build.ContentError, error):
                self.validate()
            if original is None:
                paper.pop(name)
            else:
                paper[name] = original
        paper['doi'] = ''
        self.validate()
        paper.pop('doi')
        self.pubs.append(deepcopy(paper))
        with self.assertRaisesRegex(build.ContentError, 'duplicate publication ID'):
            self.validate()

    def test_doi_less_publication_citation_bibtex_and_both_views_use_verified_url(self):
        paper = self.doi_less_fixture()
        self.pubs.append(paper)
        self.validate()
        self.assertEqual(build.publication_reference(paper), paper['id'])
        self.assertEqual(build.publication_identity(paper), 'id:' + paper['id'])
        self.assertTrue(build.citation(paper).endswith(paper['url']))
        output = build.bibtex(paper)
        self.assertIn('url = {' + paper['url'] + '}', output)
        self.assertNotIn('doi =', output)
        self.assertTrue(output.startswith('@inproceedings{'))
        second = deepcopy(paper)
        second['id'] = 'another-conference-paper'
        self.assertNotEqual(build.bibtex(paper).splitlines()[0], build.bibtex(second).splitlines()[0])
        for markup in (build.publication_card(paper), build.latest_publication(paper), build.publication_sections(self.pubs)):
            self.assertIn('href="' + paper['url'] + '"', markup)
            self.assertIn(build.e(build.citation(paper)), markup)
            self.assertIn(build.e(build.bibtex(paper)), markup)
        self.assertIn(paper['id'], build.publication_card(paper), 'The stable ID must be searchable.')

    def test_featured_publication_can_reference_doi_less_source_id(self):
        paper = self.doi_less_fixture()
        self.pubs.append(paper)
        record = {'id': 'conference-highlight', 'kind': 'publication', 'reference': paper['id'],
                  'heading': 'Contribution', 'description': 'A verified source contribution'}
        build.validate_featured([record], self.pubs, self.projects)
        output = build.featured_work([record], self.pubs, self.projects)
        self.assertIn('href="' + paper['url'] + '"', output)
        self.assertIn(build.e(paper['title']), output)
        self.pubs.pop()
        with self.assertRaisesRegex(build.ContentError, 'no matching publication'):
            build.validate_featured([record], self.pubs, self.projects)

    def test_official_group_name_and_compact_brand_are_separate(self):
        official = 'Trusted Systems-on-Chip based on CMOS and integrated photonics technologies'
        self.site.update(name=official, shortName='Lab & Research')
        self.validate()
        with patch.object(build, 'load_content', return_value=(self.site, self.team, self.pubs, self.projects)):
            pages = build.build_site()
        self.assertIn('<title>' + official + ' | Lab &amp; Research</title>', pages['index.html'])
        for page in pages.values():
            self.assertIn('aria-label="Lab &amp; Research home"', page)
            self.assertIn(official, page)
        self.site['shortName'] = ''
        with self.assertRaisesRegex(build.ContentError, r'site.json.shortName'):
            self.validate()
        self.site.pop('shortName')
        with patch.object(build, 'load_content', return_value=(self.site, self.team, self.pubs, self.projects)):
            page = build.build_site()['index.html']
        self.assertIn('aria-label="' + official + ' home"', page)

    def test_unsafe_links_and_invalid_crop_are_rejected(self):
        self.team['members'][0]['links'] = [{'label': 'Profile', 'url': 'javascript:alert(1)'}]
        with self.assertRaisesRegex(build.ContentError, 'HTTPS'):
            self.validate()
        self.team['members'][0]['links'] = []
        self.team['members'][0]['photoPosition'] = '50%; background: url(x)'
        with self.assertRaisesRegex(build.ContentError, 'two percentages'):
            self.validate()

    def test_optional_profile_fields_and_initials_need_no_html_edits(self):
        person = self.team['members'][0]
        person.pop('photo', None)
        person.update(bio='Hardware & photonics', affiliation='IMSE-CNM', tags=['RISC-V'], links=[], photoPosition='50% 20%')
        self.validate()
        result = build.team_sections(self.team)
        self.assertIn('class="initials"', result)
        self.assertIn('Hardware &amp; photonics', result)
        self.assertIn('Research interests', result)
        person['visible'] = False
        self.assertNotIn(f'id="{person["id"]}"', build.team_sections(self.team))

    def test_data_is_escaped_in_html(self):
        self.pubs[0]['title'] = '<script>alert("x")</script> & "quotes"'
        output = build.publication_card(self.pubs[0])
        self.assertNotIn('<script>', output)
        self.assertIn('&lt;script&gt;', output)
        self.assertIn('&quot;quotes&quot;', output)

    def test_conference_and_journal_citations_preserve_metadata(self):
        conference = deepcopy(self.pubs[0])
        conference.update(type='conference', volume='17', issue='3', pages='10-20', article='35')
        output = build.bibtex(conference)
        self.assertTrue(output.startswith('@inproceedings{'))
        self.assertIn('booktitle = {', output)
        self.assertIn('pages = {10--20}', output)
        self.assertIn('eid = {35}', output)
        self.assertIn('no. 3', build.citation(conference))
        self.assertIn('article 35', build.citation(conference))
        conference['type'] = 'journal'
        self.assertTrue(build.bibtex(conference).startswith('@article{'))
        self.assertIn('journal = {', build.bibtex(conference))

    def test_bibtex_special_characters_and_keys(self):
        self.assertEqual(build.tex('A & B_2 %'), r'A \& B\_2 \%')
        keys = [build.bibtex(p).splitlines()[0] for p in self.pubs]
        self.assertEqual(len(keys), len(set(keys)))

    def test_build_is_deterministic(self):
        self.assertEqual(build.build_site(), build.build_site())

    def test_dataset_photographer_credits_reach_captions_and_shared_notes(self):
        datasets = build.load_photo_credits(build.ROOT)
        for dataset in datasets:
            dataset.update(label='Label ' + dataset['id'], photographer='Photographer ' + dataset['id'], affiliation='Lab & Institute')
        with patch.object(build, 'load_photo_credits', return_value=datasets):
            pages = build.build_site()
        homepage = pages['index.html']
        for image in ('assets/images/lab/packaged-chip.webp', 'assets/images/grupo.jpeg'):
            self.assertIn(build.photo_credit(image, datasets), homepage)
        for feature in build.load_featured(self.pubs, self.projects):
            if feature.get('cover'):
                self.assertIn(build.photo_credit(feature['cover']['image'], datasets), homepage)
            if feature.get('figure'):
                self.assertIn(build.e(feature['figure']['credit']), homepage)
                self.assertEqual(build.photo_credit(feature['figure']['image'], datasets), '')
        self.assertIn('Label spirs: Photographer spirs (Lab &amp; Institute)', homepage)
        self.assertIn('Label photonics: Photographer photonics (Lab &amp; Institute)', homepage)
        self.assertEqual(pages['team.html'].count('Photography · Photographer team'), 1)

    def test_photo_credits_escape_metadata_deduplicate_and_hide_blank_names(self):
        datasets = build.load_photo_credits(build.ROOT)
        for dataset in datasets:
            dataset.update(photographer='<Name> & "Surname"', affiliation='Lab <A>', url='https://example.org/?a=1&b=2')
        markup = build.photo_credit('assets/images/lab/packaged-chip.webp', datasets)
        self.assertIn('&lt;Name&gt; &amp; &quot;Surname&quot;', markup)
        self.assertIn('(Lab &lt;A&gt;)', markup)
        self.assertIn('href="https://example.org/?a=1&amp;b=2"', markup)
        self.assertNotIn('<Name>', markup)
        combined = build.collection_photo_credits([
            'assets/images/lab/spirs-evaluation.webp', 'assets/images/lab/fibre-alignment.webp',
            'assets/images/lab/spirs-measurement.webp',
        ], datasets)
        self.assertEqual(combined.count('&lt;Name&gt;'), 1)
        for dataset in datasets:
            dataset['photographer'] = ' '
        with patch.object(build, 'load_photo_credits', return_value=datasets):
            pages = build.build_site()
        for page in pages.values():
            self.assertNotIn('class="photo-credit"', page)
            self.assertNotIn('class="photo-credits"', page)

    def test_featured_references_fail_when_source_is_removed(self):
        records = build.load_featured(self.pubs, self.projects)
        publication = next(r for r in records if r['kind'] == 'publication')
        publications = [p for p in self.pubs if build.publication_reference(p).casefold() != publication['reference'].casefold()]
        with self.assertRaisesRegex(build.ContentError, r'featured.json\[\d+\].reference'):
            build.validate_featured(records, publications, self.projects)
        records = [{'id': 'test', 'kind': 'project', 'reference': 'missing', 'heading': 'Test', 'description': 'Test'}]
        with self.assertRaisesRegex(build.ContentError, 'no matching project'):
            build.validate_featured(records, self.pubs, self.projects)

    def test_featured_content_is_escaped_and_repeated_diagrams_have_unique_ids(self):
        records = build.load_featured(self.pubs, self.projects)
        records[0].pop('figure', None)
        records[0].pop('cover', None)
        records[0]['diagram'] = 'mlkem'
        record = deepcopy(records[0])
        record.update(id='second-example', heading='<script>Bad</script>', description='A & B', topics=['<b>topic</b>'])
        records.append(record)
        build.validate_featured(records, self.pubs, self.projects)
        output = build.featured_work(records, self.pubs, self.projects)
        document = Document(output)
        self.assertEqual(len(document.ids), len(set(document.ids)))
        self.assertNotIn('<script>', output)
        self.assertIn('&lt;script&gt;', output)
        self.assertIn('A &amp; B', output)

    def test_research_figure_requires_existing_asset_and_attribution(self):
        records = build.load_featured(self.pubs, self.projects)
        figure = next(r['figure'] for r in records if 'figure' in r)
        original = figure['image']
        figure['image'] = 'assets/images/missing-figure.png'
        with self.assertRaisesRegex(build.ContentError, 'local file does not exist'):
            build.validate_featured(records, self.pubs, self.projects)
        figure['image'] = original
        figure.pop('credit')
        with self.assertRaisesRegex(build.ContentError, r'figure.credit'):
            build.validate_featured(records, self.pubs, self.projects)

    def test_research_figure_rejects_unsafe_urls_and_incomplete_dimensions(self):
        records = build.load_featured(self.pubs, self.projects)
        figure = next(r['figure'] for r in records if 'figure' in r)
        original = figure['license']
        figure['license'] = 'javascript:alert(1)'
        with self.assertRaisesRegex(build.ContentError, 'HTTPS'):
            build.validate_featured(records, self.pubs, self.projects)
        figure['license'] = original
        figure.pop('height')
        with self.assertRaisesRegex(build.ContentError, 'set both width and height'):
            build.validate_featured(records, self.pubs, self.projects)

    def test_research_figure_outputs_escaped_captions_and_license_link(self):
        records = build.load_featured(self.pubs, self.projects)
        figure = next(r['figure'] for r in records if 'figure' in r)
        figure.update(caption='<b>Figure</b> & description', credit='A & B')
        output = build.featured_work(records, self.pubs, self.projects)
        self.assertIn('&lt;b&gt;Figure&lt;/b&gt; &amp; description', output)
        self.assertIn('A &amp; B', output)
        self.assertNotIn('<b>Figure</b>', output)
        self.assertIn(f'href="{figure["license"]}"', output)
        self.assertIn('Full-size figure', output)

    def test_project_period_tracks_dates_and_accepts_explicit_override(self):
        project = deepcopy(self.projects['projects'][0])
        project['endDate'] = '2029-10-31'
        self.assertEqual(build.project_period(project), '1 Nov 2025 – 31 Oct 2029')
        project['endDate'] = '2025-12-31'
        self.assertEqual(build.project_period(project), '1 Nov 2025 – 31 Dec 2025')
        project['period'] = '2025–2029 · extended'
        self.assertEqual(build.project_period(project), '2025–2029 · extended')

    def featured_cover_fixture(self):
        return [{
            'id': 'example', 'kind': 'publication', 'reference': self.pubs[0]['doi'],
            'heading': 'Short label', 'description': 'Research description',
            'cover': {'image': self.team['members'][0]['photo'], 'alt': 'Illustrative image', 'caption': 'Illustrative cover'},
        }]

    def test_featured_cover_requires_description_safe_asset_and_complete_dimensions(self):
        records = self.featured_cover_fixture()
        cover = records[0]['cover']
        build.validate_featured(records, self.pubs, self.projects)
        original = cover['image']
        for image, error in [('javascript:alert(1)', 'HTTPS'), ('assets/images/missing-cover.png', 'local file does not exist')]:
            cover['image'] = image
            with self.assertRaisesRegex(build.ContentError, error):
                build.validate_featured(records, self.pubs, self.projects)
        cover['image'] = original
        cover['width'] = 800
        with self.assertRaisesRegex(build.ContentError, 'set both width and height'):
            build.validate_featured(records, self.pubs, self.projects)
        cover['height'] = True
        with self.assertRaisesRegex(build.ContentError, r'cover.height'):
            build.validate_featured(records, self.pubs, self.projects)
        cover['height'] = 600
        build.validate_featured(records, self.pubs, self.projects)
        cover.pop('caption')
        with self.assertRaisesRegex(build.ContentError, r'cover.caption'):
            build.validate_featured(records, self.pubs, self.projects)

    def test_cover_keeps_paper_metadata_and_attributed_research_figure_in_static_html(self):
        records = self.featured_cover_fixture()
        figure = next(record['figure'] for record in build.load_featured(self.pubs, self.projects) if 'figure' in record)
        records[0]['figure'] = figure
        records[0]['cover'].update(alt='<script>Image</script>', caption='An illustration & "caption"')
        output = build.featured_work(records, self.pubs, self.projects)
        document = Document(output)
        self.assertEqual(len(document.featured), 1)
        self.assertNotIn('hidden', document.featured[0], 'No-JS readers must receive the complete article.')
        self.assertIn(build.e(self.pubs[0]['title']), output)
        self.assertIn(build.e(', '.join(self.pubs[0]['authors'])), output)
        self.assertIn(build.e(self.pubs[0]['journal']), output)
        self.assertIn(str(self.pubs[0]['year']), output)
        self.assertIn('feature-figure-details', output)
        self.assertIn('Research figure', output)
        self.assertIn(build.e(figure['credit']), output)
        self.assertIn(f'href="{figure["license"]}"', output)
        self.assertIn('Full-size figure', output)
        self.assertIn('&lt;script&gt;Image&lt;/script&gt;', output)
        self.assertNotIn('<script>', output)
        self.assertIn('An illustration &amp; &quot;caption&quot;', output)

    def test_home_projects_limit_uses_ongoing_source_order_and_retains_future_candidates(self):
        ongoing = [project for project in self.projects['projects'] if build.project_status(project) == 'ongoing']
        candidates = ongoing or [p for status in ('upcoming', 'completed') for p in self.projects['projects'] if build.project_status(p) == status]
        expected = [project['id'] for project in candidates[:3]]
        output = build.current_projects(self.projects)
        cards = Document(output).projects
        self.assertEqual(len(cards), len(self.projects['projects']))
        self.assertEqual([card['data-project'] for card in cards if 'hidden' not in card], expected)
        for project, card in zip(self.projects['projects'], cards):
            self.assertIn(build.e(project.get('programme', project['funder'])), output)
            self.assertIn(build.e(build.project_period(project)), output)
            self.assertIn(build.e(project['abstract']), output)
            self.assertEqual(card['data-start-date'], project['startDate'])
            self.assertEqual(card['data-end-date'], project['endDate'])
            self.assertEqual(card['data-status'], build.project_status(project))

    def test_project_groups_dates_and_badges_reach_the_archive(self):
        output = build.project_sections(self.projects)
        for project, card in zip(self.projects['projects'], Document(output).projects):
            self.assertEqual(card['data-project'], project['id'])
            self.assertEqual(card['data-group'], project['group'])
            self.assertEqual(card['data-status'], build.project_status(project))
            self.assertIn(build.e(build.project_duration(project)), output)
        self.projects['projects'][0]['endDate'] = '2025-01-01'
        with self.assertRaisesRegex(build.ContentError, r'projects.json.projects\[0\].endDate'):
            self.validate()

    def test_author_alias_validation_and_display_only_highlights(self):
        paper = next(p for p in self.pubs if 'P. Brox' in p['authors'])
        for markup in (build.publication_card(paper, team=self.team), build.latest_publication(paper, self.team),
                       build.featured_work(build.load_featured(self.pubs, self.projects), self.pubs, self.projects, self.team)):
            self.assertIn('class="team-author"', markup)
        output = build.publication_card(paper, team=self.team)
        self.assertIn(build.e(build.citation(paper)), output)
        self.assertIn(build.e(build.bibtex(paper)), output)
        self.team['members'][0]['authorNames'] = ['']
        with self.assertRaisesRegex(build.ContentError, r'authorNames'):
            self.validate()

    def test_publications_require_two_distinct_current_team_authors(self):
        for authors in [['P. Brox', 'Piedad Brox'], ['D. Martín-Sánchez', 'Another Researcher']]:
            with self.subTest(authors=authors):
                self.pubs[0]['authors'] = authors
                with self.assertRaisesRegex(build.ContentError, r'publications.json\[0\].authors: at least two distinct'):
                    self.validate()
        self.pubs[0]['authors'] = ['P. Brox', 'S. Sánchez-Solano']
        self.validate()
        # A listed external collaborator counts; hiding the profile removes it
        # from both eligibility and highlighted profile links.
        next(m for m in self.team['members'] if m['id'] == 'santiago-sanchez-solano')['visible'] = False
        with self.assertRaisesRegex(build.ContentError, 'matched 1'):
            self.validate()

    def test_documented_eligibility_exception_preserves_authorship(self):
        paper = self.doi_less_fixture()
        paper['authors'] = ['P. Navarro-Torrero', 'Another Researcher']
        self.pubs.append(paper)
        with self.assertRaisesRegex(build.ContentError, 'matched 1'):
            self.validate()
        paper['eligibilityException'] = 'Restored by explicit user request.'
        self.validate()
        self.assertEqual(build.team_member_ids(paper['authors'], self.team), {'pablo-navarro-torrero'})
        self.assertIn('P. Navarro-Torrero, Another Researcher', build.citation(paper))
        self.assertIn('P. Navarro-Torrero and Another Researcher', build.bibtex(paper))
        self.assertNotIn(paper['eligibilityException'], build.publication_card(paper, team=self.team))
        # An exception on one record must not bypass the policy for another.
        self.pubs[0]['authors'] = ['P. Brox']
        with self.assertRaisesRegex(build.ContentError, r'publications.json\[0\].authors'):
            self.validate()

    def test_eligibility_exception_requires_a_nonempty_explanation(self):
        for reason in ('', '   ', None, False, []):
            with self.subTest(reason=reason):
                self.pubs[0]['eligibilityException'] = reason
                with self.assertRaisesRegex(build.ContentError, r'\.eligibilityException: expected a non-empty string'):
                    self.validate()

    def test_profile_icons_preserve_urls_and_accessible_labels(self):
        for label, href in [('GitHub', 'https://github.com/a'), ('GitLab', 'https://gitlab.com/a'),
                            ('LinkedIn', 'https://www.linkedin.com/in/a'), ('ORCID', 'https://orcid.org/0000'),
                            ('Google Scholar', 'https://scholar.google.es/citations?user=a')]:
            description = label + ' — A & B'
            markup = build.profile_link(label, href, description)
            self.assertIn('class="icon-link"', markup)
            self.assertIn('aria-label="' + build.e(description) + '"', markup)
            self.assertIn('aria-hidden="true"', markup)
            self.assertEqual(Document(markup).references, [href])
        unknown = build.profile_link('Personal website', 'https://example.org/a')
        self.assertIn('Personal website', unknown)
        self.assertNotIn('class="icon-link"', unknown)

    def test_home_publication_has_complete_native_citations_and_escaped_metadata(self):
        paper = deepcopy(self.pubs[0])
        paper.update(title='<b>Paper</b> & title', volume='14', pages='12–18')
        output = build.latest_publication(paper)
        self.assertEqual(len(Document(output).details), 2)
        self.assertIn(build.e(', '.join(paper['authors'])), output)
        self.assertIn('Vol. 14', output)
        self.assertIn('pp. 12–18', output)
        self.assertIn(build.e(build.citation(paper)), output)
        self.assertIn(build.e(build.bibtex(paper)), output)
        self.assertIn('&lt;b&gt;Paper&lt;/b&gt;', output)
        self.assertNotIn('<b>Paper</b>', output)


if __name__ == '__main__':
    unittest.main()
