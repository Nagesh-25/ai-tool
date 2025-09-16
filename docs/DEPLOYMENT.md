# Deployment Guide

This guide covers deploying the AI Legal Document Simplifier to Google Cloud Platform.

## Prerequisites

1. **Google Cloud Account**: You need a Google Cloud account with billing enabled
2. **Google Cloud CLI**: Install and configure the gcloud CLI
3. **Docker**: Install Docker for containerization
4. **Required APIs**: Enable the following Google Cloud APIs:
   - Cloud Run API
   - Cloud Build API
   - Cloud Storage API
   - BigQuery API
   - Vertex AI API
   - Vision API

## Environment Setup

### 1. Google Cloud Project Setup

```bash
# Create a new project (or use existing)
gcloud projects create your-project-id

# Set the project
gcloud config set project your-project-id

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable vision.googleapis.com
```

### 2. Service Account Setup

```bash
# Create a service account
gcloud iam service-accounts create legal-ai-service \
    --display-name="Legal AI Service Account"

# Grant necessary permissions
gcloud projects add-iam-policy-binding your-project-id \
    --member="serviceAccount:legal-ai-service@your-project-id.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding your-project-id \
    --member="serviceAccount:legal-ai-service@your-project-id.iam.gserviceaccount.com" \
    --role="roles/bigquery.admin"

gcloud projects add-iam-policy-binding your-project-id \
    --member="serviceAccount:legal-ai-service@your-project-id.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

# Create and download service account key
gcloud iam service-accounts keys create service-account-key.json \
    --iam-account=legal-ai-service@your-project-id.iam.gserviceaccount.com
```

### 3. Environment Variables

Create a `.env` file in the backend directory:

```bash
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json

# Gemini API
GEMINI_API_KEY=your-gemini-api-key

# Cloud Storage
CLOUD_STORAGE_BUCKET=your-project-id-legal-documents

# BigQuery
BIGQUERY_DATASET=legal_documents
BIGQUERY_TABLE_USAGE=usage_analytics
BIGQUERY_TABLE_DOCUMENTS=document_metadata

# Application Settings
DEBUG=false
SECRET_KEY=your-secret-key
```

## Deployment Methods

### Method 1: Using the Deployment Script

The easiest way to deploy is using the provided script:

```bash
# Make the script executable
chmod +x scripts/deploy.sh

# Set environment variables
export GOOGLE_CLOUD_PROJECT_ID=your-project-id
export GEMINI_API_KEY=your-gemini-api-key

# Run the deployment script
./scripts/deploy.sh
```

### Method 2: Manual Deployment

#### Deploy Backend

```bash
cd backend

# Build and deploy using Cloud Build
gcloud builds submit --config cloudbuild.yaml

# Or deploy directly with gcloud run
gcloud run deploy legal-ai-backend \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --max-instances 10 \
    --set-env-vars GOOGLE_CLOUD_PROJECT_ID=your-project-id,GEMINI_API_KEY=your-gemini-api-key
```

#### Deploy Frontend

```bash
cd frontend

# Update the backend URL in the environment
export NEXT_PUBLIC_API_URL=https://legal-ai-backend-xxxxx-uc.a.run.app

# Build and deploy
gcloud builds submit --config cloudbuild.yaml
```

### Method 3: Docker Compose (Local Development)

For local development and testing:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Post-Deployment Configuration

### 1. Set Up Custom Domain (Optional)

```bash
# Map a custom domain to your frontend service
gcloud run domain-mappings create \
    --service legal-ai-frontend \
    --domain your-domain.com \
    --region us-central1
```

### 2. Configure SSL Certificate

```bash
# Create SSL certificate
gcloud compute ssl-certificates create legal-ai-ssl \
    --domains your-domain.com \
    --global
```

### 3. Set Up Monitoring

```bash
# Enable monitoring
gcloud services enable monitoring.googleapis.com

# Create alerting policies for:
# - High error rates
# - High latency
# - Low availability
```

### 4. Configure Logging

```bash
# Set up log-based metrics
gcloud logging metrics create legal_ai_errors \
    --description="Count of errors in Legal AI application" \
    --log-filter='resource.type="cloud_run_revision" AND severity>=ERROR'
```

