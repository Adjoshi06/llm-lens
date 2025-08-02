import React from 'react'

interface StatsCardProps {
  title: string
  value: string | number
  icon?: string
  variant?: 'default' | 'error' | 'success'
}

export default function StatsCard({ title, value, icon, variant = 'default' }: StatsCardProps) {
  const variantStyles = {
    default: 'bg-white border-gray-200',
    error: 'bg-red-50 border-red-200',
    success: 'bg-green-50 border-green-200',
  }

  return (
    <div className={`rounded-lg shadow p-6 border ${variantStyles[variant]}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-2">{value}</p>
        </div>
        {icon && <div className="text-4xl">{icon}</div>}
      </div>
    </div>
  )
}

