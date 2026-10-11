import React, { useEffect, useState } from 'react';

function AttendanceDashboard() {
  const [records, setRecords] = useState([]);
  const [count, setCount] = useState(0);

  const fetchAttendance = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/attendance/today/');
      const data = await res.json();
      setRecords(data.data);
      setCount(data.total_present);
    } catch (err) {
      console.error("Fetch error:", err);
    }
  };

  useEffect(() => {
    fetchAttendance();
    const interval = setInterval(fetchAttendance, 5000); // ၅ စက္ကန့်တစ်ကြိမ် Auto refresh
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-6 bg-slate-900 min-h-screen text-white">
      <h1 className="text-2xl font-bold mb-4">Smart Attendance Real-time Monitoring</h1>
      <p className="mb-4">Today Total Present: <span className="text-emerald-400 font-bold">{count}</span></p>
      
      <table className="w-full text-left border border-slate-700">
        <thead className="bg-slate-800">
          <tr>
            <th className="p-3 border-b border-slate-700">Name</th>
            <th className="p-3 border-b border-slate-700">Time</th>
            <th className="p-3 border-b border-slate-700">Confidence</th>
            <th className="p-3 border-b border-slate-700">Sync Status</th>
          </tr>
        </thead>
        <tbody>
          {records.map((row) => (
            <tr key={row.id} className="border-b border-slate-800 hover:bg-slate-800/50">
              <td className="p-3 font-semibold">{row.student_name}</td>
              <td className="p-3">{row.time}</td>
              <td className="p-3">{(row.confidence * 100).toFixed(1)}%</td>
              <td className="p-3">
                <span className={`px-2 py-1 rounded text-xs ${row.sync_status ? 'bg-green-600' : 'bg-amber-600'}`}>
                  {row.sync_status ? 'Synced' : 'Pending'}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default AttendanceDashboard;