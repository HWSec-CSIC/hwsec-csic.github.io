# HWSec-CSIC

Web estática del grupo **Trusted Systems-on-Chip based on CMOS and integrated photonics technologies**, del IMSE-CNM, identificado también como **HWSec-CSIC**. HTML, CSS y JavaScript, con un generador pequeño en **Python 3.10 o posterior, sin dependencias**. Los HTML generados se incluyen en el repositorio y se sirven directamente en GitHub Pages.

## Ver y editar la web

Desde la raíz del proyecto:

```bash
python3 scripts/serve.py
```

Abre **http://localhost:8080**. El servidor regenera los HTML cuando cambias los JSON, las plantillas o las fotos. Refresca el navegador para ver el resultado. Para usar otro puerto: `python3 scripts/serve.py --port 8081`.

Antes de subir cambios:

```bash
python3 scripts/build.py
python3 scripts/build.py --check
python3 -m unittest discover -s tests
```

Incluye en el commit los datos o plantillas editados **y los HTML regenerados**. La comprobación de GitHub Actions detecta datos inválidos y páginas pendientes de regenerar. El workflow comprueba el contenido; la publicación sigue usando la configuración de GitHub Pages del repositorio.

## Dónde cambiar cada cosa

| Contenido | Archivo que se edita |
| --- | --- |
| Personas, cargos, fotos y enlaces | `assets/docs/team.json` |
| Artículos y contribuciones a congresos | `assets/docs/publications.json` |
| Proyectos, categorías, fechas, participantes y financiación | `assets/docs/projects.json` |
| Trabajos destacados y su orden en la portada | `assets/docs/featured.json` |
| Nombre oficial, nombre corto, institución, dirección, teléfono y enlaces generales | `assets/docs/site.json` |
| Textos y estructura de las páginas | `templates/*.html` |
| Cabecera, navegación y pie compartidos | `templates/base.html` |
| Paleta, tipografías, tamaños y adaptación móvil | `css/style.css` |
| Foto del grupo en la portada | `assets/images/grupo.jpeg` |
| Fotos del laboratorio preparadas para la web | `assets/images/lab/*.webp` |
| Autores de las fotografías y enlaces a sus perfiles | `assets/docs/photo-credits.json` |
| Procedencia de las fotos y preparación reproducible | `assets/images/lab/SOURCES.md`, `scripts/prepare_photos.py` |
| Auditoría de publicaciones frente al Excel de seguimiento | `docs/PUBLICATION_SYNC.md` |
| Auditoría de perfiles ORCID/Scholar desde 2023 y criterio de pertenencia | `docs/PUBLICATION_PROFILE_AUDIT_2026-10-06.md`, `docs/PUBLICATION_PROFILE_AUDIT_2026-10-06.json` |
| Figuras de investigación y documentación de su procedencia | `assets/images/research/`, `assets/images/research/SOURCES.md` |
| Diagramas conceptuales opcionales, conservados por compatibilidad | `templates/mlkem.svg`, `templates/puf.svg`, `templates/photonics.svg` |
| Búsquedas, filtros, navegación y formulario | `js/script.js` |

**No edites directamente los HTML de la raíz**: el generador los sobrescribe. Los datos se insertan escapados como texto; no escribas HTML en los JSON.

## Nombre del grupo

En `site.json`, `name` contiene el nombre oficial completo: `Trusted Systems-on-Chip based on CMOS and integrated photonics technologies`. Se usa en la presentación de la portada y el pie. Mantén su escritura literal. `shortName` contiene `HWSec-CSIC`, empleado en la marca compacta de la cabecera, la navegación y los títulos de página. Los datos generales se mantienen en este archivo y se propagan al regenerar; no hace falta repetir el nombre en los HTML.

## Personal

`team.json` contiene dos listas: `groups` define las categorías y `members` las personas. El orden de ambas listas determina el orden de presentación. Puedes añadir categorías, incluida una de antiguos miembros, sin modificar las plantillas.

Ejemplo de categoría:

```json
{ "id": "phd-students", "label": "PhD Students" }
```

