document.addEventListener('DOMContentLoaded', cargarEstadisticas);

function cargarEstadisticas() {
  const estado = document.querySelector('#estado-estadisticas');
  const urlEstadisticas = document.querySelector('main').dataset.estadisticasUrl;

  fetch(urlEstadisticas)
    .then(respuesta => {
      if (!respuesta.ok) {
        throw new Error(`La solicitud de estadísticas falló (${respuesta.status}).`);
      }
      return respuesta.json();
    })
    .then(datos => {
      Highcharts.chart('grafico-avistamientos-dia', {
        chart: { type: 'line' },
        title: { text: null },
        xAxis: {
          categories: datos.avistamientos_por_dia.map(item => item.fecha),
          title: { text: 'Día' }
        },
        yAxis: {
          min: 0,
          title: { text: 'Cantidad de avistamientos' },
          allowDecimals: false
        },
        series: [{
          name: 'Avistamientos',
          color: '#FC2865',
          data: datos.avistamientos_por_dia.map(item => item.cantidad)
        }]
      });

      Highcharts.chart('grafico-avistamientos-ave', {
        chart: { type: 'pie' },
        title: { text: null },
        tooltip: { pointFormat: '<b>{point.y}</b> avistamientos ({point.percentage:.1f}%)' },
        series: [{
          name: 'Avistamientos',
          colorByPoint: true,
          data: datos.avistamientos_por_ave.map(item => ({
            name: item.ave,
            y: item.cantidad
          }))
        }]
      });

      Highcharts.chart('grafico-voluntarios-comuna', {
        chart: { type: 'column' },
        title: { text: null },
        xAxis: {
          categories: datos.voluntarios_por_comuna.map(item => item.comuna),
          title: { text: 'Comuna' }
        },
        yAxis: {
          min: 0,
          title: { text: 'Cantidad de voluntarios' },
          allowDecimals: false
        },
        series: [{
          name: 'Voluntarios',
          color: '#b376e4',
          data: datos.voluntarios_por_comuna.map(item => item.cantidad)
        }]
      });

      estado.textContent = '';
    })
    .catch((error) => console.error('No se pudieron cargar las estadísticas', error));
}
