# Propuesta de modernización — HWSec-CSIC

## Objetivo

Modernizar la web de **HWSec-CSIC** para que se vea más **actual, clara, científica y original**, evitando el aspecto de plantilla o de web “hecha por IA”.

La dirección visual recomendada es:

> **Scientific editorial + semiconductor engineering**

Es decir: menos estética de *cybersecurity SaaS* y más identidad de **grupo de investigación en hardware, microelectrónica y fotónica integrada**.

---

## Problemas actuales

La web funciona y es limpia, pero combina demasiados recursos visuales muy asociados a plantillas modernas genéricas:

- Fondo azul oscuro prácticamente en toda la web.
- Azul eléctrico + verde neón.
- Muchas tarjetas rectangulares.
- Icono + título + descripción repetido constantemente.
- Gradientes en titulares.
- Badges y etiquetas en mayúsculas.
- Layouts demasiado simétricos.
- Exceso de iconografía decorativa.
- Mucho espacio vacío dentro de cards.
- Apariencia cercana a dashboard/SaaS de ciberseguridad.

El principal cambio debería ser:

> **menos UI, más contenido.**

---

# 1. Identidad visual

Mantener una identidad tecnológica y oscura, pero con más contraste editorial.

### Paleta sugerida

```text
Dark background     #07111F
Light background    #F4F6F8
Dark text           #111827
Light text          #E9EDF4

HWSec blue          #2D8CFF
Photonics cyan      #61D9C5

Muted text          #8995A7
Dark border         rgba(255,255,255,.10)
```

No usar fondo oscuro en toda la web.

### Alternancia recomendada

```text
NAV           dark
HERO          dark
INTRO         light
RESEARCH      light
FEATURED      dark
PUBLICATIONS  white
TEAM          light
FOOTER        dark
```

Esto reduce inmediatamente el aspecto de template.

---

# 2. Hero

Es la parte que más debería cambiar.

## Evitar

- Texto completamente centrado.
- Grandes frases corporativas.
- Palabras con gradientes.
- Fondo abstracto borroso.
- Botones centrados debajo del título.

## Propuesta

Layout asimétrico:

```text
HARDWARE SECURITY
+ INTEGRATED PHOTONICS

We design trustworthy hardware
from transistor to system.

Secure SoCs · RISC-V · PUFs · TRNGs ·
Side-channel security · Silicon photonics

[Explore our research →]

                             [technical image]
                             [chiplet / die / IC]

IMSE-CNM · CSIC · Universidad de Sevilla
```

La imagen debería ser técnica y propia:

- chiplet CMOS + photonics;
- die shot;
- PCB o setup de laboratorio;
- micrografía;
- layout de IC;
- waveguides;
- fotografía real de hardware.

---

# 3. Lenguaje gráfico propio

En vez de partículas, grids genéricos o elementos “cyber”, usar referencias visuales al diseño de circuitos:

- rutas de interconexión;
- bond pads;
- outline de dies;
- bloques de SoC;
- líneas de waveguides;
- diagramas de chiplets;
- numeración técnica.

Ejemplos de etiquetas:

```text
HWS / 001
RESEARCH / 03
65 NM CMOS
PHOTONIC IC
FPGA
SIDE-CHANNEL
```

Esto puede convertirse en una identidad gráfica propia de HWSec.

---

# 4. Research Areas

Eliminar las tres cards grandes actuales.

Usar una composición más editorial:

```text
RESEARCH / 01

Trusted computing
────────────────────────────

Secure SoCs, RISC-V architectures,
side-channel resistance and fault tolerance.
```

Y organizar áreas como:

1. **Secure SoCs**
2. **Physical Security**
   - PUFs
   - TRNGs
   - Side-channel analysis
   - Fault injection
3. **Integrated Photonics**
4. **Open / trusted die-to-die communication**

Menos cajas, más jerarquía tipográfica, líneas, numeración e imágenes técnicas.

---

# 5. Mostrar investigación real

La home debería enseñar proyectos y resultados concretos, no solo explicar qué hace el grupo.

Crear una sección:

## Selected Work

Por ejemplo:

```text
01
High-order protected ML-KEM
Masking · PQC · FPGA / ASIC

02
Secure ChaCha20-Poly1305
AEAD · Side-channel protection

03
Integrated photonic security
PUFs · Silicon photonics
```

Idealmente acompañados de:

- esquemas propios;
- figuras de papers;
- fotografías de hardware;
- diagramas de arquitectura;
- capturas de layout o silicio.

---

# 6. Team

La página actual tiene cards demasiado grandes y mucho espacio vacío.

## Propuesta

Usar una grid editorial de retratos:

```text
[PHOTO]      [PHOTO]      [PHOTO]      [PHOTO]

Name         Name         Name         Name
Role         Role         Role         Role
```

