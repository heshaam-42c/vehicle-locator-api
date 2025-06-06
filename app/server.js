import express from 'express';
import dotenv from 'dotenv';
import vehicleRoutes from './routes/vehicleRoutes.js';
import authRoutes from './routes/authRoutes.js'
import rootRoute from './routes/rootRoute.js'
import connectDB from './data/db.js';

dotenv.config();
connectDB();

const SERVER = express();
const PORT = process.env.PORT || 3000;

SERVER.use(express.json());

SERVER.use('/vehicles', vehicleRoutes);
SERVER.use('/user', authRoutes);
SERVER.use('/', rootRoute);

SERVER.listen(PORT, () => console.log(`🚗 API server running at http://localhost:${PORT}` ));