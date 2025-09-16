'use client'

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { 
  CloudArrowUpIcon, 
  DocumentTextIcon, 
  ExclamationTriangleIcon,
  CheckCircleIcon 
} from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'
import { apiClient } from '@/lib/api'
import { DocumentMetadata, DocumentProcessingRequest } from '@/types/document'

interface DocumentUploadProps {
  onDocumentUpload: (document: DocumentMetadata) => void
  onError: (error: string) => void
}

export function DocumentUpload({ onDocumentUpload, onError }: DocumentUploadProps) {
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (!file) return

    // Validate file size (10MB limit)
    const maxSize = 10 * 1024 * 1024 // 10MB
    if (file.size > maxSize) {
      toast.error('File size must be less than 10MB')
      onError('File size exceeds the maximum allowed limit of 10MB')
      return
    }

    // Validate file type
    const allowedTypes = [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'image/jpeg',
      'image/png',
      'image/tiff',
      'text/plain'
    ]

    if (!allowedTypes.includes(file.type)) {
      toast.error('Unsupported file type. Please upload PDF, DOC, DOCX, or image files.')
      onError('Unsupported file type')
      return
    }

    setIsUploading(true)
    setUploadProgress(0)

    try {
      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return 90
          }
          return prev + 10
        })
      }, 200)

      // Upload document
      const uploadResponse = await apiClient.uploadDocument(file)
      
      clearInterval(progressInterval)
      setUploadProgress(100)

      // Convert response to DocumentMetadata
      const documentMetadata: DocumentMetadata = {
        document_id: uploadResponse.document_id,
        filename: uploadResponse.filename,
        file_type: uploadResponse.file_type,
        file_size: uploadResponse.file_size,
        upload_timestamp: uploadResponse.upload_timestamp,
        status: uploadResponse.status,
        storage_path: '', // Will be filled by backend
      }

      toast.success('Document uploaded successfully!')
      onDocumentUpload(documentMetadata)

      // Automatically start processing
      setTimeout(async () => {
        try {
          const processingRequest: DocumentProcessingRequest = {
            document_id: uploadResponse.document_id,
            simplification_level: 'standard',
            include_original: false,
            target_audience: 'general_public'
          }

          const simplifiedDocument = await apiClient.processDocument(
            uploadResponse.document_id,
            processingRequest
          )

          // This will be handled by the parent component
          // The parent should listen for processing completion
        } catch (error) {
          console.error('Processing error:', error)
          toast.error('Failed to process document')
          onError('Failed to process document')
        }
      }, 1000)

    } catch (error: any) {
      console.error('Upload error:', error)
      toast.error('Failed to upload document')
      onError(error.response?.data?.detail || 'Failed to upload document')
    } finally {
      setIsUploading(false)
      setUploadProgress(0)
    }
  }, [onDocumentUpload, onError])

  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'image/tiff': ['.tiff', '.tif'],
      'text/plain': ['.txt']
    },
    multiple: false,
    maxSize: 10 * 1024 * 1024, // 10MB
  })

  return (
    <div className="w-full">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Upload Your Legal Document
        </h2>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Drag and drop your document or click to browse. We support PDF, DOC, DOCX, and image files up to 10MB.
        </p>
      </div>

      {/* Upload Area */}
      <div
        {...getRootProps()}
        className={`
          upload-area cursor-pointer transition-all duration-200
          ${isDragActive ? 'dragover' : ''}
          ${isUploading ? 'pointer-events-none opacity-50' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        {isUploading ? (
          <div className="text-center">
            <div className="mx-auto h-12 w-12 mb-4">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Uploading Document...
            </h3>
            <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
              <div 
                className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
            <p className="text-sm text-gray-500">
              {uploadProgress}% complete
            </p>
          </div>
        ) : (
          <div className="text-center">
            <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {isDragActive ? 'Drop your document here' : 'Upload a legal document'}
            </h3>
            <p className="text-sm text-gray-500 mb-4">
              Drag and drop your file here, or click to select
            </p>
            <button
              type="button"
              className="btn-primary"
              disabled={isUploading}
            >
              Choose File
            </button>
          </div>
        )}
      </div>

      {/* File Rejections */}
      {fileRejections.length > 0 && (
        <div className="mt-4">
          {fileRejections.map(({ file, errors }) => (
            <div key={file.name} className="flex items-center p-3 bg-red-50 border border-red-200 rounded-md">
              <ExclamationTriangleIcon className="h-5 w-5 text-red-400 mr-2" />
              <div>
                <p className="text-sm font-medium text-red-800">
                  {file.name} was rejected
                </p>
                <ul className="text-sm text-red-600 mt-1">
                  {errors.map((error) => (
                    <li key={error.code}>
                      {error.code === 'file-too-large' && 'File is too large (max 10MB)'}
                      {error.code === 'file-invalid-type' && 'File type not supported'}
                      {error.code === 'too-many-files' && 'Only one file allowed'}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Supported Formats */}
      <div className="mt-8">
        <h4 className="text-sm font-medium text-gray-900 mb-3">Supported Formats:</h4>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            { type: 'PDF', icon: '📄', desc: 'Portable Document Format' },
            { type: 'DOC', icon: '📝', desc: 'Microsoft Word Document' },
            { type: 'DOCX', icon: '📝', desc: 'Microsoft Word Document' },
            { type: 'Images', icon: '🖼️', desc: 'JPEG, PNG, TIFF' },
          ].map((format) => (
            <div key={format.type} className="flex items-center space-x-2 p-2 bg-gray-50 rounded-md">
              <span className="text-lg">{format.icon}</span>
              <div>
                <p className="text-xs font-medium text-gray-900">{format.type}</p>
                <p className="text-xs text-gray-500">{format.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Security Notice */}
      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-md">
        <div className="flex items-start">
          <CheckCircleIcon className="h-5 w-5 text-blue-400 mt-0.5 mr-2" />
          <div>
            <h4 className="text-sm font-medium text-blue-800">Secure & Private</h4>
            <p className="text-sm text-blue-700 mt-1">
              Your documents are processed securely and are not stored permanently. 
              We use industry-standard encryption to protect your data.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
