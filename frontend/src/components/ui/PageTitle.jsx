const PageTitle = ({ 
  title, 
  subtitle = '', 
  icon: Icon, 
  action = null,
  className = ''
}) => {
  return (
    <div className={`mb-8 ${className}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          {Icon && (
            <div className="mr-4 p-2 bg-primary-100 rounded-lg">
              <Icon className="w-6 h-6 text-primary-600" />
            </div>
          )}
          <div>
            <h1 className="text-3xl font-bold text-navy-900 font-display">{title}</h1>
            {subtitle && (
              <p className="mt-1 text-sm text-gray-600">{subtitle}</p>
            )}
          </div>
        </div>
        {action && (
          <div>{action}</div>
        )}
      </div>
    </div>
  )
}

export default PageTitle

