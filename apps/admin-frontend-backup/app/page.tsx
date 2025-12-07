import { Button } from "@nowex/ui"
import { useAuth } from "@nowex/api"

export default function HomePage() {
  const { login, logout, isAuthenticated, isLoading } = useAuth()

  const handleLogin = async () => {
    try {
      await login({
        email: "admin@nowex.com",
        password: "password123"
      })
      alert("Login successful!")
    } catch (error) {
      console.error("Login failed:", error)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">NOWEX Admin Panel</h1>
          <p className="text-gray-600 mt-2">
            Welcome to the administration dashboard
          </p>
        </header>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="mb-6">
            <h2 className="text-xl font-semibold mb-4">Authentication Status</h2>
            <div className="flex items-center gap-4">
              <div className={`px-3 py-1 rounded-full ${isAuthenticated() ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                {isAuthenticated() ? 'Authenticated' : 'Not Authenticated'}
              </div>
              <Button 
                onClick={handleLogin} 
                disabled={isLoading}
                variant="primary"
              >
                {isLoading ? 'Logging in...' : 'Test Login'}
              </Button>
              <Button 
                onClick={logout}
                variant="secondary"
              >
                Logout
              </Button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold mb-2">User Management</h3>
              <p className="text-gray-600 text-sm">Manage platform users</p>
            </div>
            
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold mb-2">KYC Verification</h3>
              <p className="text-gray-600 text-sm">Review KYC requests</p>
            </div>
            
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold mb-2">System Analytics</h3>
              <p className="text-gray-600 text-sm">View platform metrics</p>
            </div>
          </div>
        </div>

        <footer className="mt-8 text-center text-gray-500 text-sm">
          <p>NOWEX Platform Admin Panel v0.1.0</p>
        </footer>
      </div>
    </div>
  )
}