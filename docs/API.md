# API Documentation

The AI Legal Document Simplifier provides a RESTful API for document processing and simplification.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-backend-url.run.app`

## Authentication

Currently, the API does not require authentication for basic operations. Future versions will include JWT-based authentication.

## Endpoints

### Health Check

Check the health status of the API and its dependencies.

```http
GET /api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "services": {
    "api": "healthy",
    "storage": "healthy",
    "ai_service": "healthy",
    "analytics": "healthy"
  }
}
```

### Upload Document

Upload a legal document for processing.

```http
POST /api/v1/documents/upload
Content-Type: multipart/form-data
```

**Parameters:**
- `file` (required): The document file (PDF, DOC, DOCX, or image)
- `user_id` (optional): User identifier for analytics

**Response:**
```json
{
  "document_id": "uuid-string",
  "filename": "contract.pdf",
  "file_type": "pdf",
  "file_size": 1024000,
  "upload_timestamp": "2024-01-15T10:30:00Z",
  "status": "uploaded",
  "message": "Document uploaded successfully"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid file type or size
- `413 Payload Too Large`: File exceeds size limit
- `500 Internal Server Error`: Upload failed

### Process Document

Process and simplify an uploaded document.

```http
POST /api/v1/documents/{document_id}/process
Content-Type: application/json
```

**Request Body:**
```json
{
  "document_id": "uuid-string",
  "simplification_level": "standard",
  "include_original": false,
  "target_audience": "general_public"
}
```

**Parameters:**
- `simplification_level`: `"basic"`, `"standard"`, or `"detailed"`
- `include_original`: Include original text in response
- `target_audience`: `"general_public"`, `"business_owners"`, `"individuals"`, or `"students"`

**Response:**
```json
{
  "document_id": "uuid-string",
  "original_filename": "contract.pdf",
  "summary": "This is a service agreement between...",
  "key_points": [
    "The agreement is for 12 months",
    "Payment is due monthly",
    "Either party can terminate with 30 days notice"
  ],
  "important_terms": {
    "Service Agreement": "A contract for providing services",
    "Termination Clause": "Conditions for ending the agreement"
  },
  "deadlines_obligations": [
    "Payment due on the 1st of each month",
    "30-day notice required for termination"
  ],
  "warnings": [
    "Late payments may incur additional fees",
    "Service may be suspended for non-payment"
  ],
  "next_steps": [
    "Review all terms carefully",
    "Contact legal counsel if needed",
    "Sign and return the agreement"
  ],
  "processing_timestamp": "2024-01-15T10:35:00Z",
  "simplification_level": "standard",
  "confidence_score": 0.85,
  "word_count_original": 2500,
  "word_count_simplified": 800,
  "reading_level": "intermediate"
}
```

### Get Simplified Document

Retrieve a previously processed document.

```http
GET /api/v1/documents/{document_id}
```

**Response:** Same as Process Document response

### Get Document Metadata

Get metadata for an uploaded document.

```http
GET /api/v1/documents/{document_id}/metadata
```

**Response:**
```json
{
  "document_id": "uuid-string",
  "filename": "contract.pdf",
  "file_type": "pdf",
  "file_size": 1024000,
  "upload_timestamp": "2024-01-15T10:30:00Z",
  "processing_timestamp": "2024-01-15T10:35:00Z",
  "status": "completed",
  "user_id": "user-123",
  "extraction_method": "pdfplumber",
  "ocr_confidence": null,
  "language_detected": "en",
  "storage_path": "uploads/uuid-string/contract.pdf",
  "processed_path": "processed/uuid-string/simplified.json"
}
```

### Batch Process Documents

Process multiple documents in batch.

```http
POST /api/v1/documents/batch/process
Content-Type: application/json
```

**Request Body:**
```json
{
  "document_ids": ["uuid-1", "uuid-2", "uuid-3"],
  "simplification_level": "standard",
  "target_audience": "general_public",
  "include_original": false
}
```

**Response:**
```json
{
  "batch_id": "batch-uuid",
  "total_documents": 3,
  "processed_documents": 2,
  "failed_documents": 1,
  "results": [
    // Array of SimplifiedDocument objects
  ],
  "errors": [
    {
      "error": "processing_error",
      "message": "Failed to process document uuid-3",
      "detail": "Text extraction failed"
    }
  ],
  "processing_time": 45.2
}
```

### Delete Document

Delete a document and all associated data.

```http
DELETE /api/v1/documents/{document_id}
```

**Response:**
```json
{
  "message": "Document deleted successfully"
}
```

## Analytics Endpoints

### Get Usage Statistics

```http
GET /api/v1/analytics/usage?start_date=2024-01-01&end_date=2024-01-31
```

**Response:**
```json
{
  "period": {
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-01-31T23:59:59Z"
  },
  "total_actions": 1250,
  "unique_documents": 450,
  "unique_users": 200,
  "uploads": 450,
  "processing_events": 400,
  "views": 300,
  "deletions": 50,
  "average_processing_time": 12.5,
  "average_confidence_score": 0.82,
  "feedback_count": 25
}
```

### Get Performance Metrics

```http
GET /api/v1/analytics/performance?start_date=2024-01-01&end_date=2024-01-31
```

**Response:**
```json
{
  "period": {
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-01-31T23:59:59Z"
  },
  "daily_metrics": [
    {
      "date": "2024-01-01",
      "daily_actions": 45,
      "daily_documents": 20,
      "daily_users": 15,
      "average_processing_time": 11.2,
      "average_confidence_score": 0.85,
      "slow_processing_count": 2,
      "low_confidence_count": 1
    }
    // ... more daily metrics
  ]
}
```

### Get Document Analytics

```http
GET /api/v1/analytics/documents/{document_id}
```

**Response:**
```json
{
  "document_id": "uuid-string",
  "total_events": 5,
  "unique_actions": 3,
  "first_event": "2024-01-15T10:30:00Z",
  "last_event": "2024-01-15T11:00:00Z",
  "uploads": 1,
  "processing_events": 1,
  "views": 2,
  "average_processing_time": 12.5,
  "average_confidence_score": 0.85,
  "feedback_count": 1
}
```

### Track User Feedback

```http
POST /api/v1/analytics/track
Content-Type: application/json
```

**Request Body:**
```json
{
  "document_id": "uuid-string",
  "user_id": "user-123",
  "action": "user_feedback",
  "metadata": {
    "rating": 5
  },
  "user_feedback": "Very helpful simplification!"
}
```

## Error Handling

All endpoints return appropriate HTTP status codes and error messages.

### Error Response Format

```json
{
  "error": "error_type",
  "message": "Human-readable error message",
  "detail": "Detailed error information (in debug mode)",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Common Error Codes

- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `413 Payload Too Large`: File size exceeds limit
- `422 Unprocessable Entity`: Document processing failed
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily unavailable

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **General endpoints**: 100 requests per hour per IP
- **Upload endpoint**: 10 requests per hour per IP
- **Processing endpoint**: 20 requests per hour per IP

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248000
```

## File Upload Limits

- **Maximum file size**: 10MB
- **Supported formats**: PDF, DOC, DOCX, JPEG, PNG, TIFF, TXT
- **Processing timeout**: 2 minutes per document

## WebSocket Support (Future)

Real-time processing updates will be available via WebSocket:

```javascript
const ws = new WebSocket('wss://api.example.com/ws/processing/{document_id}');

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  console.log('Processing update:', update);
};
```

## SDKs and Libraries

### JavaScript/TypeScript

```javascript
import { ApiClient } from '@legal-ai/sdk';

const client = new ApiClient({
  baseUrl: 'https://api.example.com',
  apiKey: 'your-api-key'
});

// Upload and process document
const result = await client.processDocument(file, {
  simplificationLevel: 'standard',
  targetAudience: 'general_public'
});
```

### Python

```python
from legal_ai import ApiClient

client = ApiClient(
    base_url='https://api.example.com',
    api_key='your-api-key'
)

# Upload and process document
result = client.process_document(
    file_path='contract.pdf',
    simplification_level='standard',
    target_audience='general_public'
)
```

## Changelog

### Version 1.0.0
- Initial API release
- Document upload and processing
- Basic analytics endpoints
- Batch processing support

### Future Versions
- Authentication and authorization
- WebSocket real-time updates
- Advanced analytics and reporting
- Custom simplification templates
- Multi-language support
