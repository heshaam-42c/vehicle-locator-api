import mongoose from 'mongoose';

const connectDB = async () => {
    try {
        const connection = await mongoose.connect(process.env.MONGO_URI); 

        console.log(`✅ MongoDB Database successfully connected: ${connection.connection.host}`);

    } catch (error) {
        console.log(`❌ MongoDB connection Error: ${error.message}`);
        process.exit(1);
    }
}

export default connectDB;