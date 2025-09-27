#!/bin/sh

# This script is used to start the vehicle locator API service.

if [ "$1" == "down" ]; then
  echo "Stopping Vehicle Locator API, Firewall and DB..."

  # Stop the Database
  cd ./database
  ./database.sh down

  # Stop the API Firewall
  cd ../api-firewall
  ./deployFirewall.sh down

  exit 0
elif [ "$1" == "restart" ]; then
  echo "Restarting Vehicle Locator API, Firewall and DB..."

  # Stop the Database
  cd ./database
  ./database.sh down

  # Stop the API Firewall
  cd ../api-firewall
  ./deployFirewall.sh down

  # Start the Database
  cd ../database
  ./database.sh

  # Start the API Firewall
  cd ../api-firewall
  ./deployFirewall.sh

  # Start the Vehicle Locator API
  cd ../app
  npm install -y
  npm start
elif [ $# -lt 1 ]; then
  echo "Starting Vehicle Locator API, Firewall and DB..."
  # Start the Database
  cd ./database
  ./database.sh

  # Start the API Firewall
  cd ../api-firewall
  ./deployFirewall.sh

  # Start the Vehicle Locator API
  cd ../app
  npm install -y
  npm start
else
  echo "Invalid argument. Use 'down' to stop the services or no arguments to start."
  exit 1
fi