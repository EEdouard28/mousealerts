/**
 * Tailwind CSS Test Page
 * 
 * This page tests if Tailwind CSS is working properly.
 * It should show colored elements if Tailwind is working.
 */

export default function TailwindTestPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-red-500 via-yellow-500 to-green-500 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-6xl font-bold text-white mb-8 text-center">
          Tailwind CSS Test
        </h1>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-red-500 p-6 rounded-lg text-white">
            <h2 className="text-2xl font-bold mb-2">Red Card</h2>
            <p>If you see this in red, Tailwind is working!</p>
          </div>
          
          <div className="bg-blue-500 p-6 rounded-lg text-white">
            <h2 className="text-2xl font-bold mb-2">Blue Card</h2>
            <p>If you see this in blue, Tailwind is working!</p>
          </div>
          
          <div className="bg-green-500 p-6 rounded-lg text-white">
            <h2 className="text-2xl font-bold mb-2">Green Card</h2>
            <p>If you see this in green, Tailwind is working!</p>
          </div>
        </div>
        
        <div className="bg-white p-8 rounded-lg shadow-lg">
          <h2 className="text-3xl font-bold text-gray-800 mb-4">Custom Classes Test</h2>
          <div className="space-y-4">
            <div className="btn btn-primary">Primary Button</div>
            <div className="btn btn-secondary">Secondary Button</div>
            <div className="btn btn-accent">Accent Button</div>
          </div>
        </div>
      </div>
    </div>
  );
}
