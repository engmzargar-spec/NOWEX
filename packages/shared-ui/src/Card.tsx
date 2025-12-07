import React from "react"

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string
  subtitle?: string
}

export const Card: React.FC<CardProps> = ({
  title,
  subtitle,
  children,
  className = "",
  ...props
}) => {
  return (
    <div
      className={`
        bg-white rounded-lg shadow-md border border-gray-200
        overflow-hidden
        ${className}
      `}
      {...props}
    >
      {(title || subtitle) && (
        <div className="px-6 py-4 border-b border-gray-200">
          {title && (
            <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
          )}
          {subtitle && (
            <p className="text-sm text-gray-600 mt-1">{subtitle}</p>
          )}
        </div>
      )}
      <div className="px-6 py-4">
        {children}
      </div>
    </div>
  )
}