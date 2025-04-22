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

router.route('/')
    .get(api_token_check, getVehicles)
    .post(api_token_check, addVehicle)

router.route('/:id')
    .get(api_token_check, getVehicle)
    .delete(api_token_check, deleteVehicle)

router.route('/:id/location')
    .put(api_token_check, updateVehicle)

export default router;