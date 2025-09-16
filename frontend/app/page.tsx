'use client'

import { useState } from 'react'
import { Header } from '@/components/Header'
import { Hero } from '@/components/Hero'
import { DocumentUpload } from '@/components/DocumentUpload'
import { DocumentResults } from '@/components/DocumentResults'
import { Features } from '@/components/Features'
import { Footer } from '@/components/Footer'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { DocumentMetadata, SimplifiedDocument } from '@/types/document'

export default function HomePage() {
  const [uploadedDocument, setUploadedDocument] = useState<DocumentMetadata | null>(null)
  const [simplifiedDocument, setSimplifiedDocument] = useState<SimplifiedDocument | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleDocumentUpload = (document: DocumentMetadata) => {
    setUploadedDocument(document)
    setSimplifiedDocument(null)
    setError(null)
  }

  const handleDocumentProcessed = (document: SimplifiedDocument) => {
    setSimplifiedDocument(document)
    setIsProcessing(false)
  }

  const handleProcessingStart = () => {
    setIsProcessing(true)
    setError(null)
  }

  const handleError = (errorMessage: string) => {
    setError(errorMessage)
    setIsProcessing(false)
  }

  const handleReset = () => {
    setUploadedDocument(null)
    setSimplifiedDocument(null)
    setIsProcessing(false)
    setError(null)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main>
        {/* Hero Section */}
        {!uploadedDocument && !simplifiedDocument && (
          <Hero />
        )}

        {/* Document Upload Section */}
        {!uploadedDocument && !simplifiedDocument && (
          <section className="py-16">
            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
              <DocumentUpload
                onDocumentUpload={handleDocumentUpload}
                onError={handleError}
              />
            </div>
          </section>
        )}

        {/* Processing Section */}
        {uploadedDocument && isProcessing && (
          <section className="py-16">
            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="text-center">
                <LoadingSpinner size="lg" />
                <h2 className="mt-4 text-2xl font-bold text-gray-900">
                  Processing Your Document
                </h2>
                <p className="mt-2 text-gray-600">
                  Our AI is analyzing and simplifying your legal document. This may take a few moments...
                </p>
                <div className="mt-4 text-sm text-gray-500">
                  Document: {uploadedDocument.filename}
                </div>
              </div>
            </div>
          </section>
        )}

        {/* Results Section */}
        {simplifiedDocument && (
          <section className="py-16">
            <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
              <DocumentResults
                document={simplifiedDocument}
                onReset={handleReset}
              />
            </div>
          </section>
        )}

        {/* Error Section */}
        {error && (
          <section className="py-16">
            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="card">
                <div className="card-body text-center">
                  <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 mb-4">
                    <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Processing Error
                  </h3>
                  <p className="text-gray-600 mb-4">
                    {error}
                  </p>
                  <button
                    onClick={handleReset}
                    className="btn-primary"
                  >
                    Try Again
                  </button>
                </div>
              </div>
            </div>
          </section>
        )}

        {/* Features Section - Show when no document is uploaded */}
        {!uploadedDocument && !simplifiedDocument && (
          <Features />
        )}
      </main>

      <Footer />
    </div>
  )
}
