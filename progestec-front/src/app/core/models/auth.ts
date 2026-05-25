// src/app/core/models/auth.ts

import { CurrentUser } from './user';

export interface LoginRequest {
    email: string;
    password: string;
}

export interface LoginResponse {
    access_token: string;
    token_type: string;
    must_change_password: boolean;
    // si después tu backend devuelve el usuario, lo añadimos:
    user?: CurrentUser;
}

export interface SetPasswordRequest {
    new_password: string;
}

export interface MessageResponse {
    message: string;
}