Ejemplo de perfil con todos los campos disponibles. Sustituye los valores por los de la persona antes de añadirlo:

```json
{
  "id": "nombre-apellidos",
  "name": "Nombre Apellidos",
  "authorNames": ["N. Apellidos"],
  "role": "PhD Student",
  "group": "phd-students",
  "photo": "assets/images/team/nombre.jpg",
  "photoPosition": "50% 30%",
  "affiliation": "IMSE-CNM",
  "bio": "Breve descripción de su trabajo de investigación.",
  "tags": ["RISC-V", "Hardware security"],
  "visible": true,
  "links": [
    { "label": "Website", "url": "https://example.org" }
  ]
}
```

| Campo | Uso |
| --- | --- |
| `id` | Obligatorio y único. Minúsculas, números y guiones. También sirve como enlace directo: `team.html#nombre-apellidos`. |
| `name`, `role` | Nombre y cargo; obligatorios. |
| `authorNames` | Lista opcional con las variantes bibliográficas exactas de la persona, por ejemplo `P. Brox`. Permite reconocerla en las publicaciones sin cambiar sus nombres originales. |
| `group` | Obligatorio. Debe coincidir con el `id` de una categoría. |
| `photo` | Opcional. Ruta local de una foto existente o URL HTTPS. Si se omite o queda vacío, se muestran iniciales. |
| `photoPosition` | Opcional. Dos porcentajes para ajustar el encuadre, por ejemplo `50% 20%`. Por defecto: `50% 30%`. |
| `affiliation`, `bio` | Textos opcionales. Solo se muestran si están rellenados. |
| `tags` | Lista opcional de intereses. También se incluye en las búsquedas. |
| `links` | Lista opcional de `{ "label": "…", "url": "https://…" }`. Permite ORCID, Scholar, web personal u otros enlaces. Omite los enlaces que no existan. |
| `visible` | Opcional; `true` por defecto. `false` oculta el perfil sin borrarlo del archivo. |

Para añadir una persona: guarda su foto, copia un perfil, asigna un `id` único y modifica sus campos. Para cambiar su categoría, cambia `group`. Los contadores y el directorio se actualizan al regenerar. Todas las categorías usan fichas con retratos compactos del mismo tamaño y proporción 4:5, incluidos estudiantes de doctorado e investigadores técnicos. Los retratos conservan su color original; usa `photoPosition` para centrar la cara. El encuadre se aplica con CSS sin modificar el archivo original.

Los enlaces a GitHub, GitLab, LinkedIn, ORCID y Google Scholar se reconocen por su URL y se presentan con su icono. La etiqueta sigue disponible para lectores de pantalla y al pasar el puntero. Mantén `label` y `url` en los datos; los enlaces a otros sitios conservan texto visible. Este comportamiento también se aplica a los enlaces generales y al código de publicaciones y destacados.

Isabel Fernández Poyato y Cristina Gómez de la Rosa están incluidas como `Technical Researcher`, con `photo: ""` y sin enlaces añadidos. Sus perfiles muestran iniciales mientras no se disponga de una foto. Para completarlos, guarda la fotografía en `assets/images/team/` y cambia únicamente `photo`; añade los enlaces y otros datos que correspondan.

## Publicaciones

Se mantiene `assets/docs/publications.json` como lista de publicaciones. Ejemplo real:

```json
{
  "title": "Timing-Optimized Hardware Implementation to Accelerate Polynomial Multiplication in the NTRU Algorithm",
  "authors": ["E. Camacho-Ruiz", "S. Sánchez-Solano", "P. Brox", "M.C. Martínez-Rodríguez"],
  "journal": "ACM Journal on Emerging Technologies in Computing Systems",
  "type": "journal",
  "volume": "17",
  "issue": "3",
  "article": "35",
  "year": 2021,
  "doi": "10.1145/3445979"
}
```

**Por defecto, cada publicación debe incluir al menos dos personas distintas del equipo actual visible en `team.json`**, incluidos sus colaboradores externos. La regla se aplica a todos los años del catálogo. El generador utiliza el mismo reconocimiento de autores que el resaltado de nombres y rechaza registros que no cumplan el mínimo; repetir variantes de una misma persona no suma miembros. Conserva siempre la lista bibliográfica completa, también los autores que no pertenecen al equipo.

