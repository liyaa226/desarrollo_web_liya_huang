const campoBusqueda = document.querySelector('#termino');
const estadoBusqueda = document.querySelector('#estado-busqueda');
const resultadosBusqueda = document.querySelector('#resultados-busqueda');
const notasUrl = document.querySelector('.buscador-container').dataset.notasUrl
  || 'http://localhost:8080/api/avistamientos/notas';
let temporizadorBusqueda;
let solicitudActiva = 0;
let promedios = new Map();

cargarPromedios();

campoBusqueda.addEventListener('input', () => {
  clearTimeout(temporizadorBusqueda);
  const termino = campoBusqueda.value.trim();
  solicitudActiva += 1;
  resultadosBusqueda.replaceChildren();

  if (!termino) {
    estadoBusqueda.textContent = '';
    return;
  }

  estadoBusqueda.textContent = 'Buscando…';
  temporizadorBusqueda = setTimeout(() => buscar(termino), 180);
});

resultadosBusqueda.addEventListener('click', event => {
  const boton = event.target.closest('button[data-action="evaluar"]');
  if (!boton) return;
  const formulario = boton.parentElement.querySelector('.evaluacion-avistamiento');
  formulario.hidden = !formulario.hidden;
  if (!formulario.hidden) formulario.querySelector('select').focus();
});

resultadosBusqueda.addEventListener('change', guardarNota);

async function buscar(termino) {
  const idSolicitud = ++solicitudActiva;
  try {
    const respuesta = await fetch(`/api/avistamientos/buscar?q=${encodeURIComponent(termino)}`);
    if (!respuesta.ok) throw new Error('No fue posible completar la búsqueda.');
    const avistamientos = await respuesta.json();
    if (idSolicitud !== solicitudActiva || campoBusqueda.value.trim() !== termino) return;

    resultadosBusqueda.replaceChildren();
    if (avistamientos.length === 0) {
      estadoBusqueda.textContent = 'No se encontraron avistamientos para tu búsqueda.';
      return;
    }

    estadoBusqueda.textContent = `${avistamientos.length} avistamiento(s) encontrado(s).`;
    avistamientos.forEach(avistamiento => {
      resultadosBusqueda.appendChild(crearResultado(avistamiento, termino));
    });
    actualizarNotasVisibles();
  } catch (error) {
    if (idSolicitud !== solicitudActiva) return;
    estadoBusqueda.textContent = 'Ocurrió un error al buscar avistamientos. Intenta nuevamente.';
  }
}

function crearResultado(avistamiento, termino) {
  const item = document.createElement('li');
  item.dataset.avistamientoId = avistamiento.id;
  item.append(
    document.createTextNode('Voluntario: '), resaltar(avistamiento.voluntario, termino),
    document.createTextNode(' · Día: '), resaltar(avistamiento.fecha, termino),
    document.createTextNode(' · Ave: '), resaltar(avistamiento.ave, termino),
    document.createTextNode(' · Comuna: '), resaltar(avistamiento.comuna, termino)
  );

  const promedio = document.createElement('span');
  promedio.className = 'resultado-nota';
  promedio.setAttribute('aria-live', 'polite');
  item.append(document.createTextNode(' · Nota: '), promedio);

  const boton = document.createElement('button');
  boton.type = 'button';
  boton.dataset.action = 'evaluar';
  boton.textContent = 'Evaluar';
  item.append(document.createTextNode(' '), boton, crearFormularioNota(avistamiento.id));
  return item;
}

function crearFormularioNota(id) {
  const formulario = document.createElement('div');
  formulario.className = 'evaluacion-avistamiento';
  formulario.hidden = true;

  const selector = document.createElement('select');
  selector.required = true;
  selector.setAttribute('aria-label', `Selecciona una nota para el avistamiento ${id}`);
  const opcionInicial = document.createElement('option');
  opcionInicial.value = '';
  opcionInicial.textContent = 'Selecciona (1-7)';
  selector.appendChild(opcionInicial);
  for (let valor = 1; valor <= 7; valor += 1) {
    const opcion = document.createElement('option');
    opcion.value = String(valor);
    opcion.textContent = String(valor);
    selector.appendChild(opcion);
  }

  const estado = document.createElement('p');
  estado.className = 'estado-evaluacion';
  estado.setAttribute('role', 'status');
  estado.setAttribute('aria-live', 'polite');
  formulario.append(selector, estado);
  return formulario;
}

async function guardarNota(event) {
  const selector = event.target.closest('.evaluacion-avistamiento select');
  if (!selector || !selector.value) return;

  const nota = Number(selector.value);
  const formulario = selector.closest('.evaluacion-avistamiento');
  const estado = formulario.querySelector('.estado-evaluacion');
  if (!Number.isInteger(nota) || nota < 1 || nota > 7) {
    estado.textContent = 'Selecciona una nota entera entre 1 y 7.';
    selector.value = '';
    return;
  }

  const item = selector.closest('li[data-avistamiento-id]');
  const id = item.dataset.avistamientoId;
  selector.disabled = true;
  estado.textContent = 'Guardando nota…';
  try {
    const url = `${notasUrl.replace(/\/notas\/?$/, '')}/${encodeURIComponent(id)}/notas`;
    const respuesta = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nota })
    });
    const resultado = await leerRespuesta(respuesta);
    promedios.set(String(resultado.avistamientoId), Number(resultado.promedio));
    actualizarNotasVisibles();
    estado.textContent = 'Nota guardada.';
    selector.value = '';
  } catch (error) {
    estado.textContent = `No se pudo guardar la nota: ${error.message}`;
    selector.value = '';
  } finally {
    selector.disabled = false;
  }
}

async function cargarPromedios() {
  try {
    const respuesta = await fetch(notasUrl);
    const datos = await leerRespuesta(respuesta);
    promedios = new Map(datos.map(item => [String(item.avistamientoId), Number(item.promedio)]));
    actualizarNotasVisibles();
  } catch {
    // Si la API no está disponible, los avistamientos siguen apareciendo con nota "-".
  }
}

function actualizarNotasVisibles() {
  resultadosBusqueda.querySelectorAll('li[data-avistamiento-id]').forEach(item => {
    const promedio = promedios.get(item.dataset.avistamientoId);
    item.querySelector('.resultado-nota').textContent =
      promedio === undefined ? '-' : promedio.toFixed(1);
  });
}

async function leerRespuesta(respuesta) {
  const texto = await respuesta.text();
  let datos;
  try {
    datos = texto ? JSON.parse(texto) : {};
  } catch {
    throw new Error(`respuesta inválida (HTTP ${respuesta.status})`);
  }
  if (!respuesta.ok) throw new Error(datos.error || `error HTTP ${respuesta.status}`);
  return datos;
}

function resaltar(texto, termino) {
  const fragmento = document.createDocumentFragment();
  const valor = String(texto ?? '');
  const inicio = valor.toLocaleLowerCase().indexOf(termino.toLocaleLowerCase());
  if (inicio < 0) {
    fragmento.appendChild(document.createTextNode(valor));
    return fragmento;
  }
  fragmento.appendChild(document.createTextNode(valor.slice(0, inicio)));
  const marca = document.createElement('mark');
  marca.textContent = valor.slice(inicio, inicio + termino.length);
  fragmento.appendChild(marca);
  fragmento.appendChild(document.createTextNode(valor.slice(inicio + termino.length)));
  return fragmento;
}
