import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { usePermissions } from '../../hooks/usePermissions'
import { 
  LayoutDashboard, 
  FileText, 
  User, 
  Shield, 
  Mic, 
  LogOut,
  Settings
} from 'lucide-react'

const Sidebar = ({ onLogout }) => {
  const location = useLocation()
  const { user } = useAuth()
  const { isUser, isAdmin, isAuditor, hasPermission } = usePermissions()

  const isActive = (path) => location.pathname === path

  const menuItems = [
    {
      label: 'Dashboard',
      path: '/dashboard',
      icon: LayoutDashboard,
      show: true,
    },
    {
      label: 'Apply for Loan',
      path: '/apply',
      icon: FileText,
      show: isUser(),
    },
    {
      label: 'My Profile',
      path: '/profile',
      icon: User,
      show: isUser(),
    },
    {
      label: 'Consent',
      path: '/consent',
      icon: Shield,
      show: isUser(),
    },
    {
      label: 'Voice Assistant',
      path: '/voice',
      icon: Mic,
      show: hasPermission('voice_assistant_full') || hasPermission('voice_assistant_limited'),
    },
    {
      label: 'Governance',
      path: '/governance',
      icon: Settings,
      show: isAdmin() || isAuditor(),
    },
  ].filter(item => item.show)

  return (
    <div className="w-64 bg-navy-900 min-h-screen flex flex-col">
      <div className="p-6 border-b border-navy-800">
        <h1 className="text-2xl font-bold text-white font-display">FairFinance</h1>
        <p className="text-xs text-gray-400 mt-1">Ethical AI Banking</p>
      </div>

      <nav className="flex-1 p-4 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon
          const active = isActive(item.path)
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center px-4 py-3 rounded-lg transition-all duration-200 ${
                active
                  ? 'bg-primary-500 text-white shadow-lg'
                  : 'text-gray-300 hover:bg-navy-800 hover:text-white'
              }`}
            >
              <Icon className="w-5 h-5 mr-3" />
              <span className="font-medium">{item.label}</span>
            </Link>
          )
        })}
      </nav>

      <div className="p-4 border-t border-navy-800">
        <div className="flex items-center px-4 py-3 mb-2">
          <div className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center mr-3">
            <span className="text-white text-sm font-semibold">
              {user?.full_name?.charAt(0).toUpperCase()}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-white truncate">{user?.full_name}</p>
            <p className="text-xs text-gray-400 capitalize">{user?.role}</p>
          </div>
        </div>
        <button
          onClick={onLogout}
          className="w-full flex items-center px-4 py-3 rounded-lg text-gray-300 hover:bg-navy-800 hover:text-white transition-all duration-200"
        >
          <LogOut className="w-5 h-5 mr-3" />
          <span className="font-medium">Logout</span>
        </button>
      </div>
    </div>
  )
}

export default Sidebar

