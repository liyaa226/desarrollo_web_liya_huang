# desarrollo_web_liya_huang

La página responden en el puerto 5000, es decir en http://127.0.0.1:5000/ 

Usé Java versión 27 con Spring Boot 4.2.0 y las dependencias recomendadas por el auxiliar.

La API de notas se implementó en `springboot/` con Java 27, Spring Boot 4.2.0 y JPA.
Se utiliza la misma base MySQL `tarea2` que Flask. Antes de iniciar el servicio,
ejecuta `database/tabla-nota.sql` en esa base para crear la tabla de notas.

En PowerShell, configura `DB_USERNAME` y `DB_PASSWORD` con las credenciales de
MySQL que usa la aplicación Flask y ejecuta:

```powershell
$env:DB_USERNAME = "<usuario MySQL de Flask>"
$env:DB_PASSWORD = "<contraseña MySQL de Flask>"
cd springboot
.\mvnw.cmd spring-boot:run
```

Inicia Flask en otra terminal. El listado consulta los promedios en
`http://localhost:8080/api/avistamientos/notas` y envía cada evaluación a
`/api/avistamientos/{id}/notas`. 


