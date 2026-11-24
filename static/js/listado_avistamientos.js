document.addEventListener('DOMContentLoaded', init, false);

let table;
let sortCol;
let sortAsc = false;
const pageSize = 3;
let curPage = 1;
let avistamientos = [];
let staticUrl;
let notasUrl;

async function init() {
  table = document.querySelector('#tablaAvistamientos tbody');
  const main = document.querySelector('#tablaAvistamientos').closest('main');
  staticUrl = main.dataset.staticUrl;
  notasUrl = main.dataset.notasUrl;
  avistamientos = JSON.parse(document.querySelector('#datos-avistamientos').textContent);

  document.querySelector('#nextButton').addEventListener('click', nextPage);
  document.querySelector('#prevButton').addEventListener('click', previousPage);
  document.querySelectorAll('#tablaAvistamientos th[data-sort]').forEach(header => {
    header.addEventListener('click', sort);
  });
  table.addEventListener('click', mostrarFormularioNota);
  table.addEventListener('change', guardarNota);

  renderTable();
  await cargarPromedios();
}

function renderTable() {
  const start = (curPage - 1) * pageSize;
  const visibles = avistamientos.slice(start, start + pageSize);
  table.replaceChildren();

  visibles.forEach(avistamiento => {
    const fila = document.createElement('tr');
    fila.dataset.avistamientoId = avistamiento.id;
    agregarTexto(fila, avistamiento.ave);
    agregarTexto(fila, avistamiento.fecha);
    agregarTexto(fila, avistamiento.lugar);
    fila.appendChild(crearCeldaArchivo(avistamiento));

    const promedio = document.createElement('td');
    promedio.className = 'nota-promedio';
    promedio.textContent = '-';
    promedio.setAttribute('aria-live', 'polite');
    fila.appendChild(promedio);

    const evaluar = document.createElement('td');
    const boton = document.createElement('button');
    boton.type = 'button';
    boton.dataset.action = 'evaluar';
    boton.textContent = 'Evaluar';
    evaluar.appendChild(boton);
    evaluar.appendChild(crearFormularioNota(avistamiento.id));
    fila.appendChild(evaluar);

    const detalle = document.createElement('td');
    const enlace = document.createElement('a');
    enlace.href = `/avistamientos/${encodeURIComponent(avistamiento.id)}`;
    enlace.textContent = 'Ver detalle';
    detalle.appendChild(enlace);
    fila.appendChild(detalle);

    table.appendChild(fila);
  });
}

function agregarTexto(fila, valor) {
  const celda = document.createElement('td');
  celda.textContent = valor ?? '';
  fila.appendChild(celda);
}

function crearCeldaArchivo(avistamiento) {
  const celda = document.createElement('td');
  if (!avistamiento.archivo) return celda;

  const extension = avistamiento.archivo.split('.').pop().toLowerCase();
  const url = `${staticUrl}${avistamiento.archivo}`;
  if (['png', 'jpg', 'jpeg', 'gif'].includes(extension)) {
    const imagen = document.createElement('img');
    imagen.className = 'miniatura-avistamiento';
    imagen.src = url;
    imagen.alt = `Foto del avistamiento ${avistamiento.id}`;
    celda.appendChild(imagen);
  } else if (['mp4', 'webm', 'mov', 'avi', 'mkv', 'mpeg', 'mpg'].includes(extension)) {
    const enlace = document.createElement('a');
    enlace.href = url;
    enlace.textContent = 'Ver video';
    celda.appendChild(enlace);
  }
  return celda;
}

