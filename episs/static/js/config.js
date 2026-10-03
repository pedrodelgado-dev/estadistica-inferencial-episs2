// Configuración y estado de los formularios. No contiene fórmulas.
export const modules = {
  hypothesis: [
    'Prueba de hipótesis',
    'Contrasta una media o proporción con evidencia estadística.',
  ],
  sample: ['Tamaño de muestra', 'Planifica la precisión de tu estudio antes de recopilar datos.'],
  interval: ['Intervalos de confianza', 'Cuantifica la incertidumbre de tus estimaciones.'],
  variance: [
    'Análisis de varianzas',
    'Evalúa una varianza o compara la dispersión de dos poblaciones.',
  ],
  compare: ['Comparación de medias', 'Analiza grupos independientes o mediciones antes y después.'],
  power: [
    'Potencia y errores',
    'Explora el equilibrio entre tamaño, efecto y errores estadísticos.',
  ],
  sampling: [
    'Selección de muestras',
    'Selecciona registros de una base de datos de forma reproducible.',
  ],
};

export const state = {
  mode: 'hypothesis',
  method: 't',
  source: 'summary',
  parameter: 'proportion',
  finite: false,
  advancedType: {
    variance: 'chi',
    compare: 'welch',
    sampling: 'mas',
  },
};