La única excepción actual es el artículo de ML-KEM, restaurado por petición expresa del usuario el 7 de octubre de 2026. Su campo `eligibilityException` documenta el motivo: solo Pablo Navarro-Torrero pertenece al equipo actual. La excepción permite conservar el registro y su destacado sin cambiar los tres autores originales ni el reconocimiento de nombres, las citas o BibTeX.

Obligatorios en todos los registros: `title`, `authors` (lista no vacía de nombres), `journal` (revista o actas) y `year` (número). La referencia necesita una de estas dos formas:

- **Con DOI:** `doi` contiene el identificador único, sin `https://doi.org/`, por ejemplo `10.1145/3445979`.
- **Sin DOI verificado:** omite `doi` y usa `id` (único, con minúsculas, números y guiones) y `url` (fuente HTTPS). No inventes un DOI para completar un registro.

Los artículos completos pueden incorporarse sin DOI cuando su publicación y autoría estén verificadas. Los posters, resúmenes extendidos y comunicaciones breves solo se incorporan con un DOI individual válido para esa contribución; el DOI de unas actas completas no sirve como identificador del trabajo.

Ejemplo real de contribución sin DOI verificado:

```json
{
  "id": "chacha20-poly1305-ares-2026",
  "title": "Towards a Side-Channel-Resistant and Scalable ChaCha20-Poly1305 Hardware Implementation",
  "authors": ["F. J. Rubio-Barbero", "P. Navarro-Torrero", "E. Camacho-Ruiz", "M. C. Martínez-Rodríguez", "P. Brox"],
  "journal": "The International Conference on Availability, Reliability and Security (ARES 2026)",
  "year": 2026,
  "type": "conference",
  "url": "https://www.ares-conference.eu/conference/program"
}
```

Opcionales:

- `type`: `journal` por defecto, o `conference`. Determina la etiqueta y el formato BibTeX: `@article`/`journal` o `@inproceedings`/`booktitle`.
- `volume`, `issue`, `pages`, `article`: metadatos bibliográficos. Omite los que todavía no conozcas.
- `pdf`: ruta de un PDF local o URL HTTPS.
- `code`: URL HTTPS del código asociado.
- `id` y `url`: opcionales cuando existe DOI; obligatorios cuando falta. El DOI tiene prioridad como referencia y enlace principal si se especifica.
- `eligibilityException`: motivo no vacío de una excepción al mínimo de dos miembros, únicamente cuando exista una petición o aprobación expresa del usuario. No añade autores ni modifica su resaltado, las citas o BibTeX. Omítelo en los registros que cumplen la regla habitual.

Los años, contadores, citas y las tres publicaciones más recientes de la portada se generan automáticamente. Dentro de un año se respeta el orden del JSON: coloca primero el trabajo más reciente de ese año.

Los nombres de autores que corresponden al personal visible se destacan y enlazan a su perfil en las listas de publicaciones y los destacados. La coincidencia utiliza el nombre del perfil y sus variantes `authorNames`, normalizando mayúsculas, acentos y puntuación; no deduce identidades a partir de un apellido parecido. Si falta una coincidencia, añade la variante bibliográfica exacta y comprobada de esa persona en `team.json`. Esto también permite verificar el mínimo de dos miembros. La escritura y el orden de `authors`, las citas y BibTeX se conservan.

El generador rechaza DOI duplicados, `id` duplicados y registros sin referencia válida. Las citas utilizan el enlace DOI cuando existe y la fuente `url` cuando no. BibTeX incluye `doi` o `url` según corresponda, y genera claves distintas incluso para publicaciones del mismo autor y año.

En el archivo de publicaciones, las entradas sin DOI muestran **View source** como acción principal. Si una entrada con DOI también contiene `url`, se ofrece un enlace **Repository** adicional, como en los enlaces de DIGITAL.CSIC incorporados desde el Excel.

