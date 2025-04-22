import mongoose from 'mongoose';

// 🚗 Vehicle schema & model
const vehicleSchema = new mongoose.Schema(
    {
        id: { type: String, required: true, unique: true },
        vin: { type: String, required: true, unique: true },
        lat: { type: Number, required: true },
        lng: { type: Number, required: true },
        make: { type: String, required: true },
        model: { type: String, required: true },
        year: { type: Number, required: true },
        color: { type: String, required: true },
        status: { type: String, enum: ['active', 'inactive'], default: 'active' },
        lastUpdated: { type: Date, default: Date.now }
    }, 
    {
        versionKey: false,
        // _id: false
    }
);
  
const VehicleModel = mongoose.model('Vehicle', vehicleSchema);

export default VehicleModel;