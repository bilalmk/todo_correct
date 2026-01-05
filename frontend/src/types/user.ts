/**
 * User type definitions
 */

export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface UserCreate {
  email: string;
  password: string;
  name: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface JWTPayload {
  sub: string; // user_id
  email: string;
  exp: number; // expiration timestamp
  iat: number; // issued at timestamp
  type: "access";
}

export interface Session {
  user: {
    id: string;
    email: string;
    name: string;
  };
  session: {
    userId: string;
    expiresAt: Date;
    token: string;
  };
}
