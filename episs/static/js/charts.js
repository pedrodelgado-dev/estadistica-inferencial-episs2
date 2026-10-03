// Dibujar los elementos SVG preparados en Python; aquí no se evalúan distribuciones.
import { $ } from './dom.js';

const tags = new Set(['line', 'path', 'text', 'circle', 'rect']);
const attributes = new Set([
  'x',
  'y',
  'x1',
  'y1',
  'x2',
  'y2',
  'cx',
  'cy',
  'r',
  'rx',
  'width',
  'height',
  'd',
  'fill',
  'stroke',
  'stroke-width',
  'stroke-dasharray',
  'text-anchor',
  'font-size',
]);

export function drawChart(chart) {
  const target = $('chart');
  target.replaceChildren();
  for (const item of chart.elements) {
    if (!tags.has(item.tag)) continue;
    const element = document.createElementNS('http://www.w3.org/2000/svg', item.tag);
    for (const [key, value] of Object.entries(item.attrs)) {
      if (attributes.has(key)) element.setAttribute(key, String(value));
    }
    if (item.text !== null) element.textContent = item.text;
    target.append(element);
  }
  target.setAttribute('aria-label', chart.label);
  $('graphNote').textContent = chart.note;
}
