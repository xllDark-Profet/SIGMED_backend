Backend del proyecto de SIGMED

Para poder ejecutar el proyecto por primera vez se debe hacer lo siguiente:
1. Clonar el repo
2. Tener configurado el mysql con una nueva base de datos "sigmed"
3. En la carpeta principal sigmed en settings se debe modificar el acceso a la base de datos (usuario y contraseña)
4. Ejecutar en consola python -m pip install -r requirements.txt para instalar los paquetes necesarios para su ejecución (bien sea en un entorno o en el global)
5. En la carpeta codigo ejecutar en consola: python .\manage.py makemigrations y despues: python .\manage.py migrate, para crear y postear las tablas en la base de datos de mysql
6. Ya se puede ejecutar: py manage.py runserver para correr el proyecto y verificar con las peticiones el funcionamiento del mismo (con postman o cualquier api de peticiones)

Ahora, si se van a actualizar la versión del back:
1. Ir al workbench o manejador de mysql y eliminar la versión actual de "sigmed".
2. Verificar que en las Apps de django dentro de las carpetas migrations no haya ninguna migración aparte de __init__.py
3. Ejecutar los pasos 5 y 6 de la primera vez de ejecución del proyecto.