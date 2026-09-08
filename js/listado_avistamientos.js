

document.addEventListener('DOMContentLoaded', init, false);

let table, sortCol;
let sortAsc = false;
const pageSize = 3;
let curPage = 1;

const avistamientos = [
  { ave: "Cóndor", fecha: "2026-09-01", lugar: "Cajón del Maipo" },
  { ave: "Águila", fecha: "2026-08-28", lugar: "Farellones" },
  { ave: "Flamenco", fecha: "2026-08-25", lugar: "San Pedro de Atacama" },
  { ave: "Halcón", fecha: "2026-08-20", lugar: "Valparaíso" },
  { ave: "Cóndor", fecha: "2026-08-15", lugar: "Torres del Paine" },
  { ave: "Águila", fecha: "2026-08-10", lugar: "Rancagua" },
  { ave: "Flamenco", fecha: "2026-08-05", lugar: "Chañaral" },
  { ave: "Halcón", fecha: "2026-07-30", lugar: "Santiago" }
];


async function init() {
  
  // Seleccionar la tabla
  table = document.querySelector('#tablaAvistamientos tbody');

  renderTable()
  document.querySelector('#nextButton').addEventListener('click', nextPage, false);
  document.querySelector('#prevButton').addEventListener('click', previousPage, false);
}

function renderTable() {
  // create html
  let result = '';
  avistamientos.filter((row, index) => {
        let start = (curPage-1)*pageSize;
        let end =curPage*pageSize;
        if(index >= start && index < end) return true;
  }).forEach(c => {
     result += `<tr>
     <td>${c.ave}</td>
     <td>${c.fecha}</td>
     <td>${c.lugar}</td>
     </tr>`;
  });
  table.innerHTML = result;
}

function sort(e) {
  let thisSort = e.target.dataset.sort;
  if(sortCol === thisSort) sortAsc = !sortAsc;
  sortCol = thisSort;
  console.log('sort dir is ', sortAsc);
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

/*
esto fue hecho basado en https://www.raymondcamden.com/2022/03/14/building-table-sorting-and-pagination-in-javascript
/*