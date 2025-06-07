#! /bin/sh

docker_yaml=docker-compose-firewall.yaml

if [ "$1" == "down" ]; then
  echo "Stopping API Firewall..."
  docker-compose -f $docker_yaml down
  exit 0
fi

echo "Deploying API Firewall"
docker-compose -f $docker_yaml up -d