function crearFormularioNota(avistamientoId) {
  const formulario = document.createElement('div');
  formulario.className = 'form-nota';
  formulario.hidden = true;

  const selector = document.createElement('select');
  selector.name = 'nota';
  selector.required = true;
  selector.setAttribute('aria-label', `Selecciona una nota para el avistamiento ${avistamientoId}`);

  const inicial = document.createElement('option');
  inicial.value = '';
  inicial.textContent = 'Selecciona (1-7)';
  selector.appendChild(inicial);
  for (let nota = 1; nota <= 7; nota += 1) {
    const opcion = document.createElement('option');
    opcion.value = nota;
    opcion.textContent = nota;
    selector.appendChild(opcion);
  }

  const estado = document.createElement('p');
  estado.className = 'estado-nota';
  estado.setAttribute('role', 'status');
  estado.setAttribute('aria-live', 'polite');

  formulario.append(selector, estado);
  return formulario;
}

async function cargarPromedios() {
  const estado = document.querySelector('#estado-notas');
  estado.textContent = 'Cargando promedios...';
  try {
    const respuesta = await fetch(notasUrl);
    const datos = await leerRespuesta(respuesta);
    const promedios = new Map(
      datos.map(nota => [String(nota.avistamientoId), nota.promedio])
    );

    document.querySelectorAll('#tablaAvistamientos tbody tr').forEach(fila => {
      const promedio = promedios.get(fila.dataset.avistamientoId);
      if (promedio !== undefined) {
        fila.querySelector('.nota-promedio').textContent = Number(promedio).toFixed(1);
      }
    });
    estado.textContent = '';
  } catch (error) {
    estado.textContent = `No se pudieron cargar las notas: ${error.message}`;
  }
}

function mostrarFormularioNota(event) {
  const boton = event.target.closest('button[data-action="evaluar"]');
  if (!boton) return;

  const formulario = boton.parentElement.querySelector('.form-nota');
  formulario.hidden = !formulario.hidden;
  if (!formulario.hidden) {
    formulario.querySelector('select').focus();
  }
}

async function guardarNota(event) {
  const selector = event.target.closest('.form-nota select[name="nota"]');
  if (!selector || !selector.value) return;

  const formulario = selector.closest('.form-nota');
  const estado = formulario.querySelector('.estado-nota');
  const nota = Number(selector.value);
  if (!Number.isInteger(nota) || nota < 1 || nota > 7) {
    estado.textContent = 'Selecciona una nota entera entre 1 y 7.';
    return;
  }

  const id = formulario.closest('tr').dataset.avistamientoId;
  selector.disabled = true;
  estado.textContent = 'Guardando nota...';
  try {
    const respuesta = await fetch(`${notasUrl.replace(/\/notas$/, '')}/${encodeURIComponent(id)}/notas`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nota })
    });
    const resultado = await leerRespuesta(respuesta);
    formulario.closest('tr').querySelector('.nota-promedio').textContent =
      Number(resultado.promedio).toFixed(1);
    estado.textContent = `Nota guardada.`;
    selector.value = '';
  } catch (error) {
    estado.textContent = `No se pudo guardar la nota: ${error.message}`;
  } finally {
    selector.disabled = false;
  }
}

async function leerRespuesta(respuesta) {
  const texto = await respuesta.text();
  let datos;
  try {
    datos = texto ? JSON.parse(texto) : {};
  } catch {
    throw new Error(`respuesta inválida (HTTP ${respuesta.status})`);
  }
  if (!respuesta.ok) {
    throw new Error(datos.error || `error HTTP ${respuesta.status}`);
  }
  return datos;
}

function sort(event) {
  const columna = event.target.dataset.sort;
  if (!columna) return;
  if (sortCol === columna) sortAsc = !sortAsc;
  sortCol = columna;
  avistamientos.sort((a, b) => {
    if (a[sortCol] < b[sortCol]) return sortAsc ? 1 : -1;
    if (a[sortCol] > b[sortCol]) return sortAsc ? -1 : 1;
    return 0;
  });
  renderTable();
  cargarPromedios();
}

function previousPage() {
  if (curPage > 1) {
    curPage -= 1;
    renderTable();
    cargarPromedios();
  }
}

function nextPage() {
  if (curPage * pageSize < avistamientos.length) {
    curPage += 1;
    renderTable();
    cargarPromedios();
  }
}
