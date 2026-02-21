import { apiClient } from "./api"

export interface User {
  id: number
  email: string
  role: string
  created_at: string
}

export interface SignupRequest {
  email: string
  password: string
  role: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  token: string
  user: User
}

export async function signup(
  email: string,
  password: string,
  role: string
): Promise<LoginResponse> {
  const response = await apiClient.post<LoginResponse>("/auth/signup", {
    email,
    password,
    role,
  })
  apiClient.setToken(response.token)
  return response
}

export async function login(email: string, password: string): Promise<LoginResponse> {
  const response = await apiClient.post<LoginResponse>("/auth/login", {
    email,
    password,
  })
  apiClient.setToken(response.token)
  return response
}

export function logout() {
  apiClient.setToken(null)
  if (typeof window !== "undefined") {
    window.location.href = "/login"
  }
}

export function getToken(): string | null {
  if (typeof window !== "undefined") {
    return localStorage.getItem("token")
  }
  return null
}
