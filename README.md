# Suytex Verify — Certificados de Suytex Academy

Sistema de emisión y verificación de certificados para alumnos de Suytex Academy.
Genera, por cada alumno, un **PDF del certificado** con QR único y una **página
web de verificación** pública, ambos a partir de un solo CSV.

Sitio en vivo: **https://verify.suytex.com/{codigo}**
Ejemplo: https://verify.suytex.com/ape-2026-0003

---

## 1. Cómo funciona

```
alumnos.csv  ──push──▶  GitHub Actions  ──▶  generar_certificados.py
                                                      │
                                    ┌─────────────────┴─────────────────┐
                                    ▼                                   ▼
                        output/certificados/*.pdf            output/verify/{codigo}/
                                    │                                   │
                                    ▼                                   ▼
                        GitHub Release "tanda-N"          copiado a la raíz del repo
                        (PDFs adjuntos)                            │
                                                                    ▼
                                                        GitHub Pages
                                                    verify.suytex.com/{codigo}
```

**El flujo completo es automático.** Editas `alumnos.csv`, haces push, y en ~45s
tienes los PDFs en un Release y las páginas de verificación en vivo.

### Disparadores del workflow

`.github/workflows/generar-certificados.yml` corre en dos casos, **y solo en esos dos**:

| Disparador | Cuándo |
|---|---|
| `push` con cambios en `alumnos.csv` | Automático al agregar/editar alumnos |
| `workflow_dispatch` | Manual |

⚠️ **Un push que cambie el template, el script o el logo NO dispara nada.** El
filtro `paths:` solo mira `alumnos.csv`. Si cambiaste el diseño y quieres una
tanda nueva, lánzalo a mano:

```bash
gh workflow run generar-certificados.yml
```

O desde la web: **Actions → Generar certificados → Run workflow**.

---

## 2. Agregar alumnos (flujo normal)

1. Edita `alumnos.csv` — dos columnas, `nombre,codigo`:

   ```csv
   nombre,codigo
   Isaac Suero Cerda,APE-2026-0001
   Francisco Suero,APE-2026-0002
   ```

2. Commit y push a `main`.
3. El workflow arranca solo. Revisa **Actions** hasta que quede en verde.
4. Los PDFs quedan en el Release `tanda-N` (N = número de run).
5. Las páginas quedan en vivo en `verify.suytex.com/{codigo-en-minúsculas}`.

### Espacios y líneas en blanco

- **Los valores toleran espacios alrededor**: `Jasmali Rodriguez, APE-2026-0006`
  funciona — el script hace `.strip()` sobre nombre y código.
- **Las líneas en blanco al final se ignoran** (`csv.DictReader` las salta).
- ⚠️ **La cabecera NO tolera espacios.** Tiene que ser exactamente
  `nombre,codigo`. Con ` codigo` (con espacio), `DictReader` crea una clave con
  el espacio incluido y el script muere con `KeyError: 'codigo'`.

### Sobre los códigos

- El código se muestra **tal cual lo escribes** en el certificado y en la página
  (`APE-2026-0001`).
- La **URL usa el slug en minúsculas**: `APE-2026-0001` → `/ape-2026-0001`.
  Lo hace `slugify_codigo()` (minúsculas + espacios a guiones).
- El QR apunta al slug, así que ambos siempre coinciden.

⚠️ **El CSV es acumulativo.** Cada corrida regenera *todos* los alumnos del
archivo, no solo los nuevos. No borres alumnos viejos salvo que quieras
despublicar su certificado.

---

## 3. Correr en local

```bash
pip install qrcode pillow playwright
python -m playwright install --with-deps chromium

python3 generar_certificados.py alumnos.csv
```

Resultado en `output/` (ignorado por git):

```
output/
├── certificados/
│   ├── ape-2026-0001.html   # HTML intermedio, con todo embebido
│   └── ape-2026-0001.pdf    # el entregable
└── verify/
    └── ape-2026-0001/
        └── index.html       # página de verificación
```

`pillow` no es opcional: `qrcode.make()` devuelve una imagen PIL y el script la
guarda con `img.save()`. Sin pillow, revienta al generar el primer QR.

---

## 4. Estructura de archivos

