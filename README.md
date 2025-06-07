# vehicle-locator-api

Code repository for the intentionally vulnerable Vehicle Locator API. This is a NodeJS API built with OWASP API Top 10 security vulnerabilities.

#### OpenAPI Spec:
`openapi-spec/openapi-spec.json`

#### Postman Collection:
`postman-collection/Vehicle-Locator-API.postman_collection.json`

#### Conformance Scan (v2) configuration:
`.42c/scan/vehicle-locator-api/scanconf.json`

#### GitHub Actions workflow (includes 42Crunch Audit, Scan, and Protect):
`.github/workflows/42crunch.yml`

## Run the Vehicle Locator API

### 1. Start the Database
```
cd database
./database.sh
```

### 2. Install NodeJS dependencies & Run the API
```
cd app
npm install
npm start
```

#### Vehicle Locator API should be ready and running at http://localhost:3000 with default seed users created:
- Admin User (scanadmin@test.com)
- Regular User (scanuser@test.com)
- BOLA Test User (scanbola@test.com)

#### Optional - create .env file inside app folder to override these default variables:
```
PORT=3000
MONGO_URI=mongodb://localhost:27017/vehicleLocator
```

## Run the API Firewall

### 1. Create .env file inside api-firewall folder with your PROTECTION_TOKEN
```
PROTECTION_TOKEN=<your_protection_token>
```

### 2. Start the Firewall
```
cd api-firewall
./deployFirewall.sh
```

Firewall should be running at http://vehicle-api-secured.42crunch.test:4241

## Stop the API Firwall
```
cd api-firewall
./deployFirewall.sh down
```

## Stop the Database
```
cd database
./database.sh down
```

## Quick-start script to run all of the above (Database, API, and API Firewall):
```
./start.sh
```
### Quick shut-down:
```
Ctrl+C

./start.sh down
```

## OWASP API Top 10 Vulnerabilities

![image](https://github.com/user-attachments/assets/1149d806-6418-4af4-96c2-e04f832010a1)

| Vulnerability                                                       | Location                                   |
| ------------------------------------------------------------------- | ------------------------------------------ |
| API1:2023 - Broken Object Level Authorization                       | [GET /vehicles/{id}](#api12023)            |
| API1:2023 - Broken Object Level Authorization                       | [DELETE /vehicles/{id}](#api12023)         |
| API1:2023 - Broken Object Level Authorization                       | [PUT /vehicles/{id}/location](#api12023)   |
| API2:2023 - Broken Authentication                                   | [GET /](#api22023)                         |
| API3:2023 (API6:2019) - Broken Object Property Level Authorization  | [POST /vehicles](#api32023api62019)        |
| API3:2023 (API6:2019) - Broken Object Property Level Authorization  | [PUT /vehicles/{id}/location](#api32023api62019)|
| API3:2023 (API3:2019) - Broken Object Property Level Authorization  | [GET /vehicles](#api32023api32019)         |
| API5:2023 - Broken Function Level Authorization                     | [GET /vehicles](#api52023)                 |
| API8:2019 - Injection                                               | [POST /vehicles](#api82019)                |

### API1:2023
Description: User is able to GET and DELETE vehicles with invalid authorization. User is able to update (PUT) vehicles with invalid authorization.

![image](https://github.com/user-attachments/assets/9f4f0786-f519-4aa9-937c-24910f235476)

### API2:2023
Description: User is able to get API root without authentication

![image](https://github.com/user-attachments/assets/934ae725-6065-43f4-bd1d-82df576b9470)

### API3:2023(API6:2019)
Description: User is able to inject invalid properties into POST and PUT request schemas

![image](https://github.com/user-attachments/assets/c867542f-0e01-41ac-929a-887f10d120fa)

### API3:2023(API3:2019)
Description: Endpoint leaks excessive data like vehicle location (latitude & longitude) to the user

![image](https://github.com/user-attachments/assets/27af7e30-c440-4edd-9dd4-25d307e3f015)

### API5:2023
Description: Unauthorized user is able to access admin endpoint

![image](https://github.com/user-attachments/assets/079324e8-432c-462d-87fb-742298b3addb)

### API8:2019
VIN parameter in request schema is not properly validated

![image](https://github.com/user-attachments/assets/ee9f19dc-d89f-4723-ace3-cc4169253aa2)

