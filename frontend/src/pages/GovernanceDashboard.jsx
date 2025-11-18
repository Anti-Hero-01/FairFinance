import { useEffect, useState } from 'react'
import Sidebar from '../components/ui/Sidebar'
import Card from '../components/ui/Card'
import PageTitle from '../components/ui/PageTitle'
import Button from '../components/ui/Button'
import DataTable from '../components/ui/DataTable'
import MetricCard from '../components/ui/MetricCard'
import { governanceService } from '../services/governanceService'
import { useAuth } from '../context/AuthContext'
import { usePermissions } from '../hooks/usePermissions'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts'
import toast from 'react-hot-toast'
import { Shield, AlertTriangle, CheckCircle, Download, RefreshCw, Edit, X, Check } from 'lucide-react'

const GovernanceDashboard = () => {
  const { user, logout } = useAuth()
  const { hasPermission, isAdmin } = usePermissions()
  const [fairnessReport, setFairnessReport] = useState(null)
  const [decisionLogs, setDecisionLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedUserId, setSelectedUserId] = useState(null)
  const [overrideModal, setOverrideModal] = useState(null)
  const [overrideReason, setOverrideReason] = useState('')
  const [overrideDecision, setOverrideDecision] = useState(true)

  useEffect(() => {
    // Wait until auth has loaded user info before fetching governance data
    if (user) {
      loadData()
    }
  }, [user])

  const loadData = async (userId = null) => {
    try {
      setLoading(true)
      // For users: fetch own logs; for admin/auditor: fetch all logs
      const shouldFetchOwnOnly = user.role === 'user'
      const [report, logs] = await Promise.all([
        governanceService.getFairnessReport().catch(() => null),
        shouldFetchOwnOnly 
          ? governanceService.getDecisionLog(user.id).catch(() => [])
          : governanceService.getDecisionLogs().catch(() => [])
      ])
      setFairnessReport(report)
      setDecisionLogs(logs || [])
    } catch (error) {
      console.error('Failed to load governance data:', error)
      toast.error('Failed to load governance data')
    } finally {
      setLoading(false)
    }
  }

  const handleExportLogs = async () => {
    try {
      const response = await governanceService.exportLogs(selectedUserId, 'csv')
      const blob = response.data instanceof Blob ? response.data : new Blob([JSON.stringify(response.data)], { type: 'text/csv' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `decision_logs_${new Date().toISOString().split('T')[0]}.csv`
      a.click()
      window.URL.revokeObjectURL(url)
      toast.success('Logs exported successfully')
    } catch (error) {
      console.error('Failed to export logs:', error)
      toast.error('Failed to export logs')
    }
  }

  const handleRetrain = async () => {
    try {
      await governanceService.triggerRetraining()
      toast.success('Model retraining initiated')
    } catch (error) {
      toast.error('Failed to trigger retraining')
    }
  }

  const handleOverride = async () => {
    if (!overrideModal || !overrideReason.trim()) {
      toast.error('Please provide a reason for the override')
      return
    }

    try {
      await governanceService.adminOverride(
        overrideModal.application_id,
        overrideDecision,
        overrideReason
      )
      toast.success(`Decision ${overrideDecision ? 'approved' : 'denied'} successfully`)
      setOverrideModal(null)
      setOverrideReason('')
      setOverrideDecision(true)
      loadData()
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to override decision')
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-screen bg-gray-50">
        <Sidebar onLogout={logout} />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading governance data...</p>
          </div>
        </div>
      </div>
    )
  }

  // Prepare chart data for fairness metrics
  const fairnessChartData = fairnessReport?.metrics?.map(metric => ({
    name: `${metric.metric_name.replace(/_/g, ' ')} (${metric.attribute})`,
    value: Math.abs(metric.value),
    threshold: metric.threshold,
    status: metric.status
  })) || []

  const violationCount = fairnessReport?.violations?.length || 0
  const passCount = (fairnessReport?.metrics?.filter(m => m.status === 'pass').length || 0)

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar onLogout={logout} />
      <div className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          <PageTitle
            title="Governance Dashboard"
            subtitle="Monitor fairness metrics, audit logs, and manage decisions"
            icon={Shield}
            action={
              <div className="flex gap-3">
                {hasPermission('export_logs_full') || hasPermission('export_logs_limited') ? (
                  <Button variant="secondary" onClick={handleExportLogs}>
                    <Download className="w-4 h-4 mr-2 inline" />
                    Export Logs
                  </Button>
                ) : null}
                {hasPermission('trigger_retraining') && (
                  <Button variant="secondary" onClick={handleRetrain}>
                    <RefreshCw className="w-4 h-4 mr-2 inline" />
                    Retrain Model
                  </Button>
                )}
              </div>
            }
          />

          {/* Fairness Metrics Summary */}
          {fairnessReport && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <MetricCard
                title="Fairness Violations"
                value={violationCount}
                subtitle="Issues requiring attention"
                icon={AlertTriangle}
                borderColor={violationCount > 0 ? 'red' : 'green'}
              />
              <MetricCard
                title="Metrics Passing"
                value={passCount}
                subtitle={`of ${fairnessReport.metrics?.length || 0} total metrics`}
                icon={CheckCircle}
                borderColor="green"
              />
              <MetricCard
                title="Total Metrics"
                value={fairnessReport.metrics?.length || 0}
                subtitle="Monitored fairness indicators"
                icon={Shield}
                borderColor="primary"
              />
            </div>
          )}

          {/* Fairness Report */}
          {fairnessReport && (
            <>
              {/* Violations Alert */}
              {fairnessReport.violations && fairnessReport.violations.length > 0 && (
                <Card className="mb-6 border-l-4 border-red-500 bg-red-50">
                  <div className="flex items-start gap-3">
                    <AlertTriangle className="w-6 h-6 text-red-600 mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-red-800 mb-2">Fairness Violations Detected</h3>
                      <ul className="space-y-2">
                        {fairnessReport.violations.map((violation, idx) => (
                          <li key={idx} className="text-sm text-red-700">
                            <strong>{violation.attribute}</strong> - {violation.metric}: {violation.value?.toFixed(4) || 'N/A'} 
                            (threshold: {violation.threshold})
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </Card>
              )}

              {/* No Violations */}
              {(!fairnessReport.violations || fairnessReport.violations.length === 0) && (
                <Card className="mb-6 border-l-4 border-green-500 bg-green-50">
                  <div className="flex items-center gap-3">
                    <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0" />
                    <p className="text-green-800 font-semibold">No Fairness Violations Detected</p>
                  </div>
                </Card>
              )}

              {/* Fairness Chart */}
              {fairnessChartData.length > 0 && (
                <Card className="mb-6">
                  <h2 className="text-xl font-semibold text-navy-900 mb-6">Fairness Metrics Overview</h2>
                  <ResponsiveContainer width="100%" height={400}>
                    <BarChart data={fairnessChartData} margin={{ top: 20, right: 30, left: 20, bottom: 100 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                      <XAxis 
                        dataKey="name" 
                        angle={-45} 
                        textAnchor="end" 
                        height={120}
                        tick={{ fill: '#64748b', fontSize: 11 }}
                      />
                      <YAxis 
                        label={{ value: 'Value', angle: -90, position: 'insideLeft' }}
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
                      <Bar dataKey="value" fill="#0EA5E9" name="Current Value" radius={[8, 8, 0, 0]} />
                      <Bar dataKey="threshold" fill="#ef4444" name="Threshold" radius={[8, 8, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </Card>
              )}

              {/* Metrics Table */}
              {fairnessReport.metrics && fairnessReport.metrics.length > 0 && (
                <Card className="mb-6">
                  <h2 className="text-xl font-semibold text-navy-900 mb-4">Fairness Metrics Details</h2>
                  <DataTable
                    headers={['Metric', 'Attribute', 'Value', 'Threshold', 'Status']}
                    data={fairnessReport.metrics}
                    renderRow={(metric) => (
                      <>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {metric.metric_name.replace(/_/g, ' ')}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {metric.attribute}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-medium">
                          {metric.value?.toFixed(4) || 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {metric.threshold}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-3 py-1 text-xs font-semibold rounded-full ${
                            metric.status === 'pass' 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {metric.status}
                          </span>
                        </td>
                      </>
                    )}
                  />
                </Card>
              )}

              {/* Recommendations */}
              {fairnessReport.recommendations && fairnessReport.recommendations.length > 0 && (
                <Card className="mb-6">
                  <h2 className="text-xl font-semibold text-navy-900 mb-4">Recommendations</h2>
                  <ul className="space-y-2">
                    {fairnessReport.recommendations.map((rec, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-gray-700">
                        <CheckCircle className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </Card>
              )}
            </>
          )}

          {/* Decision Logs */}
          <Card>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-navy-900">Decision Log</h2>
              <Button variant="secondary" size="sm" onClick={() => loadData()}>
                <RefreshCw className="w-4 h-4 mr-2 inline" />
                Refresh
              </Button>
            </div>
            <DataTable
              headers={['Application ID', 'User ID', 'Prediction', 'Probability', 'Timestamp', 'Override', 'Actions']}
              data={decisionLogs.slice(0, 20)}
              emptyMessage="No decision logs available"
              renderRow={(log) => (
                <>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-medium">
                    #{log.application_id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {log.user_id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-3 py-1 text-xs font-semibold rounded-full ${
                      log.prediction 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {log.prediction ? 'Approved' : 'Denied'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {((log.probability || 0) * 100).toFixed(2)}%
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {log.timestamp ? new Date(log.timestamp).toLocaleString() : 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {log.admin_override ? (
                      <span className="px-2 py-1 text-xs font-semibold bg-yellow-100 text-yellow-800 rounded-full">
                        Overridden
                      </span>
                    ) : (
                      <span className="text-xs text-gray-400">-</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {(hasPermission('override_decision_approve') || hasPermission('override_decision_recommend')) && (
                      <button
                        onClick={() => setOverrideModal(log)}
                        className="text-primary-600 hover:text-primary-800 font-medium"
                      >
                        <Edit className="w-4 h-4 inline mr-1" />
                        Override
                      </button>
                    )}
                  </td>
                </>
              )}
            />
          </Card>
        </div>
      </div>

      {/* Override Modal */}
      {overrideModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <Card className="max-w-md w-full">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold text-navy-900">Override Decision</h3>
              <button
                onClick={() => {
                  setOverrideModal(null)
                  setOverrideReason('')
                  setOverrideDecision(true)
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="mb-4">
              <p className="text-sm text-gray-600 mb-2">
                Application ID: <strong>#{overrideModal.application_id}</strong>
              </p>
              <p className="text-sm text-gray-600 mb-4">
                Current Decision: <strong>{overrideModal.prediction ? 'Approved' : 'Denied'}</strong>
              </p>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-semibold text-navy-900 mb-2">
                New Decision
              </label>
              <div className="flex gap-4">
                <button
                  onClick={() => setOverrideDecision(true)}
                  className={`flex-1 py-2 px-4 rounded-lg border-2 transition-all ${
                    overrideDecision
                      ? 'border-green-500 bg-green-50 text-green-700'
                      : 'border-gray-300 bg-white text-gray-700'
                  }`}
                >
                  Approve
                </button>
                <button
                  onClick={() => setOverrideDecision(false)}
                  className={`flex-1 py-2 px-4 rounded-lg border-2 transition-all ${
                    !overrideDecision
                      ? 'border-red-500 bg-red-50 text-red-700'
                      : 'border-gray-300 bg-white text-gray-700'
                  }`}
                >
                  Deny
                </button>
              </div>
            </div>

            <div className="mb-6">
              <label className="block text-sm font-semibold text-navy-900 mb-2">
                Reason for Override <span className="text-red-500">*</span>
              </label>
              <textarea
                value={overrideReason}
                onChange={(e) => setOverrideReason(e.target.value)}
                placeholder="Provide a detailed reason for this override..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                rows={4}
              />
            </div>

            <div className="flex gap-3">
              <Button
                variant="secondary"
                onClick={() => {
                  setOverrideModal(null)
                  setOverrideReason('')
                  setOverrideDecision(true)
                }}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button
                onClick={handleOverride}
                disabled={!overrideReason.trim()}
                className="flex-1"
              >
                <Check className="w-4 h-4 mr-2 inline" />
                Confirm Override
              </Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  )
}

export default GovernanceDashboard
