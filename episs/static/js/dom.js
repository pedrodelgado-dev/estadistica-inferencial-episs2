// Utilidades de DOM compartidas; crear contenido con textContent evita inyectar HTML.
export const $ = (id) => document.getElementById(id);

export function showSteps(items) {
  $('steps').replaceChildren(
    ...items.map(([title, body]) => {
      const li = document.createElement('li');
      const strong = document.createElement('strong');
      strong.textContent = title;
      li.append(strong, document.createTextNode(body));
      return li;
    }),
  );
}

export function showError(message) {
  $('error').textContent = message;
  $('error').hidden = false;
}

export function busy(active) {
  const form = $('form');
  const button = form.querySelector('[type="submit"]');
  form.setAttribute('aria-busy', String(active));
  button.disabled = active;
  button.textContent = active ? 'CALCULANDO…' : 'CALCULAR ↗';
}
