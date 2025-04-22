import express from 'express';
import mongoose from 'mongoose';
import { v4 as uuidv4 } from 'uuid';

const app = express();
const port = 3000;

app.use(express.json());

//auth/token stuff
import jwt from 'jsonwebtoken';

import fs from 'fs';

// PRIVATE and PUBLIC key
var privateKey = fs.readFileSync('./keys/private.key', 'utf8');
var publicKey = fs.readFileSync('./keys/public.key', 'utf8');

// 🔌 MongoDB connection
mongoose.connect('mongodb://localhost:27017/vehicleLocator', {
  useNewUrlParser: true,
  useUnifiedTopology: true
}).then(() => console.log('✅ Connected to MongoDB'))
  .catch(err => console.error('❌ MongoDB connection error:', err));


// 🚗 User schema & model
const userSchema = new mongoose.Schema({
  id: { type: String, required: true, unique: true },
  email: { type: String, required: true, unique: true },
  pass: { type: String, required: true },
  name: { type: String, required: true },
  is_admin: { type: Boolean, required: true }
}, {
  versionKey: false
});

const User = mongoose.model('User', userSchema);

async function api_authenticate(email, pass, req, res) {
  console.log('>>> Logging user ' + email + ' with password: ' + pass);
  
  try {
    let user = await User.findOne({ email: email, pass: pass });    

    if (!user) {
      return res.status(401).send('Invalid email or password');
    } else {
      // Create JWT token
      var token = create_jwt ('RS384', 'vehicleLocatorUsers', 'https://issuer.42crunch.demo', user.email, { id: user.id }, privateKey);
      res.status(200).json({ message: "success", token: token, _id: user.id });
    }
  } catch (err) {
    console.error('Error during authentication:', err);
    res.status(500).send('Internal server error');
  }
}

async function api_register(email, pass, req, res) {
  console.log('>>> Registering user: ' + email + ' with password: ' + pass);

  const name = req.body.name;
  const is_admin = req.body.is_admin || false;

  if (!email || !pass || !name) {
    return res.status(400).send('Missing required fields: email, password, name');
  }
  
  try {
    let user = await User.findOne({ email: email });
    if (user) {
      return res.status(400).send('User already exists');
    } else {
      user = new User({ email, pass, name, is_admin });
      user.id = uuidv4();
      await user.save();
      res.status(200).json({ message: "success", _id: user.id });
    }
  } catch (err) {
    if (err.code === 11000) {
      res.status(409).send('User ID already exists - ' + err.message);
    } else {
      res.status(500).send('Error saving user - ' + err.message);
    }
  }
}

function create_jwt (algorithm, audience, issuer, subject, jwt_payload, key) {
  var token = "";
  try {
    token = jwt.sign(jwt_payload, key, {
      algorithm: algorithm,
      issuer: issuer,
      subject: subject,
      expiresIn: "4w",
      audience: audience
    })
    return token	
  }
  catch (e) {
    // Re-throw original issue.
    throw e
  }
}

function api_token_check(req, res, next) {

  console.log('>>> Validating token: ' + JSON.stringify(req.headers['authorization']));
  var bearerToken = req.headers['authorization'];
  var token = null;
  if (bearerToken) {
    // Bearer token is in the format "Bearer <token>"
    var parts = bearerToken.split(' ');
    if (parts.length === 2 && parts[0] === 'Bearer') {
      token = parts[1];
    }
  }

  // decode jwt token
  if (token) {
    // Verify token
    jwt.verify(token, publicKey, function (err, user) {
      if (err) {
        console.log(err)
        return res.status(403).json({ success: false, message: 'Failed to authenticate token' });
      } else {
        // if everything is good, save to request for use in other routes
        req.user = user;
        console.log('>>> Authenticated User: ' + JSON.stringify(req.user));
        next();
      }
    });

  } else {
    // if there is no token
    // return an error
    return res.status(403).send({
      success: false,
      message: 'No token provided'
    });
  }
}

// user related.
app.post('/user/login', async (req, res) => {
	if ((!req.body.email) || (!req.body.pass)) {
		res.status(422).json({ "message": "missing username and or password parameters" });
	}
	else {
		api_authenticate(req.body.email, req.body.pass, req, res);
	}
})

app.post('/user/register', async (req, res) => {
	if ((!req.body.email) || (!req.body.pass)) {
		res.status(422).json({ "message": "missing email and or password parameters" });
	} else if (req.body.pass.length <= 4) {
		res.status(422).json({ "message": "password length too short, minimum of 5 characters" })
	} else {
		api_register(req.body.email, req.body.pass, req, res);
	}
})

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
app.get('/vehicles', api_token_check, async (req, res) => {
  const vehicles = await Vehicle.find();
  res.json(vehicles);
});

// Get a single vehicle by ID
app.get('/vehicles/:id', api_token_check, async (req, res) => {
  const vehicle = await Vehicle.findOne({ id: req.params.id });
  vehicle ? res.json(vehicle) : res.status(404).send('Vehicle not found');
});

// Add a new vehicle
app.post('/vehicles', api_token_check, async (req, res) => {
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
app.put('/vehicles/:id/location', api_token_check, async (req, res) => {
  const { lat, lng } = req.body;

  if (lat == null || lng == null) {
    return res.status(400).send('Missing lat or lng');
  }

  try {
    const vehicle = await Vehicle.findOneAndUpdate(
      { id: req.params.id },
      { lat, lng },
      { new: true }
    );
  
    if (!vehicle) return res.status(404).send('Vehicle not found');
  
    res.json(vehicle);
  } catch (err) {
    res.status(500).send('Error updating vehicle location - ' + err.message);
  }

});

// Delete a vehicle
app.delete('/vehicles/:id', api_token_check, async (req, res) => {
  const vehicle = await Vehicle.findOneAndDelete({ id: req.params.id });
  if (!vehicle) return res.status(404).send('Vehicle not found');
  res.json(vehicle);
});

app.listen(port, () => {
  console.log(`🚗 API running at http://localhost:${port}`);
});
