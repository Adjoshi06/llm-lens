'use client'

import { useEffect, useState } from 'react'
import StatsCard from '@/components/StatsCard'
import MetricsChart from '@/components/MetricsChart'
import CostTracker from '@/components/CostTracker'
import RecentCalls from '@/components/RecentCalls'
import { fetchMetricsOverview, fetchTimeSeries, fetchConversations } from '@/lib/api'

export default function Dashboard() {
  const [metrics, setMetrics] = useState<any>(null)
  const [timeSeriesData, setTimeSeriesData] = useState<any>(null)
  const [conversations, setConversations] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [selectedMetric, setSelectedMetric] = useState<'requests' | 'cost' | 'latency'>('requests')

  useEffect(() => {
    loadData()
    // Refresh data every 30 seconds
    const interval = setInterval(loadData, 30000)
    return () => clearInterval(interval)
  }, [selectedMetric])

  const loadData = async () => {
    try {
      setLoading(true)
      
      // Calculate time range (last 24 hours)
      const endTime = new Date()
      const startTime = new Date(endTime.getTime() - 24 * 60 * 60 * 1000)

      // Fetch all data in parallel
      const [metricsData, timeSeries, conversationsData] = await Promise.all([
        fetchMetricsOverview(24),
        fetchTimeSeries(startTime, endTime, '1h', selectedMetric),
        fetchConversations(1, 100)
      ])

      setMetrics(metricsData)
      setTimeSeriesData(timeSeries)
      setConversations(conversationsData)
    } catch (error) {
      console.error('Error loading data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading && !metrics) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">LLM Monitor Dashboard</h1>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatsCard
            title="Total Requests (24h)"
            value={metrics?.total_requests?.toLocaleString() || '0'}
            icon="📊"
          />
          <StatsCard
            title="Total Cost (24h)"
            value={`$${metrics?.total_cost?.toFixed(2) || '0.00'}`}
            icon="💰"
          />
          <StatsCard
            title="Avg Latency"
            value={`${Math.round(metrics?.avg_latency_ms || 0)}ms`}
            icon="⚡"
          />
          <StatsCard
            title="Error Rate"
            value={`${metrics?.error_rate || 0}%`}
            icon="⚠️"
            variant={metrics?.error_rate > 5 ? 'error' : 'default'}
          />
        </div>

        {/* Metrics Chart */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <MetricsChart
            data={timeSeriesData?.data || []}
            metric={selectedMetric}
            onMetricChange={setSelectedMetric}
          />
        </div>

        {/* Cost Tracker and Recent Calls */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <CostTracker metrics={metrics} />
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <RecentCalls events={conversations?.events || []} />
          </div>
        </div>
      </div>
    </div>
  )
}

