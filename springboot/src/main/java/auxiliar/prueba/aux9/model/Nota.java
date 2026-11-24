package auxiliar.prueba.aux9.model;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;

@Entity
@Table(name = "nota")
public class Nota {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "avistamiento_id", nullable = false)
    private Avistamiento avistamiento;

    @Min(1)
    @Max(7)
    @Column(name = "nota", nullable = false)
    private Integer nota;

    protected Nota() {
    }

    public Nota(Avistamiento avistamiento, Integer nota) {
        this.avistamiento = avistamiento;
        this.nota = nota;
    }
}
