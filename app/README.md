# vehicle-locator-api
Vehicle Locator API code repository

### Docker compose
docker compose -f docker-compose-db.yaml up -d

### Dockerfile
docker build -t vehicle-mongodb .

docker run -d --name mongodb -p 27017:27017 -p 28017:28017 vehicle-mongodb