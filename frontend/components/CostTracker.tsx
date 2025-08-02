'use client'

import React from 'react'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'

interface CostTrackerProps {
  metrics: {
    requests_by_model?: Record<string, number>
    total_cost?: number
  } | null
}

export default function CostTracker({ metrics }: CostTrackerProps) {
  if (!metrics || !metrics.requests_by_model) {
    return (
      <div>
        <h2 className="text-xl font-semibold mb-4">Cost Breakdown</h2>
        <p className="text-gray-500">No data available</p>
      </div>
    )
  }

  // For now, we'll show requests by model as a proxy for cost
  // In a real implementation, you'd want to fetch actual cost data per model
  const data = Object.entries(metrics.requests_by_model).map(([model, count]) => ({
    name: model,
    value: count,
  }))

  const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">Cost Breakdown by Model</h2>
      <div className="flex items-center justify-center">
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-4">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b">
              <th className="text-left py-2">Model</th>
              <th className="text-right py-2">Requests</th>
            </tr>
          </thead>
          <tbody>
            {data.map((item, index) => (
              <tr key={item.name} className="border-b">
                <td className="py-2">{item.name}</td>
                <td className="text-right py-2">{item.value.toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

