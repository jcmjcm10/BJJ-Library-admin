
IMAGE_NAME=bjj-library
VERSION=0.1.0
rm bjj-library.tar
docker build -t ${IMAGE_NAME}:${VERSION} .  
# guardar imagen en .tar
docker save ${IMAGE_NAME}:${VERSION} -o ${IMAGE_NAME}.tar
