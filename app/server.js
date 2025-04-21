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


function api_authenticate(user, pass, req, res) {
  console.log('>>> Logging user ' + user + ' with password: ' + pass);
  const users = db.collection('users');

  users.findOne({ email: user, password: pass }, function (err, result) {
    if (err) {
      console.log('>>> Query error...' + err);
      res.status(500).json({ "message": "system error" });
    }
    if (result !== null) {
      // API10: This is bad logging, as it dumps the full user record
      console.log('>>> Found User:  ' + result);
      var user_profile = result;
      // API7/API3: Add full record to JWT token (including clear password)
      var payload = { user_profile };
      var token = create_jwt ('RS384', 'pixiUsers', 'https://issuer.42crunch.demo', user_profile.email, payload, privateKey);
      res.status(200).json({ message: "success", token: token, _id: user_profile._id });
    }
    else
      res.status(401).json({ message: "sorry dear, invalid login" });
  });
}

function api_register(user, pass, req, res) {
  console.log('>>> Registering user: ' + user + ' with password: ' + pass);
  const users = db.collection('users');
  // Check if user exists first
  users.findOne({ email: user }, function (err, result) {
    if (err) {
      console.log('>>> Query error...' + err);
      res.status(500).json({ "message": "system error" });
    }
    if (result !== null) {
      // Bad message: the error message should not indicate what the error is.
      res.status(400).json({ "message": "user is already registered" });
    }
    else {
      if (req.body.is_admin) {
        var admin = true;
      }
      else {
        var admin = false
      }
      var name = req.body.name;
      var subject = user;
      console.log(">>> Username: " + name);
      // Voluntary error to return an exception is the account_balance is negative.
      if (req.body.account_balance < 0) {
        var err = new Error().stack;
        res.status(400).json(err);
        return;
      }
      var payload = {
        _id: uuidv4(),
        email: user,
        password: pass,
        name: name,
        account_balance: req.body.account_balance,
        is_admin: admin,
        onboarding_date: new Date()
      };
      // forceServerObjectId forces Mongo to use the specified _id instead of generating a random one.
      users.insertOne(payload, { forceServerObjectId: true }, function (err, user) {
        if (err) {
          console.log('>>> Query error...' + err);
          res.status(500).json({ "message": "system error" });
        }
        if (user.insertedId != null) {
          var user_profile = payload;
          var jwt_payload = { user_profile };
          try {
            var token = create_jwt ('RS384', 'pixiUsers', 'https://issuer.42crunch.demo', subject, jwt_payload, privateKey);
            res.status(200).json({ message: "success", token: token, _id: payload._id });
          }
          catch {
            console.log(">>> Error occurred during JWT creation");
            res.status(400).json({ message: "registration failure", token: null, _id: null });
          }
        } //if user
      }) //insert
    } // else
  });
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

  console.log('>>> Validating token: ' + JSON.stringify(req.headers['x-access-token']));
  var token = req.headers['x-access-token'];

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
app.post('/api/user/login', async (req, res) => {
	if ((!req.body.user) || (!req.body.pass)) {
		res.status(422).json({ "message": "missing username and or password parameters" });
	}
	else {
		api_authenticate(req.body.user, req.body.pass, req, res);
	}
})

app.post('/api/user/register', async (req, res) => {
	if ((!req.body.user) || (!req.body.pass)) {
		res.status(422).json({ "message": "missing username and or password parameters" });
	} else if (req.body.pass.length <= 4) {
		res.status(422).json({ "message": "password length too short, minimum of 5 characters" })
	} else {
		api_register(req.body.user, req.body.pass, req, res);
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

  const vehicle = await Vehicle.findOneAndUpdate(
    { id: req.params.id },
    { lat, lng },
    { new: true }
  );

  if (!vehicle) return res.status(404).send('Vehicle not found');

  res.json(vehicle);
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
