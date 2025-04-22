import jwt from 'jsonwebtoken';
import fs from 'fs';

// PRIVATE and PUBLIC key
var publicKey = fs.readFileSync('./keys/public.key', 'utf8');

function create_jwt(algorithm, audience, issuer, subject, jwt_payload, key) {
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

export {
    create_jwt,
    api_token_check
}