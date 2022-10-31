# myproject_v1

1. Descargar los archivos
2. crear un virtual env con los siguientes comandos
    - python3 -m venv env
    - source env/bin/activate
    - pip install --upgrade pip
3. instalar los requirements.txt con el siguiente comando: python3 -m pip install -r requirements.txt
4. Ejecutar la siguiente tarea: python3 api_test.py
5. En postman validar el host y port de la API y realizar la consulta de la siguiente manera:
6. http://127.0.0.1:4040/main/"customer_id":"1111" #### TENER EN CUENTA QUE EL CUSTOMER_ID ES UN VALOR DE LA DATA DE DYNAMO Y A ESTA NO SE PUEDE ACCEDER SIN MIS CREDENCIALES
7. http://127.0.0.1:4040/save/"customer_id":"1092"/"path":"_home_kevin-martinez_Downloads_" #### TENER EN CUENTA QUE EL CUSTOMER_ID ES DE AMAZON Y EL PATH ENVIADO ES EL DE MI EQUIPO LOCAL ESTE DEBE CAMBIAR

CONSIDERACIONES
1. Cambiar en constans.py las variables de tabla y realizar logueo a AWS desde su equipo local para probar esto
2. Probar con una tabla que tenga una columna de customer_id
3. Codigo desarrollado con Python 3.8.0
4. Instalar las mismas versiones de las librerias (se recomienda que sea con distribucion de linux para mayor conexion con los servicios de AWS)
5. Se envia un doc de docker para mayor entendimiento de la API
6. En el notebook se evidencia la funcionalidad de la conexion propia de los servicios de aws