| Archivo | Qué es |
|---|---|
| `alumnos.csv` | **La única fuente de verdad.** Columnas `nombre,codigo` |
| `generar_certificados.py` | El generador. Único script del sistema |
| `certificado_ai_productivity_experience.html` | Template del **PDF** (A4 horizontal) |
| `verificacion_template.html` | Template de la **página web** de verificación |
| `logo_white.png` | Logo embebido en el PDF como base64 |
| `.github/workflows/generar-certificados.yml` | El pipeline |
| `CNAME` | `verify.suytex.com` — dominio de GitHub Pages |
| `ape-2026-000X/index.html` | Páginas publicadas (**generadas, no editar a mano**) |
| `index.html` | Landing del sitio + buscador de códigos (hecho a mano) |
| `404.html` | Página de "código no encontrado". Pages la sirve sola |
| `isc/index.html` | Página suelta, de otro programa. Ver §8 |
| `DISENO_CERTIFICADO.md` | Decisiones de diseño del certificado |

### Placeholders de los templates

`certificado_ai_productivity_experience.html` — los cuatro son obligatorios:

| Placeholder | Se reemplaza por |
|---|---|
| `{{NOMBRE}}` | Nombre del alumno |
| `{{CODIGO}}` | Código tal cual está en el CSV |
| `{{QR_BASE64}}` | QR del `verify_url`, como data URI |
| `{{LOGO_BASE64}}` | `logo_white.png` como data URI |

`verificacion_template.html` usa solo `{{NOMBRE}}` y `{{CODIGO}}`.

Todo va **embebido en base64** — el PDF tiene que ser autocontenido, sin
referencias a archivos locales que se rompan al moverlo.

---

## 5. DNS y publicación

- `CNAME` en el repo → `verify.suytex.com`
- DNS gestionado en **Hostinger**: registro `CNAME  verify → suytex.github.io`
- GitHub Pages sirve la raíz del repo (`main`)

Al ser Pages estático, cada página de verificación es un directorio con su
`index.html`. Por eso el workflow hace `cp -r output/verify/* .` — para que
`verify.suytex.com/ape-2026-0001` resuelva a `ape-2026-0001/index.html`.

---

## 6. ⚠️ Gotchas — problemas ya resueltos, NO reintroducir

Cada uno de estos costó una tanda de debugging. Están resueltos; la lista existe
para que nadie los vuelva a meter.

### 6.1 No usar `background-clip: text` con degradado en el template

Chromium lo **exporta mal a PDF**: en vez del texto con degradado, imprime una
**franja sólida** sobre el texto. Se ve bien en pantalla y roto en el PDF, que es
justo el entregable.
→ Para texto de color usa un color plano (`var(--brand-blue)`).

### 6.2 `page.wait_for_timeout(300)` antes de `page.pdf()` es obligatorio

Sin esa espera, el runner imprime el PDF **antes de que carguen la fuente Inter
(desde Google Fonts) y las imágenes base64**. El resultado: certificados con
tipografía de fallback y/o sin logo, de forma intermitente.
→ **No la quites ni la bajes.** No es una pausa decorativa.

### 6.3 El workflow debe instalar `pillow`

`pip install qrcode pillow playwright` — las tres. `qrcode` no arrastra `pillow`
como dependencia, y el script necesita PIL para serializar el QR a PNG.

### 6.4 `logo_white.png` se llama así por razones históricas

**El logo es a color** (círculo azul marino con la S), no blanco. El nombre quedó
de una versión anterior. `generar_certificados.py` lo busca con ese nombre exacto:

```python
LOGO_FILE = BASE_DIR / "logo_white.png"
```

→ **No lo renombres.** Si falta, el script no falla: avisa con `⚠️` y emite el
certificado sin logo — un fallo silencioso fácil de pasar por alto.

### 6.5 El azul de marca `#1c57e6` es violáceo

Difuminado sobre blanco **vira a lavanda**, que ensucia el certificado. Por eso
hay dos azules distintos y a propósito:

| Uso | Color | Por qué |
|---|---|---|
| Fondo, glows, degradados | `#cfe4fb`, `#cfe5fc`, `rgba(0,112,228,…)` | Azul más **frío**, no vira |
| Nombre del alumno, acentos, marco | `#1c57e6` (`--brand-blue`) | Color de marca, en plano |

→ Si añades un degradado o un glow nuevo, usa `rgba(0,112,228,…)`, **no**
`#1c57e6`. Detalle completo en [`DISENO_CERTIFICADO.md`](DISENO_CERTIFICADO.md).

---

## 7. Troubleshooting

### El Release sale sin PDFs

Mira el paso **"Diagnostico output"** del run — hace `ls -laR output/`. Existe
exactamente para esto.

