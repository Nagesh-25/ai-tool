#!/bin/bash

# AI Legal Document Simplifier - Google Cloud Setup Script
# This script sets up your Google Cloud environment and creates necessary resources

set -e

# Configuration
PROJECT_ID="legal-ai-470918"
REGION="us-central1"
BUCKET_NAME="legal-ai-470918-legal-documents"
DATASET_NAME="legal_documents"

echo "🚀 Setting up Google Cloud environment for AI Legal Document Simplifier..."

# Check if gcloud is installed and authenticated
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI is not installed. Please install it first:"
    echo "   https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Not authenticated with gcloud. Please run 'gcloud auth login' first."
    exit 1
fi

# Set the project
echo "📋 Setting project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required Google Cloud APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable vision.googleapis.com
gcloud services enable secretmanager.googleapis.com

echo "✅ All required APIs enabled"

# Create Cloud Storage bucket
echo "🪣 Creating Cloud Storage bucket..."
if gsutil ls -b gs://$BUCKET_NAME &> /dev/null; then
    echo "   Bucket $BUCKET_NAME already exists"
else
    gsutil mb -l $REGION gs://$BUCKET_NAME
    echo "   ✅ Created bucket: gs://$BUCKET_NAME"
fi

# Set bucket permissions
echo "🔐 Setting bucket permissions..."
gsutil iam ch serviceAccount:legal-ai-service@$PROJECT_ID.iam.gserviceaccount.com:objectAdmin gs://$BUCKET_NAME

# Create BigQuery dataset
echo "📊 Creating BigQuery dataset..."
if bq ls -d $PROJECT_ID:$DATASET_NAME &> /dev/null; then
    echo "   Dataset $DATASET_NAME already exists"
else
    bq mk --dataset --location=US $PROJECT_ID:$DATASET_NAME
    echo "   ✅ Created dataset: $DATASET_NAME"
fi

# Create BigQuery tables
echo "📋 Creating BigQuery tables..."

# Usage analytics table
USAGE_TABLE="$PROJECT_ID.$DATASET_NAME.usage_analytics"
if bq ls -t $USAGE_TABLE &> /dev/null; then
    echo "   Table usage_analytics already exists"
else
    bq mk --table $USAGE_TABLE \
        document_id:STRING,user_id:STRING,action:STRING,timestamp:TIMESTAMP,metadata:JSON,processing_time:FLOAT,file_size:INTEGER,simplification_level:STRING,confidence_score:FLOAT,user_feedback:STRING
    echo "   ✅ Created table: usage_analytics"
fi

# Document metadata table
METADATA_TABLE="$PROJECT_ID.$DATASET_NAME.document_metadata"
if bq ls -t $METADATA_TABLE &> /dev/null; then
    echo "   Table document_metadata already exists"
else
    bq mk --table $METADATA_TABLE \
        document_id:STRING,filename:STRING,file_type:STRING,file_size:INTEGER,upload_timestamp:TIMESTAMP,processing_timestamp:TIMESTAMP,status:STRING,user_id:STRING,extraction_method:STRING,ocr_confidence:FLOAT,language_detected:STRING,storage_path:STRING,processed_path:STRING
    echo "   ✅ Created table: document_metadata"
fi

# Set BigQuery permissions
echo "🔐 Setting BigQuery permissions..."
bq query --use_legacy_sql=false "
GRANT \`roles/bigquery.dataEditor\` ON DATASET \`$PROJECT_ID.$DATASET_NAME\` 
TO 'serviceAccount:legal-ai-service@$PROJECT_ID.iam.gserviceaccount.com'
"

# Create .env file
echo "📝 Creating .env file..."
cat > backend/.env << EOF
# AI Legal Document Simplifier - Environment Configuration

# Application Settings
APP_NAME="AI Legal Document Simplifier"
DEBUG=true
VERSION="1.0.0"

# Server Settings
HOST="0.0.0.0"
PORT=8000

# CORS Settings (comma-separated)
ALLOWED_ORIGINS="http://localhost:3000,http://localhost:3001"

# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT_ID="$PROJECT_ID"
GOOGLE_APPLICATION_CREDENTIALS="./legal-ai-470918-952813a27573.json"

# Vertex AI Settings
VERTEX_AI_LOCATION="$REGION"
VERTEX_AI_MODEL_NAME="gemini-pro"

# Gemini API Settings (Get from Google AI Studio: https://makersuite.google.com/app/apikey)
GEMINI_API_KEY="your-gemini-api-key-here"

# Cloud Storage Settings
CLOUD_STORAGE_BUCKET="$BUCKET_NAME"
UPLOAD_FOLDER="uploads"
PROCESSED_FOLDER="processed"

# BigQuery Settings
BIGQUERY_DATASET="$DATASET_NAME"
BIGQUERY_TABLE_USAGE="usage_analytics"
BIGQUERY_TABLE_DOCUMENTS="document_metadata"

# File Processing Settings
MAX_FILE_SIZE=10485760
ALLOWED_FILE_TYPES="application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,image/jpeg,image/png,image/tiff,text/plain"

# AI Processing Settings
MAX_TOKENS=4000
TEMPERATURE=0.3

# Security Settings
SECRET_KEY="$(openssl rand -hex 32)"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
EOF

echo "✅ Created backend/.env file"

# Test Google Cloud connection
echo "🧪 Testing Google Cloud connection..."
cd backend
python3 -c "
import os
from google.cloud import storage, bigquery
from google.oauth2 import service_account

# Load credentials
credentials = service_account.Credentials.from_service_account_file('legal-ai-470918-952813a27573.json')

# Test Storage
storage_client = storage.Client(credentials=credentials, project='$PROJECT_ID')
buckets = list(storage_client.list_buckets())
print(f'✅ Storage connection successful. Found {len(buckets)} buckets.')

# Test BigQuery
bq_client = bigquery.Client(credentials=credentials, project='$PROJECT_ID')
datasets = list(bq_client.list_datasets())
print(f'✅ BigQuery connection successful. Found {len(datasets)} datasets.')
"

echo ""
echo "🎉 Google Cloud setup complete!"
echo ""
echo "Next steps:"
echo "1. Get your Gemini API key from: https://makersuite.google.com/app/apikey"
echo "2. Update the GEMINI_API_KEY in backend/.env"
echo "3. Run: cd backend && pip install -r requirements.txt"
echo "4. Test the application: python main.py"
echo ""
echo "Your Google Cloud resources:"
echo "  Project ID: $PROJECT_ID"
echo "  Storage Bucket: gs://$BUCKET_NAME"
echo "  BigQuery Dataset: $DATASET_NAME"
echo "  Region: $REGION"
