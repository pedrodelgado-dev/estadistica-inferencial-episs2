# Calculadora de Estadística Inferencial · UNAJ / EPISS

con interpolación lineal conservada.
Docente: Palaco Charaja Edgar Whashigton.

## Ejecutar en Visual Studio Code

Abre esta carpeta en VS Code. Necesitas Python 3.10 o posterior.

```bash
python -m venv .venv
```

Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
source .venv/bin/activate
```

Instala las dependencias e inicia el servidor:

```bash
python -m pip install -r requirements.txt
python run.py
```

Abre http://127.0.0.1:5000. Las páginas requieren Flask; Live Server no ejecuta los cálculos Python.

## Orden del menú

Primero `1.pdf`: selección de muestras (sección 7.1), luego tamaño de muestra (7.2).
Después `Materialdepruebadehipotesis.pdf`: pruebas de una media y una proporción (6.2.1–6.2.2), luego comparación de medias independientes y relacionadas (6.2.3–6.2.4).
Finalmente, interpolación lineal. Inicio e Información permanecen disponibles.

Por solicitud, se eliminaron por completo Dos proporciones · Z e Intervalo de dos proporciones: formularios, navegación, rutas API, funciones y gráficos exclusivos. Se conserva la prueba Z de **una** proporción y el tamaño muestral para proporciones.

## Alcance

| Herramienta | Contenido | Referencia |
|---|---|---|
| Selección de muestras | Aleatorio simple, sistemático y estratificado proporcional / óptimo (Neyman, costos iguales). Exportación CSV. | 1.pdf, pp. 1–6 |
| Tamaño de muestra | Media y proporción, población finita o desconocida; redondeo hacia arriba. | 1.pdf, pp. 3–5 |
| Hipótesis de una muestra | Media Z con σ conocida; Z con s y n ≥ 30; t; proporción Z. Corrección opcional por población finita. | Hipótesis, pp. impresas 197–212 |
| Comparación de medias | Z con σ conocidas; Z con s y ambas n ≥ 30; t combinada; t de varianzas diferentes; t pareada. | Hipótesis, pp. 212–225 |
| Interpolación lineal | Dos puntos, procedimiento y gráfico. | Conservada por solicitud |

Se retiraron de la interfaz, API y servicios las pruebas de una varianza χ², razón de varianzas F, la planificación por potencia y los intervalos de una sola muestra (incluido Wilson). La teoría de errores tipo I y II permanece en la guía porque aparece en el material.

Los PDF también describen conglomerados y métodos no probabilísticos; no se han añadido nuevos selectores para esos métodos. La regresión solo aparece como introducción al final del PDF: no se añade una calculadora de regresión.

## Criterios de cálculo

### Ejemplo 7.2.3: totales por estrato

En **Selección de muestras → Estratificado → Totales por estrato**, ingresa:

```text
Públicos;6000
Privados parroquiales;3000
Privados no parroquiales;1000
```

Usa **Tamaño de la muestra n = 600** y pulsa **Calcular**. Se obtiene N = 10000
y muestras de **360, 180 y 60**. Estos datos ya están precargados como ejemplo.
Este modo calcula la afijación proporcional; no elige personas individuales.
Para seleccionar identificadores y exportar CSV, cambia a **Registros individuales**.
Las cuotas decimales se distribuyen por restos mayores para conservar el total n.

- Todos los cálculos y gráficos se generan en Python / SciPy; JavaScript recoge datos y presenta resultados.
- Para la comparación t con varianzas diferentes se redondean los grados de libertad al entero más cercano, como indica el material. Se usa la fórmula correcta con n₂−1; el PDF imprime n₂−2 en la p. 218.
- Las pruebas muestran «No se rechaza H₀», que no demuestra que H₀ sea verdadera.
- Z con s es la aproximación de muestras grandes utilizada en el material. Se valida n ≥ 30.
- La corrección de una muestra exige N > n para evitar un error estándar nulo.
- Se usan cuantiles y cálculos sin redondeos intermedios; pueden diferir de las aproximaciones o erratas del PDF. En el ejemplo de quejas (p. 212), Z es aproximadamente 3.88, no 5.
- En 1.pdf, α/2 para 95 % es 0.025. El ejemplo de proporciones en p. 5 mezcla un error anunciado de 3 % con 0.033: ingresa 0.03 para 3 %.

## Organización

- `episs/services/`: fórmulas, validación, muestreo e interpolación.
- `episs/presentation/`: pasos explicados y gráficos SVG.
- `episs/routes/api.py`: herramientas disponibles por API.
- `episs/templates/`: páginas, menú y guía.
- `episs/static/js/`: formularios y navegación.
- `tests/`: casos numéricos, validaciones y pruebas de regresión.

## Verificación

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
```
