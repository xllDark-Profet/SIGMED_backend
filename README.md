Backend del proyecto de SIGMED

Para poder ejecutar el proyecto se debe hacer lo siguiente:
1. Clonar el repo
2. Tener configurado el mysql con la base de datos "sigmed"
3. En la carpeta principal sigmed en settings se debe modificar el acceso a la base de datos (usuario y contraseña)
4. Ejecutar en consola python -m pip install -r requirements.txt para instalar los paquetes necesarios
5. En la carpeta codigo ejecutar en consola: python .\manage.py makemigrations y despues: python .\manage.py migrate
6. Ya se puede ejecutar: py manage.py runserver para correr el proyecto y verificar con las peticiones el funcionamiento del mismo
