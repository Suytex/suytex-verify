# Decisiones de diseño — Certificado AI Productivity Experience

Referencia para mantener coherencia visual en cambios futuros.
Archivo que implementa todo esto: `certificado_ai_productivity_experience.html`.

---

## Formato

| Propiedad | Valor | Nota |
|---|---|---|
| Tamaño | **297mm × 210mm** (A4 horizontal) | Declarado en `.page` y en `@page` |
| Orientación | Landscape | `page.pdf(format="A4", landscape=True)` |
| Márgenes de impresión | `0` en los cuatro lados | El diseño llega al borde; el margen es visual |
| Fondo | Se imprime | `print_background=True` + `print-color-adjust: exact` |

Los tres tienen que coincidir: CSS `.page`, la regla `@page` y los argumentos de
`page.pdf()`. Si cambias uno, cambia los tres o el PDF sale recortado o con una
franja blanca.

---

## Color

### Los dos azules

La decisión menos obvia del diseño: **hay dos azules a propósito.**

```
--brand-blue: #1c57e6   /* marca — solo en plano */
--ink:        #1a1a2e   /* texto principal */
```

`#1c57e6` es un azul **violáceo**. En plano se ve bien, pero difuminado sobre
blanco vira a **lavanda** y ensucia todo el certificado. Por eso los degradados y
glows usan un azul **más frío** que no vira:

| Elemento | Color | Opacidad |
|---|---|---|
| Degradado del fondo | `#cfe4fb` → `#ffffff` → `#cfe5fc` | — |
| Glow superior izquierdo | `rgba(0,112,228,…)` | `0.34` → `0` |
| Glow inferior derecho | `rgba(0,112,228,…)` | `0.26` → `0` |

**Regla:** ¿degradado, glow o sombra? → `rgba(0,112,228,…)`.
¿Color plano de marca? → `#1c57e6`.

### Dónde va `--brand-blue` en plano

- Nombre del alumno y su subrayado (3px)
- Esquinas del marco geométrico (2px)
- Separadores de la línea de competencias, en baja opacidad

### Jerarquía por opacidad, no por color

El texto secundario es `--ink` con alpha, no un gris aparte. Mantiene la
temperatura del color consistente:

```
1.00  nombres de instructor/fecha, palabras en <strong>
0.68  descripción
0.60  línea de competencias
0.58  período
0.45  "CERTIFICADO DE PARTICIPACIÓN", etiquetas del footer
```

⚠️ **Nunca** uses `background-clip: text` con degradado. Chromium lo exporta a PDF
como una **franja sólida** sobre el texto. Se ve bien en pantalla y roto en el
PDF. Ver gotcha 6.1 del README.

---

## Tipografía

**Inter** (Google Fonts), pesos 400–900, con fallback a system-ui.

| Elemento | Tamaño | Peso | Tracking |
|---|---|---|---|
| Nombre del alumno | 70px | 800 | — |
| Titular del programa | 58px | 900 | `-0.5px` |
| "CERTIFICADO DE PARTICIPACIÓN" | 18px | 600 | `7px`, mayúsculas |
| Footer (valores) | 18px | 700 | — |
| Descripción | 16px | 400 | — |
| Período | 14px | 400 | — |
| Marca "SUYTEX ACADEMY" | 14px | 800 | `1.8px`, mayúsculas |
| Línea de competencias | 12.5px | 500 | `0.3px` |
| Etiquetas del footer | 12px | 400 | `1.5px`, mayúsculas |
| Bloque del QR | 10px | 400/700 | — |

**Lógica:** el nombre del alumno (70px) es más grande que el nombre del programa
(58px). El certificado es de la persona, no del curso — la jerarquía lo dice.

El tracking amplio (`7px`) en el eyebrow y las etiquetas es lo que da el aire
editorial; sin él el diseño se lee apretado.

⚠️ Inter se carga por `@import` desde Google Fonts, o sea **por red durante la
generación del PDF**. De ahí el `wait_for_timeout(300)` (gotcha 6.2). Si añades
pesos nuevos, verifica que estén en la URL del `@import`.

