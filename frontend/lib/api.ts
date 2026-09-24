// API client for the LLM Monitor backend.
// This module was missing from the repository (dashboard imports `@/lib/api`).
// Implemented against the endpoints documented in README.md.
import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

export interface TimeSeriesDataPoint {
  timestamp: string
  model: string
  value: number
}

export interface LLMEvent {
  id: string
  timestamp: string
  model: string
  prompt_tokens: number | null
  completion_tokens: number | null
  total_tokens: number | null
  latency_ms: number | null
  cost_usd: number | null
  status: 'success' | 'error'
  error_message: string | null
  tags: Record<string, string> | null
  created_at: string
}

export interface MetricsOverview {
  total_requests: number
  total_cost: number
  avg_latency_ms: number
  error_rate: number
  requests_by_model: Record<string, number>
}

export async function fetchMetricsOverview(hours: number = 24): Promise<MetricsOverview> {
  const response = await api.get<MetricsOverview>('/api/metrics/overview', {
    params: { hours },
  })
  return response.data
}

export async function fetchTimeSeries(
  startTime: Date,
  endTime: Date,
  interval: '1h' | '1d',
  metric: 'requests' | 'cost' | 'latency'
): Promise<{ data: TimeSeriesDataPoint[] }> {
  const response = await api.get<{ data: TimeSeriesDataPoint[] }>('/api/metrics/timeseries', {
    params: {
      start_time: startTime.toISOString(),
      end_time: endTime.toISOString(),
      interval,
      metric,
    },
  })
  return response.data
}

export async function fetchConversations(
  page: number = 1,
  pageSize: number = 100
): Promise<{ events: LLMEvent[]; total: number; page: number; page_size: number }> {
  const response = await api.get('/api/conversations', {
    params: { page, page_size: pageSize },
  })
  return response.data
}
