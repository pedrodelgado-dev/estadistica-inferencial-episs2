// Configuración y estado de los formularios. No contiene fórmulas.
export const modules = {
  sampling: ['Selección de muestras', 'Muestreo aleatorio simple, sistemático y estratificado.'],
  sample: ['Tamaño de muestra', 'Tamaño para estimar una media o proporción.'],
  hypothesis: ['Pruebas de hipótesis', 'Contrasta una media o una proporción con Z y t.'],
  compare: ['Comparación de medias', 'Pruebas para dos medias independientes o relacionadas.'],
};

export const state = {
  mode: 'hypothesis',
  method: 't',
  source: 'summary',
  parameter: 'proportion',
  finite: false,
  samplingSource: 'summary',
  advancedType: {
    compare: 'welch',
    sampling: 'mas',
  },
};
