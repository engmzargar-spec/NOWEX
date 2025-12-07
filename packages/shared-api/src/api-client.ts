import axios, { AxiosInstance, AxiosRequestConfig } from "axios"
import type { ApiError, LoginRequest, LoginResponse } from "@nowex/types"

export class ApiClient {
  private client: AxiosInstance
  private baseURL: string

  constructor(baseURL: string = "http://localhost:8000") {
    this.baseURL = baseURL
    this.client = axios.create({
      baseURL,
      timeout: 10000,
      headers: {
        "Content-Type": "application/json",
      },
    })

    // Add request interceptor for auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem("access_token")
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        const apiError: ApiError = {
          code: error.response?.data?.code || "UNKNOWN_ERROR",
          message: error.response?.data?.message || error.message,
          details: error.response?.data?.details,
        }
        return Promise.reject(apiError)
      }
    )
  }

  // Auth methods
  async login(data: LoginRequest): Promise<LoginResponse> {
    const response = await this.client.post("/auth/login", data)
    return response.data
  }

  async logout(): Promise<void> {
    await this.client.post("/auth/logout")
  }

  // Generic methods
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get(url, config)
    return response.data
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post(url, data, config)
    return response.data
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.put(url, data, config)
    return response.data
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete(url, config)
    return response.data
  }
}

// Default instance
export const defaultApiClient = new ApiClient()
