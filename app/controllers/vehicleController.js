import VehicleModel from "../models/vehicleModel.js";
import { v4 as uuidv4 } from 'uuid';

// Get all vehicles
async function getVehicles(req, res) {
    const vehicles = await VehicleModel.find();
    res.json(vehicles);
}

// Get a single vehicle by ID
async function getVehicle (req, res) {
    const vehicle = await VehicleModel.findOne({ id: req.params.id });
    vehicle ? res.json(vehicle) : res.status(404).send('Vehicle not found');
}

// Add a new vehicle
async function addVehicle (req, res) {
    const { vin, lat, lng, make, model, year, color } = req.body;

    if (!vin || lat == null || lng == null || !make || !model || !year || !color) {
        return res.status(400).send('Missing required vehicle info: vin, lat, lng, make, model, year, color');
    }

    try {
        const vehicle = new VehicleModel({ vin, lat, lng, make, model, year, color });
        vehicle.id = uuidv4();
        vehicle.lastUpdated = Date.now();
        vehicle.status = 'active'; // Default status
        await vehicle.save();
        res.status(201).json(vehicle);
    } catch (err) {
        if (err.code === 11000) {
            res.status(409).send('Vehicle ID already exists - ' + err.message);
        } else {
            res.status(500).send('Error saving vehicle - ' + err.message);
        }
    }
}

// Update a vehicle's location
async function updateVehicle (req, res) {
    const { lat, lng } = req.body;

    if (lat == null || lng == null) {
        return res.status(400).send('Missing lat or lng');
    }

    try {
        const vehicle = await VehicleModel.findOneAndUpdate(
            { id: req.params.id },
            { lat, lng },
            { new: true }
        );

        if (!vehicle) return res.status(404).send('Vehicle not found');

        res.json(vehicle);
    } catch (err) {
        res.status(500).send('Error updating vehicle location - ' + err.message);
    }

}

// Delete a vehicle
async function deleteVehicle (req, res) {
    const vehicle = await VehicleModel.findOneAndDelete({ id: req.params.id });
    if (!vehicle) return res.status(404).send('Vehicle not found');
    res.json(vehicle);
}


export {
    getVehicles,
    getVehicle,
    addVehicle,
    updateVehicle,
    deleteVehicle
}