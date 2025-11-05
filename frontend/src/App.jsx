import Layout from './components/Layout/Layout';
import ConnectionTest from './components/ConnectionTest';

function App() {
  return (
    <Layout>
      <div className="space-y-6">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">
            Welcome to Synthaia
          </h2>
          <p className="text-gray-600 mb-6">
            Generate AI-powered music from a simple theme
          </p>
        </div>

        <ConnectionTest />
      </div>
    </Layout>
  );
}

export default App;
