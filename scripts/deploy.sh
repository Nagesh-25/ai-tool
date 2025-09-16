#!/bin/bash

# AI Legal Document Simplifier - Deployment Script
# This script deploys the application to Google Cloud Run

set -e

# Configuration
PROJECT_ID=${GOOGLE_CLOUD_PROJECT_ID:-"legal-ai-470918"}
REGION="us-central1"
BACKEND_SERVICE="legal-ai-backend"
FRONTEND_SERVICE="legal-ai-frontend"

echo "🚀 Deploying AI Legal Document Simplifier to Google Cloud Run..."

# Check if gcloud is installed and authenticated
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI is not installed. Please install it first."
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

# Create BigQuery dataset if it doesn't exist
echo "📊 Setting up BigQuery dataset..."
bq mk --dataset --location=US $PROJECT_ID:legal_documents || echo "Dataset already exists"

# Create Cloud Storage bucket if it doesn't exist
BUCKET_NAME="${PROJECT_ID}-legal-documents"
echo "🪣 Setting up Cloud Storage bucket..."
gsutil mb gs://$BUCKET_NAME || echo "Bucket already exists"

# Set bucket permissions
echo "🔐 Setting bucket permissions..."
gsutil iam ch serviceAccount:legal-ai-service@$PROJECT_ID.iam.gserviceaccount.com:objectAdmin gs://$BUCKET_NAME

# Deploy backend
echo "🐍 Deploying backend service..."
cd backend

# Build and deploy backend
gcloud builds submit --config cloudbuild.yaml \
    --substitutions=_GEMINI_API_KEY=$GEMINI_API_KEY,_CLOUD_STORAGE_BUCKET=$BUCKET_NAME,_BIGQUERY_DATASET=legal_documents

# Get backend URL
BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE --region=$REGION --format="value(status.url)")
echo "✅ Backend deployed at: $BACKEND_URL"

cd ..

# Deploy frontend
echo "⚛️  Deploying frontend service..."
cd frontend

# Update the backend URL in cloudbuild.yaml
sed -i.bak "s|_BACKEND_URL:.*|_BACKEND_URL: $BACKEND_URL|" cloudbuild.yaml

# Build and deploy frontend
gcloud builds submit --config cloudbuild.yaml

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE --region=$REGION --format="value(status.url)")
echo "✅ Frontend deployed at: $FRONTEND_URL"

# Restore original cloudbuild.yaml
mv cloudbuild.yaml.bak cloudbuild.yaml

cd ..

# Set up custom domain (optional)
echo "🌐 Setting up custom domain (optional)..."
echo "To set up a custom domain, run:"
echo "  gcloud run domain-mappings create --service=$FRONTEND_SERVICE --domain=your-domain.com --region=$REGION"

# Display deployment summary
echo ""
echo "🎉 Deployment complete!"
echo ""
echo "Services deployed:"
echo "  Backend: $BACKEND_URL"
echo "  Frontend: $FRONTEND_URL"
echo ""
echo "Next steps:"
echo "1. Update your DNS records to point to the frontend URL"
echo "2. Set up SSL certificates for custom domains"
echo "3. Configure monitoring and alerting"
echo "4. Set up CI/CD pipeline for automatic deployments"
echo ""
echo "To view logs:"
echo "  gcloud logs tail --service=$BACKEND_SERVICE"
echo "  gcloud logs tail --service=$FRONTEND_SERVICE"
