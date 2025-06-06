#! /bin/sh

echo "Deploying API Firewall"
docker-compose -f docker-compose-firewall.yaml up -d