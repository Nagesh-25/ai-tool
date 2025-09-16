# 🚀 Google Cloud Platform Setup Guide

This guide will help you set up your AI Legal Document Simplifier with Google Cloud Platform using your service account credentials.

## 📋 Prerequisites

1. **Google Cloud CLI** installed and authenticated
2. **Python 3.9+** installed
3. **Node.js 18+** installed
4. **Docker** (optional, for containerized deployment)

## 🔧 Step-by-Step Setup

### Step 1: Install Google Cloud CLI (if not already installed)

```bash
# Download and install gcloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Authenticate with your Google account
gcloud auth login
```

### Step 2: Run the Automated Setup Script

```bash
# Make the script executable (if on Linux/Mac)
chmod +x scripts/setup-gcp.sh

# Run the setup script
./scripts/setup-gcp.sh
```

**What this script does:**
- ✅ Sets your project ID to `legal-ai-470918`
- ✅ Enables all required Google Cloud APIs
- ✅ Creates Cloud Storage bucket: `legal-ai-470918-legal-documents`
- ✅ Creates BigQuery dataset: `legal_documents`
- ✅ Creates necessary BigQuery tables
- ✅ Sets up proper permissions for your service account
- ✅ Creates your `.env` file with correct configuration

### Step 3: Get Your Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key

### Step 4: Update Your Environment Configuration

Edit `backend/.env` and replace:
```bash
GEMINI_API_KEY="your-gemini-api-key-here"
```

With your actual API key:
```bash
GEMINI_API_KEY="AIzaSyC..."
```

### Step 5: Install Dependencies

```bash
# Backend dependencies
cd backend
pip install -r requirements.txt

# Frontend dependencies
cd ../frontend
npm install
```

### Step 6: Test Your Setup

```bash
# Run the integration test
python scripts/test-gcp-integration.py
```

This will verify:
- ✅ Environment configuration
- ✅ Google Cloud services connection
- ✅ Application services initialization

## 🧪 Testing Your Application

### Local Development

```bash
# Start the backend
cd backend
python main.py

# In another terminal, start the frontend
cd frontend
npm run dev
```

Your application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Test the API

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Test document upload (replace with actual file)
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test-document.pdf"
```

## 🚀 Deploy to Google Cloud Run

### Option 1: Automated Deployment

```bash
# Set your Gemini API key as environment variable
export GEMINI_API_KEY="your-actual-api-key"

# Run the deployment script
./scripts/deploy.sh
```

### Option 2: Manual Deployment

```bash
# Deploy backend
cd backend
gcloud builds submit --config cloudbuild.yaml

# Deploy frontend
cd ../frontend
gcloud builds submit --config cloudbuild.yaml
```

## 📊 Your Google Cloud Resources

After setup, you'll have:

| Resource | Name | Purpose |
|----------|------|---------|
| **Project** | `legal-ai-470918` | Your main GCP project |
| **Storage Bucket** | `legal-ai-470918-legal-documents` | Document storage |
| **BigQuery Dataset** | `legal_documents` | Analytics data |
| **Service Account** | `legal-ai-service@legal-ai-470918.iam.gserviceaccount.com` | API access |

## 🔍 Monitoring and Logs

```bash
# View application logs
gcloud logs tail --service=legal-ai-backend
gcloud logs tail --service=legal-ai-frontend

# View BigQuery data
bq query "SELECT * FROM \`legal-ai-470918.legal_documents.usage_analytics\` LIMIT 10"

# View storage contents
gsutil ls gs://legal-ai-470918-legal-documents/
```

## 🛠️ Troubleshooting

### Common Issues

1. **Authentication Error**
   ```bash
   # Re-authenticate
   gcloud auth login
   gcloud auth application-default login
   ```

2. **Permission Denied**
   ```bash
   # Check service account permissions
   gcloud projects get-iam-policy legal-ai-470918
   ```

3. **API Not Enabled**
   ```bash
   # Enable required APIs
   gcloud services enable aiplatform.googleapis.com
   gcloud services enable storage.googleapis.com
   gcloud services enable bigquery.googleapis.com
   ```

4. **Gemini API Key Issues**
   - Verify the key is correct
   - Check if the API key has proper permissions
   - Ensure you're using the correct project

### Getting Help

- **Google Cloud Documentation**: https://cloud.google.com/docs
- **Gemini API Documentation**: https://ai.google.dev/docs
- **Project Issues**: Check the logs and error messages

## 🎯 Next Steps

1. **Test with Real Documents**: Upload various legal documents to test the AI simplification
2. **Monitor Performance**: Check BigQuery analytics for usage patterns
3. **Scale Up**: Adjust Cloud Run settings based on usage
4. **Add Features**: Implement additional AI capabilities

## 📈 Cost Optimization

- **Cloud Run**: Scales to zero when not in use
- **BigQuery**: Pay only for queries and storage used
- **Cloud Storage**: Low-cost storage for documents
- **Gemini API**: Pay per token used

Monitor your costs in the [Google Cloud Console](https://console.cloud.google.com/billing).

---

**🎉 Congratulations!** Your AI Legal Document Simplifier is now fully integrated with Google Cloud Platform and ready for production use!
