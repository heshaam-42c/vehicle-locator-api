import express from 'express';
import { api_token_check } from "../middleware/authHandlers.js";
import {     
    getVehicles,
    getVehicle,
    addVehicle,
    updateVehicle,
    deleteVehicle
 } from '../controllers/vehicleController.js';

const router  = express.Router();

/**
 * @openapi
 * /vehicles:
 *   get:
 *     summary: Get all vehicles
 *     operationId: getVehicles
 *     security: []
 *     responses:
 *       200:
 *         description: A list of all vehicles
 *         content:
 *           application/json:
 *             schema:
 *               type: array
 *               items:
 *                 $ref: '#/components/schemas/Vehicle'
 *   post:
 *     summary: Add a new vehicle
 *     operationId: postVehicle
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/VehicleInput'
 *     responses:
 *       201:
 *         description: Vehicle created
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/Vehicle'
 *       default:
 *         description: Unexpected error
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ErrorMessage'
 */
router.route('/')
    // API2 - Missing Authentication: enforce auth so only authenticated users can list vehicles
    .get(api_token_check, getVehicles)
    .post(api_token_check, addVehicle)

/**
 * @openapi
 * /vehicles/{id}:
 *   get:
 *     summary: Get a vehicle by ID
 *     operationId: getVehicleById
 *     parameters:
 *       - name: id
 *         in: path
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: Vehicle found
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/Vehicle'
 *       default:
 *         description: Unexpected error
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ErrorMessage'
 *   delete:
 *     summary: Delete a vehicle by ID
 *     operationId: deleteVehicleById
 *     parameters:
 *       - name: id
 *         in: path
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: Vehicle deleted
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/Vehicle'
 *       default:
 *         description: Unexpected error
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ErrorMessage'
 */
router.route('/:id')
    .get(api_token_check, getVehicle)
    .delete(api_token_check, deleteVehicle)

/**
 * @openapi
 * /vehicles/{id}/location:
 *   put:
 *     summary: Update vehicle location
 *     operationId: updateVehicleLocation
 *     parameters:
 *       - name: id
 *         in: path
 *         required: true
 *         schema:
 *           type: string
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/LocationUpdate'
 *     responses:
 *       200:
 *         description: Location updated
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/Vehicle'
 *       default:
 *         description: Unexpected error
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ErrorMessage'
 */
router.route('/:id/location')
    .put(api_token_check, updateVehicle)

export default router;