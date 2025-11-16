import { useEffect, useState } from 'react'
import Sidebar from '../components/ui/Sidebar'
import Card from '../components/ui/Card'
import PageTitle from '../components/ui/PageTitle'
import Button from '../components/ui/Button'
import { consentService } from '../services/consentService'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'
import { Shield, AlertCircle, CheckCircle, Info } from 'lucide-react'

const ConsentDashboard = () => {
  const { user, logout } = useAuth()
  const [dashboard, setDashboard] = useState(null)
  const [loading, setLoading] = useState(true)
  const [updating, setUpdating] = useState({})
  const [error, setError] = useState(null)

  useEffect(() => {
    loadDashboard()
  }, [])

  const loadDashboard = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await consentService.getDashboard()
      setDashboard(data)
    } catch (error) {
      console.error('Failed to load consent dashboard:', error)
      setError(error.response?.data?.detail || 'Failed to load consent dashboard')
      toast.error(error.response?.data?.detail || 'Failed to load consent dashboard')
    } finally {
      setLoading(false)
    }
  }

  const handleConsentUpdate = async (dataCategory, consentGiven) => {
    try {
      setUpdating(prev => ({ ...prev, [dataCategory]: true }))
      setError(null)
      
      const result = await consentService.updateConsent(dataCategory, consentGiven)
      
      // Update local state immediately for better UX
      setDashboard(prev => ({
        ...prev,
        consents: prev.consents.map(consent =>
          consent.data_category === dataCategory
            ? { ...consent, consent_given: consentGiven, last_updated: result.last_updated }
            : consent
        )
      }))
      
      toast.success(`Consent ${consentGiven ? 'granted' : 'revoked'} successfully`)
      
      // Reload to get updated alerts
      await loadDashboard()
    } catch (error) {
      console.error('Failed to update consent:', error)
      setError(error.response?.data?.detail || 'Failed to update consent')
      toast.error(error.response?.data?.detail || 'Failed to update consent')
      
      // Reload to revert UI state
      await loadDashboard()
    } finally {
      setUpdating(prev => ({ ...prev, [dataCategory]: false }))
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-screen bg-gray-50">
        <Sidebar onLogout={logout} />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading consent dashboard...</p>
          </div>
        </div>
      </div>
    )
  }

  if (error && !dashboard) {
    return (
      <div className="flex min-h-screen bg-gray-50">
        <Sidebar onLogout={logout} />
        <div className="flex-1 p-8">
          <Card className="text-center py-12">
            <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-navy-900 mb-2">Unable to Load Dashboard</h2>
            <p className="text-gray-600 mb-6">{error}</p>
            <Button onClick={loadDashboard}>Retry</Button>
          </Card>
        </div>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar onLogout={logout} />
      <div className="flex-1 p-8">
        <div className="max-w-4xl mx-auto">
          <PageTitle
            title="Privacy Consent Dashboard"
            subtitle="Manage your data usage permissions and privacy settings"
            icon={Shield}
          />

          {/* Alert Messages */}
          {dashboard?.alert_messages && dashboard.alert_messages.length > 0 && (
            <Card className="mb-6 border-l-4 border-yellow-500 bg-yellow-50">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5 flex-shrink-0" />
                <div className="flex-1">
                  <h3 className="text-sm font-semibold text-yellow-800 mb-2">Important Alerts</h3>
                  <ul className="space-y-1">
                    {dashboard.alert_messages.map((msg, idx) => (
                      <li key={idx} className="text-sm text-yellow-700">{msg}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </Card>
          )}

          {/* Error Message */}
          {error && (
            <Card className="mb-6 border-l-4 border-red-500 bg-red-50">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
                <div>
                  <h3 className="text-sm font-semibold text-red-800 mb-1">Error</h3>
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              </div>
            </Card>
          )}

          {/* Consent Cards */}
          <Card>
            <h2 className="text-xl font-semibold text-navy-900 mb-6">Data Usage Permissions</h2>
            
            {dashboard?.consents && dashboard.consents.length > 0 ? (
              <div className="space-y-4">
                {dashboard.consents.map((consent) => {
                  const isUpdating = updating[consent.data_category]
                  const categoryName = consent.data_category
                    .split('_')
                    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                    .join(' ')

                  return (
                    <div 
                      key={consent.data_category} 
                      className={`border-2 rounded-lg p-5 transition-all duration-200 ${
                        consent.consent_given 
                          ? 'border-green-200 bg-green-50' 
                          : 'border-red-200 bg-red-50'
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            {consent.consent_given ? (
                              <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0" />
                            ) : (
                              <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0" />
                            )}
                            <h3 className="text-lg font-semibold text-navy-900">
                              {categoryName}
                            </h3>
                          </div>
                          
                          {consent.description && (
                            <p className="text-sm text-gray-700 mb-2 ml-9">
                              {consent.description}
                            </p>
                          )}
                          
                          {consent.required_for && consent.required_for.length > 0 && (
                            <div className="ml-9">
                              <p className="text-xs font-medium text-gray-600 mb-1">
                                Required for:
                              </p>
                              <div className="flex flex-wrap gap-2">
                                {consent.required_for.map((req, idx) => (
                                  <span 
                                    key={idx}
                                    className="px-2 py-1 text-xs bg-gray-200 text-gray-700 rounded-md"
                                  >
                                    {req}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                          
                          {consent.last_updated && (
                            <p className="text-xs text-gray-500 mt-2 ml-9">
                              Last updated: {new Date(consent.last_updated).toLocaleString()}
                            </p>
                          )}
                        </div>
                        
                        <div className="ml-4 flex items-center">
                          <label className="relative inline-flex items-center cursor-pointer">
                            <input
                              type="checkbox"
                              checked={consent.consent_given}
                              onChange={(e) => handleConsentUpdate(consent.data_category, e.target.checked)}
                              disabled={isUpdating}
                              className="sr-only peer"
                            />
                            <div className={`w-14 h-7 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer transition-colors duration-200 ${
                              consent.consent_given ? 'peer-checked:bg-green-500' : ''
                            } peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all ${
                              isUpdating ? 'opacity-50 cursor-not-allowed' : ''
                            }`}></div>
                          </label>
                          {isUpdating && (
                            <div className="ml-3">
                              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-500"></div>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-500">No consent settings available</p>
              </div>
            )}
          </Card>

          {/* Information Card */}
          <Card className="mt-6 border-l-4 border-blue-500 bg-blue-50">
            <div className="flex items-start gap-3">
              <Info className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
              <div>
                <h3 className="text-sm font-semibold text-blue-900 mb-1">About Your Consent</h3>
                <p className="text-sm text-blue-800">
                  You can revoke consent at any time. Some features may become unavailable if you revoke required permissions. 
                  Your data is protected and used only for the purposes you consent to. Changes take effect immediately.
                </p>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default ConsentDashboard
