const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000/api"

export interface ApiError {
  detail: string
}

export class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl
  }

  private getToken(): string | null {
    if (typeof window !== "undefined") {
      return localStorage.getItem("token")
    }
    return null
  }

  setToken(token: string | null) {
    if (typeof window !== "undefined") {
      if (token) {
        localStorage.setItem("token", token)
      } else {
        localStorage.removeItem("token")
      }
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    const token = this.getToken()
    const headers: HeadersInit = {
      "Content-Type": "application/json",
      ...options.headers,
    }

    if (token) {
      headers["Authorization"] = `Bearer ${token}`
    }

    const response = await fetch(url, {
      ...options,
      headers,
    })

    if (!response.ok) {
      // Handle 401 Unauthorized - redirect to login
      if (response.status === 401) {
        this.setToken(null)
        if (typeof window !== "undefined") {
          window.location.href = "/login"
        }
      }

      const error: ApiError = await response.json().catch(() => ({
        detail: "An error occurred",
      }))
      throw new Error(error.detail || "Request failed")
    }

    return response.json()
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: "GET" })
  }

  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: "POST",
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  async put<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: "PUT",
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: "DELETE" })
  }

  async getIncidentForecast(incidentId: number | string) {
    return this.get<{
      incident_id: number
      forecasts: any[]
      computed_at: string
    }>(`/incidents/${incidentId}/forecast`)
  }

  async getAgentTrace(incidentId: number | string) {
    return this.get<{
      incident_id: number
      session_id: string | null
      events: any[]
    }>(`/incidents/${incidentId}/agent-trace`)
  }
}

export const apiClient = new ApiClient()
