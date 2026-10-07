# Publication profile audit — 6 October 2026

Updated and imported on **7 October 2026** following the user's review.

Reviewed the ORCID and Google Scholar links in `assets/docs/team.json` against the 21-record catalogue present at the start of this audit. Discovery covers 2023 onward. By default, each included work must have at least **two distinct authors from the current 16 visible team members**, including External Collaborators. Eros Camacho-Ruiz and other former/unlisted researchers do not count toward that threshold. Repeated names and aliases count as one person. The user's explicit restoration of ML-KEM is the sole documented exception.

**Result:** all **nine confirmed missing full papers** were imported: eight conference papers and one journal article, whose publisher record and complete original article resolved the initial uncertainty. One published short proceedings communication and four poster/extended-abstract contributions remain excluded because no individual DOI was verified for them. The user's DOI restriction applies to these short outputs; verified full papers can use a stable ID and an official source URL when no individual DOI is available.

The user's eligibility rule initially removed four existing one-member entries, leaving 17. ML-KEM was restored by explicit request on 7 October, and the nine full-paper imports bring the live generated archive to **27 publications**. The landing page now contains **six featured items**, following the subsequent request to feature the existing SECRYPT 2026 masked KECCAK paper (`10.5220/0015074600004103`); no duplicate publication was added. The other 26 publications meet the two-member rule. Generation rejects records below that minimum unless a non-empty `eligibilityException` documents an explicit user-approved exception; published name variants can be supplied through `team.json.authorNames`.

The [structured audit](PUBLICATION_PROFILE_AUDIT_2026-10-06.json) preserves full author order, team matches, identifiers, source URLs, profile coverage and exclusions. Its 45-record lead-profile inventory compares with the original 21-record baseline; `currentCatalogueEligibility` reflects the current 27-record catalogue and its one explicit exception.

## Full papers imported on 7 October 2026

