# Use the official MongoDB image as the base image
FROM mongodb/mongodb-community-server:latest

# Set the working directory inside the container
WORKDIR /data/db

# Expose the default MongoDB ports
EXPOSE 27017 28017

# Start the MongoDB server
CMD ["mongod"]