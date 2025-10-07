#!/bin/sh

# This script is used to start the vehicle locator API service.

if [ "$1" == "-h" ]; then
    echo "usage: $0 [down|restart]\n"
    echo "This script is used to manage the Vehicle Locator API"
    echo "   -h          Show this help message"
    echo "   down        Shut down the Vehicle Locator API"
    echo "   restart     Restart the Vehicle Locator API"
    exit 0
fi

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
  nodemon start
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
  nodemon start
else
  echo "Invalid argument. Use -h for help."
  exit 1
fi