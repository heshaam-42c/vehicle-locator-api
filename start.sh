#!/bin/sh

# This script is used to start the vehicle locator API service.

if [ "$1" == "down" ]; then
  echo "Stopping Vehicle Locator API Firewall and DB..."

  # Stop the Database
  cd ./database
  ./database.sh down

  # Stop the API Firewall
  cd ../api-firewall
  ./deployFirewall.sh down

  exit 0
fi

# Start the Database
cd ./database
./database.sh

# Start the API Firewall
cd ../api-firewall
./deployFirewall.sh

# Start the Vehicle Locator API
cd ../app
npm start