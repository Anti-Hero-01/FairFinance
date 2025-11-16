import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import Sidebar from '../components/ui/Sidebar'
import Card from '../components/ui/Card'
import PageTitle from '../components/ui/PageTitle'
import Button from '../components/ui/Button'
import { applicationService } from '../services/applicationService'
import { useAuth } from '../context/AuthContext'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts'
import toast from 'react-hot-toast'
import { ArrowLeft, CheckCircle, XCircle, TrendingUp, TrendingDown, Info } from 'lucide-react'

const ExplanationDashboard = () => {
  const { applicationId } = useParams()
  const { user, logout } = useAuth()
  const [explanation, setExplanation] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadExplanation()
  }, [applicationId])

  const loadExplanation = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await applicationService.getExplanation(applicationId)
      console.log('Explanation data:', data)
      
      if (data) {
        setExplanation(data)
      } else {
        setError('No explanation data available')
        toast.error('No explanation data available')
      }
    } catch (error) {
      console.error('Failed to load explanation:', error)
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to load explanation'
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
            <p className="text-gray-600">Loading explanation...</p>
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
            <XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-navy-900 mb-2">Unable to Load Explanation</h2>
            <p className="text-gray-600 mb-6">{error || 'No explanation available for this application'}</p>
            <div className="flex gap-4 justify-center">
              <Button onClick={loadExplanation}>Retry</Button>
              <Link to="/dashboard">
                <Button variant="secondary">Back to Dashboard</Button>
              </Link>
            </div>
          </Card>
        </div>
      </div>
    )
  }

  // Prepare chart data with proper structure
  const chartData = [
    ...(explanation.top_positive_features || []).map(f => ({
      feature: f.feature || 'Unknown',
      contribution: Math.abs(f.contribution || 0),
      type: 'Positive',
      color: '#10b981'
    })),
    ...(explanation.top_negative_features || []).map(f => ({
      feature: f.feature || 'Unknown',
      contribution: Math.abs(f.contribution || 0),
      type: 'Negative',
      color: '#ef4444'
    }))
  ]
    .sort((a, b) => b.contribution - a.contribution)
    .slice(0, 10)

  const COLORS = ['#10b981', '#ef4444']

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar onLogout={logout} />
      <div className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-6">
            <Link to="/dashboard">
              <Button variant="outline" size="sm">
                <ArrowLeft className="w-4 h-4 mr-2 inline" />
                Back to Dashboard
              </Button>
            </Link>
          </div>

          <PageTitle
            title="Loan Decision Explanation"
            subtitle="Understand how your application was evaluated"
            icon={Info}
          />

          {/* Decision Summary Card */}
          <Card className="mb-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-semibold text-navy-900 mb-2">Decision Summary</h2>
                <p className="text-sm text-gray-600">Application #{applicationId}</p>
              </div>
              <div className="flex items-center gap-4">
                {explanation.prediction ? (
                  <div className="flex items-center gap-2 px-4 py-2 bg-green-50 rounded-lg border border-green-200">
                    <CheckCircle className="w-6 h-6 text-green-600" />
                    <span className="text-lg font-bold text-green-700">Approved</span>
                  </div>
                ) : (
                  <div className="flex items-center gap-2 px-4 py-2 bg-red-50 rounded-lg border border-red-200">
                    <XCircle className="w-6 h-6 text-red-600" />
                    <span className="text-lg font-bold text-red-700">Denied</span>
                  </div>
                )}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                <p className="text-sm font-medium text-blue-900 mb-1">Approval Probability</p>
                <p className="text-2xl font-bold text-blue-700">
                  {((explanation.probability || 0) * 100).toFixed(2)}%
                </p>
              </div>
              <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                <p className="text-sm font-medium text-gray-900 mb-1">Positive Factors</p>
                <p className="text-2xl font-bold text-gray-700">
                  {explanation.top_positive_features?.length || 0}
                </p>
              </div>
              <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                <p className="text-sm font-medium text-gray-900 mb-1">Negative Factors</p>
                <p className="text-2xl font-bold text-gray-700">
                  {explanation.top_negative_features?.length || 0}
                </p>
              </div>
            </div>

            <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-r-lg">
              <p className="text-blue-900 font-medium">{explanation.explanation_text || 'No explanation available'}</p>
            </div>
          </Card>

          {/* SHAP Feature Contributions Chart */}
          {chartData.length > 0 && (
            <Card className="mb-6">
              <h2 className="text-xl font-semibold text-navy-900 mb-6">SHAP Feature Contributions</h2>
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
                    label={{ value: 'Contribution', angle: -90, position: 'insideLeft' }}
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
                  <Bar dataKey="contribution" name="Contribution" radius={[8, 8, 0, 0]}>
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </Card>
          )}

          {/* Feature Details Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            {/* Positive Factors */}
            <Card>
              <div className="flex items-center gap-2 mb-4">
                <TrendingUp className="w-5 h-5 text-green-600" />
                <h3 className="text-lg font-semibold text-navy-900">Top Positive Factors</h3>
              </div>
              {explanation.top_positive_features && explanation.top_positive_features.length > 0 ? (
                <div className="space-y-3">
                  {explanation.top_positive_features.map((feature, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 bg-green-50 rounded-lg border border-green-200">
                      <span className="text-gray-900 font-medium">{feature.feature || 'Unknown'}</span>
                      <span className="text-green-700 font-bold text-lg">
                        +{(feature.contribution || 0).toFixed(4)}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-4">No positive factors identified</p>
              )}
            </Card>

            {/* Negative Factors */}
            <Card>
              <div className="flex items-center gap-2 mb-4">
                <TrendingDown className="w-5 h-5 text-red-600" />
                <h3 className="text-lg font-semibold text-navy-900">Top Negative Factors</h3>
              </div>
              {explanation.top_negative_features && explanation.top_negative_features.length > 0 ? (
                <div className="space-y-3">
                  {explanation.top_negative_features.map((feature, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 bg-red-50 rounded-lg border border-red-200">
                      <span className="text-gray-900 font-medium">{feature.feature || 'Unknown'}</span>
                      <span className="text-red-700 font-bold text-lg">
                        {(feature.contribution || 0).toFixed(4)}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-4">No negative factors identified</p>
              )}
            </Card>
          </div>

          {/* Ethical Twin Explanation */}
          {explanation.ethical_twin_explanation && (
            <Card>
              <h2 className="text-xl font-semibold text-navy-900 mb-4">Ethical Twin Explanation</h2>
              <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                {explanation.ethical_twin_explanation.rules && (
                  <div className="mb-4">
                    <p className="text-sm font-semibold text-gray-900 mb-2">Decision Rules:</p>
                    <ul className="list-disc list-inside space-y-1">
                      {explanation.ethical_twin_explanation.rules.map((rule, idx) => (
                        <li key={idx} className="text-gray-700">{rule}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {explanation.ethical_twin_explanation.summary && (
                  <p className="text-gray-700">{explanation.ethical_twin_explanation.summary}</p>
                )}
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}

export default ExplanationDashboard
