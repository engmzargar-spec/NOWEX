export interface User {
  id: string
  email: string
  name: string
  role: "user" | "admin"
  status: "active" | "inactive" | "suspended"
  createdAt: string
  updatedAt: string
}

export interface CreateUserRequest {
  email: string
  password: string
  name: string
  role?: User["role"]
}

export interface UpdateUserRequest {
  name?: string
  status?: User["status"]
}
