#! /bin/sh

if [ "$1" == "down" ]; then
  docker-compose -f docker-compose-firewall.yaml down
  exit 0
fi

echo "Deploying API Firewall"
docker-compose -f docker-compose-firewall.yaml up -d