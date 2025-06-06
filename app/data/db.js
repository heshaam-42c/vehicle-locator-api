import mongoose from 'mongoose';
import UserModel from '../models/userModel.js';
import { v4 as uuidv4 } from 'uuid';

const connectDB = async () => {
    try {
        const connection = await mongoose.connect(process.env.MONGO_URI || 'mongodb://localhost:27017/vehicleLocator'); 

        console.log(`✅ MongoDB Database successfully connected: ${connection.connection.host}`);
        // Seed default users
        await seedDefaultUsers();
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

export default connectDB;