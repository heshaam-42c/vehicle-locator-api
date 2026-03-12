import swaggerJsdoc from 'swagger-jsdoc';

const options = {
    definition: {
        openapi: '3.0.3',
        info: {
            title: 'Vehicle Locator API',
            description: 'API to track and manage vehicle locations',
            version: '1.0.0',
        },
        servers: [{ url: 'http://localhost:3000' }],
        security: [{ bearerAuth: [] }],
        components: {
            schemas: {
                ErrorMessage: {
                    required: ['message'],
                    type: 'object',
                    properties: {
                        message: { type: 'string' },
                    },
                },
                UserRegistrationData: {
                    required: ['is_admin', 'name', 'pass', 'email'],
                    type: 'object',
                    example: {
                        email: 'register@test.com',
                        pass: 'testpassword',
                        name: 'VehicleUser',
                        is_admin: false,
                    },
                    properties: {
                        email: { type: 'string' },
                        pass: { type: 'string' },
                        name: { type: 'string' },
                        is_admin: { type: 'boolean' },
                    },
                },
                Vehicle: {
                    type: 'object',
                },
                VehicleInput: {
                    type: 'object',
                    required: ['vin', 'lat', 'lng', 'make', 'model', 'year', 'color'],
                    properties: {
                        vin:   { type: 'string' },
                        lat:   { type: 'number', format: 'float' },
                        lng:   { type: 'number', format: 'float' },
                        make:  { type: 'string' },
                        model: { type: 'string' },
                        year:  { type: 'integer' },
                        color: { type: 'string' },
                    },
                },
                LocationUpdate: {
                    type: 'object',
                    required: ['lat', 'lng'],
                    properties: {
                        lat: { type: 'number', format: 'float' },
                        lng: { type: 'number', format: 'float' },
                    },
                },
            },
            securitySchemes: {
                bearerAuth: {
                    type: 'http',
                    scheme: 'bearer',
                    bearerFormat: 'JWT',
                },
            },
        },
    },
    apis: ['./routes/*.js'],
};

export const swaggerSpec = swaggerJsdoc(options);
