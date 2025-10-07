import VehicleModel from "../models/vehicleModel.js";
import { v4 as uuidv4 } from 'uuid';

// Get all vehicles
async function getVehicles(req, res) {
    // Fetch all vehicles, excluding the MongoDB _id field
    const vehicles = await VehicleModel.find().select('-_id').limit(10);
    res.json(vehicles);
}

// Get a single vehicle by ID
async function getVehicle (req, res) {
    const vehicle = await VehicleModel.findOne({ id: req.params.id });
    vehicle ? res.json(vehicle) : res.status(404).json({ message: "Vehicle not found" });
}

// Add a new vehicle
async function addVehicle (req, res) {
    const { vin, lat, lng, make, model, year, color } = req.body;

    if (!vin || lat == null || lng == null || !make || !model || !year || !color) {
        return res.status(400).json({ message: "Missing required vehicle info: vin, lat, lng, make, model, year, color" });
    }

    try {
        // Check if a vehicle with the same VIN already exists
        const existingVehicle = await VehicleModel.findOne({ vin });
        if (existingVehicle) {
            return res.status(409).json({ message: "A vehicle with this VIN already exists" });
        }

        // Create and save the new vehicle
        const vehicle = new VehicleModel({ vin, lat, lng, make, model, year, color });
        vehicle.id = uuidv4();
        vehicle.lastUpdated = Date.now();
        vehicle.status = 'active'; // Default status
        await vehicle.save();
        res.status(201).json(vehicle);
    } catch (err) {
        res.status(500).json({ message: "Error saving vehicle - " + err.message });
    }
}

// Update a vehicle's location
async function updateVehicle (req, res) {
    const { lat, lng } = req.body;

    if (lat == null || lng == null) {
        return res.status(400).json({ message: "Missing lat or lng" });
    }

    try {
        const vehicle = await VehicleModel.findOneAndUpdate(
            { id: req.params.id },
            // API6:2019 - Mass Assignment - FIX: Update only the lat and lng fields
            // { lat, lng },
            req.body,
            { new: true }
        );

        if (!vehicle) return res.status(404).json({ message: "Vehicle not found" });

        res.json(vehicle);
    } catch (err) {
        res.status(500).json({ message: "Error updating vehicle location - " + err.message });
    }

}

// Delete a vehicle
async function deleteVehicle (req, res) {
    const vehicle = await VehicleModel.findOneAndDelete({ id: req.params.id });
    if (!vehicle) return res.status(404).json({ message: "Vehicle not found" });
    res.json(vehicle);
}


export {
    getVehicles,
    getVehicle,
    addVehicle,
    updateVehicle,
    deleteVehicle
}