import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { usePermissions } from '../hooks/usePermissions'
import { LogOut, User, Shield } from 'lucide-react'

const Navbar = () => {
  const { user, logout } = useAuth()
  const { hasPermission, isUser, isAdmin, isAuditor } = usePermissions()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <nav className="bg-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <Link to="/dashboard" className="flex items-center">
              <span className="text-2xl font-bold text-primary-600">FairFinance</span>
            </Link>
            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
              <Link
                to="/dashboard"
                className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
              >
                Dashboard
              </Link>
              {/* User-only links */}
              {isUser() && (
                <>
                  <Link
                    to="/apply"
                    className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                  >
                    Apply for Loan
                  </Link>
                  <Link
                    to="/profile"
                    className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                  >
                    My Profile
                  </Link>
                  <Link
                    to="/consent"
                    className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                  >
                    Consent
                  </Link>
                </>
              )}
              {/* All authenticated users can use voice assistant */}
              {(hasPermission('voice_assistant_full') || hasPermission('voice_assistant_limited')) && (
                <Link
                  to="/voice"
                  className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                >
                  Voice Assistant
                </Link>
              )}
              {/* Admin and Auditor can access governance */}
              {(isAdmin() || isAuditor()) && (
                <Link
                  to="/governance"
                  className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                >
                  <Shield className="w-4 h-4 mr-1" />
                  Governance
                </Link>
              )}
            </div>
          </div>
          <div className="flex items-center">
            <div className="flex items-center mr-4">
              <User className="w-5 h-5 text-gray-500 mr-2" />
              <span className="text-sm text-gray-700">{user?.full_name}</span>
              <span className="ml-2 text-xs text-gray-500">({user?.role})</span>
            </div>
            <button
              onClick={handleLogout}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar

