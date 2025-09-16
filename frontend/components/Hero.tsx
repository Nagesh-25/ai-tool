'use client'

import { ArrowDownIcon, DocumentTextIcon, SparklesIcon, ShieldCheckIcon } from '@heroicons/react/24/outline'

export function Hero() {
  return (
    <div className="relative bg-white">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="py-20 text-center lg:py-32">
          <div className="mx-auto max-w-4xl">
            {/* Badge */}
            <div className="mb-8">
              <span className="inline-flex items-center rounded-full bg-primary-50 px-4 py-2 text-sm font-medium text-primary-700 ring-1 ring-inset ring-primary-600/20">
                <SparklesIcon className="mr-2 h-4 w-4" />
                Powered by Google Gemini AI
              </span>
            </div>

            {/* Main heading */}
            <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl lg:text-7xl">
              Simplify Legal Documents with{' '}
              <span className="text-primary-600">AI</span>
            </h1>
            
            {/* Subheading */}
            <p className="mt-6 text-lg leading-8 text-gray-600 sm:text-xl lg:text-2xl">
              Transform complex legal jargon into clear, easy-to-understand language. 
              Upload your documents and get instant, accurate simplifications powered by advanced AI.
            </p>

            {/* Features */}
            <div className="mt-10 grid grid-cols-1 gap-4 sm:grid-cols-3 sm:gap-6">
              <div className="flex items-center justify-center space-x-2 text-sm text-gray-600">
                <DocumentTextIcon className="h-5 w-5 text-primary-600" />
                <span>PDF, DOC, DOCX, Images</span>
              </div>
              <div className="flex items-center justify-center space-x-2 text-sm text-gray-600">
                <SparklesIcon className="h-5 w-5 text-primary-600" />
                <span>AI-Powered Simplification</span>
              </div>
              <div className="flex items-center justify-center space-x-2 text-sm text-gray-600">
                <ShieldCheckIcon className="h-5 w-5 text-primary-600" />
                <span>Secure & Private</span>
              </div>
            </div>

            {/* CTA */}
            <div className="mt-10 flex items-center justify-center gap-x-6">
              <a
                href="#upload"
                className="btn-primary text-lg px-8 py-3"
              >
                Get Started Free
              </a>
              <a
                href="#how-it-works"
                className="text-sm font-semibold leading-6 text-gray-900 hover:text-primary-600 transition-colors duration-200"
              >
                Learn more <span aria-hidden="true">→</span>
              </a>
            </div>

            {/* Scroll indicator */}
            <div className="mt-16">
              <div className="flex flex-col items-center">
                <span className="text-sm text-gray-500 mb-2">Scroll to upload</span>
                <ArrowDownIcon className="h-6 w-6 text-gray-400 animate-bounce" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Background decoration */}
      <div className="absolute inset-x-0 top-[calc(100%-13rem)] -z-10 transform-gpu overflow-hidden blur-3xl sm:top-[calc(100%-30rem)]">
        <div
          className="relative left-[calc(50%+3rem)] aspect-[1155/678] w-[36.125rem] -translate-x-1/2 bg-gradient-to-tr from-primary-400 to-primary-600 opacity-20 sm:left-[calc(50%+36rem)] sm:w-[72.1875rem]"
          style={{
            clipPath:
              'polygon(74.1% 44.1%, 100% 61.6%, 97.5% 26.9%, 85.5% 0.1%, 80.7% 2%, 72.5% 32.5%, 60.2% 62.4%, 52.4% 68.1%, 47.5% 58.3%, 45.2% 34.5%, 27.5% 76.7%, 0.1% 64.9%, 17.9% 100%, 27.6% 76.8%, 76.1% 97.7%, 74.1% 44.1%)',
          }}
        />
      </div>
    </div>
  )
}
