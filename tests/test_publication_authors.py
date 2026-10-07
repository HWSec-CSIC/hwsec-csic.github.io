"""Check identity matching and preservation of bibliographic author strings."""

from copy import deepcopy
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from publication_authors import authored_names, name_tokens, team_member_ids


class AuthorHTML(HTMLParser):
    def __init__(self, output):
        super().__init__(convert_charrefs=True)
        self.targets = []
        self.words = []
        self.feed(output)

    def handle_starttag(self, tag, attributes):
        if tag == "a":
            self.targets.append(dict(attributes)["href"])

    def handle_data(self, data):
        self.words.append(data)


class PublicationAuthorTests(unittest.TestCase):
    def setUp(self):
        self.team = json.loads((ROOT / "assets/docs/team.json").read_text())

    def assert_matches(self, author, member_id):
        output = AuthorHTML(authored_names([author], self.team))
        self.assertEqual(output.targets, ["team.html#" + member_id], author)
        self.assertEqual("".join(output.words), author)

    def test_dataset_abbreviations_and_accent_variants(self):
        expected = {
            "P. Brox": "piedad-brox-jimenez",
            "Piedad Brox": "piedad-brox-jimenez",
            "Piedad Brox-Jiménez": "piedad-brox-jimenez",
            "M.C. Martínez-Rodríguez": "macarena-c-martinez-rodriguez",
            "M. C. MartÍnez-RodrÍguez": "macarena-c-martinez-rodriguez",
            "Macarena C. Martínez-Rodríguez": "macarena-c-martinez-rodriguez",
            "Macarena Cristina Martinez Rodriguez": "macarena-c-martinez-rodriguez",
            "D. Martín-Sánchez": "david-martin-sanchez",
            "P. Ortega-Castro": "pau-ortega-castro",
            "P. Navarro-Torrero": "pablo-navarro-torrero",
            "F. J. Rubio-Barbero": "francisco-javier-rubio-barbero",
            "Francisco J. Rubio-Barbero": "francisco-javier-rubio-barbero",
            "Juan Manuel Moreno-Cenizo": "juan-manuel-moreno-cenizo",
            "S. Sánchez-Solano": "santiago-sanchez-solano",
        }
        for author, member_id in expected.items():
            with self.subTest(author=author):
                self.assert_matches(author, member_id)

    def test_placeholder_members_and_particles(self):
        self.assert_matches("I. Fernández-Poyato", "isabel-fernandez-poyato")
        self.assert_matches("C. Gomez de la Rosa", "cristina-gomez-de-la-rosa")
        self.assert_matches("Cristina Gómez-de-la-Rosa", "cristina-gomez-de-la-rosa")

    def test_collaborators_and_similar_names_are_not_guessed(self):
        for author in ("J. M. Mora-Gutiérrez", "E. Camacho-Ruiz", "L. F. Rojas-Muñoz",
                       "P. Beard", "Paula Ortega-Castro", "Macarena Carolina Martínez-Rodríguez",
                       "P. B.", "Piedad", "Brox"):
            with self.subTest(author=author):
                output = AuthorHTML(authored_names([author], self.team))
                self.assertEqual(output.targets, [])
                self.assertEqual("".join(output.words), author)

    def test_ambiguous_initials_and_explicit_aliases_are_not_linked(self):
        self.team["members"].append({"id": "paula-ortega-castro", "name": "Paula Ortega Castro"})
        self.assertEqual(AuthorHTML(authored_names(["P. Ortega-Castro"], self.team)).targets, [])
        self.assert_matches("Pau Ortega Castro", "pau-ortega-castro")
        self.team["members"].append({"id": "other-brox", "name": "Another Person",
                                    "authorNames": ["Piedad Brox"]})
        self.assertEqual(AuthorHTML(authored_names(["Piedad Brox"], self.team)).targets, [])

    def test_invisible_members_are_not_linked(self):
        next(member for member in self.team["members"]
             if member["id"] == "pau-ortega-castro")["visible"] = False
        self.assertEqual(AuthorHTML(authored_names(["P. Ortega-Castro"], self.team)).targets, [])

    def test_distinct_member_ids_do_not_count_repeated_author_variants(self):
        authors = ["P. Brox", "Piedad Brox", "Piedad Brox-Jiménez", "P. Brox",
                   "M.C. Martínez-Rodríguez", "Macarena Cristina Martínez-Rodríguez",
                   "E. Camacho-Ruiz"]
        self.assertEqual(team_member_ids(authors, self.team),
                         {"piedad-brox-jimenez", "macarena-c-martinez-rodriguez"})
        self.assertEqual(len(team_member_ids(authors[:4], self.team)), 1)
        self.assertEqual(team_member_ids([], self.team), set())

    def test_ambiguous_or_invisible_author_does_not_inflate_member_count(self):
        authors = ["P. Ortega-Castro", "P. Brox", "S. Sánchez-Solano"]
        self.team["members"].append({"id": "paula-ortega-castro", "name": "Paula Ortega Castro"})
        next(member for member in self.team["members"]
             if member["id"] == "santiago-sanchez-solano")["visible"] = False
        self.assertEqual(team_member_ids(authors, self.team), {"piedad-brox-jimenez"})
        self.assertEqual(team_member_ids(["Pau Ortega Castro"], self.team), {"pau-ortega-castro"})

    def test_member_count_and_display_use_identical_identity_resolution(self):
        authors = ["D. Martín-Sánchez", "F. J. Rubio-Barbero", "Juan Manuel Moreno-Cenizo",
                   "P. Navarro-Torrero", "A. <script>alert(1)</script>", "J. M. Mora-Gutiérrez"]
        before = deepcopy((authors, self.team))
        output = AuthorHTML(authored_names(authors, self.team))
        self.assertEqual(team_member_ids(authors, self.team),
                         {target.split("#", 1)[1] for target in output.targets})
        self.assertEqual(team_member_ids(authors, self.team),
                         {"david-martin-sanchez", "francisco-javier-rubio-barbero",
                          "juan-manuel-moreno-cenizo", "pablo-navarro-torrero"})
        self.assertEqual((authors, self.team), before)

    def test_safe_html_and_original_names_order_are_preserved(self):
        authors = ['P. Brox', 'A. <script>alert("x")</script>', 'M.C. Martínez-Rodríguez', "A. & B."]
        before = deepcopy((authors, self.team))
        output = authored_names(authors, self.team)
        self.assertNotIn("<script>", output)
        self.assertIn("&lt;script&gt;", output)
        document = AuthorHTML(output)
        self.assertEqual("".join(document.words), ", ".join(authors))
        self.assertEqual(document.targets, ["team.html#piedad-brox-jimenez",
                                             "team.html#macarena-c-martinez-rodriguez"])
        self.assertEqual((authors, self.team), before)

    def test_citation_and_bibtex_keep_original_author_strings(self):
        import build
        paper = {"title": "Author identity test", "authors": ["P. Brox", "M.C. Martínez-Rodríguez"],
                 "journal": "Example Journal", "year": 2026, "doi": "10.1234/example"}
        citation_before, bibtex_before = build.citation(paper), build.bibtex(paper)
        authored_names(paper["authors"], self.team)
        self.assertEqual(build.citation(paper), citation_before)
        self.assertEqual(build.bibtex(paper), bibtex_before)
        self.assertNotIn("<a", citation_before + bibtex_before)
        self.assertIn(", ".join(paper["authors"]), citation_before)
        self.assertIn(" and ".join(paper["authors"]), bibtex_before)

    def test_every_publication_author_is_preserved(self):
        publications = json.loads((ROOT / "assets/docs/publications.json").read_text())
        for paper in publications:
            with self.subTest(paper=paper["title"]):
                document = AuthorHTML(authored_names(paper["authors"], self.team))
                self.assertEqual("".join(document.words), ", ".join(paper["authors"]))

    def test_normalization_preserves_name_boundaries(self):
        self.assertEqual(name_tokens(" Dr. M.C. Martínez-Rodríguez "), ("m", "c", "martinez", "rodriguez"))
        self.assertNotEqual(name_tokens("J. M. Mora-Gutiérrez"), name_tokens("Juan Manuel Moreno Cenizo"))


if __name__ == "__main__":
    unittest.main()
