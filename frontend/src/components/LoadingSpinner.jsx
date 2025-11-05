/**
 * Loading Spinner Component
 * 
 * Simple loading spinner for general use
 */

export default function LoadingSpinner({ message = "Loading..." }) {
  return (
    <div className="flex flex-col items-center justify-center p-8">
      <div className="animate-spin rounded-full h-12 w-12 border-b-4 border-purple-600 mb-4"></div>
      <p className="text-gray-600">{message}</p>
    </div>
  );
}

