import mongoose from 'mongoose';

// User schema & model
const userSchema = new mongoose.Schema(
    {
        id: { type: String, required: true, unique: true },
        email: { type: String, required: true, unique: true },
        pass: { type: String, required: true },
        name: { type: String, required: true },
        is_admin: { type: Boolean, required: true }
    }, {
        versionKey: false
    }
);  

const UserModel = mongoose.model('User', userSchema);

export default UserModel;