import { useEffect, useState } from 'react'
import Sidebar from '../components/ui/Sidebar'
import Card from '../components/ui/Card'
import PageTitle from '../components/ui/PageTitle'
import MetricCard from '../components/ui/MetricCard'
import { explanationService } from '../services/explanationService'
import { useAuth } from '../context/AuthContext'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts'
import toast from 'react-hot-toast'
import { User, TrendingUp, TrendingDown, AlertCircle, CheckCircle } from 'lucide-react'

const ProfileExplanation = () => {
  const { user, logout } = useAuth()
  const [explanation, setExplanation] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (user?.id) {
      loadExplanation()
    }
  }, [user])

  const loadExplanation = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await explanationService.explainProfile(user.id)
      console.log('Profile explanation data:', data)
      
      if (data) {
        setExplanation(data)
      } else {
        setError('No profile data available')
        toast.error('No profile data available')
      }
    } catch (error) {
      console.error('Failed to load profile explanation:', error)
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to load profile explanation'
      setError(errorMessage)
      toast.error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-screen bg-gray-50">
        <Sidebar onLogout={logout} />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
            <p className="text-gray-600">Analyzing your profile...</p>
          </div>
        </div>
      </div>
    )
  }

  if (error || !explanation) {
    return (
      <div className="flex min-h-screen bg-gray-50">
        <Sidebar onLogout={logout} />
        <div className="flex-1 p-8">
          <Card className="text-center py-12">
            <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-navy-900 mb-2">Unable to Load Profile</h2>
            <p className="text-gray-600 mb-6">{error || 'No profile data available'}</p>
            <button onClick={loadExplanation} className="btn-primary">
              Retry
            </button>
          </Card>
        </div>
      </div>
    )
  }

  const getRiskColor = (risk) => {
    switch (risk?.toLowerCase()) {
      case 'low':
        return { bg: 'bg-green-100', text: 'text-green-800', border: 'border-green-500', icon: CheckCircle }
      case 'medium':
        return { bg: 'bg-yellow-100', text: 'text-yellow-800', border: 'border-yellow-500', icon: AlertCircle }
      case 'high':
        return { bg: 'bg-red-100', text: 'text-red-800', border: 'border-red-500', icon: AlertCircle }
      default:
        return { bg: 'bg-gray-100', text: 'text-gray-800', border: 'border-gray-500', icon: AlertCircle }
    }
  }

  const riskInfo = getRiskColor(explanation.risk_category)
  const RiskIcon = riskInfo.icon

  // Prepare chart data for global features
  const chartData = (explanation.top_global_features || [])
    .map(f => ({
      feature: f.feature || 'Unknown',
      contribution: Math.abs(f.contribution || 0),
      isPositive: (f.contribution || 0) > 0
    }))
    .sort((a, b) => b.contribution - a.contribution)
    .slice(0, 10)

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar onLogout={logout} />
      <div className="flex-1 p-8">
        <div className="max-w-6xl mx-auto">
          <PageTitle
            title="Explain My Profile"
            subtitle="Understand your financial profile and loan eligibility factors"
            icon={User}
          />

          {/* Risk Category Card */}
          <Card className="mb-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-xl font-semibold text-navy-900 mb-2">Risk Assessment</h2>
                <p className="text-sm text-gray-600">Based on your application history</p>
              </div>
              <div className={`flex items-center gap-3 px-6 py-3 rounded-lg border-2 ${riskInfo.bg} ${riskInfo.border}`}>
                <RiskIcon className={`w-6 h-6 ${riskInfo.text}`} />
                <span className={`text-lg font-bold ${riskInfo.text}`}>
                  {explanation.risk_category?.toUpperCase() || 'UNKNOWN'}
                </span>
              </div>
            </div>

            <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-r-lg">
              <p className="text-blue-900">{explanation.explanation_text || 'No explanation available'}</p>
            </div>
          </Card>

          {/* Global SHAP Features Chart */}
          {chartData.length > 0 && (
            <Card className="mb-6">
              <h2 className="text-xl font-semibold text-navy-900 mb-6">Top Influencing Factors</h2>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 100 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis 
                    dataKey="feature" 
                    angle={-45} 
                    textAnchor="end" 
                    height={120}
                    tick={{ fill: '#64748b', fontSize: 12 }}
                  />
                  <YAxis 
                    label={{ value: 'Importance', angle: -90, position: 'insideLeft' }}
                    tick={{ fill: '#64748b' }}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'white', 
                      border: '1px solid #e2e8f0',
                      borderRadius: '8px',
                      padding: '12px'
                    }}
                  />
                  <Legend />
                  <Bar dataKey="contribution" name="Feature Importance" radius={[8, 8, 0, 0]}>
                    {chartData.map((entry, index) => (
                      <Cell 
                        key={`cell-${index}`} 
                        fill={entry.isPositive ? '#10b981' : '#ef4444'} 
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </Card>
          )}

          {/* Top Global Features List */}
          <Card className="mb-6">
            <h2 className="text-xl font-semibold text-navy-900 mb-4">Key Profile Factors</h2>
            {explanation.top_global_features && explanation.top_global_features.length > 0 ? (
              <div className="space-y-3">
                {explanation.top_global_features.map((feature, idx) => {
                  const isPositive = (feature.contribution || 0) > 0
                  return (
                    <div 
                      key={idx} 
                      className={`flex items-center justify-between p-4 rounded-lg border ${
                        isPositive 
                          ? 'bg-green-50 border-green-200' 
                          : 'bg-red-50 border-red-200'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        {isPositive ? (
                          <TrendingUp className="w-5 h-5 text-green-600" />
                        ) : (
                          <TrendingDown className="w-5 h-5 text-red-600" />
                        )}
                        <span className="text-gray-900 font-medium">
                          {feature.feature || 'Unknown Feature'}
                        </span>
                      </div>
                      <span className={`font-bold text-lg ${
                        isPositive ? 'text-green-700' : 'text-red-700'
                      }`}>
                        {isPositive ? '+' : ''}{(feature.contribution || 0).toFixed(4)}
                      </span>
                    </div>
                  )
                })}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">No profile factors available</p>
            )}
          </Card>

          {/* Improvement Suggestions */}
          {explanation.improvement_suggestions && explanation.improvement_suggestions.length > 0 && (
            <Card>
              <h2 className="text-xl font-semibold text-navy-900 mb-4">Improvement Suggestions</h2>
              <div className="space-y-3">
                {explanation.improvement_suggestions.map((suggestion, idx) => (
                  <div key={idx} className="flex items-start gap-3 p-4 bg-blue-50 rounded-lg border border-blue-200">
                    <CheckCircle className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="text-gray-900 font-medium mb-1">
                        Improve {suggestion}
                      </p>
                      <p className="text-sm text-gray-600">
                        Consider improving your <strong>{suggestion}</strong> to increase loan eligibility and approval probability.
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}

export default ProfileExplanation
