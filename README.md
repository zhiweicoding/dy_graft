# rz fake api
## fastapi

## 打包

```shell
docker build -t loveqianqian/rz_fake_api:develop .
```

```shell
docker run -d -p 8000:8000 loveqianqian/rz_fake_api:develop
```

docker-compose.yml
```docker
version: '3.8'

services:
  fastapi-app:
    image: loveqianqian/rz_fake_api:develop
    container_name: rz_fake_api
    ports:
      - "8000:8000"
    environment:
      - MODULE_NAME=main 
      - VARIABLE_NAME=app
    restart: always  
```