## Scaling Configuration

### Backend Scaling

```bash
# Update backend service with scaling parameters
gcloud run services update legal-ai-backend \
    --region us-central1 \
    --min-instances 1 \
    --max-instances 20 \
    --cpu-throttling \
    --concurrency 100
```

### Frontend Scaling

```bash
# Update frontend service with scaling parameters
gcloud run services update legal-ai-frontend \
    --region us-central1 \
    --min-instances 0 \
    --max-instances 10 \
    --cpu-throttling \
    --concurrency 1000
```

## Security Configuration

### 1. Enable IAM

```bash
# Restrict access to authenticated users only
gcloud run services update legal-ai-backend \
    --region us-central1 \
    --no-allow-unauthenticated
```

### 2. Set Up VPC Connector (Optional)

```bash
# Create VPC connector
gcloud compute networks vpc-access connectors create legal-ai-connector \
    --region us-central1 \
    --subnet default \
    --subnet-project your-project-id \
    --min-instances 2 \
    --max-instances 10
```

### 3. Configure CORS

Update the backend configuration to restrict CORS origins:

```python
# In backend/app/core/config.py
ALLOWED_ORIGINS = [
    "https://your-domain.com",
    "https://legal-ai-frontend-xxxxx-uc.a.run.app"
]
```

## Monitoring and Maintenance

### 1. View Logs

```bash
# Backend logs
gcloud logs tail --service legal-ai-backend

# Frontend logs
gcloud logs tail --service legal-ai-frontend

# Filter by severity
gcloud logs tail --service legal-ai-backend --severity=ERROR
```

### 2. Monitor Performance

```bash
# View service metrics
gcloud run services describe legal-ai-backend --region us-central1

# Check BigQuery usage
bq query --use_legacy_sql=false "
SELECT 
  COUNT(*) as total_requests,
  AVG(processing_time) as avg_processing_time
FROM \`your-project-id.legal_documents.usage_analytics\`
WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
"
```

### 3. Update Services

```bash
# Update backend
cd backend
gcloud builds submit --config cloudbuild.yaml

# Update frontend
cd frontend
gcloud builds submit --config cloudbuild.yaml
```

## Troubleshooting

### Common Issues

1. **Service won't start**: Check logs for missing environment variables
2. **File upload fails**: Verify Cloud Storage bucket permissions
3. **AI processing fails**: Check Gemini API key and quotas
4. **Database errors**: Verify BigQuery dataset and table permissions

### Debug Commands

```bash
# Check service status
gcloud run services list --region us-central1

# View service details
gcloud run services describe legal-ai-backend --region us-central1

# Check IAM permissions
gcloud projects get-iam-policy your-project-id

# Test API endpoints
curl -X GET https://legal-ai-backend-xxxxx-uc.a.run.app/api/v1/health
```

## Cost Optimization

### 1. Resource Optimization

- Use appropriate CPU and memory settings
- Set minimum instances to 0 for development
- Use CPU throttling for cost savings

### 2. Storage Optimization

- Set up lifecycle policies for Cloud Storage
- Use appropriate storage classes
- Clean up old documents regularly

### 3. Monitoring Costs

```bash
# View current costs
gcloud billing budgets list

# Set up budget alerts
gcloud billing budgets create \
    --billing-account=your-billing-account \
    --display-name="Legal AI Budget" \
    --budget-amount=100USD \
    --threshold-rule=percent=80 \
    --threshold-rule=percent=100
```

## Backup and Recovery

### 1. Database Backup

```bash
# Export BigQuery data
bq extract your-project-id:legal_documents.usage_analytics \
    gs://your-backup-bucket/usage_analytics_backup.json
```

### 2. Configuration Backup

```bash
# Export service configurations
gcloud run services describe legal-ai-backend --region us-central1 > backend-config.yaml
gcloud run services describe legal-ai-frontend --region us-central1 > frontend-config.yaml
```

This deployment guide provides comprehensive instructions for deploying and maintaining the AI Legal Document Simplifier on Google Cloud Platform.
