import express from 'express';
import {
    getRoot
 } from '../controllers/rootController.js';

const router  = express.Router();

/**
 * @openapi
 * /:
 *   get:
 *     summary: API status
 *     operationId: getStatus
 *     security: []
 *     responses:
 *       200:
 *         description: Welcome message
 */
router.route('/')
    .get(getRoot)

export default router;