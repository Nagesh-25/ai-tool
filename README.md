# AI Legal Document Simplifier

An AI-powered platform that demystifies complex legal documents into simple, easy-to-understand language for the general public.

## Features

- **Multi-format Support**: Accepts raw text, images (OCR-enabled), DOC/DOCX, and PDF files
- **AI-Powered Simplification**: Uses Google's Gemini API for intelligent document analysis and simplification
- **Modern UI**: Built with React.js and Next.js for a responsive, user-friendly interface
- **Cloud-Native**: Powered by Google Cloud services for scalability and reliability
- **Secure Processing**: Secure handling of user data with proper validation and storage

## Architecture

### Frontend
- **Next.js 14** with React 18
- **TypeScript** for type safety
- **Tailwind CSS** for modern styling
- **File upload** with drag-and-drop support
- **Real-time processing** status updates

### Backend
- **Python FastAPI** for high-performance API
- **Google Cloud Integration**:
  - Vertex AI for model hosting
  - Gemini API for language understanding
  - Cloud Run for scalable microservices
  - Cloud Storage for document storage
  - BigQuery for analytics

### Document Processing
- **PDF processing** with PyPDF2/pdfplumber
- **DOC/DOCX processing** with python-docx
- **OCR capabilities** with Tesseract/Google Vision API
- **Text extraction** and preprocessing

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.9+
- Google Cloud account with enabled APIs
- Docker (for containerization)

### Installation

1. Clone the repository
2. Set up Google Cloud credentials
3. Install dependencies:
   ```bash
   # Frontend
   cd frontend
   npm install
   
   # Backend
   cd ../backend
   pip install -r requirements.txt
   ```

### Environment Setup

Create `.env` files in both frontend and backend directories with your Google Cloud configuration.

## Quick Start

### Option 1: Using Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/ai-legal-document-simplifier.git
   cd ai-legal-document-simplifier
   ```

2. **Set up environment variables**
   ```bash
   # Copy environment files
   cp backend/env.example backend/.env
   cp frontend/.env.example frontend/.env.local
   
   # Edit the files with your Google Cloud credentials
   nano backend/.env
   nano frontend/.env.local
   ```

3. **Start the application**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Option 2: Manual Setup

1. **Backend Setup**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Environment Configuration

### Backend Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json

# Gemini API
GEMINI_API_KEY=your-gemini-api-key

# Cloud Storage
CLOUD_STORAGE_BUCKET=your-bucket-name

# BigQuery
BIGQUERY_DATASET=legal_documents
BIGQUERY_TABLE_USAGE=usage_analytics
BIGQUERY_TABLE_DOCUMENTS=document_metadata

# Application Settings
DEBUG=false
SECRET_KEY=your-secret-key
MAX_FILE_SIZE=10485760  # 10MB
```

### Frontend Environment Variables

Create a `.env.local` file in the `frontend` directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NODE_ENV=development
```

## Google Cloud Setup

### 1. Create a Google Cloud Project

```bash
gcloud projects create your-project-id
gcloud config set project your-project-id
```

### 2. Enable Required APIs

```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable vision.googleapis.com
```

### 3. Create Service Account

```bash
gcloud iam service-accounts create legal-ai-service \
    --display-name="Legal AI Service Account"

gcloud projects add-iam-policy-binding your-project-id \
    --member="serviceAccount:legal-ai-service@your-project-id.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding your-project-id \
    --member="serviceAccount:legal-ai-service@your-project-id.iam.gserviceaccount.com" \
    --role="roles/bigquery.admin"

gcloud projects add-iam-policy-binding your-project-id \
    --member="serviceAccount:legal-ai-service@your-project-id.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"
```

### 4. Create and Download Service Account Key

```bash
gcloud iam service-accounts keys create service-account-key.json \
    --iam-account=legal-ai-service@your-project-id.iam.gserviceaccount.com
```

## Usage

### Web Interface

1. **Upload Document**: Drag and drop or click to upload your legal document
2. **Select Options**: Choose simplification level and target audience
3. **Process**: Click "Simplify Document" to start AI processing
4. **View Results**: Review the simplified document with key points, definitions, and next steps
5. **Download**: Save the simplified document as a markdown file

### API Usage

```python
import requests

# Upload document
with open('contract.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/v1/documents/upload',
        files={'file': f}
    )
    document_id = response.json()['document_id']

