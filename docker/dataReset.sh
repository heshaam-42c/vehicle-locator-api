#! /bin/sh

if [ "$1" != "clean" ]; then
    echo "Refreshing DB"
    docker-compose -f docker-compose-db.yaml down
fi

docker-compose -f docker-compose-db.yaml up -d

echo "Creating Users..."

# JSON data for the API request 
json_data_user_test='{"email": "scanuser@test.com","pass": "scanpassword","name": "Scan Test User","is_admin": false}'
json_data_user_admin='{"email": "scanadmin@test.com","pass": "scanpassword","name": "Scan Admin User","is_admin": true}'
json_data_user_bola='{"email": "scanbola@test.com","pass": "scanpassword","name": "Scan BOLA User","is_admin": false}'

# Invoke the API using curl with POST method and passing the JSON data
api_url="http://localhost:3000/user/register"
curl_response_test=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" -d "$json_data_user_test" "$api_url")
curl_response_admin=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" -d "$json_data_user_admin" "$api_url")
curl_response_bola=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" -d "$json_data_user_bola" "$api_url")

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