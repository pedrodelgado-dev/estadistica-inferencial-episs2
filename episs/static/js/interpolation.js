// Formulario de interpolación: enviar cinco entradas y mostrar la respuesta Python.
import { $, busy, showError, showSteps } from './dom.js';
import { calculate } from './api.js';
import { drawChart } from './charts.js';
import { initShell } from './navigation.js';

const ids = ['x1', 'y1', 'x2', 'y2', 'x'];
let pending;

function reset(message = 'Datos modificados. Pulsa CALCULAR.') {
  pending?.abort();
  pending = null;
  busy(false);
  $('error').hidden = true;
  $('value').textContent = 'y = —';
  $('kind').textContent = 'RESULTADO';
  $('caption').textContent = message;
  $('chart').replaceChildren();
  $('chart').setAttribute('aria-label', 'Sin resultado calculado');
  $('steps').replaceChildren();
  $('graphNote').textContent = 'Calcula un resultado para ver la recta.';
}

async function solve() {
  reset('Calculando…');
  const controller = new AbortController();
  pending = controller;
  busy(true);
  const timeout = setTimeout(() => controller.abort(), 30000);
  try {
    const data = Object.fromEntries(ids.map((id) => [id, $(id).value]));
    const payload = await calculate('interpolation', data, controller.signal);
    if (pending !== controller) return;
    $('kind').textContent = payload.view.label;
    $('value').textContent = payload.view.headline;
    $('caption').textContent = payload.view.conclusion;
    showSteps(payload.view.steps);
    drawChart(payload.view.chart);
  } catch (error) {
    if (pending !== controller) return;
    $('caption').textContent = 'Revisa los datos e inténtalo de nuevo.';
    showError(
      error.name === 'AbortError'
        ? 'El cálculo tardó demasiado. Inténtalo nuevamente.'
        : error.message,
    );
  } finally {
    clearTimeout(timeout);
    if (pending === controller) {
      pending = null;
      busy(false);
    }
  }
}

$('form').addEventListener('submit', (event) => {
  event.preventDefault();
  solve();
});
$('form').addEventListener('input', () => reset());
$('example').addEventListener('click', () => {
  ['10', '100', '20', '200', '15'].forEach((value, index) => {
    $(ids[index]).value = value;
  });
  solve();
});
$('clear').addEventListener('click', () => {
  ids.forEach((id) => {
    $(id).value = '';
  });
  reset('Ingresa tus puntos para comenzar.');
  $('x1').focus();
});
initShell();
document.querySelector('a[href="/interpolacion.html"]').setAttribute('aria-current', 'page');
solve();
