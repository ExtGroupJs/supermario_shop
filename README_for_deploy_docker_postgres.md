Actualizar el sistema:
Abre una terminal y ejecuta el siguiente comando para asegurarte de que todos los paquetes estén actualizados:

Copiar
sudo apt update
sudo apt upgrade
Instalar dependencias:
Instala las dependencias necesarias para permitir que apt use paquetes a través de HTTPS:

Copiar
sudo apt install apt-transport-https ca-certificates curl software-properties-common
Agregar la clave GPG de Docker:
Ejecuta este comando para agregar la clave GPG oficial de Docker:

Copiar
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
Agregar el repositorio de Docker:
Añade el repositorio de Docker a tus fuentes de APT:

Copiar
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
Actualizar el índice de paquetes:
Después de agregar el repositorio, actualiza el índice de paquetes nuevamente:

Copiar
sudo apt update
Instalar Docker:
Ahora puedes instalar Docker con el siguiente comando:

Copiar
sudo apt install docker-ce
Verificar la instalación:
Para comprobar que Docker se ha instalado correctamente, ejecuta:

Copiar
sudo systemctl status docker
Deberías ver que el servicio Docker está activo y en ejecución.

Ejecutar Docker sin sudo (opcional):
Si deseas ejecutar Docker sin utilizar sudo, agrega tu usuario al grupo docker:

Copiar
sudo usermod -aG docker $USER
Luego, cierra la sesión y vuelve a iniciar sesión para que los cambios surtan efecto.


*****************************************************
docker run --name my_postgres_container -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=mario_shop_db -p 5432:5432 -v my_data_volume:/var/lib/postgresql/data -d postgres

docker ps