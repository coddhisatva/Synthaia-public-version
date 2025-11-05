/**
 * Progress Indicator Component
 * 
 * Displays real-time progress during song generation
 */

export default function ProgressIndicator({ step, total, message, percentage }) {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6 max-w-md mx-auto">
      <div className="text-center mb-4">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-4 border-purple-600 mb-4"></div>
        <h3 className="text-xl font-semibold text-gray-800">Generating Song...</h3>
      </div>
      
      <div className="space-y-3">
        <div className="text-center">
          <p className="text-gray-600 font-medium">
            Step {step} of {total}
          </p>
          <p className="text-purple-600 mt-1">{message}</p>
        </div>
        
        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <div 
            className="bg-gradient-to-r from-purple-600 to-blue-600 h-3 rounded-full transition-all duration-300"
            style={{ width: `${percentage}%` }}
          ></div>
        </div>
        
        <p className="text-center text-sm text-gray-500">
          {percentage}% complete
        </p>
      </div>
    </div>
  );
}

