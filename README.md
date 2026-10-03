# Estadística Inferencial — EPISS / UNAJ

Aplicación web educativa reorganizada en Python, HTML, CSS y módulos JavaScript.
Los cálculos se ejecutan en **Python**. Flask sirve las páginas y la API; SciPy
proporciona las distribuciones normal, t de Student, χ² y F.

**Docente:** Palaco Charaja Edgar Whashigton.  
**Desarrolladores:** Mamani Delgado Pedro y Jove Benites Danny.  
**Institución:** Universidad Nacional de Juliaca, Escuela Profesional de
Ingeniería de Software y Sistemas.  
**Curso:** Estadística Inferencial.

## Ejecutar en tu computadora

Requiere Python 3.10 o posterior e Internet para instalar dependencias.
Abre una terminal dentro de la carpeta que contiene `run.py`.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run.py
```

### Windows PowerShell

No hace falta activar el entorno:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run.py
```

Abre **http://127.0.0.1:5000**. Detén el servidor con `Ctrl+C`.
Si el puerto está ocupado, en macOS/Linux usa `PORT=5001 python run.py`;
en PowerShell, `$env:PORT="5001"` antes de ejecutar `run.py`.

**No abras los HTML directamente ni uses Live Server:** los formularios necesitan
la API Python. Las plantillas incluyen bloques compartidos que Flask ensambla.

## Organización de los archivos

| Archivo o carpeta | Responsabilidad |
|---|---|
| `run.py` | Iniciar la aplicación local; exponer `app` para producción. |
| `episs/__init__.py` | Configuración, registro de rutas y errores HTTP. |
| `episs/routes/pages.py` | Servir inicio e interpolación. |
| `episs/routes/api.py` | Recibir JSON, ejecutar el servicio y responder. |
| `episs/services/validation.py` | Validación numérica, listas y límites. |
| `episs/services/statistics.py` | Estadística descriptiva, Z/t, Wilson, intervalos y tamaño muestral. |
| `episs/services/comparisons.py` | χ², F, Welch, t combinada/relacionada y potencia Z. |
| `episs/services/sampling.py` | MAS, sistemático, estratificado, asignación y CSV. |
| `episs/services/interpolation.py` | Interpolación y extrapolación lineal. |
| `episs/presentation/results.py` | Interpretación, métricas y procedimiento educativo. |
| `episs/presentation/charts.py` | Densidades, escalas y elementos SVG calculados en Python. |
| `episs/presentation/formatting.py` | Formato de números en español. |
| `episs/templates/index.html` | Inicio, herramientas e Información, incluido el docente. |
| `episs/templates/interpolacion.html` | Formulario y presentación de interpolación. |
| `episs/templates/partials/` | Cabecera, menú y pie compartidos. |
| `episs/static/css/` | Estilos estadísticos e institucionales, con reglas en varias líneas. |
| `episs/static/img/` | Logotipo institucional original. |
| `episs/static/js/config.js` | Estado y títulos de las herramientas. |
| `episs/static/js/form-fields.js` | Constructores de controles reutilizables. |
| `episs/static/js/forms.js` | Un constructor de formulario por herramienta. |
| `episs/static/js/payload.js` | Recoger entradas sin calcular ni convertir observaciones. |
| `episs/static/js/api.js` | Enviar peticiones a Python y manejar errores de conexión. |
| `episs/static/js/charts.js` | Dibujar los elementos SVG recibidos. |
| `episs/static/js/results.js` | Mostrar resultados y descargar el CSV recibido. |
| `episs/static/js/navigation.js` | Menú, fragmentos y accesibilidad. |
| `episs/static/js/app.js` | Coordinar la página principal y cancelar respuestas obsoletas. |
| `episs/static/js/interpolation.js` | Coordinar el formulario de interpolación. |
| `tests/` | Pruebas de regresión, entradas y contratos de la API. |

Las fórmulas antiguas de `estadistica.js`, `avanzado.js` y `app.js` ya no están en
la interfaz. JavaScript se utiliza para interacción, navegación, peticiones y
dibujo; Python calcula también la media, desviación, valores p, cuantiles,
intervalos, potencia, selecciones aleatorias, porcentajes, CSV y los datos de
los gráficos.

## Flujo de un cálculo

1. El formulario recoge las entradas como texto, aceptando coma decimal.
2. `api.js` envía un `POST` a la herramienta correspondiente.
3. `routes/api.py` llama a un servicio de `services/`.
4. Python valida y calcula; `presentation/` construye mensajes y gráficos.
5. La interfaz muestra la respuesta. Cambiar entradas, limpiar o navegar cancela
   la petición pendiente para evitar presentar un resultado desactualizado.

## Herramientas y API

| Ruta POST | Funciones |
|---|---|
| `/api/hypothesis` | Una media Z/t o una proporción Z; colas izquierda, derecha y bilateral. |
| `/api/interval` | Intervalos bilaterales Z/t o Wilson. |
| `/api/sample` | Tamaño para media/proporción; corrección finita opcional. |
| `/api/variance` | Una varianza χ² o razón de varianzas F. |
| `/api/compare` | Welch, varianza combinada y pares alineados. |
| `/api/power` | Potencia Z, β y menor n que alcanza el objetivo. |
| `/api/sampling` | MAS, sistemático y estratificado proporcional/Neyman. |
| `/api/interpolation` | Interpolación/extrapolación a partir de dos puntos. |

