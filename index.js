import express from 'express';
import mongoose from 'mongoose';
import { v4 as uuidv4 } from 'uuid';

const app = express();
const port = 3000;

app.use(express.json());

// 🔌 MongoDB connection
mongoose.connect('mongodb://localhost:27017/vehicleLocator', {
  useNewUrlParser: true,
  useUnifiedTopology: true
}).then(() => console.log('✅ Connected to MongoDB'))
  .catch(err => console.error('❌ MongoDB connection error:', err));

// 🚗 Vehicle schema & model
const vehicleSchema = new mongoose.Schema({
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
}, {
  versionKey: false
});

const Vehicle = mongoose.model('Vehicle', vehicleSchema);

// Root
app.get('/', (req, res) => {
  res.send('Vehicle Locator API');
});

// Get all vehicles
app.get('/vehicles', async (req, res) => {
  const vehicles = await Vehicle.find();
  res.json(vehicles);
});

// Get a single vehicle by ID
app.get('/vehicles/:id', async (req, res) => {
  const vehicle = await Vehicle.findOne({ id: req.params.id });
  vehicle ? res.json(vehicle) : res.status(404).send('Vehicle not found');
});

// Add a new vehicle
app.post('/vehicles', async (req, res) => {
  const { vin, lat, lng, make, model, year, color } = req.body;

  if (!vin || lat == null || lng == null || !make || !model || !year || !color) {
    return res.status(400).send('Missing required vehicle info: vin, lat, lng, make, model, year, color');
  }

  try {
    const vehicle = new Vehicle({ vin, lat, lng, make, model, year, color });
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
});

// Update a vehicle's location
app.put('/vehicles/:id/location', async (req, res) => {
  const { lat, lng } = req.body;

  if (lat == null || lng == null) {
    return res.status(400).send('Missing lat or lng');
  }

  const vehicle = await Vehicle.findOneAndUpdate(
    { id: req.params.id },
    { lat, lng },
    { new: true }
  );

  if (!vehicle) return res.status(404).send('Vehicle not found');

  res.json(vehicle);
});

// Delete a vehicle
app.delete('/vehicles/:id', async (req, res) => {
  const vehicle = await Vehicle.findOneAndDelete({ id: req.params.id });
  if (!vehicle) return res.status(404).send('Vehicle not found');
  res.json(vehicle);
});

app.listen(port, () => {
  console.log(`🚗 API running at http://localhost:${port}`);
});
