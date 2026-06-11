// app/page.tsx
'use client';

import { gql, useQuery, useSubscription } from '@apollo/client';
import EventTable from '@/components/EventTable';
import StatsCard from '@/components/StatsCard';
import { useEffect, useState } from 'react';

const GET_STATS = gql`
  query GetStats {
    httpEventsAggregate(groupBy: [type], where: { startTime: { since: "24h" }}) {
      count
      groupBy { type }
    }
  }
`;

const NEW_DETECTION_SUBSCRIPTION = gql`
  subscription OnNewEvent {
    httpEventsAdded {
      id
      path
      method
      status_code
      type
      headers
      session {
        client_ip
      }
    }
  }
`;

export default function Dashboard() {
  const { data: statsData, loading: statsLoading } = useQuery(GET_STATS);
  const { data: subData, error } = useSubscription(NEW_DETECTION_SUBSCRIPTION);

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <header className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">PassiveBugBounty Dashboard</h1>
        <p className="mt-2 text-gray-500">Real-time passive reconnaissance & vulnerability signals</p>
      </header>

      {/* Stats Row */}
      {statsLoading ? (
        <div>Loading stats...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <StatsCard 
            title="Total Requests" 
            value={statsData?.httpEventsAggregate.find(s => s.groupBy.type === 'request')?.count || 0}
          />
          <StatsCard 
            title="Suspicious Events" 
            value={subData ? subData.httpEventsAdded.length : 0} // Simplified; use detection flag in real impl
            highlight 
          />
        </div>
      )}

      {/* Live Event Stream */}
      <EventTable events={subData?.httpEventsAdded || []} />
    </div>
  );
}
