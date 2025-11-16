import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Sidebar from '../components/ui/Sidebar'
import Card from '../components/ui/Card'
import PageTitle from '../components/ui/PageTitle'
import Button from '../components/ui/Button'
import InputField from '../components/ui/InputField'
import { applicationService } from '../services/applicationService'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'
import { FileText, ArrowLeft } from 'lucide-react'
import { Link } from 'react-router-dom'

const LoanApplication = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    age: '',
    income: '',
    credit_score: '',
    loan_amount: '',
    employment_years: '',
    debt_to_income: '',
    credit_history_length: '',
    number_of_accounts: '',
    defaults: '',
    gender: '',
    region: '',
    age_group: ''
  })
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData({
      ...formData,
      [name]: value
    })
    // Clear error for this field
    if (errors[name]) {
      setErrors({
        ...errors,
        [name]: ''
      })
    }
  }

  const validateForm = () => {
    const newErrors = {}
    
    if (!formData.age || parseInt(formData.age) < 18 || parseInt(formData.age) > 100) {
      newErrors.age = 'Age must be between 18 and 100'
    }
    if (!formData.income || parseFloat(formData.income) <= 0) {
      newErrors.income = 'Income must be greater than 0'
    }
    if (!formData.credit_score || parseInt(formData.credit_score) < 300 || parseInt(formData.credit_score) > 850) {
      newErrors.credit_score = 'Credit score must be between 300 and 850'
    }
    if (!formData.loan_amount || parseFloat(formData.loan_amount) <= 0) {
      newErrors.loan_amount = 'Loan amount must be greater than 0'
    }
    if (!formData.employment_years || parseInt(formData.employment_years) < 0) {
      newErrors.employment_years = 'Employment years cannot be negative'
    }
    if (!formData.debt_to_income || parseFloat(formData.debt_to_income) < 0 || parseFloat(formData.debt_to_income) > 1) {
      newErrors.debt_to_income = 'Debt to income ratio must be between 0 and 1'
    }
    if (!formData.credit_history_length || parseInt(formData.credit_history_length) < 0) {
      newErrors.credit_history_length = 'Credit history length cannot be negative'
    }
    if (!formData.number_of_accounts || parseInt(formData.number_of_accounts) < 0) {
      newErrors.number_of_accounts = 'Number of accounts cannot be negative'
    }
    if (formData.defaults === '' || parseInt(formData.defaults) < 0) {
      newErrors.defaults = 'Number of defaults cannot be negative'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!validateForm()) {
      toast.error('Please fix the errors in the form')
      return
    }

    setLoading(true)

    try {
      const applicationData = {
        ...formData,
        age: parseInt(formData.age),
        income: parseFloat(formData.income),
        credit_score: parseInt(formData.credit_score),
        loan_amount: parseFloat(formData.loan_amount),
        employment_years: parseInt(formData.employment_years),
        debt_to_income: parseFloat(formData.debt_to_income),
        credit_history_length: parseInt(formData.credit_history_length),
        number_of_accounts: parseInt(formData.number_of_accounts),
        defaults: parseInt(formData.defaults)
      }

      const result = await applicationService.predict(applicationData)
      console.log('Application result:', result)
      
      if (result && result.application_id) {
        toast.success(`Loan ${result.approved ? 'Approved' : 'Denied'}!`)
        navigate(`/explain/${result.application_id}`)
      } else {
        toast.error('Application submitted but no response received. Please check your applications.')
        navigate('/dashboard')
      }
    } catch (error) {
      console.error('Application error:', error)
      const errorMessage = error.response?.data?.detail || error.message || 'Application failed. Please try again.'
      toast.error(errorMessage)
      
      // If it's a consent error, redirect to consent page
      if (error.response?.status === 403 && errorMessage.includes('consent')) {
        setTimeout(() => navigate('/consent'), 2000)
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar onLogout={logout} />
      <div className="flex-1 p-8">
        <div className="max-w-4xl mx-auto">
          <div className="mb-6">
            <Link to="/dashboard">
              <Button variant="outline" size="sm">
                <ArrowLeft className="w-4 h-4 mr-2 inline" />
                Back to Dashboard
              </Button>
            </Link>
          </div>

          <PageTitle
            title="Loan Application"
            subtitle="Fill in your details to apply for a loan"
            icon={FileText}
          />

          <Card>
            <form onSubmit={handleSubmit}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <InputField
                  label="Age"
                  name="age"
                  type="number"
                  value={formData.age}
                  onChange={handleChange}
                  placeholder="Enter your age"
                  required
                  error={errors.age}
                  min="18"
                  max="100"
                />

                <InputField
                  label="Monthly Income (₹)"
                  name="income"
                  type="number"
                  value={formData.income}
                  onChange={handleChange}
                  placeholder="Enter monthly income"
                  required
                  error={errors.income}
                  min="0"
                  step="0.01"
                />

                <InputField
                  label="Credit Score"
                  name="credit_score"
                  type="number"
                  value={formData.credit_score}
                  onChange={handleChange}
                  placeholder="Enter credit score (300-850)"
                  required
                  error={errors.credit_score}
                  min="300"
                  max="850"
                />

                <InputField
                  label="Loan Amount (₹)"
                  name="loan_amount"
                  type="number"
                  value={formData.loan_amount}
                  onChange={handleChange}
                  placeholder="Enter loan amount"
                  required
                  error={errors.loan_amount}
                  min="0"
                  step="0.01"
                />

                <InputField
                  label="Employment Years"
                  name="employment_years"
                  type="number"
                  value={formData.employment_years}
                  onChange={handleChange}
                  placeholder="Years of employment"
                  required
                  error={errors.employment_years}
                  min="0"
                />

                <InputField
                  label="Debt to Income Ratio"
                  name="debt_to_income"
                  type="number"
                  value={formData.debt_to_income}
                  onChange={handleChange}
                  placeholder="0.0 to 1.0"
                  required
                  error={errors.debt_to_income}
                  min="0"
                  max="1"
                  step="0.01"
                />

                <InputField
                  label="Credit History Length (years)"
                  name="credit_history_length"
                  type="number"
                  value={formData.credit_history_length}
                  onChange={handleChange}
                  placeholder="Years of credit history"
                  required
                  error={errors.credit_history_length}
                  min="0"
                />

                <InputField
                  label="Number of Accounts"
                  name="number_of_accounts"
                  type="number"
                  value={formData.number_of_accounts}
                  onChange={handleChange}
                  placeholder="Total number of accounts"
                  required
                  error={errors.number_of_accounts}
                  min="0"
                />

                <InputField
                  label="Number of Defaults"
                  name="defaults"
                  type="number"
                  value={formData.defaults}
                  onChange={handleChange}
                  placeholder="Number of payment defaults"
                  required
                  error={errors.defaults}
                  min="0"
                />

                <div className="mb-4">
                  <label className="block text-sm font-semibold text-navy-900 mb-2">
                    Gender (Optional)
                  </label>
                  <select
                    name="gender"
                    value={formData.gender}
                    onChange={handleChange}
                    className="input-field"
                  >
                    <option value="">Select Gender</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                <div className="mb-4">
                  <label className="block text-sm font-semibold text-navy-900 mb-2">
                    Region (Optional)
                  </label>
                  <select
                    name="region"
                    value={formData.region}
                    onChange={handleChange}
                    className="input-field"
                  >
                    <option value="">Select Region</option>
                    <option value="urban">Urban</option>
                    <option value="rural">Rural</option>
                    <option value="semi-urban">Semi-Urban</option>
                  </select>
                </div>
              </div>

              <div className="mt-8 pt-6 border-t border-gray-200">
                <div className="flex gap-4">
                  <Button
                    type="submit"
                    disabled={loading}
                    className="flex-1"
                  >
                    {loading ? 'Processing...' : 'Submit Application'}
                  </Button>
                  <Link to="/dashboard" className="flex-1">
                    <Button
                      type="button"
                      variant="secondary"
                      className="w-full"
                    >
                      Cancel
                    </Button>
                  </Link>
                </div>
              </div>
            </form>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default LoanApplication
