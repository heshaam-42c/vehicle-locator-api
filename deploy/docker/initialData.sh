#! /bin/sh

echo "Creating Users..."

# JSON data for the API request 
json_data_user_inbound='{"email": "scanuser@test.com","password": "scanpassword","name": "Conf Scan User","number": "1001"}'
json_data_user_attack='{"email": "attackuser@test.com","password": "scanpassword","name": "Attack Scan User","number": "1002"}'

# Invoke the API using curl with POST method and passing the JSON data
api_url="http://localhost:8888/identity/api/auth/signup"

# DEBUG: Save entire response
curl_response_inbound=$(curl -s -o /dev/null -D - POST -H "Content-Type: application/json" -d "$json_data_user_inbound" "$api_url")
curl_response_attack=$(curl -s -o /dev/null -D - POST -H "Content-Type: application/json" -d "$json_data_user_attack" "$api_url")

echo "Inbound User \n$curl_response_inbound"
echo "Attack User \n$curl_response_attack"