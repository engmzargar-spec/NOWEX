"use client"

import { useState } from "react"
import { defaultApiClient } from "./api-client"
import type { User, ApiError } from "@nowex/types"

export const useUsers = () => {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<ApiError | null>(null)

  const getUsers = async (page = 1, limit = 10) => {
    setIsLoading(true)
    setError(null)
    try {
      const users = await defaultApiClient.get<User[]>(
        `/admin/users?page=${page}&limit=${limit}`
      )
      return users
    } catch (err) {
      setError(err as ApiError)
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  const getUserById = async (id: string) => {
    setIsLoading(true)
    setError(null)
    try {
      const user = await defaultApiClient.get<User>(`/admin/users/${id}`)
      return user
    } catch (err) {
      setError(err as ApiError)
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  return {
    getUsers,
    getUserById,
    isLoading,
    error,
  }
}