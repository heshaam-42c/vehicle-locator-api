import express from 'express';
import {
    userLogin,
    userRegistration
} from '../controllers/authController.js'

const router = express.Router();

/**
 * @openapi
 * /user/register:
 *   post:
 *     tags:
 *       - anyone
 *     security: []
 *     summary: register for an account
 *     description: user supplies email and password to register and receives a json web token.
 *     operationId: register
 *     x-42c-no-authentication: true
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/UserRegistrationData'
 *     responses:
 *       200:
 *         description: successfully registered, token received
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *       default:
 *         description: unexpected error
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ErrorMessage'
 */
router.route('/register')
    .post(userRegistration)

/**
 * @openapi
 * /user/login:
 *   post:
 *     tags:
 *       - anyone
 *     security: []
 *     summary: user/password based login
 *     description: user supplies user name and password and receives a json web token
 *     operationId: authenticate
 *     x-42c-no-authentication: true
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             required:
 *               - pass
 *               - email
 *             type: object
 *             properties:
 *               email:
 *                 type: string
 *               pass:
 *                 type: string
 *     responses:
 *       200:
 *         description: 200 OK
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *       default:
 *         description: unexpected error
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ErrorMessage'
 */
router.route('/login')
    .post(userLogin)

export default router;