El catálogo se contrastó con las dos hojas de `inputs/Seguimiento.xlsx` el 6 de octubre de 2026: nueve filas con publicaciones corresponden a ocho trabajos distintos, cinco de ellos nuevos para la web. La conciliación histórica produjo 22 registros y trató ML-KEM/CHES como un único trabajo. La retirada solicitada del artículo de 2020 sobre membranas de silicio poroso dejó 21. Al aplicar el mínimo de dos miembros actuales se retiraron ML-KEM y tres artículos de óptica con un solo miembro, quedando 17. El 7 de octubre se restauró ML-KEM por petición expresa y se incorporaron nueve artículos completos identificados en la auditoría de perfiles: el catálogo actual contiene **27 registros**. Los tres artículos de óptica y el de 2020 siguen retirados. [PUBLICATION_SYNC.md](docs/PUBLICATION_SYNC.md) conserva los cambios bibliográficos, la deduplicación y los motivos.

La [auditoría de perfiles ORCID y Google Scholar desde 2023](docs/PUBLICATION_PROFILE_AUDIT_2026-10-06.md) documenta los nueve artículos completos incorporados el 7 de octubre: ocho de congresos y uno de Anales de la Academia de Ciencias de Cuba. RECSI y el artículo cubano usan referencias estables y fuentes oficiales porque no se verificó un DOI individual. Una comunicación breve y cuatro posters o resúmenes extendidos permanecen fuera del catálogo al no disponer de un DOI individual verificado. La escritura correcta de Apurba es **Karmakar**, también en los metadatos importados. Las fuentes y límites de la revisión se conservan en el informe y su versión estructurada, [PUBLICATION_PROFILE_AUDIT_2026-10-06.json](docs/PUBLICATION_PROFILE_AUDIT_2026-10-06.json).

El Excel es una fuente de seguimiento, no una dependencia del generador ni una sincronización automática. Para incorporar futuras actualizaciones, contrasta sus filas con el JSON, añade o modifica los registros, actualiza la auditoría y ejecuta las comprobaciones habituales. Cuando un trabajo reciba DOI, añádelo al registro existente y actualiza su `reference` en `featured.json` si aparece destacado; no crees una segunda publicación.

## Proyectos

`projects.json` tiene dos listas: `groups` define las categorías y `projects` contiene los registros. El campo `group` de cada proyecto debe coincidir con el `id` de una categoría. Las listas determinan el orden de las secciones y sus proyectos. Añadir una categoría o proyecto no requiere modificar las plantillas, igual que con el personal; las publicaciones se agrupan automáticamente por año.

Ejemplo de categoría y proyecto:

```json
{
  "groups": [
    { "id": "european-projects", "label": "European Projects" }
  ],
  "projects": [
    {
      "id": "q-fence",
      "name": "Q-FENCE",
      "title": "Securing Tomorrow’s Digital Infrastructure with Quantum-Resistant Cryptography",
      "group": "european-projects",
      "startDate": "2025-11-01",
      "endDate": "2028-10-31",
      "abstract": "A hybrid security framework combining classical, quantum and post-quantum cryptographic techniques to protect digital infrastructure.",
      "funder": "European Commission (Horizon Europe)",
      "programme": "Horizon Europe",
      "details": [
        { "label": "PI", "value": "Piedad Brox Jiménez" },
        { "label": "GA", "value": "101225708" }
      ]
    }
  ]
}
```

Campos de cada proyecto:

- `id`, `name` (acrónimo), `title`, `group`.
- `startDate`, `endDate`: fechas ISO `YYYY-MM-DD`. Deben aparecer juntas, ser fechas válidas y estar en orden. Ambos días están incluidos en el intervalo.
- `abstract`, `funder`.
- `programme`: nombre corto opcional del programa, mostrado en el índice; si se omite se usa `funder`.
- `details`: lista de pares `{ "label": "PI", "value": "Nombre" }`. Puedes añadir participantes, financiación u otros parámetros sin tocar HTML. **Duration** se genera a partir de las fechas; no repitas ese dato en `details`.
- `period`: texto opcional que sustituye únicamente la presentación del intervalo de fechas. Por defecto, el índice, la portada y los destacados muestran día, mes y año, por ejemplo `1 Nov 2025 – 31 Oct 2028`. No cambia las fechas, la duración ni el estado; para registrar una prórroga, modifica `endDate`.
- `datePrecision`: opcional; `day` por defecto. Usa `year` cuando la fuente solo proporciona años, con límites del 1 de enero y 31 de diciembre. TECHNOQUANTUM se muestra como `1 Jan 2025 – 31 Dec 2026 (year-based dates)`: la anotación aclara que esos límites son una convención de calendario, no fechas contractuales verificadas.
- `url`: web externa opcional en HTTPS.

