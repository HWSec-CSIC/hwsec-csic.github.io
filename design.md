# HWSec-CSIC · Criterios de diseño

La composición sigue la referencia visual facilitada por el usuario: una cabecera compacta, una portada con fotografía propia de hardware, secciones claras para consultar contenido y una sección oscura de investigación destacada. La identidad del grupo se concreta con su nombre oficial, sus cuatro líneas de investigación, publicaciones y proyectos existentes, las fotografías del laboratorio y del equipo, y su pertenencia al IMSE-CNM.

El nombre oficial es **Trusted Systems-on-Chip based on CMOS and integrated photonics technologies**. Se mantiene en `site.json.name` y se muestra en la presentación de la portada y el pie. `site.json.shortName`, **HWSec-CSIC**, se usa en la marca compacta. Ambos se insertan desde los datos al generar la web.

## Color

| Variable en `css/style.css` | Color | Uso |
| --- | --- | --- |
| `--navy` | `#071522` | Cabecera, hero, destacados y pie |
| `--paper` | `#f5f8fc` | Fondo claro de lectura |
| `--white` | `#ffffff` | Tarjetas y figuras científicas |
| `--ink` | `#111f34` | Texto principal sobre fondo claro |
| `--muted` | `#53647c` | Texto secundario sobre fondo claro |
| `--accent` | `#1765ce` | Enlaces, botones y foco sobre fondo claro |
| `--blue` | `#268dff` | Marca y acentos sobre fondo oscuro |
| `--wash` | `#eaf0f7` | Fondos secundarios |
| `--line` | `#dce5f0` | Separadores y bordes discretos |
| `--light-ink` | `#f4f7fc` | Texto principal sobre fondo oscuro |
| `--light-muted` | `#afc0d4` | Texto secundario sobre fondo oscuro |

Los botones con texto blanco utilizan el azul más oscuro de `--accent`. El azul luminoso de la marca se reserva para el fondo marino. El hero aplica una capa oscura sobre la imagen para sostener la lectura del texto; no comunica información científica mediante efectos de luz.

## Tipografía y detalles

Geist se utiliza en títulos, textos y controles para mantener una jerarquía coherente. IBM Plex Mono se reserva para fechas y referencias. Ambas fuentes se sirven localmente y sus licencias SIL OFL están en `assets/fonts/`.

Los títulos se distinguen por tamaño y peso; las etiquetas de sección son pequeñas y llevan una regla fina. Las tarjetas tienen bordes discretos y esquinas de pocos píxeles. La marca compartida combina un símbolo de chip en SVG y el nombre HWSec-CSIC.

Los enlaces a GitHub, GitLab, LinkedIn, ORCID y Google Scholar utilizan iconos reconocidos por la URL, con nombre accesible y etiqueta al pasar el puntero. Los destinos sin un icono conocido conservan texto. La identificación no depende de añadir un parámetro visual a cada enlace del JSON.

## Composición de la portada

El contenido tiene un ancho máximo de 1240 px. La cabecera oscura incorpora navegación directa y un botón de contacto. El hero es asimétrico: el nombre oficial y la presentación ocupan la izquierda y la fotografía de un chip encapsulado domina la derecha. Una nota identifica su contexto como fotografía del laboratorio.

La portada presenta, en este orden:

1. Hero con nombre oficial, presentación, términos de investigación y enlaces a investigación y al grupo.
2. Cuatro áreas: SoCs seguros sobre RISC-V, primitivas de seguridad física, fotónica integrada y comunicación die-to-die. Cada tarjeta combina una fotografía del laboratorio, número, título, descripción y enlace a contenido existente.
3. Investigación destacada sobre fondo oscuro, con una imagen y una referencia científica o proyecto a su lado.
4. Tres cifras: áreas de investigación, publicaciones registradas y proyectos en curso.
5. Presentación institucional junto a la fotografía real del grupo.
6. Las tres publicaciones más recientes, con autores, revista y acceso a cita y BibTeX.
7. Los tres primeros proyectos en curso, con programa, periodo y resumen; si no hay proyectos en curso, próximos y completados.
8. Pie oscuro con dirección, teléfono y enlaces institucionales.

