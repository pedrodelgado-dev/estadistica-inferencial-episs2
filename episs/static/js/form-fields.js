// Controles reutilizables. Los títulos y ejemplos provienen de la configuración.
export const field = (id, title, value = '') => `
  <label for="${id}">
    ${title}
    <input id="${id}" inputmode="decimal" value="${value}" autocomplete="off">
  </label>
`;

export const area = (id, title, value = '', placeholder = '') => `
  <label for="${id}">
    ${title}
    <textarea id="${id}" spellcheck="false" placeholder="${placeholder}">${value}</textarea>
  </label>
`;

export const select = (id, title, options, value) => `
  <label for="${id}">
    ${title}
    <select id="${id}">
      ${options
        .map(
          ([key, text]) => `
        <option value="${key}" ${key === value ? 'selected' : ''}>${text}</option>
      `,
        )
        .join('')}
    </select>
  </label>
`;

export const row = (...fields) => `<div class="row">${fields.join('')}</div>`;
export const hint = (text) => `<p class="small">${text}</p>`;

export const confidence = () =>
  select(
    'confidence',
    'Nivel de confianza',
    [
      ['0.90', '90 % (α = 0,10)'],
      ['0.95', '95 % (α = 0,05)'],
      ['0.99', '99 % (α = 0,01)'],
    ],
    '0.95',
  );

export const tail = () =>
  select(
    'tail',
    'Hipótesis alternativa H₁',
    [
      ['two', 'Diferente (≠) · bilateral'],
      ['left', 'Menor (<) · izquierda'],
      ['right', 'Mayor (>) · derecha'],
    ],
    'two',
  );
