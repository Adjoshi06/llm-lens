'use client'

import React from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { format } from 'date-fns'
import { TimeSeriesDataPoint } from '@/lib/api'

interface MetricsChartProps {
  data: TimeSeriesDataPoint[]
  metric: 'requests' | 'cost' | 'latency'
  onMetricChange: (metric: 'requests' | 'cost' | 'latency') => void
}

export default function MetricsChart({ data, metric, onMetricChange }: MetricsChartProps) {
  // Group data by timestamp and model
  const groupedData = data.reduce((acc, point) => {
    const timestamp = point.timestamp
    if (!acc[timestamp]) {
      acc[timestamp] = { timestamp: new Date(timestamp) }
    }
    const model = point.model || 'unknown'
    acc[timestamp][model] = point.value
    return acc
  }, {} as Record<string, any>)

  const chartData = Object.values(groupedData).sort((a: any, b: any) => 
    a.timestamp.getTime() - b.timestamp.getTime()
  )

  // Get unique models
  const models = Array.from(new Set(data.map(d => d.model || 'unknown')))

  const metricLabels = {
    requests: 'Requests',
    cost: 'Cost (USD)',
    latency: 'Latency (ms)',
  }

  const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold">{metricLabels[metric]} Over Time</h2>
        <div className="flex gap-2">
          {(['requests', 'cost', 'latency'] as const).map((m) => (
            <button
              key={m}
              onClick={() => onMetricChange(m)}
              className={`px-4 py-2 rounded ${
                metric === m
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {metricLabels[m]}
            </button>
          ))}
        </div>
      </div>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="timestamp"
            tickFormatter={(value) => format(new Date(value), 'HH:mm')}
          />
          <YAxis />
          <Tooltip
            labelFormatter={(value) => format(new Date(value), 'PPp')}
            formatter={(value: number) => {
              if (metric === 'cost') {
                return `$${value.toFixed(4)}`
              }
              if (metric === 'latency') {
                return `${Math.round(value)}ms`
              }
              return value.toLocaleString()
            }}
          />
          <Legend />
          {models.map((model, index) => (
            <Line
              key={model}
              type="monotone"
              dataKey={model}
              stroke={colors[index % colors.length]}
              strokeWidth={2}
              dot={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

