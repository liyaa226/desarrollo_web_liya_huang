

document.addEventListener('DOMContentLoaded', init, false);

let table, sortCol;
let sortAsc = false;
const pageSize = 3;
let curPage = 1;

let avistamientos = [];
let staticUrl;


async function init() {
  
  // Seleccionar la tabla
  table = document.querySelector('#tablaAvistamientos tbody');
  staticUrl = document.querySelector('#tablaAvistamientos').closest('main').dataset.staticUrl;
  avistamientos = JSON.parse(document.querySelector('#datos-avistamientos').textContent)

  document.querySelector('#nextButton').addEventListener('click', nextPage);
  document.querySelector('#prevButton').addEventListener('click', previousPage);
  document.querySelectorAll('#tablaAvistamientos th[data-sort]').forEach(header => {
    header.addEventListener('click', sort);
  });

  renderTable();
}

function renderTable() {
  // create html
  let result = '';
  avistamientos.filter((row, index) => {
        let start = (curPage-1)*pageSize;
        let end =curPage*pageSize;
        if(index >= start && index < end) return true;
  }).forEach(c => {
     let foto = '';
     if (c.archivo) {
       const extension = c.archivo.split('.').pop().toLowerCase();
       if (['png', 'jpg', 'jpeg', 'gif'].includes(extension)) {
         foto = `<img class="miniatura-avistamiento" src="${staticUrl}${c.archivo}" alt="Foto del avistamiento ${c.id}">`;
       }
     }

     result += `<tr>
     <td>${c.ave}</td>
     <td>${c.fecha}</td>
     <td>${c.lugar}</td>
     <td>${foto}</td>
     <td><a href="/avistamientos/${encodeURIComponent(c.id)}">Ver detalle</a></td>
     </tr>`;
  });
  table.innerHTML = result;
}

function sort(e) {
  let thisSort = e.target.dataset.sort;
  if(sortCol === thisSort) sortAsc = !sortAsc;
  sortCol = thisSort;
  avistamientos.sort((a, b) => {
    if(a[sortCol] < b[sortCol]) return sortAsc?1:-1;
    if(a[sortCol] > b[sortCol]) return sortAsc?-1:1;
    return 0;
  });
  renderTable();
}

function previousPage() {
  if(curPage > 1) {
    curPage--;
    renderTable();
  }
}

function nextPage() {
  if((curPage * pageSize) < avistamientos.length) {
    curPage++;
    renderTable();
  }
}


// esto fue hecho basado en https://www.raymondcamden.com/2022/03/14/building-table-sorting-and-pagination-in-javascript
