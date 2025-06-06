#! /bin/sh

if [ "$1" == "down" ]; then
    echo "Stopping DB..."
    docker-compose -f docker-compose-db.yaml down
    exit 0
fi

if [ "$1" == "clean" ]; then
    echo "Stopping DB..."
    docker-compose -f docker-compose-db.yaml down
fi

echo "Creating DB..."
docker-compose -f docker-compose-db.yaml up -d

# Check if API is running
api_invoke_url="http://localhost:3000/"
curl_response_invoke=$(curl -s -o /dev/null -w "%{http_code}" "$api_invoke_url")

if [ "$curl_response_invoke" == "200" ]; then
    echo "API is up and running"
else
    echo "API is not reachable, got $curl_response_invoke"
    exit 1
fi

echo "Creating Users..."

# JSON data for the API request 
json_data_user_test='{"email": "scanuser@test.com","pass": "scanpassword","name": "Scan Test User","is_admin": false}'
json_data_user_admin='{"email": "scanadmin@test.com","pass": "scanpassword","name": "Scan Admin User","is_admin": true}'
json_data_user_bola='{"email": "scanbola@test.com","pass": "scanpassword","name": "Scan BOLA User","is_admin": false}'

# Invoke the API using curl with POST method and passing the JSON data
api_register_url="http://localhost:3000/user/register"
curl_response_test=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" -d "$json_data_user_test" "$api_register_url")
curl_response_admin=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" -d "$json_data_user_admin" "$api_register_url")
curl_response_bola=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" -d "$json_data_user_bola" "$api_register_url")

if [ "$curl_response_test" == "200" ]; then
    echo "Test User Created"
else
    echo "Test User Creation Failed, got $curl_response_test"
fi

if [ "$curl_response_admin" == "200" ]; then
    echo "Admin User Created"
else
    echo "Admin User Creation Failed, got $curl_response_admin"
fi

if [ "$curl_response_bola" == "200" ]; then
    echo "BOLA User Created"
else
    echo "BOLA User Creation Failed, got $curl_response_bola"
fi