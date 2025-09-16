#!/usr/bin/env python3
"""
Test script to verify Google Cloud integration
"""

import os
import sys
import json
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

def test_environment():
    """Test environment configuration"""
    print("🔍 Testing environment configuration...")
    
    # Check if .env file exists
    env_file = backend_dir / ".env"
    if not env_file.exists():
        print("❌ .env file not found. Run setup-gcp.sh first.")
        return False
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv(env_file)
    
    required_vars = [
        "GOOGLE_CLOUD_PROJECT_ID",
        "GOOGLE_APPLICATION_CREDENTIALS",
        "CLOUD_STORAGE_BUCKET",
        "BIGQUERY_DATASET"
    ]
    
    for var in required_vars:
        if not os.getenv(var):
            print(f"❌ Missing environment variable: {var}")
            return False
    
    print("✅ Environment configuration looks good")
    return True

def test_google_cloud_services():
    """Test Google Cloud services connection"""
    print("🔍 Testing Google Cloud services...")
    
    try:
        # Test imports
        from google.cloud import storage, bigquery
        from google.oauth2 import service_account
        from google.generativeai import genai
        print("✅ Google Cloud libraries imported successfully")
        
        # Load credentials
        credentials_path = backend_dir / "legal-ai-470918-952813a27573.json"
        if not credentials_path.exists():
            print("❌ Service account key file not found")
            return False
        
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        print("✅ Service account credentials loaded")
        
        # Test Storage
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
        storage_client = storage.Client(credentials=credentials, project=project_id)
        buckets = list(storage_client.list_buckets())
        print(f"✅ Storage connection successful. Found {len(buckets)} buckets.")
        
        # Test BigQuery
        bq_client = bigquery.Client(credentials=credentials, project=project_id)
        datasets = list(bq_client.list_datasets())
        print(f"✅ BigQuery connection successful. Found {len(datasets)} datasets.")
        
        # Test Gemini API (if key is provided)
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key and gemini_key != "your-gemini-api-key-here":
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content("Hello, this is a test.")
            print("✅ Gemini API connection successful")
        else:
            print("⚠️  Gemini API key not configured. Get it from: https://makersuite.google.com/app/apikey")
        
        return True
        
    except Exception as e:
        print(f"❌ Google Cloud services test failed: {e}")
        return False

def test_application_services():
    """Test application services"""
    print("🔍 Testing application services...")
    
    try:
        # Test service imports
        from app.services.storage_service import StorageService
        from app.services.analytics_service import AnalyticsService
        from app.services.ai_simplifier import AISimplifier
        from app.services.document_processor import DocumentProcessor
        print("✅ Application services imported successfully")
        
        # Test service initialization
        storage_service = StorageService()
        analytics_service = AnalyticsService()
        ai_simplifier = AISimplifier()
        document_processor = DocumentProcessor()
        print("✅ Application services initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Application services test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Google Cloud integration tests...\n")
    
    tests = [
        ("Environment Configuration", test_environment),
        ("Google Cloud Services", test_google_cloud_services),
        ("Application Services", test_application_services)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Testing: {test_name}")
        print('='*50)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print('='*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Your Google Cloud integration is ready.")
        print("\nNext steps:")
        print("1. Get your Gemini API key from: https://makersuite.google.com/app/apikey")
        print("2. Update GEMINI_API_KEY in backend/.env")
        print("3. Run: cd backend && python main.py")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
