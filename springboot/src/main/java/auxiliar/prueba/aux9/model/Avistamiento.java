package auxiliar.prueba.aux9.model;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "avistamiento")
public class Avistamiento {

    @Id
    private Integer id;

    protected Avistamiento() {
    }

    public Integer getId() {
        return id;
    }
}
