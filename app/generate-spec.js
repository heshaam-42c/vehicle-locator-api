import { writeFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import { swaggerSpec } from './swagger.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const outputPath = resolve(__dirname, '../openapi-spec/openapi-spec.json');

writeFileSync(outputPath, JSON.stringify(swaggerSpec, null, 4));
console.log(`OpenAPI spec written to ${outputPath}`);
