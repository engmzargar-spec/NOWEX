"use client"

import { useState, useEffect } from "react"
import { defaultApiClient } from "./api-client"
import type { LoginRequest, LoginResponse, ApiError } from "@nowex/types"

export const useAuth = () => {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<ApiError | null>(null)

  const login = async (data: LoginRequest) => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await defaultApiClient.login(data)
      localStorage.setItem("access_token", response.access_token)
      localStorage.setItem("refresh_token", response.refresh_token)
      return response
    } catch (err) {
      setError(err as ApiError)
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async () => {
    try {
      await defaultApiClient.logout()
    } finally {
      localStorage.removeItem("access_token")
      localStorage.removeItem("refresh_token")
    }
  }

  const isAuthenticated = () => {
    return !!localStorage.getItem("access_token")
  }

  return {
    login,
    logout,
    isAuthenticated,
    isLoading,
    error,
  }
}