import UserModel from '../models/userModel.js';
import { create_jwt } from "../middleware/authHandlers.js";
import { v4 as uuidv4 } from 'uuid';
import fs from 'fs';

// PRIVATE and PUBLIC key
var privateKey = fs.readFileSync('./keys/private.key', 'utf8');

// user related.
async function userLogin (req, res) {
	if ((!req.body.email) || (!req.body.pass)) {
		res.status(422).json({ "message": "missing username and or password parameters" });
    // API8:2019 - Injection
    // Solution: Validate input types
	// } else if ((typeof req.body.email !== 'string') || (typeof req.body.pass !== 'string')){
    //     res.status(400).json({ "message": "invalid username and or password parameters" });
    } else {
		api_authenticate(req.body.email, req.body.pass, req, res);
	}
}

async function userRegistration (req, res) {
	if ((!req.body.email) || (!req.body.pass)) {
		res.status(422).json({ "message": "missing email and or password parameters" });
	} else if (req.body.pass.length <= 4) {
		res.status(422).json({ "message": "password length too short, minimum of 5 characters" })
	} else {
		api_register(req.body.email, req.body.pass, req, res);
	}
}

async function api_authenticate(email, pass, req, res) {
    console.log('>>> Logging user ' + email + ' with password: ' + pass);

    try {
        let user = await UserModel.findOne({ email: email, pass: pass });

        if (!user) {
            return res.status(401).json({ message: "Invalid email or password" });
        } else {
            // Create JWT token
            var token = create_jwt('RS384', 'vehicleLocatorUsers', 'https://issuer.42crunch.demo', user.email, { id: user.id }, privateKey);
            res.status(200).json({ message: "success", token: token, _id: user.id });
        }
    } catch (err) {
        console.error('Error during authentication:', err);
        res.status(500).send({ message: "Internal server error" });
    }
}

async function api_register(email, pass, req, res) {
    console.log('>>> Registering user: ' + email + ' with password: ' + pass);

    const name = req.body.name;
    const is_admin = req.body.is_admin || false;

    if (!email || !pass || !name) {
        return res.status(400).json({ message: "Missing required fields: email, password, name" });
    }

    try {
        let user = await UserModel.findOne({ email: email });
        if (user) {
            return res.status(400).json({ message: "User already exists" });
        } else {
            user = new UserModel({ email, pass, name, is_admin });
            user.id = uuidv4();
            await user.save();
            res.status(200).json({ message: "success", _id: user.id });
        }
    } catch (err) {
        if (err.code === 11000) {
            res.status(409).json({ message: "User ID already exists - " + err.message });
        } else {
            res.status(500).json({ message: "Error saving user - " + err.message });
        }
    }
}

export {
    userLogin,
    userRegistration
}