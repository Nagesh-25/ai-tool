#!/bin/bash

# AI Legal Document Simplifier - Setup Script
# This script sets up the development environment

set -e

echo "🚀 Setting up AI Legal Document Simplifier..."

# Check if required tools are installed
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ $1 is not installed. Please install it first."
        exit 1
    fi
}

echo "📋 Checking prerequisites..."
check_command "python3"
check_command "node"
check_command "npm"
check_command "docker"
check_command "docker-compose"

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if [[ $(echo "$python_version < 3.9" | bc -l) -eq 1 ]]; then
    echo "❌ Python 3.9 or higher is required. Current version: $python_version"
    exit 1
fi

# Check Node version
node_version=$(node -v | cut -d'v' -f2)
if [[ $(echo "$node_version < 18.0" | bc -l) -eq 1 ]]; then
    echo "❌ Node.js 18 or higher is required. Current version: $node_version"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Setup backend
echo "🐍 Setting up Python backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file for backend..."
    cp env.example .env
    echo "⚠️  Please update the .env file with your Google Cloud credentials"
fi

cd ..

# Setup frontend
echo "⚛️  Setting up React frontend..."
cd frontend

# Install dependencies
npm install

# Create .env.local file if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo "📝 Creating .env.local file for frontend..."
    cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
NODE_ENV=development
EOF
fi

cd ..

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p ssl

# Setup Google Cloud (optional)
echo "☁️  Google Cloud setup (optional)..."
if command -v gcloud &> /dev/null; then
    echo "gcloud CLI found. You can run the following commands to set up Google Cloud:"
    echo "  gcloud auth login"
    echo "  gcloud config set project YOUR_PROJECT_ID"
    echo "  gcloud services enable cloudbuild.googleapis.com"
    echo "  gcloud services enable run.googleapis.com"
    echo "  gcloud services enable storage.googleapis.com"
    echo "  gcloud services enable bigquery.googleapis.com"
    echo "  gcloud services enable aiplatform.googleapis.com"
else
    echo "gcloud CLI not found. Please install it if you want to deploy to Google Cloud."
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update backend/.env with your Google Cloud credentials"
echo "2. Update frontend/.env.local if needed"
echo "3. Run 'docker-compose up' to start the application"
echo "4. Or run the development servers:"
echo "   - Backend: cd backend && source venv/bin/activate && uvicorn main:app --reload"
echo "   - Frontend: cd frontend && npm run dev"
echo ""
echo "The application will be available at:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
