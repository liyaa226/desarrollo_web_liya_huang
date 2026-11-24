package auxiliar.prueba.aux9.model;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import auxiliar.prueba.aux9.web.NotaPromedioResponse;

public interface NotaRepository extends JpaRepository<Nota, Integer> {

    @Query("""
            SELECT new auxiliar.prueba.aux9.web.NotaPromedioResponse(
                n.avistamiento.id, AVG(n.nota)
            )
            FROM Nota n
            GROUP BY n.avistamiento.id
            """)
    List<NotaPromedioResponse> findPromedios();

    @Query("SELECT AVG(n.nota) FROM Nota n WHERE n.avistamiento.id = :avistamientoId")
    Double findPromedioByAvistamientoId(@Param("avistamientoId") Integer avistamientoId);
}
