'use client'

import { useState } from 'react'
import { 
  DocumentTextIcon, 
  ClockIcon, 
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ArrowDownTrayIcon,
  ShareIcon,
  StarIcon
} from '@heroicons/react/24/outline'
import { SimplifiedDocument } from '@/types/document'
import { formatDistanceToNow } from 'date-fns'
import toast from 'react-hot-toast'

interface DocumentResultsProps {
  document: SimplifiedDocument
  onReset: () => void
}

export function DocumentResults({ document, onReset }: DocumentResultsProps) {
  const [activeTab, setActiveTab] = useState<'summary' | 'key-points' | 'terms' | 'warnings' | 'next-steps'>('summary')
  const [showOriginal, setShowOriginal] = useState(false)

  const handleDownload = () => {
    const content = `
# Simplified Legal Document: ${document.original_filename}

## Summary
${document.summary}

## Key Points
${document.key_points.map(point => `- ${point}`).join('\n')}

## Important Terms
${Object.entries(document.important_terms).map(([term, definition]) => `**${term}**: ${definition}`).join('\n')}

## Deadlines & Obligations
${document.deadlines_obligations.map(item => `- ${item}`).join('\n')}

## Warnings
${document.warnings.map(warning => `- ${warning}`).join('\n')}

## Next Steps
${document.next_steps.map(step => `- ${step}`).join('\n')}

---
*Simplified on ${new Date(document.processing_timestamp).toLocaleDateString()}*
*Confidence Score: ${Math.round(document.confidence_score * 100)}%*
*Reading Level: ${document.reading_level}*
    `.trim()

    const blob = new Blob([content], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = window.document.createElement('a')
    a.href = url
    a.download = `simplified-${document.original_filename}.md`
    window.document.body.appendChild(a)
    a.click()
    window.document.body.removeChild(a)
    URL.revokeObjectURL(url)
    
    toast.success('Document downloaded successfully!')
  }

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: `Simplified: ${document.original_filename}`,
          text: `Check out this simplified legal document: ${document.summary}`,
          url: window.location.href,
        })
      } catch (error) {
        console.log('Error sharing:', error)
      }
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(window.location.href)
      toast.success('Link copied to clipboard!')
    }
  }

  const tabs = [
    { id: 'summary', name: 'Summary', count: null },
    { id: 'key-points', name: 'Key Points', count: document.key_points.length },
    { id: 'terms', name: 'Terms', count: Object.keys(document.important_terms).length },
    { id: 'warnings', name: 'Warnings', count: document.warnings.length },
    { id: 'next-steps', name: 'Next Steps', count: document.next_steps.length },
  ] as const

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card">
        <div className="card-body">
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0">
                <div className="h-12 w-12 bg-primary-100 rounded-lg flex items-center justify-center">
                  <DocumentTextIcon className="h-6 w-6 text-primary-600" />
                </div>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  {document.original_filename}
                </h1>
                <div className="mt-2 flex items-center space-x-4 text-sm text-gray-500">
                  <div className="flex items-center">
                    <ClockIcon className="h-4 w-4 mr-1" />
                    {formatDistanceToNow(new Date(document.processing_timestamp), { addSuffix: true })}
                  </div>
                  <div className="flex items-center">
                    <CheckCircleIcon className="h-4 w-4 mr-1 text-green-500" />
                    {Math.round(document.confidence_score * 100)}% confidence
                  </div>
                  <div className="flex items-center">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {document.reading_level} level
                    </span>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={handleDownload}
                className="btn-secondary"
              >
                <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
                Download
              </button>
              <button
                onClick={handleShare}
                className="btn-secondary"
              >
                <ShareIcon className="h-4 w-4 mr-2" />
                Share
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="card-body text-center">
            <div className="text-2xl font-bold text-primary-600">
              {document.word_count_original.toLocaleString()}
            </div>
            <div className="text-sm text-gray-500">Original Words</div>
          </div>
        </div>
        <div className="card">
          <div className="card-body text-center">
            <div className="text-2xl font-bold text-green-600">
              {document.word_count_simplified.toLocaleString()}
            </div>
            <div className="text-sm text-gray-500">Simplified Words</div>
          </div>
        </div>
        <div className="card">
          <div className="card-body text-center">
            <div className="text-2xl font-bold text-blue-600">
              {Math.round((1 - document.word_count_simplified / document.word_count_original) * 100)}%
            </div>
            <div className="text-sm text-gray-500">Reduction</div>
          </div>
        </div>
        <div className="card">
          <div className="card-body text-center">
            <div className="text-2xl font-bold text-purple-600">
              {document.key_points.length + Object.keys(document.important_terms).length}
            </div>
            <div className="text-sm text-gray-500">Key Insights</div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="card">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8 px-6" aria-label="Tabs">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap
                  ${activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                {tab.name}
                {tab.count !== null && (
                  <span className={`
                    ml-2 py-0.5 px-2 rounded-full text-xs
                    ${activeTab === tab.id
                      ? 'bg-primary-100 text-primary-600'
                      : 'bg-gray-100 text-gray-900'
                    }
                  `}>
                    {tab.count}
                  </span>
                )}
              </button>
            ))}
          </nav>
        </div>

        <div className="card-body">
          {/* Summary Tab */}
          {activeTab === 'summary' && (
            <div className="prose max-w-none">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Document Summary</h3>
              <p className="text-gray-700 leading-relaxed text-lg">
                {document.summary}
              </p>
            </div>
          )}

          {/* Key Points Tab */}
          {activeTab === 'key-points' && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Key Points</h3>
              <ul className="space-y-3">
                {document.key_points.map((point, index) => (
                  <li key={index} className="flex items-start">
                    <div className="flex-shrink-0 h-6 w-6 bg-primary-100 rounded-full flex items-center justify-center mr-3 mt-0.5">
                      <span className="text-xs font-medium text-primary-600">{index + 1}</span>
                    </div>
                    <p className="text-gray-700">{point}</p>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Terms Tab */}
          {activeTab === 'terms' && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Important Terms & Definitions</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(document.important_terms).map(([term, definition]) => (
                  <div key={term} className="p-4 bg-gray-50 rounded-lg">
                    <h4 className="font-medium text-gray-900 mb-2">{term}</h4>
                    <p className="text-gray-700 text-sm">{definition}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Warnings Tab */}
          {activeTab === 'warnings' && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Important Warnings & Deadlines</h3>
              <div className="space-y-4">
                {document.deadlines_obligations.length > 0 && (
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                      <ClockIcon className="h-4 w-4 mr-2 text-blue-500" />
                      Deadlines & Obligations
                    </h4>
                    <ul className="space-y-2">
                      {document.deadlines_obligations.map((item, index) => (
                        <li key={index} className="flex items-start">
                          <div className="flex-shrink-0 h-2 w-2 bg-blue-500 rounded-full mr-3 mt-2"></div>
                          <p className="text-gray-700">{item}</p>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {document.warnings.length > 0 && (
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                      <ExclamationTriangleIcon className="h-4 w-4 mr-2 text-yellow-500" />
                      Warnings & Critical Information
                    </h4>
                    <ul className="space-y-2">
                      {document.warnings.map((warning, index) => (
                        <li key={index} className="flex items-start">
                          <div className="flex-shrink-0 h-2 w-2 bg-yellow-500 rounded-full mr-3 mt-2"></div>
                          <p className="text-gray-700">{warning}</p>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Next Steps Tab */}
          {activeTab === 'next-steps' && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Recommended Next Steps</h3>
              <ul className="space-y-3">
                {document.next_steps.map((step, index) => (
                  <li key={index} className="flex items-start">
                    <div className="flex-shrink-0 h-6 w-6 bg-green-100 rounded-full flex items-center justify-center mr-3 mt-0.5">
                      <span className="text-xs font-medium text-green-600">{index + 1}</span>
                    </div>
                    <p className="text-gray-700">{step}</p>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Original Text Toggle */}
      {document.original_text && (
        <div className="card">
          <div className="card-body">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Original Document Text</h3>
              <button
                onClick={() => setShowOriginal(!showOriginal)}
                className="btn-secondary"
              >
                {showOriginal ? 'Hide' : 'Show'} Original
              </button>
            </div>
            
            {showOriginal && (
              <div className="prose max-w-none">
                <div className="bg-gray-50 p-4 rounded-lg max-h-96 overflow-y-auto">
                  <pre className="whitespace-pre-wrap text-sm text-gray-700 font-mono">
                    {document.original_text}
                  </pre>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => {
              // TODO: Implement feedback system
              toast.success('Thank you for your feedback!')
            }}
            className="btn-secondary"
          >
            <StarIcon className="h-4 w-4 mr-2" />
            Rate This Simplification
          </button>
        </div>
        
        <button
          onClick={onReset}
          className="btn-primary"
        >
          Simplify Another Document
        </button>
      </div>
    </div>
  )
}
