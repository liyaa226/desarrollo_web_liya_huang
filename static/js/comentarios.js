document.addEventListener('DOMContentLoaded', () => {
  const main = document.querySelector('.detalle-container');
  const url = main.dataset.comentariosUrl;
  const lista = document.querySelector('#lista-comentarios');
  const estado = document.querySelector('#estado-comentarios');
  const formulario = document.querySelector('#form-comentario');
  const resultado = document.querySelector('#resultado-comentario');

  cargarComentarios();

  formulario.addEventListener('submit', event => {
    event.preventDefault();
    resultado.textContent = '';

    if (!formulario.reportValidity()) {
      return;
    }

    const nombre = formulario.elements.nombre.value.trim();
    const texto = formulario.elements.texto.value.trim();
    if (nombre.length < 3 || nombre.length > 50 || texto.length < 5 || texto.length > 300) {
      resultado.textContent = 'Revisa el nombre (3 a 50 caracteres) y el comentario (5 a 300 caracteres).';
      return;
    }

    fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nombre, texto })
    })
      .then(leerRespuesta)
      .then(({ respuesta, datos }) => {
        if (!respuesta.ok) {
          throw new Error(datos.error || 'No se pudo agregar el comentario.');
        }

        formulario.reset();
        resultado.textContent = 'Comentario agregado.';
        cargarComentarios();
      })
      .catch(error => {
        resultado.textContent = error.message;
      });
  });

  function cargarComentarios() {
    estado.textContent = 'Cargando comentarios...';

    fetch(url)
      .then(leerRespuesta)
      .then(({ respuesta, datos }) => {
        if (!respuesta.ok) {
          throw new Error(datos.error || 'No se pudieron cargar los comentarios.');
        }
        return datos;
      })
      .then(comentarios => {
        lista.replaceChildren();

        if (comentarios.length === 0) {
          estado.textContent = 'Este avistamiento todavía no tiene comentarios.';
          return;
        }

        comentarios.forEach(comentario => {
          const item = document.createElement('li');
          const encabezado = document.createElement('p');
          const texto = document.createElement('p');

          encabezado.textContent = `${comentario.fecha} — ${comentario.nombre}`;
          texto.textContent = comentario.texto;
          item.append(encabezado, texto);
          lista.append(item);
        });

        estado.textContent = '';
      })
      .catch(error => {
        estado.textContent = error.message;
      });
  }

  function leerRespuesta(respuesta) {
    return respuesta.text().then(texto => {
      let datos;
      try {
        datos = JSON.parse(texto);
      } catch {
        throw new Error(`El servidor respondió con un error (HTTP ${respuesta.status}). Revisa la consola de Flask.`);
      }
      return { respuesta, datos };
    });
  }
});
