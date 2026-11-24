package auxiliar.prueba.aux9.service;

import java.util.List;
import java.util.Optional;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import auxiliar.prueba.aux9.model.AvistamientoRepository;
import auxiliar.prueba.aux9.model.Nota;
import auxiliar.prueba.aux9.model.NotaRepository;
import auxiliar.prueba.aux9.web.NotaPromedioResponse;

@Service
public class NotaService {

    private final AvistamientoRepository avistamientoRepository;
    private final NotaRepository notaRepository;

    public NotaService(
            AvistamientoRepository avistamientoRepository,
            NotaRepository notaRepository) {
        this.avistamientoRepository = avistamientoRepository;
        this.notaRepository = notaRepository;
    }

    @Transactional(readOnly = true)
    public List<NotaPromedioResponse> obtenerPromedios() {
        return notaRepository.findPromedios();
    }

    @Transactional
    public Optional<NotaPromedioResponse> agregarNota(Integer avistamientoId, int nota) {
        if (nota < 1 || nota > 7) {
            throw new IllegalArgumentException("La nota debe ser un entero entre 1 y 7.");
        }

        return avistamientoRepository.findById(avistamientoId).map(avistamiento -> {
            notaRepository.saveAndFlush(new Nota(avistamiento, nota));
            Double promedio = notaRepository.findPromedioByAvistamientoId(avistamientoId);
            return new NotaPromedioResponse(avistamientoId, promedio);
        });
    }
}