Las cifras de publicaciones y proyectos en curso proceden de los JSON. El número de áreas corresponde a las cuatro tarjetas de `templates/index.html`. El estado y la selección de proyectos se calculan a partir de `startDate` y `endDate`, al generar el HTML y al cargar la página; se respeta el orden de `projects.json`. La cuenta y las tarjetas se ajustan a la fecha local del visitante. Las publicaciones se ordenan por año y conservan el orden del JSON dentro de cada año.

## Investigación destacada

`assets/docs/featured.json` selecciona publicaciones y proyectos existentes y determina su orden. Una referencia de publicación utiliza su DOI o su `id` cuando no tiene DOI verificado; una referencia de proyecto utiliza su `id`. El generador recupera el título científico, autores y revista, o el título y programa del proyecto, y construye los enlaces disponibles.

La selección actual tiene seis entradas, en este orden: ChaCha20-Poly1305 (ARES 2026), evaluación RO-PUF/TRNG (Sensors 2023), HOPE-MLKEM, KECCAK con enmascaramiento de segundo orden (SECRYPT 2026), RO-PUF en CMOS de 65 nm y CryptoPIC. La primera abre la sección. La navegación y el número de trabajos se calculan a partir del JSON y no fijan una cantidad de destacados. Las publicaciones destacadas proceden del catálogo; ML-KEM conserva la excepción expresa del usuario al mínimo habitual de dos miembros actuales.

Con JavaScript, el carrusel muestra un trabajo cada vez y avanza automáticamente cada 10 segundos. Las flechas anterior y siguiente conservan la navegación manual; el botón **Pause/Resume** permite detener y reanudar la rotación. El puntero o el foco dentro de la sección, una pestaña oculta o la sección fuera de pantalla suspenden temporalmente el temporizador; al volver comienza otro intervalo completo. La pausa expresa del usuario se mantiene hasta reanudar. La preferencia de movimiento reducido inicia la rotación pausada, con posibilidad de activarla expresamente. Un estado accesible anuncia la navegación manual, mientras los avances automáticos no interrumpen la lectura. Sin JavaScript, todos los registros se muestran en orden y los controles de mejora permanecen ocultos.

Debajo de la cabecera, una barra azul de 3 px indica cuánto falta para el siguiente trabajo. Comparte el intervalo de 10 segundos del carrusel, conserva su posición durante las pausas y se reinicia al reanudar o navegar. Su semántica de progreso ofrece los segundos restantes o el estado de pausa sin anuncios continuos. La barra se oculta sin JavaScript y al imprimir.

El objeto opcional `cover` contiene `image`, `alt`, `caption` y, opcionalmente, las dimensiones originales `width` y `height`. Define la fotografía principal de presentación. Puede cambiarse sin modificar la referencia científica; su pie describe el contexto conocido y no debe atribuir el equipo mostrado a un prototipo sin verificarlo.

El objeto `figure` conserva una figura científica y su atribución. Cuando el registro también tiene `cover`, la figura se consulta en el desplegable nativo **Research figure**; si no tiene `cover`, la figura ocupa la columna visual. La atribución, fuente, licencia y enlace a tamaño completo se mantienen junto al recurso.

## Imágenes y procedencia

`assets/images/grupo.jpeg` y las fotografías de `assets/images/team/` son los archivos reales del grupo. Se conserva su color y no se alteran los originales. Los retratos tienen proporción 4:5, con encuadre ajustable mediante `photoPosition` en el JSON.

Las seis fotografías preparadas para la web están en `assets/images/lab/`. Proceden de los originales aportados en `inputs/Fotos_SPIRS/` y `inputs/Mesa óptica - set up/`:

| Recurso WebP | Original | Uso y contexto |
| --- | --- | --- |
| `packaged-chip.webp` | `A60A1685.jpg` | Hero: chip encapsulado y sus conexiones |
| `spirs-evaluation.webp` | `A60A1673.jpg` | Área de SoCs: equipo de evaluación SPIRS |
| `wire-bonded-die.webp` | `A60A1681.jpg` | Seguridad física: chip con conexiones; contexto del artículo RO-PUF |
| `fibre-alignment.webp` | `DSC01395.JPG` | Fotónica: montaje y alineación de fibra |
| `spirs-measurement.webp` | `_60A9978.jpg` | Área de comunicación y destacado ChaCha20-Poly1305: contexto de medidas de hardware SPIRS |
| `optical-bench.webp` | `DSC01384.JPG` | Contexto de mesa óptica para CryptoPIC |

