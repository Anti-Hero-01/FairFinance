import Card from './Card'

const MetricCard = ({ 
  title, 
  value, 
  subtitle = '', 
  icon: Icon, 
  trend = null,
  className = '',
  borderColor = 'primary'
}) => {
  const borderColors = {
    primary: 'border-l-primary-500',
    teal: 'border-l-teal-500',
    green: 'border-l-green-500',
    red: 'border-l-red-500',
    yellow: 'border-l-yellow-500',
  }
  
  return (
    <Card className={`metric-card ${borderColors[borderColor]} ${className}`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
          <p className="text-2xl font-bold text-navy-900">{value}</p>
          {subtitle && (
            <p className="text-xs text-gray-500 mt-1">{subtitle}</p>
          )}
          {trend && (
            <div className={`flex items-center mt-2 text-sm ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
              {trend > 0 ? (
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              ) : (
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
                </svg>
              )}
              {Math.abs(trend)}%
            </div>
          )}
        </div>
        {Icon && (
          <div className="ml-4 p-3 bg-primary-50 rounded-lg">
            <Icon className="w-6 h-6 text-primary-500" />
          </div>
        )}
      </div>
    </Card>
  )
}

export default MetricCard

