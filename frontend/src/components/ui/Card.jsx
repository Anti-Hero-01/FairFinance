const Card = ({ children, className = '', hover = false, ...props }) => {
  return (
    <div
      className={`card ${hover ? 'hover:shadow-card-hover cursor-pointer' : ''} ${className}`}
      {...props}
    >
      {children}
    </div>
  )
}

export default Card

