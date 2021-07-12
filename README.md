## Technic Test HABI - Python developer vacancy

### - Tecnologías usadas:
> * Python (v3.8.10)
> * Flask (v1.1.2)
> * Flask-JWT (v0.3.2)
> * Flask-JWT-Extended (v4.1.0)
> * Flask-RESTful (v0.3.8)
> * Flask-SQLAlchemy (v2.5.1)
> * jwt (v1.2.0)
> * PyJWT (v2.0.1)
> * python-dotenv (v0.17.0)
> * SQLAlchemy (v1.3.24)
> * sqlalchemy-filters 

### Desarrollo del sistema:
Para este sistema (API RestFul) se utilizó un "simil" de una arquitectura MVC. Donde los modelos (User, Property, Story, 
StatusHistoryModel, Like) y las vistas para cada modelo son estructurados como una App para que el controlador de las 
URI como Blueprints sean llamados a raíz de estos endpoints del view_endpoints para cada app. Por ejemplo: el modelo 
Property está contenido en una clase: PropertyModel y el mismo contiene sus endpoints en otra clase/script llamado 
view_endpoints. Los view_endpoints contienen métodos HTTP correspondientes para administrar datos del modelo Property y 
el primer caso de uso de la prueba. La demostración gráfica de la arquitectura de diseño de la API es la siguiente:

```
apps -->
    property -->
            PropertyModel
            view_endpoints
    status -->
            StatusModel
            view_endpoints
    status_history -->
            StatusHistoryModel
            view_endpoints
    user -->
            AuthUserModel
            view_endpoints
    like -->
            LikeModel
            view_endpoints
auth_controller -->
db_controller -->
handler_controller -->
logger_controller -->
settings -->
utilities -->
api_config.py
main.py
wsgi.py
Procfile
``` 

Y los controladores para la base de datos (función conector, inicio de sesión, cierre de sesión, etc), de la 
autenticación a los endpoints de administración de datos, el loggeo de la información en archivo .log, los errores de
cada endpoint representado por un JSON (handler_controller), las propiedades y constantes de la API, algunas utilerias y 
el manejo de los endpoints para su transaccionalidad (rutas) mediante Blueprints configurados a una Api de Flask, están 
contenidos en los demás módulos según corresponde.

## Dudas principales
* ¿Se debe generar un administrador de los datos (funciones CRUD)?
    - R= Se tomó la decisión de generar funciones CRUD para manejo de los datos de cada modelo, esto es: Insertar datos, 
         modificarlos, consultarlos y eliminarlos. Lo anterior con el objetivo de hacer mantenibles estos de una manera
         general mediante el uso de URIs específicos en la API con cada método HTTP correspondiente a cada función del 
         CRUD.

* ¿Los endpoints para ambos casos de uso requeridos sostienen los modelos y sus relaciones directas?
    - R= SI. Cada modelo entre si es independiente para su mantenimiento (funciones CRUD) pero no para su funcionalidad.
             Esto es que si el modelo `Property` y `Status` están relacionados, entonces el caso de uso de consulta de 
             propiedades por un usuario debera de contener la relación correspondiente en el modelo `status_history` a 
             cada modelo y en el endpoint GET para `Property` establecer un URI a esta consulta que involucra los 3 
             modelos mencionados.
             
* En el caso de uso de `Likes` a Propiedades, ¿qué modelo utilizar?
    - R= Se tomó la desición de usar un modelo específico para `Likes` (y se le puede añadir atributos de `comments/
    comentarios`). Para este modelo, es necesario que el usuario esté logueado a la app y pueda rankear mediante el botón 
    Like a la propiedad que le agrade, así mismo pueda comentar para que este registro quede grabado en la BD. Así mismo 
    el usuario tendrá la opción de usar los filtros de búsqueda de propiedades según caso de uso 1 establecido.      

                 