- ¿`output/certificados/` vacío? → falló Playwright. Busca `❌ ERROR generando PDF`
  en el paso "Generar certificados".
- ¿`NO EXISTE output/`? → el script murió antes de escribir. Casi siempre es una
  dependencia (ver 6.3) o un CSV mal formado.

### El certificado sale sin logo

Busca `⚠️  No encontré logo_white.png` en el log. Confirma que el archivo está en
la raíz y con ese nombre exacto (ver 6.4).

### El certificado sale con la tipografía equivocada

Es 6.2. Verifica que `page.wait_for_timeout(300)` siga ahí.

### Cambié el diseño y no pasó nada

El workflow solo se dispara con `alumnos.csv`. Lánzalo a mano (ver §1).

### La página de verificación no aparece

1. ¿El run quedó verde?
2. ¿El paso "Commit y push" hizo commit? Si dice `Everything up-to-date`, las
   páginas no cambiaron — normal si el alumno ya estaba publicado.
3. GitHub Pages tarda ~1 min en propagar tras el commit.
4. Recuerda que la URL va en **minúsculas**.

### `KeyError: 'nombre'` o `'codigo'`

La cabecera del CSV no coincide. Tiene que ser exactamente `nombre,codigo`.

---

## 8. La raíz del sitio

Estas tres páginas son **hechas a mano** — no las genera el script, y el
workflow no las toca (ver más abajo).

| URL | Archivo | Qué es |
|---|---|---|
| `verify.suytex.com/` | `index.html` | Landing + buscador de códigos |
| Cualquier ruta inexistente | `404.html` | "Este código no corresponde a ningún certificado" |
| `verify.suytex.com/isc/` | `isc/index.html` | Página de otro programa (ver abajo) |

### El buscador de la raíz

Un input y un botón, sin backend. Normaliza la entrada **con el mismo criterio
que `slugify_codigo()`** en el script, y redirige a `/{codigo}`:

```js
valor.trim().toLowerCase().replace(/\s+/g, '-')
```

Esto importa porque el certificado muestra `APE-2026-0001` pero la URL publicada
es `/ape-2026-0001`. Sin normalizar, quien escriba el código en mayúsculas —o sea,
tal como lo ve en su certificado— se lleva un 404.

Casos cubiertos: mayúsculas, minúsculas, espacios alrededor, espacios internos
(`APE 2026 0003` → `/ape-2026-0003`), Enter además del clic, e input vacío (no
redirige y muestra un aviso).

El destino se construye con `encodeURIComponent`, no por estética: sin él, un
valor como `/ejemplo.com` produciría `//ejemplo.com`, que el navegador interpreta
como URL protocol-relative y sacaría al visitante del sitio.

### `404.html`

GitHub Pages lo sirve automáticamente en cualquier ruta que no exista, dejando la
URL intentada en la barra. La página la muestra para ayudar a detectar el typo, y
enlaza de vuelta a la raíz.

⚠️ Sus rutas internas son **absolutas** (`/logo_white.png`, `/`), y tiene que
seguir así. Con rutas relativas, un 404 en `/ape-9999` buscaría el logo en
`/ape-9999/logo_white.png` y saldría roto.

### `isc/index.html`

Es la página que **antes ocupaba la raíz**, movida aquí sin cambios.

Origen: la escribiste a mano en `72ff74a`, cuando el `CNAME` apuntaba a
`isc.suytex.com` (`8305846`, isc = Isaac Suero Cerda). Al revertir el dominio a
`verify.suytex.com` (`b891d35`), quedó huérfana sirviéndose como portada del
sitio — o sea, `verify.suytex.com/` mostraba el certificado de un alumno concreto.

Su contenido **no es** del AI Productivity Experience: habla de billetera de
Bitcoin y de apoyo en operaciones diarias. Es un certificado de otro programa, y
por eso no se fusionó con `ape-2026-0001/`, que es la verificación de Isaac para
este programa y es otra cosa.

Vive en `isc/` para conservar el guiño al subdominio original.

### Por qué el workflow no las pisa

El paso "Publicar paginas de verificacion" hace `cp -r output/verify/* .`, y
`output/verify/` contiene **solo directorios** `{codigo}/` — nunca archivos
sueltos. Así que no puede sobrescribir `index.html` ni `404.html`.

`isc/` tampoco corre riesgo: solo lo pisaría un alumno cuyo código slugificara
exactamente a `isc`, imposible con el formato `APE-AAAA-NNNN`.
