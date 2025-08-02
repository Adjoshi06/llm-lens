'use client'

import React, { useState } from 'react'
import { format } from 'date-fns'
import { LLMEvent } from '@/lib/api'

interface RecentCallsProps {
  events: LLMEvent[]
}

export default function RecentCalls({ events }: RecentCallsProps) {
  const [expandedEvent, setExpandedEvent] = useState<string | null>(null)

  const toggleExpand = (eventId: string) => {
    setExpandedEvent(expandedEvent === eventId ? null : eventId)
  }

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">Recent API Calls</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b">
              <th className="text-left py-2">Timestamp</th>
              <th className="text-left py-2">Model</th>
              <th className="text-right py-2">Tokens</th>
              <th className="text-right py-2">Latency</th>
              <th className="text-right py-2">Cost</th>
              <th className="text-left py-2">Status</th>
            </tr>
          </thead>
          <tbody>
            {events.map((event) => (
              <React.Fragment key={event.id}>
                <tr
                  className={`border-b cursor-pointer hover:bg-gray-50 ${
                    event.status === 'error' ? 'bg-red-50' : ''
                  }`}
                  onClick={() => toggleExpand(event.id)}
                >
                  <td className="py-2">
                    {format(new Date(event.timestamp), 'MMM dd, HH:mm:ss')}
                  </td>
                  <td className="py-2">{event.model}</td>
                  <td className="text-right py-2">
                    {event.total_tokens?.toLocaleString() || '-'}
                  </td>
                  <td className="text-right py-2">
                    {event.latency_ms ? `${event.latency_ms}ms` : '-'}
                  </td>
                  <td className="text-right py-2">
                    {event.cost_usd ? `$${event.cost_usd.toFixed(4)}` : '-'}
                  </td>
                  <td className="py-2">
                    <span
                      className={`px-2 py-1 rounded text-xs ${
                        event.status === 'error'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-green-100 text-green-800'
                      }`}
                    >
                      {event.status}
                    </span>
                  </td>
                </tr>
                {expandedEvent === event.id && (
                  <tr>
                    <td colSpan={6} className="py-4 bg-gray-50">
                      <div className="space-y-2">
                        {event.error_message && (
                          <div>
                            <strong>Error:</strong>{' '}
                            <span className="text-red-600">{event.error_message}</span>
                          </div>
                        )}
                        {event.tags && Object.keys(event.tags).length > 0 && (
                          <div>
                            <strong>Tags:</strong>
                            <pre className="mt-1 text-xs bg-white p-2 rounded">
                              {JSON.stringify(event.tags, null, 2)}
                            </pre>
                          </div>
                        )}
                        <div className="grid grid-cols-2 gap-2 text-xs">
                          <div>
                            <strong>Prompt Tokens:</strong> {event.prompt_tokens || '-'}
                          </div>
                          <div>
                            <strong>Completion Tokens:</strong>{' '}
                            {event.completion_tokens || '-'}
                          </div>
                        </div>
                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>
        {events.length === 0 && (
          <p className="text-center text-gray-500 py-8">No events found</p>
        )}
      </div>
    </div>
  )
}