Sin caja alrededor.

### Fotos

Unificar:

- ratio fijo `4:5`;
- tamaño de rostro similar;
- recorte consistente;
- fondos simples;
- blanco y negro suave;
- opcional: color al hacer hover.

Debajo del nombre:

- cargo;
- ORCID;
- Scholar;
- LinkedIn;
- áreas de investigación.

---

# 7. Publications

Actualmente parece demasiado una interfaz de dashboard.

## Sustituir cards por una lista editorial

```text
PUBLICATIONS

2026

01  Robust and Scalable Cell-Based 65-nm CMOS RO-PUF
    P. Ortega-Castro, E. Camacho-Ruiz, ...
    IEEE ...
    DOI ↗     BibTeX

02  Hardware-Rooted Device Identity for IoT
    ...
```

Filtro superior sencillo:

```text
Search publications...        2026  2025  2024  All
```

Ventajas:

- mayor densidad informativa;
- aspecto más académico;
- lectura más rápida;
- menos ruido visual.

---

# 8. Projects

Los proyectos actuales parecen paneles administrativos.

Sustituir por un índice editorial:

```text
PROJECT                     PROGRAMME       PERIOD       STATUS

DECIDE
Democratizing European
Chip Innovation             Chips JU        2025–28      ACTIVE →

Q-FENCE                      Horizon Europe  2025–28      ACTIVE →

QUBIP                        Horizon Europe  2023–26      ACTIVE →

SQPRIM                       National        2023–25      COMPLETED →
```

Al hacer clic se puede mostrar el detalle completo.

---

# 9. Iconografía

Reducir mucho los iconos decorativos.

Usarlos únicamente cuando aporten una función clara:

- GitHub;
- ORCID;
- Google Scholar;
- DOI;
- email;
- external link.

Para secciones, usar mejor:

```text
01
02
03
04
```

o etiquetas de metadata.

---

# 10. Tipografía

La tipografía actual funciona, pero refuerza el aspecto de startup.

### Combinación recomendada

**Geist + IBM Plex Mono**

Uso:

- Geist: títulos, párrafos, navegación.
- IBM Plex Mono: metadata, años, tecnologías, DOI, FPGA, CMOS, etc.

Alternativas:

- Instrument Sans + IBM Plex Mono.
- Manrope + Roboto Mono.

---

# 11. Home propuesta

```text
HEADER
────────────────────────────────

HERO
Hardware Security
+ Integrated Photonics

[text]                     [chip / chiplet image]


RESEARCH
────────────────────────────────

01  Secure SoCs
02  Physical Security
03  Integrated Photonics
04  Die-to-Die Trust


SELECTED WORK
────────────────────────────────

[large technical image]

HOPE-MLKEM
High-order side-channel protected ML-KEM

View project →


LATEST PUBLICATIONS
────────────────────────────────

2026   Robust and Scalable Cell-Based...
2026   Hardware-Rooted Device Identity...
2026   A Framework for...


GROUP
────────────────────────────────

                         [group photo]

HWSec-CSIC is part of the
Instituto de Microelectrónica de Sevilla...


CURRENT PROJECTS
────────────────────────────────

DECIDE      Chips JU          2025–2028
Q-FENCE     Horizon Europe    2025–2028
QUBIP       Horizon Europe    2023–2026


FOOTER
```

No es necesario mostrar Team completo ni todas las publicaciones en portada.

---

# Dirección visual final

## Actual

> Cybersecurity startup  
> SaaS dashboard  
> Cards + gradients + icons + badges

## Propuesta

> Semiconductor research lab  
> Scientific editorial design  
> Silicon / photonics visual language  
> Precise typography  
> Real engineering imagery  
> More content, less UI

---

# Prioridades

| Prioridad | Cambio | Impacto |
|---|---|---|
| Alta | Rediseñar Hero | Muy alto |
| Alta | Eliminar la mayoría de cards | Muy alto |
| Alta | Introducir imágenes técnicas propias | Muy alto |
| Alta | Rediseñar Team | Alto |
| Media | Publications como lista editorial | Alto |
| Media | Projects como índice | Alto |
| Media | Alternar secciones dark/light | Alto |
| Media | Cambiar tipografía | Medio |
| Media | Reducir iconos y badges | Medio |
| Baja | Microanimaciones | Bajo |

---

# Principio general

No empezar añadiendo animaciones, partículas, glow o WebGL.

Primero:

1. Identidad.
2. Composición.
3. Tipografía.
4. Fotografía e imágenes técnicas.
5. Jerarquía visual.
6. Contenido real de investigación.

Después, si hace falta, añadir microinteracciones discretas.

La web puede seguir funcionando perfectamente con **GitHub Pages y el stack actual**, centrándose en modernizar HTML, CSS, layout, imágenes y sistema visual.