`assets/images/lab/SOURCES.md` documenta la relación con los originales. `scripts/prepare_photos.py` reproduce la reducción de tamaño y conversión a WebP, sin retoques ni cambios de color. Pillow es una dependencia opcional de esta preparación; la generación HTML y el servidor siguen utilizando únicamente la biblioteca estándar de Python. El repositorio conserva en `inputs/` las seis fotografías originales seleccionadas que permiten reproducir los WebP actuales; las páginas solo referencian los recursos preparados en `assets/`.

Los autores de las fotografías, sus instituciones y sus enlaces opcionales se mantienen en `assets/docs/photo-credits.json`, con colecciones separadas para SPIRS, fotónica, la foto del grupo y los retratos del equipo. SPIRS se acredita a Juan Carlos Ortiz (CSIC Andalucía) y fotónica a Sofía Villar (IMSE-CNM); grupo y equipo conservan nombres vacíos, que omiten el crédito público. Los pies existentes del hero, las fotos de los destacados y la foto del grupo incorporan **Photo: Nombre (institución)** cuando se rellena el autor; la institución es opcional. Una línea compartida **Photography** debajo de las tarjetas de investigación relaciona las colecciones con sus autores, y otra debajo del directorio del equipo acredita sus retratos. Estas líneas evitan repetir a la misma persona. Las rutas de archivos o directorios definen las colecciones, sin comodines ni solapamientos; el directorio del equipo incluye los nuevos retratos. Editar el autor una vez por colección y regenerar basta para actualizar sus créditos, sin modificar los hashes de procedencia ni las atribuciones científicas.

Las fotografías de contexto no se identifican como el circuito RO-PUF de 65 nm o hardware concreto de CryptoPIC sin una correspondencia verificada. Sus pies y textos alternativos describen el equipo y su origen conocido.

La evaluación RO-PUF/TRNG utiliza una figura científica original como imagen principal, sin una foto `cover`: figura 15 del artículo Sensors 2023, DOI `10.3390/s23084070`, con el montaje de caracterización, la placa, las fuentes de alimentación y el control de temperatura. El recurso `ro-puf-trng-characterization-setup.png` conserva la imagen original de 1034 × 472 píxeles sin recorte para que sus números sigan siendo legibles. Este montaje corresponde al estudio de 2023 y no se atribuye al artículo de CMOS de 65 nm de 2026.

La figura 6 de HOPE-MLKEM, planificación de K-PKE.KeyGen para ML-KEM-512, se muestra en el destacado restaurado, desde `assets/images/research/hope-mlkem-scheduling.png`. La publicación y su destacado se recuperaron por petición expresa del usuario el 7 de octubre de 2026. La figura conserva su atribución y licencia.

Ambas figuras tienen licencia CC BY 4.0 y su procedencia se conserva en `assets/images/research/SOURCES.md`. El generador muestra autores, enlace al artículo y licencia, y permite abrir cada figura a tamaño completo. `README.md` describe los campos de edición.

Las plantillas SVG `mlkem.svg`, `puf.svg` y `photonics.svg` permanecen como recursos conceptuales heredados. El campo opcional `diagram` admite estos tres esquemas. Una figura científica tiene prioridad sobre estos diagramas; una imagen `cover` ocupa la presentación principal cuando se especifica. Los esquemas conceptuales deben identificarse como tales.

## Directorios y adaptación

Las páginas interiores comparten la cabecera oscura, el fondo claro y la tipografía de la portada. El personal se organiza por categorías con cabeceras compactas. Todas las categorías usan fichas horizontales y retratos compactos de tamaño uniforme, ajustados al ancho de pantalla; estudiantes de doctorado e investigadores técnicos mantienen la misma proporción 4:5 que el resto. Isabel Fernández Poyato y Cristina Gómez de la Rosa aparecen como investigadoras técnicas con iniciales hasta que se incorpore su fotografía; no se inventan retratos, biografías ni enlaces.

Las publicaciones forman una bibliografía numerada y agrupada por año, con filtros, ordenación y citas desplegables. Las entradas pueden identificarse mediante DOI o mediante un `id` estable y una URL HTTPS cuando no se conoce DOI. Las citas y BibTeX conservan esta diferencia sin añadir identificadores provisionales. Por defecto, el catálogo admite trabajos con al menos dos personas distintas del equipo actual visible en `team.json`, incluidos colaboradores externos. Esta regla se valida para todos los años usando el mismo reconocimiento que resalta autores. Una excepción expresa se documenta en `eligibilityException`; actualmente solo la publicación restaurada de ML-KEM utiliza ese campo, sin alterar su autoría.