El estado se calcula con las mismas fechas al generar el HTML y al cargar la página: **Upcoming** antes de `startDate`, **Ongoing** desde el inicio hasta el final inclusive y **Completed** desde el día siguiente. En el navegador se utiliza la fecha local del visitante. Las etiquetas, los filtros y el contador de proyectos en curso se actualizan aunque el HTML se hubiera generado antes. Sin JavaScript permanece el estado calculado en la fecha de generación.

La portada selecciona los tres primeros proyectos en curso según el orden del JSON y recalcula esa selección al cargar. Si no queda ninguno en curso, muestra hasta tres próximos proyectos y, después, proyectos completados. El contador incluye todos los proyectos en curso, no solo los tres visibles. El directorio permite combinar búsqueda, categoría y estado; el resumen y la financiación se pueden desplegar sin JavaScript.

Los nueve proyectos actuales usan fechas como fuente única. Para compatibilidad, un registro antiguo sin fechas puede usar `status: "upcoming"`, `"ongoing"` o `"completed"`; `"active"` también se reconoce como `"ongoing"`. Ese estado manual no evoluciona con el calendario: añade las dos fechas para obtener la actualización automática. Si hay fechas y un `status` heredado, prevalecen las fechas.

## Trabajos destacados

`featured.json` selecciona publicaciones y proyectos existentes para la sección oscura de investigación destacada. En escritorio, cada trabajo combina una imagen a la izquierda y su información a la derecha; en móvil, ambos se apilan. Con JavaScript se muestra un trabajo cada vez y el carrusel avanza automáticamente **cada 10 segundos**. Las flechas permiten recorrerlo manualmente y el botón **Pause/Resume** controla la rotación. Sin JavaScript, todos los trabajos quedan visibles. Para cambiar el orden, mueve los registros.

La rotación se detiene temporalmente cuando el puntero o el foco del teclado están dentro del carrusel, la pestaña está oculta o la sección está fuera de la pantalla. Al volver, empieza un nuevo intervalo completo de 10 segundos. Una pausa elegida con **Pause** se conserva hasta pulsar **Resume**. Si el visitante prefiere movimiento reducido, la rotación empieza pausada y puede activarse expresamente con **Resume**; las flechas siguen disponibles. Los cambios automáticos no generan anuncios periódicos para lectores de pantalla; la navegación manual anuncia el título seleccionado.

Una barra azul bajo la cabecera muestra el progreso hacia el siguiente cambio. Se llena durante el mismo intervalo de 10 segundos, queda detenida al pausar y vuelve a empezar al reanudar o cambiar de trabajo. Su información accesible indica los segundos restantes o el estado de pausa. Sin JavaScript, la barra permanece oculta.

La selección actual contiene seis trabajos, en este orden: ChaCha20-Poly1305 (ARES 2026), evaluación RO-PUF/TRNG (Sensors 2023), HOPE-MLKEM, KECCAK con enmascaramiento de segundo orden (SECRYPT 2026), RO-PUF en CMOS de 65 nm y CryptoPIC. La primera entrada determina el trabajo mostrado al abrir la página; el número de entradas y los controles se derivan de los registros, sin un límite fijo. Ejemplo real de RO-PUF/TRNG, que utiliza su figura científica como imagen principal:

