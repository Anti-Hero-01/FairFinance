import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import Sidebar from '../components/ui/Sidebar'
import Card from '../components/ui/Card'
import PageTitle from '../components/ui/PageTitle'
import Button from '../components/ui/Button'
import MetricCard from '../components/ui/MetricCard'
import { useAuth } from '../context/AuthContext'
import { usePermissions } from '../hooks/usePermissions'
import { applicationService } from '../services/applicationService'
import { FileText, CheckCircle, XCircle, Clock, TrendingUp, TrendingDown, ArrowRight } from 'lucide-react'
import toast from 'react-hot-toast'

const Dashboard = () => {
  const { user, logout } = useAuth()
  const { hasPermission, isUser } = usePermissions()
  const [applications, setApplications] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadApplications()
  }, [])

  const loadApplications = async () => {
    try {
      setLoading(true)
      const data = await applicationService.getApplications()
      setApplications(data || [])
    } catch (error) {
      console.error('Failed to load applications:', error)
      toast.error('Failed to load applications')
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'approved':
        return <CheckCircle className="w-5 h-5 text-green-600" />
      case 'denied':
        return <XCircle className="w-5 h-5 text-red-600" />
      default:
        return <Clock className="w-5 h-5 text-yellow-600" />
    }
  }

  const approvedCount = applications.filter(app => app.status === 'approved').length
  const deniedCount = applications.filter(app => app.status === 'denied').length
  const totalAmount = applications.reduce((sum, app) => sum + (app.loan_amount || 0), 0)
  const avgProbability = applications.length > 0
    ? applications.reduce((sum, app) => sum + (app.probability || 0), 0) / applications.length
    : 0

  if (loading) {
    return (
      <div className="flex min-h-screen bg-gray-50">
        <Sidebar onLogout={logout} />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading dashboard...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar onLogout={logout} />
      <div className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          <PageTitle
            title="Dashboard"
            subtitle="View and manage your loan applications"
            action={
              hasPermission('apply_for_loan') && (
                <Link to="/apply">
                  <Button>
                    <FileText className="w-4 h-4 mr-2 inline" />
                    New Loan Application
                  </Button>
                </Link>
              )
            }
          />

          {/* Metrics Cards */}
          {applications.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <MetricCard
                title="Total Applications"
                value={applications.length}
                subtitle="All time"
                icon={FileText}
                borderColor="primary"
              />
              <MetricCard
                title="Approved"
                value={approvedCount}
                subtitle={`${applications.length > 0 ? ((approvedCount / applications.length) * 100).toFixed(1) : 0}% approval rate`}
                icon={CheckCircle}
                borderColor="green"
              />
              <MetricCard
                title="Denied"
                value={deniedCount}
                subtitle={`${applications.length > 0 ? ((deniedCount / applications.length) * 100).toFixed(1) : 0}% denial rate`}
                icon={XCircle}
                borderColor="red"
              />
              <MetricCard
                title="Avg. Probability"
                value={`${(avgProbability * 100).toFixed(1)}%`}
                subtitle="Average approval probability"
                icon={TrendingUp}
                borderColor="teal"
              />
            </div>
          )}

          {/* Applications List */}
          <Card>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-navy-900">Loan Applications</h2>
              {applications.length > 0 && (
                <span className="text-sm text-gray-600">
                  {applications.length} {applications.length === 1 ? 'application' : 'applications'}
                </span>
              )}
            </div>

            {applications.length === 0 ? (
              <div className="text-center py-12">
                <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">No applications yet</h3>
                <p className="text-gray-600 mb-6">
                  {hasPermission('apply_for_loan') 
                    ? 'Get started by submitting your first loan application'
                    : 'No applications available'}
                </p>
                {hasPermission('apply_for_loan') && (
                  <Link to="/apply">
                    <Button>
                      <FileText className="w-4 h-4 mr-2 inline" />
                      Apply for Loan
                    </Button>
                  </Link>
                )}
              </div>
            ) : (
              <div className="space-y-4">
                {applications.map((app) => (
                  <div
                    key={app.id}
                    className="border border-gray-200 rounded-lg p-5 hover:shadow-md transition-shadow duration-200"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4 flex-1">
                        {getStatusIcon(app.status)}
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-1">
                            <h3 className="text-lg font-semibold text-navy-900">
                              Application #{app.id}
                            </h3>
                            <span className={`px-3 py-1 text-xs font-semibold rounded-full ${
                              app.status === 'approved' 
                                ? 'bg-green-100 text-green-800' 
                                : app.status === 'denied'
                                ? 'bg-red-100 text-red-800'
                                : 'bg-yellow-100 text-yellow-800'
                            }`}>
                              {app.status}
                            </span>
                          </div>
                          <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600">
                            <span>
                              <strong>Amount:</strong> ₹{app.loan_amount?.toLocaleString('en-IN') || '0'}
                            </span>
                            <span>
                              <strong>Probability:</strong> {((app.probability || 0) * 100).toFixed(1)}%
                            </span>
                            {app.created_at && (
                              <span>
                                <strong>Date:</strong> {new Date(app.created_at).toLocaleDateString()}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        {app.prediction !== null && (
                          <Link to={`/explain/${app.id}`}>
                            <Button variant="outline" size="sm">
                              View Explanation
                              <ArrowRight className="w-4 h-4 ml-2 inline" />
                            </Button>
                          </Link>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
