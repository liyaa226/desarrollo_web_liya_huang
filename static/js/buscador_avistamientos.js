const campoBusqueda = document.querySelector('#termino');
const estadoBusqueda = document.querySelector('#estado-busqueda');
const resultadosBusqueda = document.querySelector('#resultados-busqueda');
let temporizadorBusqueda;
let solicitudActiva = 0;

campoBusqueda.addEventListener('input', () => {
  clearTimeout(temporizadorBusqueda);
  const termino = campoBusqueda.value.trim();
  resultadosBusqueda.replaceChildren();

  if (!termino) {
    estadoBusqueda.textContent = '';
    return;
  }

  estadoBusqueda.textContent = 'Buscando…';
  temporizadorBusqueda = setTimeout(() => buscar(termino), 180);
});

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
      const item = document.createElement('li');
      item.append(
        document.createTextNode('Voluntario: '), resaltar(avistamiento.voluntario, termino),
        document.createTextNode(' · Día: '), resaltar(avistamiento.fecha, termino),
        document.createTextNode(' · Ave: '), resaltar(avistamiento.ave, termino),
        document.createTextNode(' · Comuna: '), resaltar(avistamiento.comuna, termino)
      );
      resultadosBusqueda.appendChild(item);
    });
  } catch (error) {
    if (idSolicitud !== solicitudActiva) return;
    estadoBusqueda.textContent = 'Ocurrió un error al buscar avistamientos. Intenta nuevamente.';
  }
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
