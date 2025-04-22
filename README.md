# vehicle-locator-api
Vehicle Locator API code repository

### Start Database
#### Docker compose
docker compose -f docker-compose-db.yaml up -d

#### Dockerfile
docker build -t vehicle-mongodb .\n
docker run -d --name mongodb -p 27017:27017 -p 28017:28017 vehicle-mongodb

### Install dependencies & run API
cd app\n
npm install\n
npm start\n

API running at http://localhost:3000

## Vulnerabilities