| Year | Publication | Listed team authors | Evidence |
| --- | --- | --- | --- |
| 2025 | Open Source API for a Hardware Root-of-Trust | Apurba Karmakar, Pablo Navarro-Torrero, Piedad Brox Jiménez, Macarena C. Martínez-Rodríguez (4) | [Primary source](https://publicaciones.unileon.es/product/xviii-reunion-espanola-sobre-criptologia-y-seguridad-de-la-informacion-xviii-recsi/) |
| 2025 | Optimizing Secure Elements Implementation Methods for a seamless Post-Quantum Transition | Pablo Navarro-Torrero, Macarena C. Martínez-Rodríguez, Piedad Brox Jiménez (3) | [DOI](https://doi.org/10.1109/iscc65549.2025.11326228) |
| 2024 | Cryptographic Security Through a Hardware Root of Trust | Santiago Sánchez Solano, Macarena C. Martínez-Rodríguez, Pablo Navarro-Torrero, Apurba Karmakar, Pau Ortega Castro, Piedad Brox Jiménez (6) | [DOI](https://doi.org/10.1007/978-3-031-55673-9_8) |
| 2024 | Digital Design Flow Based on Open Tools for Programmable Logic Devices | Pablo Navarro-Torrero, Macarena C. Martínez-Rodríguez, Piedad Brox Jiménez (3) | [DOI](https://doi.org/10.1109/taee59541.2024.10604893) |
| 2024 | Full Open-Source Implementation of an Academic RISC-V on FPGA | Pablo Navarro-Torrero, Macarena C. Martínez-Rodríguez, Piedad Brox Jiménez (3) | [DOI](https://doi.org/10.1109/taee59541.2024.10604934) |
| 2023 | A Simple Power Analysis of an FPGA implementation of a polynomial multiplier for the NTRU cryptosystem | Santiago Sánchez Solano, Macarena C. Martínez-Rodríguez, Piedad Brox Jiménez (3) | [DOI](https://doi.org/10.1109/dcis58620.2023.10336001) |
| 2023 | A complete SHA-3 hardware library based on a high efficiency Keccak design | Santiago Sánchez Solano, Macarena C. Martínez-Rodríguez, Piedad Brox Jiménez (3) | [DOI](https://doi.org/10.1109/norcas58970.2023.10305448) |
| 2023 | HW/SW implementation of RSA digital signature on a RISC-V-based System-on-Chip | Apurba Karmakar, Santiago Sánchez Solano, Macarena C. Martínez-Rodríguez, Piedad Brox Jiménez (4) | [DOI](https://doi.org/10.1109/DCIS58620.2023.10335970) |
| 2023 | Contribuciones a la implementación de sistemas electrónicos digitales embebidos sobre hardware reconfigurable | Santiago Sánchez Solano, Piedad Brox Jiménez (2) | [Publisher article](https://revistaccuba.sld.cu/index.php/revacc/article/view/1482) |

ARC 2024 is a conference paper in LNCS even though Crossref describes the record as a book chapter; it is one publication. ISCC uses 2025 in publisher-deposited Crossref metadata; the project's CORDIS listing currently says 2026. RECSI was held in 2024, while the university publisher issued its proceedings in 2025. Its single catalogue record uses the 2025 publication year and retains 2024 in the venue. The primary proceedings PDF confirms pages **87–92**. No individual DOI was verified, so the paper uses a stable ID and its [CSIC repository URL](https://hdl.handle.net/10261/384049); the whole-book DOI is not assigned to this individual paper.

## Published short communication

| Year | Publication | Listed team authors | Evidence |
| --- | --- | --- | --- |
| 2023 | Análisis y evaluación de un RO-PUF como TRNG | Santiago Sánchez Solano, Macarena C. Martínez-Rodríguez, Piedad Brox Jiménez (3) | [Primary source](https://www.spirs-project.eu/dissemination/publications/) |

The JNIC contribution is a distinct two-page proceedings communication. No individual DOI was verified, so it was not imported under the user's rule for short outputs.

## Additional poster and extended-abstract contributions

| Year | Publication | Listed team authors | Evidence |
| --- | --- | --- | --- |
| 2025 | Security assessment methodology for RISC-V cores | Apurba Karmakar, Pablo Navarro-Torrero, Macarena C. Martínez-Rodríguez, Piedad Brox Jiménez (4) | [Primary source](https://riscv-europe.org/summit/2025/media/proceedings/2025-05-14-RISC-V-Summit-Europe-P2.2.06-KARMARKAR-abstract.pdf) |
| 2023 | Exploring Open-Source and Proprietary Design Tools to Implement a Symmetric Cipher on FPGAs | Pablo Navarro-Torrero, Piedad Brox Jiménez, Santiago Sánchez Solano (3) | [Primary source](https://easychair.org/smart-program/DCIS2023/2023-11-17.html) |
| 2023 | Root of Trust Components to Increase Security of RISC-V Based Systems on Chips | Macarena C. Martínez-Rodríguez, Santiago Sánchez Solano, Piedad Brox Jiménez (3) | [Primary source](https://riscv-europe.org/summit/2023/media/proceedings/posters/2023-06-06-Luis-Felipe-ROJAS-MU%C3%91OZ-abstract.pdf) |
| 2023 | Secure platform for ICT systems rooted at the silicon manufacturing process | Macarena C. Martínez-Rodríguez, Piedad Brox Jiménez (2) | [Primary source](https://riscv-europe.org/summit/2023/media/proceedings/posters/2023-06-06-Caaliph-ANDRIAMISAINA-abstract.pdf) |

RISC-V Summit items have official abstracts/posters. The DCIS design-tools contribution is verified in the official poster session; full proceedings-paper status is unverified, and Scholar/program author order differs. Its final bibliographic author order remains pending until the publication can be inspected. None of these four outputs has a verified individual DOI, so none was imported.

## Cuban journal record verified and imported

The [publisher article record](https://revistaccuba.sld.cu/index.php/revacc/article/view/1482) and its [complete 13-page original article](https://revistaccuba.sld.cu/index.php/revacc/article/download/1482/1862) confirm all nine authors, online publication on **31 October 2023**, Anales de la Academia de Ciencias de Cuba **13(4)**, article **e1482**. This resolves the initially unavailable direct reference and distinguishes the work from a poster or abstract. It meets the two-author criterion through Santiago Sánchez Solano and Piedad Brox Jiménez. No individual DOI was verified; it was imported as a full journal article using a stable ID and the publisher's article URL.

## ML-KEM restored by explicit user request

“A Framework for designing High-Order Side-Channel Protected Hardware Implementations of ML-KEM”, [DOI](https://doi.org/10.46586/tches.v2026.i2.272-295), was restored on 7 October 2026 with its original three authors: **E. Camacho-Ruiz, P. Navarro-Torrero, A. Cabrera Aldaya**. Pablo Navarro-Torrero remains its only author in the current roster. The non-empty `eligibilityException` records the user's explicit restoration; it does not add authors or change current-team matches, highlighting, citations or BibTeX. The CHES presentation refers to this same journal paper and remains deduplicated.

The HOPE-MLKEM featured entry and its original credited Figure 6 were also restored, with the source article and CC BY 4.0 license displayed alongside the figure.

## Existing entries still excluded by the minimum-two-author rule

| Publication | DOI | Only listed author |
| --- | --- | --- |
| Sensitive Broadband Ultrasound Sensor Based on a Low-Loss High-Q Fused-Silica Plano-Concave Microresonator | [DOI](https://doi.org/10.1364/OE.572433) | David Martín Sánchez |
| Laser Frequency Noise Characterisation Using High-Finesse Plano-Concave Optical Microresonators | [DOI](https://doi.org/10.1364/OL.510516) | David Martín Sánchez |
| An ABCD Transfer Matrix Model of Gaussian Beam Propagation in Plano-Concave Optical Microresonators | [DOI](https://doi.org/10.1364/OE.484212) | David Martín Sánchez |

These three optical papers remain excluded; the user requested restoration only of ML-KEM. The separately requested removal of the 2020 porous-silicon-membrane paper also remains in effect.

## Profile coverage and limitations

The original audit read all **12 linked ORCID records** and **nine linked Scholar pages**. The linked Scholar page for Ignacio appears to belong to an economics researcher and is not accepted as verified coverage of the IMSE team member. No complete, independently verified scholarly profile was found for Samuel Gutiérrez Félix, Isabel Fernández Poyato or Cristina Gómez de la Rosa during that audit. Samuel's user-supplied ORCID was restored on **7 October 2026**, after the original audit; its works have not been reviewed. An empty ORCID inventory does not establish that an author has no papers; Juan Manuel’s existing 2026 paper illustrates that limitation.

| Team member | Profile coverage |
| --- | --- |
| Piedad Brox Jiménez | [ORCID](https://orcid.org/0000-0003-1059-5338); [Google Scholar](https://scholar.google.com/citations?user=Q38fPzUAAAAJ&hl=es) |
| Macarena C. Martínez-Rodríguez | [ORCID](https://orcid.org/0000-0003-3025-5736); [Google Scholar](https://scholar.google.com/citations?user=TJRg5D4AAAAJ&hl=es) |
| David Martín Sánchez | [ORCID](https://orcid.org/0000-0003-0131-5226); [Google Scholar](https://scholar.google.com/citations?user=JBEyXwUAAAAJ&hl=es) |
| Apurba Karmakar | [ORCID](https://orcid.org/0009-0000-4743-8622); [Google Scholar](https://scholar.google.com/citations?user=ySaOudkAAAAJ&hl=es&oi=ao) |
| Pablo Navarro-Torrero | [ORCID](https://orcid.org/0009-0006-9360-4322); [Google Scholar](https://scholar.google.com/citations?user=yByHHBwAAAAJ&hl=es) |
| Francisco Javier Rubio-Barbero | [ORCID](https://orcid.org/0000-0002-0971-5825); [Google Scholar](https://scholar.google.com/citations?user=wS0BzLgAAAAJ&hl=es) |
| Jorge Ciudad Real Lacuesta | [ORCID](https://orcid.org/0009-0001-5179-650X); [Google Scholar](https://scholar.google.com/citations?user=-jub32EAAAAJ) |
| Juan Manuel Moreno Cenizo | [ORCID](https://orcid.org/0009-0002-3789-475X) — zero public ORCID works |
| Samuel Gutiérrez Félix | [ORCID](https://orcid.org/0009-0009-2851-6096) — user-supplied link restored on 7 October 2026 after the original audit; works not reviewed |
| Pau Ortega Castro | [ORCID](https://orcid.org/0009-0001-1363-6185) |
| Ignacio Martínez Fernández | [Google Scholar](https://scholar.google.com/citations?user=Bgtv9gIAAAAJ) — apparent economics namesake; link needs verification |
| Samuel Cimarro Almela | [ORCID](https://orcid.org/0009-0003-9985-8989) — zero public ORCID works |
| Manuel Roales Sánchez | [ORCID](https://orcid.org/0009-0002-6900-482X) — zero public ORCID works |
| Isabel Fernández Poyato | No verified linked scholarly profile |
| Cristina Gómez de la Rosa | No verified linked scholarly profile |
| Santiago Sánchez Solano | [ORCID](https://orcid.org/0000-0002-0700-0447); [Google Scholar](https://scholar.google.com/citations?user=lirVGPcAAAAJ&hl=en) |

Self-maintained profiles may omit work or contain duplicate dates, preprints and patents. Discovery was checked by normalized DOI/title; complete publisher/conference author lists were used to count distinct roster identities. Several Jorge ORCID records repeat his name; those repetitions do not establish multiple team authors. Solo-roster papers from Francisco’s previous research group were excluded. Patents, datasets, duplicates of existing works, preprints, and unresolved undated entries are recorded separately in the structured audit.

Some institutional PDF downloads returned access challenges; indexed primary proceedings and publisher records supplied the bibliographic evidence where available. Three undated lead-profile entries remain unresolved. The audit does not establish that no other eligible paper exists.

The user confirmed **Apurba Karmakar** as the correct spelling on 7 October 2026. Imported author metadata uses **Karmakar**. Some RECSI/Summit sources contain a typographical variant; original source URLs retain their literal spelling, and no incorrect surname alias is added to the roster.
