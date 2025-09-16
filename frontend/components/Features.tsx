'use client'

import { 
  DocumentTextIcon, 
  SparklesIcon, 
  ShieldCheckIcon, 
  ClockIcon,
  AcademicCapIcon,
  GlobeAltIcon
} from '@heroicons/react/24/outline'

export function Features() {
  const features = [
    {
      name: 'Multi-Format Support',
      description: 'Upload PDF, DOC, DOCX, and image files with OCR support for scanned documents.',
      icon: DocumentTextIcon,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100'
    },
    {
      name: 'AI-Powered Simplification',
      description: 'Advanced AI analyzes and simplifies complex legal language while maintaining accuracy.',
      icon: SparklesIcon,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100'
    },
    {
      name: 'Secure & Private',
      description: 'Your documents are processed securely with industry-standard encryption and privacy protection.',
      icon: ShieldCheckIcon,
      color: 'text-green-600',
      bgColor: 'bg-green-100'
    },
    {
      name: 'Instant Processing',
      description: 'Get simplified documents in seconds with our optimized AI processing pipeline.',
      icon: ClockIcon,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100'
    },
    {
      name: 'Educational Context',
      description: 'Learn legal concepts with clear explanations and definitions of important terms.',
      icon: AcademicCapIcon,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-100'
    },
    {
      name: 'Accessible Language',
      description: 'Transform complex legal jargon into plain English that anyone can understand.',
      icon: GlobeAltIcon,
      color: 'text-teal-600',
      bgColor: 'bg-teal-100'
    }
  ]

  return (
    <section id="features" className="py-24 bg-white">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
            Powerful Features for Legal Document Simplification
          </h2>
          <p className="mt-4 text-lg text-gray-600 max-w-3xl mx-auto">
            Our AI-powered platform combines cutting-edge technology with user-friendly design 
            to make legal documents accessible to everyone.
          </p>
        </div>

        <div className="mt-20">
          <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((feature) => (
              <div key={feature.name} className="relative">
                <div className="card h-full hover:shadow-lg transition-shadow duration-200">
                  <div className="card-body text-center">
                    <div className={`mx-auto h-12 w-12 ${feature.bgColor} rounded-lg flex items-center justify-center mb-4`}>
                      <feature.icon className={`h-6 w-6 ${feature.color}`} aria-hidden="true" />
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      {feature.name}
                    </h3>
                    <p className="text-gray-600">
                      {feature.description}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* How it Works Section */}
        <div className="mt-24">
          <div className="text-center mb-16">
            <h2 id="how-it-works" className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
              How It Works
            </h2>
            <p className="mt-4 text-lg text-gray-600 max-w-3xl mx-auto">
              Simplify your legal documents in three easy steps
            </p>
          </div>

          <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
            <div className="text-center">
              <div className="mx-auto h-16 w-16 bg-primary-100 rounded-full flex items-center justify-center mb-6">
                <span className="text-2xl font-bold text-primary-600">1</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Upload Document</h3>
              <p className="text-gray-600">
                Drag and drop your legal document or click to browse. We support PDF, DOC, DOCX, and image files.
              </p>
            </div>

            <div className="text-center">
              <div className="mx-auto h-16 w-16 bg-primary-100 rounded-full flex items-center justify-center mb-6">
                <span className="text-2xl font-bold text-primary-600">2</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">AI Processing</h3>
              <p className="text-gray-600">
                Our advanced AI analyzes your document, extracts key information, and simplifies complex legal language.
              </p>
            </div>

            <div className="text-center">
              <div className="mx-auto h-16 w-16 bg-primary-100 rounded-full flex items-center justify-center mb-6">
                <span className="text-2xl font-bold text-primary-600">3</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Get Results</h3>
              <p className="text-gray-600">
                Receive a clear, easy-to-understand summary with key points, definitions, and recommended next steps.
              </p>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="mt-24 text-center">
          <div className="card max-w-2xl mx-auto">
            <div className="card-body">
              <h3 className="text-2xl font-bold text-gray-900 mb-4">
                Ready to Simplify Your Legal Documents?
              </h3>
              <p className="text-gray-600 mb-6">
                Join thousands of users who have made legal documents accessible and understandable.
              </p>
              <a
                href="#upload"
                className="btn-primary text-lg px-8 py-3"
              >
                Get Started Free
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
