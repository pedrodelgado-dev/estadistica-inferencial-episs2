// Mostrar mensajes, procedimientos y CSV recibidos desde Python.
import { $, showSteps } from './dom.js';
import { drawChart } from './charts.js';

export function resetResults() {
  $('error').hidden = true;
  $('headline').textContent = 'Listo para resolver';
  $('resultType').textContent = 'ANÁLISIS ESTADÍSTICO';
  $('conclusion').textContent = 'Revisa los datos y pulsa CALCULAR.';
  for (const id of ['metrics', 'steps', 'warnings', 'extra', 'chart']) {
    $(id).replaceChildren();
  }
  $('chart').setAttribute('aria-label', 'Sin resultado calculado');
  $('graphNote').textContent = 'El gráfico aparecerá al resolver el problema.';
}

function downloadFile(file) {
  const url = URL.createObjectURL(
    new Blob([file.content], {
      type: 'text/csv;charset=utf-8',
    }),
  );
  const link = document.createElement('a');
  link.href = url;
  link.download = file.filename;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export function showResults(view) {
  $('resultType').textContent = view.label;
  $('headline').textContent = view.headline;
  $('conclusion').textContent = view.conclusion;
  $('graphTitle').textContent = view.graphTitle;

  $('metrics').replaceChildren(
    ...view.metrics.map(([title, value]) => {
      const div = document.createElement('div');
      const label = document.createElement('small');
      const number = document.createElement('b');
      label.textContent = title;
      number.textContent = value;
      div.append(label, number);
      return div;
    }),
  );

  showSteps(view.steps);
  $('warnings').replaceChildren(
    ...view.warnings.map((message) => {
      const paragraph = document.createElement('p');
      paragraph.className = 'warning';
      paragraph.textContent = message;
      return paragraph;
    }),
  );
  drawChart(view.chart);

  if (view.preview) {
    const paragraph = document.createElement('p');
    paragraph.className = 'sample-preview';
    paragraph.textContent = view.preview;
    $('extra').append(paragraph);
  }
  if (view.download) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'secondary';
    button.textContent = 'Descargar muestra CSV';
    button.addEventListener('click', () => downloadFile(view.download));
    $('extra').append(button);
  }
}
