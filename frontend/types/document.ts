export interface DocumentMetadata {
  document_id: string
  filename: string
  file_type: 'pdf' | 'doc' | 'docx' | 'image' | 'text'
  file_size: number
  upload_timestamp: string
  processing_timestamp?: string
  status: 'uploaded' | 'processing' | 'completed' | 'failed'
  user_id?: string
  extraction_method?: string
  ocr_confidence?: number
  language_detected?: string
  storage_path: string
  processed_path?: string
}

export interface SimplifiedDocument {
  document_id: string
  original_filename: string
  summary: string
  key_points: string[]
  important_terms: Record<string, string>
  deadlines_obligations: string[]
  warnings: string[]
  next_steps: string[]
  processing_timestamp: string
  simplification_level: string
  confidence_score: number
  original_text?: string
  word_count_original: number
  word_count_simplified: number
  reading_level: string
}

export interface DocumentUploadResponse {
  document_id: string
  filename: string
  file_type: 'pdf' | 'doc' | 'docx' | 'image' | 'text'
  file_size: number
  upload_timestamp: string
  status: 'uploaded' | 'processing' | 'completed' | 'failed'
  message: string
}

export interface DocumentProcessingRequest {
  document_id: string
  simplification_level: 'basic' | 'standard' | 'detailed'
  include_original: boolean
  target_audience: 'general_public' | 'business_owners' | 'individuals' | 'students'
}

export interface ErrorResponse {
  error: string
  message: string
  detail?: string
  timestamp: string
}

export interface HealthCheckResponse {
  status: string
  timestamp: string
  version: string
  services: Record<string, string>
}

export interface BatchProcessingRequest {
  document_ids: string[]
  simplification_level: 'basic' | 'standard' | 'detailed'
  target_audience: 'general_public' | 'business_owners' | 'individuals' | 'students'
  include_original: boolean
}

export interface BatchProcessingResponse {
  batch_id: string
  total_documents: number
  processed_documents: number
  failed_documents: number
  results: SimplifiedDocument[]
  errors: ErrorResponse[]
  processing_time: number
}

export interface AnalyticsData {
  document_id: string
  user_id?: string
  action: string
  timestamp: string
  metadata: Record<string, any>
  processing_time?: number
  file_size?: number
  simplification_level?: string
  confidence_score?: number
  user_feedback?: string
}

export interface UsageStatistics {
  period: {
    start_date: string
    end_date: string
  }
  total_actions: number
  unique_documents: number
  unique_users: number
  uploads: number
  processing_events: number
  views: number
  deletions: number
  average_processing_time: number
  average_confidence_score: number
  feedback_count: number
}

export interface PerformanceMetrics {
  period: {
    start_date: string
    end_date: string
  }
  daily_metrics: Array<{
    date: string
    daily_actions: number
    daily_documents: number
    daily_users: number
    average_processing_time: number
    average_confidence_score: number
    slow_processing_count: number
    low_confidence_count: number
  }>
}

export interface DocumentTypeStats {
  file_type: string
  count: number
  average_file_size: number
}

export interface SimplificationEffectiveness {
  simplification_levels: Array<{
    simplification_level: string
    count: number
    average_confidence: number
    average_processing_time: number
    feedback_count: number
  }>
}