---

## Layout

```
┌──────────────────────────────────────────────────────┐
│ ┌─ marco (14mm, esquinas a 46px) ─────────────────┐  │
│ │ [logo] SUYTEX          eyebrow                  │  │
│ │        ACADEMY         TITULAR                  │  │
│ │                    "Se otorga a"                │  │
│ │                   NOMBRE DEL ALUMNO             │  │
│ │                   ───────────────               │  │
│ │                     descripción                 │  │
│ │                ── competencias ──               │  │
│ │                       período                   │  │
│ │              instructor      fecha              │  │
│ │ [QR] verificar ─────────      ─────────         │  │
│ └─────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

### Esquinas en espejo

Dos anclas diagonales que equilibran la composición:

- **Logo + "SUYTEX ACADEMY"** — arriba a la izquierda (`top/left: 20mm`)
- **QR + "VERIFICAR"** — abajo a la izquierda (`bottom: 18mm`, `left: 20mm`)

Ambos comparten `display:flex`, `align-items:center` y `gap:10px`, así que la
imagen y su texto se alinean igual en los dos bloques. El marco refuerza la
diagonal con esquinas solo en superior-izquierda e inferior-derecha.

### Medidas

| Elemento | Medida | Por qué |
|---|---|---|
| Logo | 46px | Igual que la esquina del marco — rima visual |
| QR | 68px + 5px padding | Mínimo para que escanee fiable impreso |
| Marco | 14mm del borde, radio 18px | — |
| Contenido | padding lateral 26mm | — |
| Descripción | `max-width: 700px` | Largo de línea legible |
| Competencias | `max-width: 760px` | — |
| Footer | `max-width: 540px` | Firmas juntas al centro, no en los extremos |

### Fondo blanco del QR

El QR lleva `background:#ffffff` y borde propio. **Necesario**: el degradado del
fondo reduce el contraste y los lectores fallan. No lo quites.

### Competencias entre reglas finas

Las 5 áreas van en **una sola línea** (`white-space: nowrap`) entre dos reglas de
1px, separadas por guiones em en `rgba(28,87,230,0.45)`.

⚠️ Con `nowrap`, agregar una sexta competencia o textos más largos **desborda**.
Si crece la lista, baja el `font-size` o reestructura el bloque — no lo dejes
desbordar en silencio.

---

## Contenido fijo vs. variable

**Variable** (por alumno, vía placeholders): `{{NOMBRE}}`, `{{CODIGO}}`,
`{{QR_BASE64}}`, `{{LOGO_BASE64}}`.

**Fijo, hardcodeado en el template:**

- Titular: "AI Productivity Experience"
- Las 5 competencias
- Período: "11 al 25 de agosto de 2026 · 5 sesiones prácticas"
- Instructor: "Francisco Suero Pereyra"
- Fecha de emisión: "25 de agosto de 2026"

⚠️ **Para un programa nuevo, duplica el template**, no lo edites — si cambias
este archivo, cualquier re-corrida reemite los certificados viejos con los datos
nuevos. Y actualiza `CERT_TEMPLATE` en `generar_certificados.py`.

---

## Al cambiar el diseño, verifica en el PDF

El PDF es el entregable; el HTML solo un paso intermedio. Lo que se ve bien en
pantalla puede salir roto impreso (ver gotcha 6.1).

```bash
python3 generar_certificados.py alumnos.csv
# y abre output/certificados/ape-2026-0001.pdf — no el .html
```

Checklist:

- [ ] Logo presente y nítido
- [ ] Inter cargada (no fallback del sistema)
- [ ] QR escanea y apunta a `verify.suytex.com/{codigo}`
- [ ] Una sola página, sin recortes ni franja blanca
- [ ] Fondo y degradados impresos, sin viraje lavanda
- [ ] Nombre largo (~30 caracteres) sin romper el layout