```json
{
  "id": "puf-trng-evaluation",
  "kind": "publication",
  "reference": "10.3390/s23084070",
  "heading": "RO-PUF/TRNG evaluation",
  "description": "On-line evaluation and monitoring of an RO-based PUF/TRNG for IoT devices, including laboratory characterization under voltage and temperature variations.",
  "topics": ["Physical security", "PUFs and TRNGs", "Laboratory characterization"],
  "figure": {
    "image": "assets/images/research/ro-puf-trng-characterization-setup.png",
    "alt": "RO-PUF/TRNG characterization setup from Figure 15: development board (1), power supplies (2), and temperature control system (3).",
    "caption": "Figure 15. RO-PUF/TRNG characterization under voltage and temperature variations.",
    "credit": "Luis F. Rojas-Muñoz, Santiago Sánchez-Solano, Macarena C. Martínez-Rodríguez and Piedad Brox",
    "source": "https://doi.org/10.3390/s23084070",
    "license": "https://creativecommons.org/licenses/by/4.0/",
    "licenseLabel": "CC BY 4.0",
    "width": 1034,
    "height": 472
  }
}
```

`id`, `kind`, `reference`, `heading` y `description` son obligatorios. `kind` admite `publication` o `project`; `reference` debe coincidir con el DOI de una publicación, con su `id` si no tiene DOI, o con el `id` de un proyecto. El generador rechaza referencias que ya no existan. El título científico completo, los autores y la revista de una publicación, o el título y programa de un proyecto, salen de esos datos originales, junto con el año y los enlaces disponibles al artículo/proyecto y al código.

`topics`, `cover` y `figure` son opcionales. `cover` define la imagen principal de presentación de un trabajo y admite:

```json
"cover": {
  "image": "assets/images/lab/spirs-measurement.webp",
  "alt": "Laboratory evaluation hardware connected to probes and ribbon cables",
  "caption": "SPIRS hardware evaluation · group photograph.",
  "width": 1440,
  "height": 810
}
```

| Campo de `cover` | Uso |
| --- | --- |
| `image` | Ruta de una imagen local existente o URL HTTPS. Las fotos de laboratorio preparadas para la web se alojan en `assets/images/lab/` como WebP. |
| `alt` | Descripción accesible de lo que muestra la foto o figura. |
| `caption` | Pie visible que identifica el recurso y su contexto. No atribuyas una foto de contexto a un prototipo concreto sin comprobar esa relación. |
| `width`, `height` | Opcionales. Incluye ambos como enteros positivos con las dimensiones originales para reservar espacio al cargar. |

Si un registro incluye `cover` y `figure`, la imagen de presentación ocupa la columna visual y la figura científica se conserva en el desplegable **Research figure**, con toda su atribución. Si solo incluye `figure`, esa figura ocupa la columna visual. La foto de presentación puede sustituirse sin cambiar los datos bibliográficos.

El objeto `figure` identifica un recurso científico con su fuente y permiso de reutilización:

| Campo de `figure` | Uso |
| --- | --- |
| `image` | Ruta de una imagen local existente o URL HTTPS. Guarda las figuras locales en `assets/images/research/`. |
| `alt` | Descripción accesible de lo que muestra la imagen. |
| `caption` | Pie que identifica la figura y su contenido. |
| `credit` | Autores o titular al que corresponde la atribución. |
| `source` | URL HTTPS del artículo o fuente original. |
| `license` | URL HTTPS de la licencia de reutilización. |
| `licenseLabel` | Nombre visible de la licencia, por ejemplo `CC BY 4.0`. |
| `width`, `height` | Opcionales, pero deben incluirse ambos como enteros positivos si se especifica uno. Indica las dimensiones originales para reservar espacio antes de cargar la imagen. |

El generador publica el pie, la atribución, el enlace a la fuente, la licencia y un enlace a la imagen a tamaño completo. El destacado RO-PUF/TRNG utiliza la figura 15 de `10.3390/s23084070` como imagen principal, sin `cover`: montaje de caracterización con placa, fuentes de alimentación y control de temperatura. El archivo `assets/images/research/ro-puf-trng-characterization-setup.png` conserva la imagen original de 1034 × 472 píxeles, sin recorte.

