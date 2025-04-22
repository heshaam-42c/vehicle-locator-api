# vehicle-locator-api
Vehicle Locator API code repository

### Start Database
#### Docker compose
```
docker compose -f docker-compose-db.yaml up -d
```

### Install dependencies & run API
```
cd app
npm install
npm start &
```

### Run user-creation script
```
./dataReset.sh
```

API should be ready and running at http://localhost:3000

GitHub Actions workflow with 42Crunch Audit and Scan:
```
.github/workflows/42crunch.yml
```
Conformance Scan configuration:
```
.42c/scan/vehicle-locator-api/scanconf.json
```

## OWASP API Top 10 Vulnerabilities

![image](https://github.com/user-attachments/assets/1149d806-6418-4af4-96c2-e04f832010a1)

| Vulnerability                                           | Location                      |
| ------------------------------------------------------- | ----------------------------- |
| API1:2023 - Broken Object Level Authorization           | GET /vehicles/{id}            |
| API1:2023 - Broken Object Level Authorization           | DELETE /vehicles/{id}         |
| API1:2023 - Broken Object Level Authorization           | PUT /vehicles/{id}/location   |
| API2:2023 - Broken Authentication                       | GET /                         |
| API3:2023 - Broken Object Property Level Authorization  | POST /vehicles                |
| API3:2023 - Broken Object Property Level Authorization  | PUT /vehicles/{id}/location   |
| API5:2023 - Broken Function Level Authorization         | GET /vehicles                 |
| API8:2019 - Injection                                   | POST /vehicles                |

### API1:2023
Attacker is able to get and delete vehicles they do not own