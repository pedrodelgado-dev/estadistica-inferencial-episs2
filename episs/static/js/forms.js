// Un constructor por herramienta; sin operaciones estadísticas en JavaScript.
import { state, modules } from './config.js';
import { $ } from './dom.js';
import { field, select, area, row, hint, confidence, tail } from './form-fields.js';

function oneSampleForm() {
  const { mode, method, source } = state;
  const fields = [
    select(
      'method',
      'Método',
      [
        ['t', 'Media · t (σ desconocida)'],
        ['z', 'Media · Z (σ conocida)'],
        ['proportion', 'Proporción · Z / IC Wilson'],
      ],
      method,
    ),
  ];
  if (method === 'proportion') {
    fields.push(row(field('success', 'Número de éxitos', '60'), field('n', 'Tamaño n', '100')));
  } else {
    fields.push(
      select(
        'source',
        'Entrada de datos',
        [
          ['summary', 'Datos resumidos'],
          ['raw', 'Lista de observaciones'],
        ],
        source,
      ),
    );
    if (source === 'raw') {
      fields.push(
        area('raw', 'Observaciones', '', '295; 299; 301; 298; 300; 301; 305; 300'),
        hint(
          'Separa por punto y coma, espacios o saltos de línea. Usa coma o punto para decimales. El tamaño n se cuenta automáticamente.',
        ),
      );
    } else {
      fields.push(row(field('mean', 'Media x̄', '52'), field('n', 'Tamaño n', '25')));
    }
    if (source === 'summary' || method === 'z') {
      fields.push(
        field(
          'sd',
          method === 't' ? 'Desviación muestral s' : 'Desviación poblacional σ',
          method === 't' ? '5' : '15',
        ),
      );
    }
    if (method === 'z')
      fields.push(hint('σ debe ser conocida; no sustituyas aquí una desviación muestral.'));
  }
  if (mode === 'hypothesis') {
    fields.push(
      field(
        'nullValue',
        method === 'proportion' ? 'Valor hipotético p₀ (0 a 1)' : 'Valor hipotético μ₀',
        method === 'proportion' ? '0.5' : '50',
      ),
      tail(),
    );
  }
  fields.push(
    confidence(),
    hint(
      'Se analiza una sola muestra. Ingresa valores numéricos; no pegues el enunciado completo.',
    ),
  );
  return fields.join('');
}

function sampleForm() {
  const { parameter, finite } = state;
  const fields = [
    select(
      'parameter',
      '¿Qué deseas estimar?',
      [
        ['proportion', 'Una proporción'],
        ['mean', 'Una media'],
      ],
      parameter,
    ),
    confidence(),
    select(
      'finite',
      'Población',
      [
        ['no', 'Grande o tamaño desconocido'],
        ['yes', 'Finita: conozco N'],
      ],
      finite ? 'yes' : 'no',
    ),
  ];
  if (finite) fields.push(field('population', 'Tamaño de la población N', '1000'));
  if (parameter === 'proportion') {
    fields.push(field('p', 'Proporción prevista p (0 a 1)', '0.5'));
    fields.push(field('margin', 'Margen de error E (0,05 = 5 %)', '0.05'));
  } else {
    fields.push(field('sd', 'Desviación prevista σ', '15'));
    fields.push(field('margin', 'Margen de error E (unidades)', '3'));
  }
  fields.push(
    hint(
      'Tamaño para estimar con un margen de error, no para potencia estadística. Si desconoces p, utiliza 0,5. Supone muestreo aleatorio simple y respuesta completa.',
    ),
  );
  return fields.join('');
}

function varianceForm() {
  const type = state.advancedType.variance;
  const fields = [
    select(
      'advancedType',
      'Contraste',
      [
        ['chi', 'Una varianza · χ²'],
        ['f', 'Dos varianzas · F'],
      ],
      type,
    ),
    field('n1', 'Tamaño de muestra n₁', '25'),
    field('s1', 'Desviación muestral s₁', '6'),
  ];
  if (type === 'chi') fields.push(field('v0', 'Varianza hipotética σ₀² (no desviación)', '25'));
  else
    fields.push(
      field('n2', 'Tamaño de muestra n₂', '30'),
      field('s2', 'Desviación muestral s₂', '4'),
    );
  fields.push(tail(), confidence());
  return fields.join('');
}