Las figuras de RO-PUF/TRNG y HOPE-MLKEM tienen licencia CC BY 4.0 y muestran autores, fuente y licencia junto a la imagen. El destacado HOPE-MLKEM vuelve a utilizar la figura 6, conservada en `assets/images/research/hope-mlkem-scheduling.png`, tras la restauración expresa de su publicación. `assets/images/research/SOURCES.md` documenta ambos recursos. Al añadir o sustituir una figura, comprueba su permiso de reutilización y registra allí la fuente y cualquier adaptación. El pie debe indicar los cambios si recortas o modificas la figura.

## Fotografías del laboratorio

La portada, las áreas y los destacados con `cover` utilizan fotografías propias seleccionadas de `inputs/Fotos_SPIRS/` e `inputs/Mesa óptica - set up/`. Las copias publicadas se guardan en `assets/images/lab/*.webp`; `assets/images/lab/SOURCES.md` relaciona cada recurso con su original y describe el contexto conocido. Los destacados con `figure` conservan sus recursos científicos originales.

`scripts/prepare_photos.py` permite reproducir la reducción de tamaño y conversión a WebP. La preparación de imágenes requiere **Pillow** como dependencia opcional; el generador, el servidor y la lectura de la web siguen sin necesitarlo. Se conserva la proporción y no se aplican retoques ni alteraciones de color. El repositorio conserva en `inputs/` las seis fotografías originales seleccionadas que permiten reproducir los WebP actuales; estos originales no se referencian como recursos de las páginas.

Con Pillow instalado en tu entorno de preparación:

```bash
python3 scripts/prepare_photos.py
```

La selección de seis fotografías y sus tamaños de entrega está en `SELECTION`, dentro del script. También admite `--source` y `--output` para cambiar las carpetas de origen y salida; la salida debe estar fuera de la carpeta de originales. Además de las imágenes, genera `photos.json` con dimensiones y hashes de los originales y `SOURCES.md` con la procedencia. Si sustituyes una foto, actualiza su selección, los atributos `width` y `height` en la plantilla o el objeto `cover`, y sus textos alternativos y pies.

Las fotos usadas junto a ChaCha20-Poly1305, el artículo de RO-PUF de 65 nm y CryptoPIC muestran contexto del laboratorio; no se identifican como fotografías de sus prototipos sin verificar esa relación. Las figuras científicas del RO-PUF/TRNG de 2023 y de HOPE-MLKEM conservan sus fuentes y atribuciones en sus destacados. La foto del montaje de 2023 no se presenta como montaje del artículo de 65 nm de 2026.

El campo opcional heredado `diagram` sigue admitiendo `mlkem`, `puf` o `photonics`. Estos SVG son esquemas conceptuales simplificados y no se utilizan en los registros actuales. `figure` tiene prioridad si ambos campos están presentes. No presentes un diagrama conceptual como fotografía, layout de un circuito fabricado o resultado experimental.

## Créditos fotográficos

Los autores de las fotografías se editan en `assets/docs/photo-credits.json`. Su lista `datasets` contiene cuatro colecciones: `spirs`, con las cuatro imágenes del laboratorio SPIRS de Juan Carlos Ortiz (CSIC Andalucía); `photonics`, con las dos imágenes de fotónica de Sofía Villar (IMSE-CNM); `group`, para la foto del grupo; y `team`, para el directorio de retratos del equipo. Los autores de `group` y `team` siguen vacíos hasta disponer de esa información. Para cambiar el crédito de una colección, edita su campo `photographer` una sola vez y ejecuta `python3 scripts/build.py`. Puedes indicar la institución en `affiliation` y añadir un enlace HTTPS al perfil del fotógrafo en `url`.

Ejemplo de la entrada SPIRS:

```json
{
  "id": "spirs",
  "label": "SPIRS",
  "photographer": "Juan Carlos Ortiz",
  "affiliation": "CSIC Andalucía",
  "url": "",
  "paths": [
    "assets/images/lab/packaged-chip.webp",
    "assets/images/lab/spirs-evaluation.webp",
    "assets/images/lab/wire-bonded-die.webp",
    "assets/images/lab/spirs-measurement.webp"
  ]
}
```

