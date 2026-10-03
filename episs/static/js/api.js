// Único acceso a los cálculos: peticiones al servidor Python de la misma aplicación.
export async function calculate(tool, data, signal) {
  let response;
  try {
    response = await fetch(`/api/${tool}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
      signal,
    });
  } catch (error) {
    if (error.name === 'AbortError') throw error;
    throw new Error('No se pudo conectar con el servidor. Comprueba que Python siga ejecutándose.');
  }

  let payload;
  try {
    payload = await response.json();
  } catch {
    throw new Error(
      'El servidor no devolvió un resultado válido. Abre la aplicación desde su dirección HTTP.',
    );
  }
  if (!response.ok || !payload.ok) {
    throw new Error(payload.error || 'No se pudo completar el cálculo.');
  }
  return payload;
}