`GET /api/health` informa si el servidor responde. Ejemplo:

```bash
curl http://127.0.0.1:5000/api/hypothesis \
  -H 'Content-Type: application/json' \
  -d '{"method":"t","confidence":0.95,"tail":"two","n":25,"mean":52,"sd":5,"nullValue":50}'
```

La respuesta incluye `ok`, `result` con resultados numéricos y `view` con los
elementos que muestra la interfaz. Los errores de datos devuelven HTTP 422
con `ok: false` y un mensaje. JSON inválido devuelve 400; una herramienta
inexistente, 404. Los límites ilimitados se representan con `null` en JSON.

## Muestreo y datos

Pega los registros sin encabezado, uno por línea:

```text
E01;Backend;3200
E02;Backend;3500
E03;Frontend;2800
E04;Frontend;3000
```

MAS y sistemático solo necesitan identificadores. Estratificado necesita
estratos; Neyman necesita además valores numéricos. Admite hasta 100 000 registros,
sin identificadores repetidos. La misma base, orden, método y semilla reproducen
la selección. Mulberry32 y Fisher–Yates se trasladaron a Python para conservar
compatibilidad con las selecciones anteriores; no son algoritmos criptográficos.

Los datos se envían al servidor que ejecuta esta aplicación para calcular y no
se guardan en una base de datos. Si la ejecutas localmente, el servidor está en
tu computadora; si la publicas, los procesa ese servidor. No hay cuentas ni
historial persistente. No se usan servicios de cálculo externos.

## Supuestos y límites

- Muestras aleatorias e independencia; normalidad aproximada cuando corresponda.
- Las pruebas χ² y F de varianzas requieren poblaciones normales y son sensibles
  a desviaciones de ese supuesto. No son ANOVA ni pruebas de contingencia.
- La comparación combinada supone varianzas iguales; Welch es una alternativa
  si no puedes justificar esa igualdad.
- Si `n·p₀` o `n·(1−p₀)` es menor que 10, la prueba de proporción advierte que
  la aproximación Z no permite una conclusión definitiva. No se añadió una
  prueba binomial exacta.
- Los intervalos son bilaterales, incluso cuando complementan una prueba unilateral.
- No rechazar H₀ no demuestra que sea verdadera.
- El tamaño para precisión no incluye potencia, no respuesta ni efecto de diseño.
- La potencia implementada es para una media con σ conocida, no para todas las pruebas.
- El sistemático depende del orden de entrada; revisar periodicidades.
- Neyman supone costos iguales. No se calculan estimadores ponderados ni errores
  estándar de diseños complejos.
- La aplicación no interpreta automáticamente enunciados escritos.
- Inferencia: hasta 1 000 000 observaciones en datos resumidos; listas de 2 a
  10 000 observaciones. Varianzas: hasta 100 000 por grupo.
- Se rechazan valores no finitos, escalas numéricas imposibles y peticiones
  superiores a 20 MB. Los cálculos usan punto flotante.

## Verificación y mantenimiento

Instala las herramientas de desarrollo y ejecuta:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
ruff check .
ruff format --check .
```

La migración incluye 120 casos de referencia numérica de la versión JavaScript
en `tests/legacy_cases.json`, además de pruebas de entradas, API, interpolación,
CSV, potencia y páginas. No es necesario Node para ejecutar las pruebas Python.
Los casos de regresión permiten tolerancias numéricas pequeñas porque SciPy
reemplaza las aproximaciones manuales anteriores.

Verificación realizada: **142 pruebas Python aprobadas**, 19 combinaciones de
formularios en navegador, listas con coma decimal, interpolación/extrapolación,
limpieza de errores, descarga CSV y navegación. Revisión en escritorio de
1440 px y móvil de 390 px, sin errores JavaScript ni desbordamiento horizontal.
Entorno comprobado: Python 3.12.14, Flask 3.1.3, SciPy 1.17.0 y NumPy 2.3.5.

Para modificar una fórmula, edita `episs/services/`. Para modificar su explicación,
edita `episs/presentation/results.py`. Para modificar la pestaña Información,
edita `episs/templates/index.html`. Los títulos y ejemplos de formularios están
en `episs/static/js/forms.js`. `.editorconfig` establece espacios y UTF-8.

## Publicación

Esta versión requiere un proceso Python activo. El anterior `netlify.toml` para
publicación estática se retiró: subir solo HTML/CSS/JS no ejecuta esta API.
Elige un alojamiento que ejecute aplicaciones Python/WSGI.

Configuración habitual para un servidor Linux:

```bash
python -m pip install -r requirements.txt
gunicorn run:app --bind 0.0.0.0:8000
```

Usa el puerto configurado por tu proveedor. `run.py` es para desarrollo local;
el comando Gunicorn es para servir la aplicación en producción. Los cambios de
este ZIP no se publican automáticamente ni modifican GitHub por sí mismos.

## Documentación y referencias

- Flask: https://flask.palletsprojects.com/en/stable/quickstart/
- Despliegue Flask: https://flask.palletsprojects.com/en/stable/deploying/
- SciPy Stats: https://docs.scipy.org/doc/scipy/reference/stats.html
- NIST, pruebas de una media: https://www.itl.nist.gov/div898/handbook/prc/section2/prc22.htm
- NIST, Wilson: https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm
- Penn State, tamaño de muestra: https://online.stat.psu.edu/stat506/Lesson02
