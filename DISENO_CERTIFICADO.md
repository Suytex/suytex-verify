# Decisiones de diseño — Suytex Verify

Referencia para mantener coherencia visual en cambios futuros. Cubre **las cuatro
piezas** del sistema, no solo el certificado.

| Pieza | Archivo | Rol |
|---|---|---|
| Certificado (PDF) | `certificado_ai_productivity_experience.html` | El entregable |
| Página de verificación | `verificacion_template.html` | Donde aterriza el QR |
| Landing + buscador | `index.html` | Portada del sitio |
| Código no encontrado | `404.html` | Ruta inexistente |

---

## El sistema compartido

Las cuatro comparten los mismos tokens. **Si cambias uno, cámbialo en las
cuatro** — no hay CSS compartido (cada archivo es autocontenido a propósito: el
PDF tiene que funcionar sin red y las páginas sin build).

```css
--brand-blue: #1c57e6   /* marca — SOLO en plano */
--ink:        #1a1a2e   /* texto principal */

/* Fondo, idéntico en las cuatro */
linear-gradient(135deg, #cfe4fb 0%, #ffffff 40%, #ffffff 62%, #cfe5fc 100%)

/* Glows — azul frío, nunca #1c57e6 */
rgba(0,112,228, 0.28)  /* superior izquierdo */
rgba(0,112,228, 0.20)  /* inferior derecho */
```

**Lockup de marca** — igual en las cuatro: logo a la izquierda, "SUYTEX /
ACADEMY" en dos líneas a la derecha, `gap: 10px`, mayúsculas, `letter-spacing:
1.8px`, peso 800. Logo a 44px en web, 46px en el certificado (donde rima con la
esquina del marco).

**Tipografía**: Inter en todas, vía `@import` de Google Fonts.

Las secciones siguientes detallan **el certificado**. Lo específico de las
páginas web está en "Las páginas web", al final.

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

## Las páginas web

`verificacion_template.html`, `index.html` y `404.html` comparten un patrón de
tarjeta único. La página de verificación **nació con un diseño oscuro** y se
alineó después; si aparece otra página, sigue este patrón, no el viejo.

### La tarjeta

```css
max-width: 480px;
background: rgba(255,255,255,0.72);
border: 1px solid rgba(28,87,230,0.18);
border-radius: 20px;
padding: 40px 34px;
backdrop-filter: blur(12px);
```

Centrada vertical y horizontalmente, con los dos glows en `position: fixed`
detrás. Translúcida sobre el degradado: por eso el fondo se percibe a través de
la tarjeta y las cuatro piezas se sienten del mismo material.

### Jerarquía tipográfica en web

| Elemento | Tamaño | Peso |
|---|---|---|
| Nombre del alumno | 30px | 900 |
| Titular de la página | 22–24px | 800 |
| Lockup de marca | 13px | 800 |
| Filas de datos | 14px | 400 / 600 |
| Etiquetas, badge | 11–12px | 700 |
| Nota al pie | 11px | 400 |

El **nombre del alumno va en `#1c57e6`**, igual que en el certificado: es el eco
que hace evidente que la página y el papel son lo mismo.

### Badges de estado

Dos, y su color es semántico — no decorativo:

| Estado | Texto | Fondo | Borde |
|---|---|---|---|
| Válido | `#15803d` | `rgba(22,163,74,0.10)` | `rgba(22,163,74,0.32)` |
| Sin coincidencias | `#c0392b` | `rgba(192,57,43,0.08)` | `rgba(192,57,43,0.28)` |

⚠️ El verde del badge válido es **`#15803d`, no `#22c55e`**. El `#22c55e` de la
versión oscura no tiene contraste suficiente sobre fondo claro. El punto sí
mantiene `#16a34a`, que sobre su halo se lee bien.

El badge "Certificado válido" es la **señal de confianza principal** de todo el
sistema: es lo primero que busca un empleador verificando un certificado. No lo
quites ni lo suavices.

### Rutas absolutas, obligatorio

Todas las rutas internas de las páginas web van **absolutas** (`/logo_white.png`,
`/`):

- `404.html` se sirve en cualquier ruta inexistente, así que en `/ape-9999` una
  ruta relativa buscaría el logo en `/ape-9999/logo_white.png`.
- Las páginas de verificación viven en `/{codigo}/`, un nivel por debajo de la
  raíz donde está el logo.

### Normalización del buscador

`index.html` normaliza con el **mismo criterio que `slugify_codigo()`** del
script: `trim` + minúsculas + espacios internos a guiones. El certificado
muestra `APE-2026-0001` y la URL es `/ape-2026-0001`; sin normalizar, quien
escriba el código tal como lo ve se lleva un 404. Si cambia `slugify_codigo()`,
cambia esto también.

El destino se arma con `encodeURIComponent`: sin él, un valor como
`/ejemplo.com` produce `//ejemplo.com`, que el navegador lee como URL
protocol-relative y saca al visitante del sitio.

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

Y si tocaste una página web, compara **las cuatro piezas lado a lado**: el
recorrido real es certificado impreso → escanear QR → página de verificación, y
una sola pieza desalineada rompe la sensación de sistema.
