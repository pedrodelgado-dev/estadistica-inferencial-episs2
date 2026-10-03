// Coordinación de formularios y peticiones. Las fórmulas están en episs/services/.
import { $, busy, showError } from './dom.js';
import { state } from './config.js';
import { renderForm } from './forms.js';
import { gather } from './payload.js';
import { calculate } from './api.js';
import { resetResults, showResults } from './results.js';
import { initNavigation, initShell } from './navigation.js';

let pending;

function invalidate() {
  pending?.abort();
  pending = null;
  busy(false);
  resetResults();
}

async function solve() {
  invalidate();
  const controller = new AbortController();
  pending = controller;
  busy(true);
  $('headline').textContent = 'Calculando…';
  const timeout = setTimeout(() => controller.abort(), 30000);
  try {
    const payload = await calculate(state.mode, gather(), controller.signal);
    if (pending === controller) showResults(payload.view);
  } catch (error) {
    if (pending !== controller) return;
    $('headline').textContent = 'Revisa los datos';
    $('conclusion').textContent = 'No se ha calculado un resultado con estos datos.';
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
$('form').addEventListener('input', invalidate);
$('form').addEventListener('change', invalidate);
$('clear').addEventListener('click', () => {
  invalidate();
  document.querySelectorAll('#fields input, #fields textarea').forEach((input) => {
    input.value = '';
  });
  document.querySelector('#fields input, #fields textarea')?.focus();
});
$('example').addEventListener('click', () => {
  invalidate();
  renderForm();
  if ($('raw')) $('raw').value = '295; 299; 301; 298; 300; 301; 305; 300';
  solve();
});
$('print').addEventListener('click', () => window.print());

initShell();
initNavigation((page, tool) => {
  invalidate();
  if (tool) {
    state.mode = page;
    renderForm();
  }
});
