# BigQuery 500 Error Fix - Architecture Guide

## Problem Solved

The 500 error was occurring because the system was trying to store raw file content directly in BigQuery, which expects JSON-compatible data. This guide explains the fixed architecture and how to set it up properly.

## Fixed Architecture Overview

### ✅ Correct Architecture (Implemented)

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Upload   │───▶│  Cloud Storage   │───▶│   BigQuery      │
│   (PDF/DOC/etc) │    │  (Raw Files)     │    │  (Metadata Only)│
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ Document AI/     │
                       │ Vision API       │
                       │ (Processing)     │
                       └──────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ Cloud Storage    │
                       │ (Processed JSON) │
                       └──────────────────┘
```

### ❌ Previous Problematic Architecture

```
┌─────────────────┐    ┌──────────────────┐
│   User Upload   │───▶│   BigQuery       │
│   (Raw Files)   │    │   (Raw Content)  │ ❌
└─────────────────┘    └──────────────────┘
```

## Key Changes Made

### 1. BigQuery Schema Updates

**Fixed Data Types:**
- Changed `FLOAT` to `FLOAT64` for better compatibility
- Added proper retry logic for streaming buffer issues
- Added new `processing_results` table for analytics

**New Tables Created:**
- `document_metadata` - Stores file metadata only
- `usage_analytics` - Tracks user interactions
- `processing_results` - Stores structured processing results

### 2. Enhanced File Processing

**Google Cloud Vision Integration:**
- Prioritizes Google Cloud Vision API for image OCR
- Falls back to Tesseract if Vision API unavailable
- Extracts OCR confidence scores

**Document AI Integration:**
- Added Google Cloud Document AI client
- Better PDF processing for complex documents
- Structured text extraction

### 3. Improved Error Handling

**BigQuery Insertion:**
- Added retry logic with exponential backoff
- Proper data type conversion
- Streaming buffer error handling

**File Processing:**
- Multiple fallback methods for text extraction
- Better error logging and recovery

## Setup Instructions

### 1. Google Cloud Project Setup

```bash
# Set your project ID
export GOOGLE_CLOUD_PROJECT_ID="your-project-id"

# Enable required APIs
gcloud services enable storage.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable vision.googleapis.com
gcloud services enable documentai.googleapis.com
```

### 2. Service Account Configuration

```bash
# Create service account
gcloud iam service-accounts create ai-tool-service \
    --display-name="AI Tool Service Account"

# Grant necessary permissions
gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT_ID \
    --member="serviceAccount:ai-tool-service@$GOOGLE_CLOUD_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT_ID \
    --member="serviceAccount:ai-tool-service@$GOOGLE_CLOUD_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT_ID \
    --member="serviceAccount:ai-tool-service@$GOOGLE_CLOUD_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/vision.user"

gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT_ID \
    --member="serviceAccount:ai-tool-service@$GOOGLE_CLOUD_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/documentai.apiUser"

# Create and download key
gcloud iam service-accounts keys create ./service-account-key.json \
    --iam-account=ai-tool-service@$GOOGLE_CLOUD_PROJECT_ID.iam.gserviceaccount.com
```

### 3. Environment Variables

Create a `.env` file:

```env
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json

# Cloud Storage
CLOUD_STORAGE_BUCKET=your-bucket-name

# BigQuery
BIGQUERY_DATASET=legal_documents
BIGQUERY_TABLE_USAGE=usage_analytics
BIGQUERY_TABLE_DOCUMENTS=document_metadata

# AI Services
GEMINI_API_KEY=your-gemini-api-key
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_MODEL_NAME=gemini-pro
```

### 4. Cloud Storage Bucket Setup

```bash
# Create bucket
gsutil mb gs://your-bucket-name

# Set bucket permissions
gsutil iam ch serviceAccount:ai-tool-service@$GOOGLE_CLOUD_PROJECT_ID.iam.gserviceaccount.com:objectAdmin gs://your-bucket-name
```

### 5. BigQuery Dataset Setup

```bash
# Create dataset
bq mk --dataset $GOOGLE_CLOUD_PROJECT_ID:legal_documents

# Grant permissions
bq show --format=prettyjson $GOOGLE_CLOUD_PROJECT_ID:legal_documents
```

## Data Flow

### 1. Document Upload
1. User uploads file (PDF, DOC, image, etc.)
2. File stored in Cloud Storage
3. Metadata extracted and stored in BigQuery
4. Processing status set to "uploaded"

### 2. Document Processing
1. Text extracted using appropriate method:
   - **PDFs**: Document AI → pdfplumber → PyPDF2 → OCR
   - **Images**: Google Vision → Tesseract
   - **DOCX**: python-docx
2. AI simplification applied
3. Results stored in Cloud Storage as JSON
4. Processing results stored in BigQuery for analytics

### 3. Data Storage
- **Cloud Storage**: Raw files + processed JSON
- **BigQuery**: Metadata + analytics data only
- **No raw file content in BigQuery**

## Monitoring and Analytics

### BigQuery Queries

```sql
-- Document processing statistics
SELECT 
    file_type,
    COUNT(*) as document_count,
    AVG(confidence_score) as avg_confidence,
    AVG(word_count_original) as avg_original_words,
    AVG(word_count_simplified) as avg_simplified_words
FROM `your-project.legal_documents.processing_results`
GROUP BY file_type;

-- Processing performance
SELECT 
    DATE(processing_timestamp) as date,
    COUNT(*) as documents_processed,
    AVG(processing_time_seconds) as avg_processing_time
FROM `your-project.legal_documents.processing_results`
GROUP BY date
ORDER BY date DESC;

-- User activity
SELECT 
    user_id,
    COUNT(*) as documents_uploaded,
    SUM(file_size) as total_size_bytes
FROM `your-project.legal_documents.document_metadata`
WHERE user_id IS NOT NULL
GROUP BY user_id
ORDER BY documents_uploaded DESC;
```

## Troubleshooting

### Common Issues

1. **BigQuery Streaming Buffer Errors**
   - Fixed with retry logic and exponential backoff
   - Check BigQuery quotas and limits

2. **Cloud Vision API Errors**
   - Verify API is enabled
   - Check service account permissions
   - Monitor API quotas

3. **Document AI Setup**
   - Requires processor configuration
   - Currently using fallback methods

### Error Monitoring

```python
# Check service health
curl http://localhost:8000/health

# Monitor logs
gcloud logging read "resource.type=cloud_function" --limit=50
```

## Performance Optimizations

1. **Parallel Processing**: Multiple extraction methods run concurrently
2. **Caching**: Processed documents cached in Cloud Storage
3. **Retry Logic**: Handles temporary failures gracefully
4. **Structured Data**: Only metadata in BigQuery for fast queries

## Security Considerations

1. **Service Account**: Minimal required permissions
2. **Data Encryption**: Cloud Storage encryption at rest
3. **Access Control**: IAM-based permissions
4. **Audit Logging**: All operations logged

## Cost Optimization

1. **Storage Classes**: Use appropriate Cloud Storage classes
2. **BigQuery**: Only store necessary metadata
3. **API Usage**: Monitor Vision API and Document AI usage
4. **Lifecycle Policies**: Auto-delete old files

This architecture ensures reliable document processing while maintaining cost efficiency and proper data separation between storage and analytics systems.