| Campo | Uso |
| --- | --- |
| `id` | Identificador único de la colección. |
| `label` | Nombre de la colección; permite identificarla al editar el archivo y acompaña al autor en los créditos compartidos de investigación. |
| `photographer` | Nombre del autor. Vacío significa que no se publica ningún crédito para esa colección. |
| `affiliation` | Institución opcional, mostrada entre paréntesis después del nombre. Déjala vacía u omítela si no corresponde. |
| `url` | Enlace opcional al perfil del fotógrafo, en HTTPS. Déjalo vacío para mostrar solo el nombre. |
| `paths` | Lista de archivos o directorios locales que pertenecen a la colección. No admite comodines; las colecciones no pueden solaparse. |

El directorio `assets/images/team/` incluye automáticamente los nuevos retratos que se guarden allí, sin repetir el autor en cada perfil de `team.json`. Si una fotografía pertenece a otra persona, ajusta las colecciones para que sus rutas no se solapen.

Los créditos aparecen como **Photo: Juan Carlos Ortiz (CSIC Andalucía)** o **Photo: Sofía Villar (IMSE-CNM)** en los pies de las fotografías correspondientes del hero y los destacados. El pie de la foto del grupo también admite su crédito cuando se rellena. Las tarjetas de investigación y el directorio del equipo tienen una línea compartida **Photography** debajo; la primera relaciona las colecciones con sus autores y ambas evitan repetir al mismo fotógrafo. Las atribuciones, fuentes y licencias de las figuras científicas se mantienen en `featured.json` y son independientes de estos créditos. `photos.json` conserva los hashes y dimensiones de los originales, sin duplicar los nombres de los fotógrafos.

## Formulario y servicios externos

Se conserva el formulario existente de **Web3Forms con hCaptcha**. Su clave pública de integración está en `site.json`, campo `contactFormKey`; no es una clave privada de servidor. La dirección destinataria y las opciones de entrega se gestionan en Web3Forms. La integración utiliza el formato de su [documentación de hCaptcha](https://docs.web3forms.com/getting-started/customizations/spam-protection/hcaptcha).

El formulario comprueba el resultado de la API antes de mostrar éxito y conserva el mensaje cuando falla el envío. Las pruebas de navegador usan respuestas simuladas para no enviar consultas reales. Para comprobar la entrega real, haz un envío autorizado después de publicar y confirma su recepción.

El mapa de contacto y la verificación del formulario necesitan conexión a sus servicios externos. El resto del contenido, las imágenes locales, las fuentes, las búsquedas y las citas no dependen de un CDN.

## Diseño y mantenimiento

Consulta `design.md` para los criterios visuales. La composición sigue la referencia facilitada: cabecera y hero azul marino, fotografías propias del laboratorio, cuatro tarjetas de investigación sobre fondo claro, destacados oscuros, foto real del grupo y listas compactas de publicaciones y proyectos. El nombre oficial se muestra en la portada y el pie; la marca compacta mantiene HWSec-CSIC. La paleta utiliza `#071522` para las secciones oscuras, `#f5f8fc` para el fondo claro, `#111f34` para el texto y `#1765ce` para enlaces y botones; `#268dff` se reserva para acentos sobre fondo oscuro.

Geist se usa en títulos, textos y controles; IBM Plex Mono en fechas y referencias. Ambas fuentes se alojan en `assets/fonts/`, junto con sus licencias SIL Open Font License.

Las cifras de publicaciones y proyectos en curso se calculan al generar la portada a partir de los JSON. El contador de proyectos y su selección se recalculan también al cargar la página según la fecha local. El número de líneas de investigación corresponde a las cuatro áreas definidas en `templates/index.html`; actualízalo si cambias esas áreas. Las cifras muestran el contenido registrado, sin redondeos ni estimaciones.

El contenido está presente en el HTML inicial: se puede leer sin JavaScript y es accesible a buscadores. JavaScript añade filtros que ignoran mayúsculas y acentos, ordenación, copia de citas, navegación móvil y el carrusel manual de destacados. Las citas, las figuras y los detalles de proyectos utilizan desplegables HTML nativos. También se incluyen foco visible, acceso directo al contenido, estados de resultado anunciados y soporte para movimiento reducido.