# Process document
response = requests.post(
    f'http://localhost:8000/api/v1/documents/{document_id}/process',
    json={
        'simplification_level': 'standard',
        'target_audience': 'general_public',
        'include_original': False
    }
)
simplified_doc = response.json()
```

## Deployment

### Deploy to Google Cloud Run

1. **Using the deployment script**:
   ```bash
   chmod +x scripts/deploy.sh
   export GOOGLE_CLOUD_PROJECT_ID=your-project-id
   export GEMINI_API_KEY=your-gemini-api-key
   ./scripts/deploy.sh
   ```

2. **Manual deployment**:
   ```bash
   # Deploy backend
   cd backend
   gcloud builds submit --config cloudbuild.yaml
   
   # Deploy frontend
   cd frontend
   gcloud builds submit --config cloudbuild.yaml
   ```

For detailed deployment instructions, see [DEPLOYMENT.md](docs/DEPLOYMENT.md).

## API Documentation

The API provides endpoints for document upload, processing, and analytics. Full documentation is available at:

- **Development**: http://localhost:8000/docs
- **Production**: https://your-backend-url.run.app/docs

For detailed API documentation, see [API.md](docs/API.md).

## Supported File Formats

- **PDF**: Portable Document Format (including scanned PDFs with OCR)
- **DOC**: Microsoft Word Document (legacy format)
- **DOCX**: Microsoft Word Document (modern format)
- **Images**: JPEG, PNG, TIFF (with OCR text extraction)
- **Text**: Plain text files

## Features in Detail

### AI-Powered Simplification

- **Multiple Simplification Levels**:
  - Basic: High-level summary for quick understanding
  - Standard: Comprehensive explanation with key details
  - Detailed: Thorough analysis with specific clauses and implications

- **Target Audience Adaptation**:
  - General Public: Everyday language for anyone
  - Business Owners: Business-focused explanations
  - Individuals: Personal rights and obligations focus
  - Students: Educational context with examples

### Document Analysis

- **Key Points Extraction**: Identifies the most important information
- **Term Definitions**: Explains legal jargon in plain language
- **Deadline Identification**: Highlights time-sensitive obligations
- **Warning Detection**: Identifies risks and critical information
- **Next Steps**: Provides actionable recommendations

### Security & Privacy

- **Secure Upload**: Files are encrypted during transmission
- **Temporary Storage**: Documents are not stored permanently
- **Data Protection**: Industry-standard encryption and privacy measures
- **Access Control**: Configurable authentication and authorization

## Performance & Scalability

- **Cloud-Native Architecture**: Built for Google Cloud Platform
- **Auto-scaling**: Automatically scales based on demand
- **High Availability**: 99.9% uptime with redundancy
- **Global CDN**: Fast content delivery worldwide

## Monitoring & Analytics

- **Usage Analytics**: Track document processing metrics
- **Performance Monitoring**: Monitor response times and errors
- **User Feedback**: Collect and analyze user satisfaction
- **Cost Optimization**: Monitor and optimize cloud costs

## Development

### Project Structure

```
ai-legal-document-simplifier/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Configuration
│   │   ├── models/         # Data models
│   │   └── services/       # Business logic
│   ├── main.py             # Application entry point
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Container configuration
├── frontend/               # Next.js React frontend
│   ├── app/                # Next.js app directory
│   ├── components/         # React components
│   ├── lib/                # Utilities and API client
│   ├── types/              # TypeScript types
│   ├── package.json        # Node.js dependencies
│   └── Dockerfile          # Container configuration
├── docs/                   # Documentation
├── scripts/                # Setup and deployment scripts
├── docker-compose.yml      # Local development setup
└── README.md              # This file
```

### Running Tests

```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Backend linting
cd backend
black .
flake8 .

# Frontend linting
cd frontend
npm run lint
npm run type-check
```

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

### Code Style

- **Backend**: Follow PEP 8, use Black for formatting
- **Frontend**: Follow ESLint rules, use Prettier for formatting
- **Documentation**: Use clear, concise language

## Troubleshooting

### Common Issues

1. **File Upload Fails**
   - Check file size (max 10MB)
   - Verify file format is supported
   - Ensure network connection is stable

2. **Processing Errors**
   - Verify Google Cloud credentials
   - Check Gemini API quota
   - Ensure document contains extractable text

3. **Deployment Issues**
   - Verify Google Cloud project permissions
   - Check environment variables
   - Review Cloud Build logs

### Getting Help

- **Documentation**: Check the [docs/](docs/) directory
- **Issues**: Open an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions

## Roadmap

### Version 1.1 (Planned)
- [ ] User authentication and authorization
- [ ] Document templates and presets
- [ ] Batch processing improvements
- [ ] Advanced analytics dashboard

### Version 1.2 (Planned)
- [ ] Multi-language support
- [ ] Custom simplification rules
- [ ] API rate limiting improvements
- [ ] WebSocket real-time updates

### Version 2.0 (Future)
- [ ] Mobile application
- [ ] Integration with popular document management systems
- [ ] Advanced AI models and customization
- [ ] Enterprise features and compliance tools

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Google Cloud Platform** for providing the infrastructure and AI services
- **Google Gemini** for the powerful language understanding capabilities
- **Open Source Community** for the amazing tools and libraries used in this project

## Support

For support, email support@legal-ai.com or join our [Discord community](https://discord.gg/legal-ai).

---

**Made with ❤️ by the Legal AI Team**
