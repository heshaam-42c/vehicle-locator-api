# vehicle-locator-api
Vehicle Locator API code repository

### Start Database
#### Docker compose
docker compose -f docker-compose-db.yaml up -d

### Install dependencies & run API
cd app

npm install

npm start &

### Run user-creation script
./dataReset.sh

API should be ready and running at http://localhost:3000

## Vulnerabilities

| Vulnerability                                           | Location             |
| ------------------------------------------------------- | -------------------- |
| API1:2023 - Broken Object Level Authorization           | PUT /vehicles/{id}   |
| API2:2023 - Broken Authentication                       | GET /                |
| API3:2023 - Broken Object Property Level Authorization  | POST /vehicles       |
| API5:2023 - Broken Function Level Authorization         | GET /vehicles        |

