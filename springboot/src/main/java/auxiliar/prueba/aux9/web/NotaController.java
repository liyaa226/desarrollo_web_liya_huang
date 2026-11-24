package auxiliar.prueba.aux9.web;

import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import tools.jackson.databind.JsonNode;

import auxiliar.prueba.aux9.service.NotaService;

@RestController
@RequestMapping("/api/avistamientos")
public class NotaController {

    private static final String MENSAJE_NOTA_INVALIDA =
            "La nota debe ser un número entero entre 1 y 7.";

    private final NotaService notaService;

    public NotaController(NotaService notaService) {
        this.notaService = notaService;
    }

    @GetMapping("/notas")
    public List<NotaPromedioResponse> obtenerPromedios() {
        return notaService.obtenerPromedios();
    }

    @PostMapping("/{avistamientoId}/notas")
    public ResponseEntity<?> agregarNota(
            @PathVariable Integer avistamientoId,
            @RequestBody JsonNode cuerpo) {
        JsonNode valor = cuerpo != null && cuerpo.isObject() ? cuerpo.get("nota") : null;
        if (valor == null || !valor.isIntegralNumber() || !valor.canConvertToInt()) {
            return ResponseEntity.badRequest().body(new ApiError(MENSAJE_NOTA_INVALIDA));
        }

        int nota = valor.intValue();
        if (nota < 1 || nota > 7) {
            return ResponseEntity.badRequest().body(new ApiError(MENSAJE_NOTA_INVALIDA));
        }

        return notaService.agregarNota(avistamientoId, nota)
                .<ResponseEntity<?>>map(ResponseEntity::ok)
                .orElseGet(() -> ResponseEntity.status(HttpStatus.NOT_FOUND)
                        .body(new ApiError("El avistamiento no existe.")));
    }
}
