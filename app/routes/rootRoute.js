import express from 'express';
import {     
    getRoot
 } from '../controllers/rootController.js';

const router  = express.Router();

router.route('/')
    .get(getRoot)

export default router;