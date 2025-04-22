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
User is able to GET and DELETE vehicles with invalid authorization

![image](https://github.com/user-attachments/assets/9f4f0786-f519-4aa9-937c-24910f235476)

### API2:2023
User is able to get API root without authentication
![image](https://github.com/user-attachments/assets/934ae725-6065-43f4-bd1d-82df576b9470)

### API3:2023
User is able to inject invalid properties into POST and PUT request schemas
![image](https://github.com/user-attachments/assets/c867542f-0e01-41ac-929a-887f10d120fa)

### API5:2023
Unauthorized user is able to access admin endpoint
![image](https://github.com/user-attachments/assets/079324e8-432c-462d-87fb-742298b3addb)

### API8:2019
VIN parameter in request schema is not properly validated
![image](https://github.com/user-attachments/assets/ee9f19dc-d89f-4723-ace3-cc4169253aa2)

