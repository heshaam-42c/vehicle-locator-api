import mongoose from 'mongoose';
import UserModel from '../models/userModel.js';
import VehicleModel from '../models/vehicleModel.js';
import { v4 as uuidv4 } from 'uuid';

function generateRandomVIN() {
    const chars = 'ABCDEFGHJKLMNPRSTUVWXYZ0123456789'; // Excludes I, O, Q
    let vin = '';
    for (let i = 0; i < 17; i++) {
        vin += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return vin;
}

const connectDB = async () => {
    try {
        const connection = await mongoose.connect(process.env.MONGO_URI || 'mongodb://localhost:27017/vehicleLocator'); 

        console.log(`✅ MongoDB Database successfully connected: ${connection.connection.host}`);
        // Seed default users
        await seedDefaultUsers();
        await seedDefaultVehicles();
    } catch (error) {
        console.log(`❌ MongoDB connection Error: ${error.message}`);
        process.exit(1);
    }
}

// Function to seed default users
const seedDefaultUsers = async () => {
  try {
    // Check if admin user already exists
    const adminExists = await UserModel.findOne({ email: "scanadmin@test.com" });
    if (!adminExists) {
      const adminUser = new UserModel({
        email: "scanadmin@test.com",
        pass: "scanpassword", // In a real application, hash this password
        name: "Scan Admin User",
        is_admin: true,
        id: uuidv4(), // Generate a unique customerId
      });
      await adminUser.save();
      console.log("Default admin user created");
    }

    // Check if regular user already exists
    const regularUserExists = await UserModel.findOne({ email: "scanuser@test.com" });
    if (!regularUserExists) {
      const regularUser = new UserModel({
        email: "scanuser@test.com",
        pass: "scanpassword", // In a real application, hash this password
        name: "Scan Test User",
        is_admin: false,
        id: uuidv4(), // Generate a unique customerId
      });
      await regularUser.save();
      console.log("Default regular user created");
    }

    // Check if BOLA user already exists
    const bolaUserExists = await UserModel.findOne({ email: "scanbola@test.com" });
    if (!bolaUserExists) {
      const bolaUser = new UserModel({
        email: "scanbola@test.com",
        pass: "scanpassword", // In a real application, hash this password
        name: "Scan BOLA User",
        is_admin: false,
        id: uuidv4(), // Generate a unique customerId
      });
      await bolaUser.save();
      console.log("Default BOLA user created");
    }
  } catch (error) {
    console.error("Error seeding default users:", error.message);
  }
};

// Function to seed default users
const seedDefaultVehicles = async () => {
  try {
    const newVehicle = new VehicleModel({
      vin: generateRandomVIN(),
      lat: "-23", 
      lng: "96",
      make: "Honda",
      model: "Civic", 
      year: "2024",
      color: "Black",
      status: "active",
      lastUpdated: Date.now(),
      id: uuidv4(), // Generate a unique vehicle ID
    });
    await newVehicle.save();
    console.log("One vehicle created");

    const newVehicle2 = new VehicleModel({
      vin: generateRandomVIN(),
      lat: "-16.5", 
      lng: "36.5",
      make: "Toyota",
      model: "Corolla", 
      year: "2023",
      color: "White",
      status: "active",
      lastUpdated: Date.now(),
      id: uuidv4(), // Generate a unique vehicle ID
    });
    await newVehicle2.save();
    console.log("Two vehicles created");
  } catch (error) {
    console.error("Error seeding default vehicles:", error.message);
  }
};

export default connectDB;