function compareForm() {
  const type = state.advancedType.compare;
  const fields = [
    select(
      'advancedType',
      'Diseño y método',
      [
        ['welch', 'Independientes · t de Welch'],
        ['pooled', 'Independientes · varianzas iguales'],
        ['paired', 'Relacionadas · t de diferencias'],
      ],
      type,
    ),
  ];
  if (type === 'paired') {
    fields.push(
      area('listA', 'Grupo A · después', '78; 85; 82; 90; 76; 88'),
      area('listB', 'Grupo B · antes (mismo orden)', '72; 80; 79; 82; 74; 81'),
      hint('Cada posición debe corresponder a la misma persona. Separa valores con punto y coma.'),
    );
  } else {
    fields.push(
      '<div class="group-label">GRUPO A · p. ej., backend</div>',
      row(
        field('mean1', 'Media A', '3200'),
        field('s1', 'Desviación A', '450'),
        field('n1', 'Tamaño A', '30'),
      ),
      '<div class="group-label">GRUPO B · p. ej., frontend</div>',
      row(
        field('mean2', 'Media B', '2900'),
        field('s2', 'Desviación B', '400'),
        field('n2', 'Tamaño B', '28'),
      ),
    );
  }
  fields.push(field('delta', 'Diferencia hipotética μA − μB', '0'), tail(), confidence());
  return fields.join('');
}

function powerForm() {
  return [
    hint(
      'Prueba Z de una media con σ poblacional conocida. Planificación bajo un efecto específico.',
    ),
    field('sd', 'Desviación poblacional σ', '15'),
    field('delta', 'Efecto real μ₁ − μ₀ (con signo)', '5'),
    field('n', 'Tamaño actual n', '50'),
    field('target', 'Potencia objetivo (0 a 1)', '0.8'),
    tail(),
    confidence(),
  ].join('');
}

function samplingForm() {
  const type = state.advancedType.sampling;
  const fields = [
    select(
      'advancedType',
      'Método de selección',
      [
        ['mas', 'Aleatorio simple · MAS'],
        ['systematic', 'Sistemático'],
        ['stratified', 'Estratificado'],
      ],
      type,
    ),
  ];
  if (type === 'stratified') {
    fields.push(
      select(
        'allocation',
        'Asignación',
        [
          ['proportional', 'Proporcional a Nₕ'],
          ['neyman', 'Neyman · Nₕ × sₕ (costos iguales)'],
        ],
        'proportional',
      ),
    );
  }
  const example = [
    'E01;Backend;3200',
    'E02;Backend;3500',
    'E03;Backend;2900',
    'E04;Backend;3100',
    'E05;Frontend;2800',
    'E06;Frontend;3000',
    'E07;Frontend;2700',
    'E08;Frontend;3200',
    'E09;Soporte;2200',
    'E10;Soporte;2400',
    'E11;Soporte;2300',
    'E12;Soporte;2500',
  ].join('\n');
  fields.push(
    area('records', 'Base de datos · un registro por línea', example),
    hint(
      'Formato sin encabezado: identificador;estrato;valor. Solo el identificador es obligatorio para MAS y sistemático. Neyman requiere valores numéricos y estratos. Máximo 100 000 registros.',
    ),
    row(field('n', 'Registros a seleccionar', '6'), field('seed', 'Semilla reproducible', '2026')),
  );
  return fields.join('');
}

const builders = {
  hypothesis: oneSampleForm,
  interval: oneSampleForm,
  sample: sampleForm,
  variance: varianceForm,
  compare: compareForm,
  power: powerForm,
  sampling: samplingForm,
};

export function renderForm() {
  const [title, description] = modules[state.mode];
  $('pageTitle').textContent = title;
  $('pageDescription').textContent = description;
  $('formTitle').textContent =
    state.mode === 'sample' ? 'Planifica tu muestra' : 'Datos del análisis';
  $('fields').innerHTML = builders[state.mode]();
  for (const id of ['method', 'source', 'parameter', 'finite', 'advancedType']) {
    $(id)?.addEventListener('change', () => {
      if (id === 'advancedType') state.advancedType[state.mode] = $(id).value;
      else state[id] = id === 'finite' ? $(id).value === 'yes' : $(id).value;
      renderForm();
    });
  }
}