El catálogo actual contiene 27 publicaciones. [PUBLICATION_SYNC.md](docs/PUBLICATION_SYNC.md) conserva la conciliación histórica de nueve filas del Excel: 22 registros tras cinco incorporaciones, 21 tras retirar el artículo de 2020 solicitado por el usuario y 17 después de excluir cuatro trabajos con un solo miembro actual. El 7 de octubre se restauró ML-KEM por petición expresa y se incorporaron nueve artículos completos. ML-KEM y su presentación CHES siguen siendo un único trabajo; solo Pablo Navarro-Torrero coincide con el equipo actual y la excepción conserva sus tres autores originales.

La [auditoría de ORCID y Google Scholar desde 2023](docs/PUBLICATION_PROFILE_AUDIT_2026-10-06.md) documenta los nueve artículos completos incorporados: ocho de congresos y uno de Anales de la Academia de Ciencias de Cuba. Los posters, resúmenes extendidos y comunicaciones breves solo se añaden con un DOI individual verificado; los cinco de la auditoría permanecen fuera del catálogo. El informe conserva sus fuentes y límites de verificación.

Los autores que corresponden a miembros visibles del grupo, incluidos los colaboradores externos del directorio, se destacan y enlazan a sus perfiles. El reconocimiento usa el nombre de `team.json` y sus variantes opcionales `authorNames`, sin alterar los nombres bibliográficos, las citas ni BibTeX. Los autores que no pertenecen al equipo actual conservan la presentación de texto habitual.

Los proyectos se presentan como un índice de nombre, programa, periodo y estado, agrupado por las categorías de `projects.json.groups`; cada registro pertenece a una mediante `group`. Se pueden añadir categorías y registros desde el JSON, igual que en el directorio de personas. La búsqueda se combina con los filtros de categoría y estado; el resumen y la financiación se consultan mediante HTML nativo.

`startDate` y `endDate` usan fechas ISO e incluyen ambos días. El estado pasa de **Upcoming** a **Ongoing** el primer día, y a **Completed** el día posterior al final. La duración visible se genera con esas fechas y muestra día, mes y año en el índice, la portada y los destacados, por ejemplo `1 Nov 2025 – 31 Oct 2028`. El campo opcional `period` cambia solo la presentación; una prórroga requiere actualizar `endDate`. Cuando la fuente solo indica años, `datePrecision: "year"` utiliza el 1 de enero y el 31 de diciembre como convención de cálculo. TECHNOQUANTUM se muestra como `1 Jan 2025 – 31 Dec 2026 (year-based dates)`, identificando la convención sin afirmar fechas contractuales exactas. Sin JavaScript permanece la selección y el estado de la generación HTML.

En pantallas estrechas, las cuatro tarjetas pasan a dos y después a una columna. Los destacados y la sección del grupo se apilan, y el hero adapta el encuadre de la imagen para mantener legibles el texto y las acciones. Las filas bibliográficas y los proyectos distribuyen su información verticalmente cuando el ancho lo requiere.

Se conservan el foco visible, el acceso directo al contenido, la navegación con teclado y los estados anunciados. El contenido académico, las citas, las figuras y los detalles pueden leerse sin JavaScript. La preferencia de movimiento reducido elimina las transiciones.

La portada incorpora apariciones suaves al entrar en pantalla: opacidad y un desplazamiento vertical de 16 px durante 480 ms, con 60 ms entre elementos de una misma fila. Cada elemento se anima una sola vez; el hero y el contenido inicialmente visible aparecen de inmediato. Se utiliza `IntersectionObserver`, sin manejadores continuos de desplazamiento ni dependencias externas. El foco del teclado, la impresión y la preferencia de movimiento reducido muestran el contenido inmediatamente. Sin JavaScript o sin soporte del observador, todo permanece visible.

Edita los JSON para el contenido y las plantillas o CSS para la presentación. Regenera las páginas y revisa escritorio y móvil después de cambiar la estructura. `README.md` documenta los parámetros y el flujo de edición.
