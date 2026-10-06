<div align="center">

<img src="episs/static/img/logo-unaj.svg" alt="Logo de la Universidad Nacional de Juliaca" width="130">

# Estadística Inferencial — EPISS / UNAJ

**Herramientas estadísticas para aprender, calcular e interpretar resultados.**

Universidad Nacional de Juliaca  
Facultad de Ciencias de Ingenierías  
Escuela Profesional de Ingeniería de Software y Sistemas

![Python](https://img.shields.io/badge/Python-3.10%2B-1e3f67?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1%2B-1e3f67?logo=flask&logoColor=white)
![SciPy](https://img.shields.io/badge/SciPy-Cálculo_estadístico-e27c1f)
![Proyecto académico](https://img.shields.io/badge/UNAJ-Proyecto_académico-e27c1f)

</div>

---

## Presentación

Aplicación web educativa del curso **Estadística Inferencial**. Reúne pruebas de hipótesis, intervalos de confianza, tamaño de muestra, muestreo e interpolación lineal, con procedimientos, interpretaciones y gráficos para acompañar el aprendizaje.

Los cálculos se ejecutan en **Python con SciPy y NumPy**. **Flask** sirve las páginas y la API; **HTML, CSS y JavaScript** se encargan de la interfaz y la interacción.

| Información académica | Detalle |
|---|---|
| Institución | Universidad Nacional de Juliaca — UNAJ |
| Escuela profesional | Ingeniería de Software y Sistemas |
| Curso | Estadística Inferencial |
| Docente | Palaco Charaja Edgar Whashigton |
| Desarrolladores | Mamani Delgado Pedro · Jove Benites Danny Rodrigo |

## Contenido

- [Herramientas disponibles](#herramientas-disponibles)
- [Instalación y ejecución](#instalación-y-ejecución)
- [Volver a abrir y cerrar la aplicación](#volver-a-abrir-y-cerrar-la-aplicación)
- [Solución de problemas frecuentes](#solución-de-problemas-frecuentes)
- [Organización de los archivos](#organización-de-los-archivos)
- [Herramientas y API](#herramientas-y-api)
- [Muestreo y datos](#muestreo-y-datos)
- [Supuestos y límites](#supuestos-y-límites)
- [Verificación y mantenimiento](#verificación-y-mantenimiento)
- [Publicación](#publicación)
- [Documentación y referencias](#documentación-y-referencias)

## Herramientas disponibles

| Herramienta | Qué permite calcular |
|---|---|
| Pruebas de hipótesis | Una media con Z o t de Student; una proporción con Z; alternativas izquierda, derecha y bilateral. |
| Intervalos de confianza | Intervalos bilaterales para una media con Z/t y una proporción con Wilson. |
| Tamaño de muestra | Tamaño para estimar una media o proporción, con corrección por población finita opcional. |
| Pruebas de varianzas | Una varianza con χ² o comparación de dos varianzas con F. |
| Comparación de medias | Pruebas de Welch, varianza combinada y muestras relacionadas. |
| Potencia estadística | Potencia Z para una media con σ conocida, error β y tamaño necesario para una potencia objetivo. |
| Muestreo | Aleatorio simple, sistemático y estratificado con asignación proporcional o de Neyman; descarga CSV. |
| Interpolación lineal | Interpolación y extrapolación a partir de dos puntos. |

La interfaz presenta resultados numéricos, explicaciones del procedimiento y gráficos según la herramienta elegida. Consulta los [supuestos y límites](#supuestos-y-límites) antes de interpretar un resultado.

## Instalación y ejecución

### Requisitos

- **Python 3.10 o posterior**, con `pip`.
- **Git**, si vas a clonar el repositorio. También puedes descargarlo mediante **Code → Download ZIP** y extraerlo.
- Conexión a Internet para instalar las dependencias.
- Un navegador web.

### 1. Descargar el proyecto

En PowerShell, CMD o una terminal:

```bash
git clone https://github.com/pedrodelgado-dev/estadistica-inferencial-episs2.git
cd estadistica-inferencial-episs2
```

**Si ya lo descargaste, omite la clonación** y entra a la carpeta que contiene `run.py` y `requirements.txt`.

Por ejemplo, si guardaste el proyecto en `D:\Estadistica\proyecto`:

**PowerShell:**

```powershell
cd D:\Estadistica\proyecto
dir
```

**CMD:**

```cmd
cd /d D:\Estadistica\proyecto
dir
```

Ajusta la ruta a tu carpeta real. Si `dir` no muestra `run.py` y `requirements.txt`, todavía no estás en la raíz del proyecto.

### 2. Crear el entorno e instalar dependencias

**Windows — PowerShell:**

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run.py
```

**Windows — CMD:**

```cmd
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe run.py
```

Estos comandos usan directamente el Python del entorno virtual; **no necesitas activar el entorno ni cambiar la política de ejecución de PowerShell**.

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run.py
```

### 3. Abrir la página

Con el servidor ejecutándose, abre:

**[http://127.0.0.1:5000](http://127.0.0.1:5000)**

Esta dirección funciona en la computadora donde iniciaste la aplicación. Mantén abierta la terminal mientras la usas.

> La aplicación necesita su servidor Python. Abrir los HTML directamente, usar Live Server o subir únicamente los archivos estáticos no ejecuta los cálculos de la API.

## Volver a abrir y cerrar la aplicación

Después de la primera instalación, entra a la carpeta del proyecto y ejecuta solamente:

```powershell
.\.venv\Scripts\python.exe run.py
```

El mismo comando funciona en PowerShell y CMD. En macOS/Linux puedes usar `.venv/bin/python run.py`.

Para detener el servidor, vuelve a la terminal y presiona **Ctrl + C**. Cerrar la pestaña del navegador no detiene el proceso Python.

## Solución de problemas frecuentes

| Problema | Solución |
|---|---|
| `Could not open requirements file` | Ejecuta `dir` y entra a la carpeta que contiene `requirements.txt`. Si descargaste un ZIP, comprueba si hay otra carpeta del proyecto dentro. |
| `git` no se reconoce | Instala Git y abre de nuevo la terminal, o descarga y extrae el ZIP desde GitHub. |
| `py` no se reconoce | Comprueba que Python esté instalado. Si `python --version` funciona, usa `python -m venv .venv`. |
| No se encuentra `.venv\Scripts\python.exe` | Crea el entorno con `py -m venv .venv` dentro de la carpeta del proyecto. |
| Falta Flask, SciPy u otro módulo | Instala `requirements.txt` usando el Python de `.venv`, como se indica arriba. |
| El navegador no puede conectarse | Comprueba que `run.py` siga ejecutándose y revisa los errores de la terminal. |
| El puerto 5000 está ocupado | Configura otro puerto antes de iniciar el servidor y abre la dirección correspondiente. |

**Cambiar de puerto en PowerShell:**

```powershell
$env:PORT="5001"
.\.venv\Scripts\python.exe run.py
```

**En CMD:**

```cmd
set PORT=5001
.venv\Scripts\python.exe run.py
```

**En macOS/Linux, con el entorno activado:**

```bash
PORT=5001 python run.py
```

Luego abre **[http://127.0.0.1:5001](http://127.0.0.1:5001)**.

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

Con el entorno virtual activado, instala las herramientas de desarrollo y ejecuta:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m ruff check .
python -m ruff format --check .
```

La suite incluye casos de referencia numérica de la versión JavaScript
en `tests/legacy_cases.json`, además de pruebas de entradas, API, interpolación,
CSV, potencia y páginas. No es necesario Node para ejecutar las pruebas Python.
Los casos de regresión permiten tolerancias numéricas pequeñas porque SciPy
reemplaza las aproximaciones manuales anteriores.

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
el comando Gunicorn es para servir la aplicación en producción. La ejecución local no publica la aplicación en Internet. GitHub Pages no ejecuta
este backend Python. El despliegue debe configurarse por separado.

## Documentación y referencias

- Flask: https://flask.palletsprojects.com/en/stable/quickstart/
- Despliegue Flask: https://flask.palletsprojects.com/en/stable/deploying/
- SciPy Stats: https://docs.scipy.org/doc/scipy/reference/stats.html
- NIST, pruebas de una media: https://www.itl.nist.gov/div898/handbook/prc/section2/prc22.htm
- NIST, Wilson: https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm
- Penn State, tamaño de muestra: https://online.stat.psu.edu/stat506/Lesson02

