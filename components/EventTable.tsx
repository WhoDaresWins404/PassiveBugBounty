// components/EventTable.tsx
import { useMemo } from 'react';

interface Event {
  id: number;
  path: string;
  method?: string | null;
  status_code?: number | null;
  type: 'request' | 'response';
  headers: Record<string, string>;
}

export default function EventTable({ events }: { events: Event[] }) {
  const rows = useMemo(() => {
    // Deduplicate + filter by latest per session (simplified)
    return [...events].reverse().slice(0, 20);
  }, [events]);

  if (!rows.length) return <div className="text-gray-500 italic">Waiting for traffic...</div>;

  return (
    <div className="overflow-x-auto rounded-lg border">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Path</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Method</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Suspicious?</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {rows.map((e) => (
            <tr key={e.id} className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                {e.path}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{e.method || '—'}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{e.type}</td>
              <td className="px-6 py-4 whitespace-nowrap">
                {/* Detection flag will come from rule engine in later phases */}
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                  Pending
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
