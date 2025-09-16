import axios, { AxiosInstance, AxiosResponse } from 'axios'
import {
  DocumentUploadResponse,
  SimplifiedDocument,
  DocumentProcessingRequest,
  DocumentMetadata,
  ErrorResponse,
  HealthCheckResponse,
  BatchProcessingRequest,
  BatchProcessingResponse,
  AnalyticsData,
  UsageStatistics,
  PerformanceMetrics,
  DocumentTypeStats,
  SimplificationEffectiveness,
} from '@/types/document'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
      timeout: 30000, // 30 seconds
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add auth token if available
        const token = localStorage.getItem('auth_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Handle unauthorized access
          localStorage.removeItem('auth_token')
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }

  // Health check
  async healthCheck(): Promise<HealthCheckResponse> {
    const response: AxiosResponse<HealthCheckResponse> = await this.client.get('/api/v1/health')
    return response.data
  }

  // Document upload
  async uploadDocument(
    file: File,
    userId?: string
  ): Promise<DocumentUploadResponse> {
    const formData = new FormData()
    formData.append('file', file)
    if (userId) {
      formData.append('user_id', userId)
    }

    const response: AxiosResponse<DocumentUploadResponse> = await this.client.post(
      '/api/v1/documents/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 60000, // 60 seconds for file upload
      }
    )
    return response.data
  }

  // Process document
  async processDocument(
    documentId: string,
    request: DocumentProcessingRequest
  ): Promise<SimplifiedDocument> {
    const response: AxiosResponse<SimplifiedDocument> = await this.client.post(
      `/api/v1/documents/${documentId}/process`,
      request,
      {
        timeout: 120000, // 2 minutes for processing
      }
    )
    return response.data
  }

  // Get simplified document
  async getSimplifiedDocument(documentId: string): Promise<SimplifiedDocument> {
    const response: AxiosResponse<SimplifiedDocument> = await this.client.get(
      `/api/v1/documents/${documentId}`
    )
    return response.data
  }

  // Get document metadata
  async getDocumentMetadata(documentId: string): Promise<DocumentMetadata> {
    const response: AxiosResponse<DocumentMetadata> = await this.client.get(
      `/api/v1/documents/${documentId}/metadata`
    )
    return response.data
  }

  // Batch process documents
  async batchProcessDocuments(
    request: BatchProcessingRequest
  ): Promise<BatchProcessingResponse> {
    const response: AxiosResponse<BatchProcessingResponse> = await this.client.post(
      '/api/v1/documents/batch/process',
      request,
      {
        timeout: 300000, // 5 minutes for batch processing
      }
    )
    return response.data
  }

  // Delete document
  async deleteDocument(documentId: string): Promise<{ message: string }> {
    const response: AxiosResponse<{ message: string }> = await this.client.delete(
      `/api/v1/documents/${documentId}`
    )
    return response.data
  }

  // Analytics endpoints
  async getUsageStatistics(
    startDate?: string,
    endDate?: string
  ): Promise<UsageStatistics> {
    const params = new URLSearchParams()
    if (startDate) params.append('start_date', startDate)
    if (endDate) params.append('end_date', endDate)

    const response: AxiosResponse<UsageStatistics> = await this.client.get(
      `/api/v1/analytics/usage?${params.toString()}`
    )
    return response.data
  }

  async getPerformanceMetrics(
    startDate?: string,
    endDate?: string
  ): Promise<PerformanceMetrics> {
    const params = new URLSearchParams()
    if (startDate) params.append('start_date', startDate)
    if (endDate) params.append('end_date', endDate)

    const response: AxiosResponse<PerformanceMetrics> = await this.client.get(
      `/api/v1/analytics/performance?${params.toString()}`
    )
    return response.data
  }

  async getDocumentAnalytics(documentId: string): Promise<AnalyticsData> {
    const response: AxiosResponse<AnalyticsData> = await this.client.get(
      `/api/v1/analytics/documents/${documentId}`
    )
    return response.data
  }

  async getUserAnalytics(userId: string): Promise<AnalyticsData> {
    const response: AxiosResponse<AnalyticsData> = await this.client.get(
      `/api/v1/analytics/users/${userId}`
    )
    return response.data
  }

  async getPopularDocumentTypes(): Promise<DocumentTypeStats[]> {
    const response: AxiosResponse<DocumentTypeStats[]> = await this.client.get(
      '/api/v1/analytics/document-types'
    )
    return response.data
  }

  async getSimplificationEffectiveness(): Promise<SimplificationEffectiveness> {
    const response: AxiosResponse<SimplificationEffectiveness> = await this.client.get(
      '/api/v1/analytics/simplification-effectiveness'
    )
    return response.data
  }

  // Track analytics
  async trackDocumentView(
    documentId: string,
    userId?: string,
    viewDuration?: number
  ): Promise<void> {
    await this.client.post('/api/v1/analytics/track', {
      document_id: documentId,
      user_id: userId,
      action: 'document_view',
      metadata: {
        view_duration: viewDuration,
      },
    })
  }

  async trackUserFeedback(
    documentId: string,
    feedback: string,
    rating?: number,
    userId?: string
  ): Promise<void> {
    await this.client.post('/api/v1/analytics/track', {
      document_id: documentId,
      user_id: userId,
      action: 'user_feedback',
      metadata: {
        rating: rating,
      },
      user_feedback: feedback,
    })
  }
}

// Create and export a singleton instance
export const apiClient = new ApiClient()

// Export individual methods for convenience
export const {
  healthCheck,
  uploadDocument,
  processDocument,
  getSimplifiedDocument,
  getDocumentMetadata,
  batchProcessDocuments,
  deleteDocument,
  getUsageStatistics,
  getPerformanceMetrics,
  getDocumentAnalytics,
  getUserAnalytics,
  getPopularDocumentTypes,
  getSimplificationEffectiveness,
  trackDocumentView,
  trackUserFeedback,
} = apiClient
