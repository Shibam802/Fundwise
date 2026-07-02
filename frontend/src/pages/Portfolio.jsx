import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import Layout from '../components/Layout';
import { api } from '../api';
import { useUser } from '../context/UserContext';

const PALETTE = ['#1B2A4A', '#0F9D74', '#D98E2B', '#C1523E', '#6B7FA8'];

export default function Portfolio() {
  const { userId } = useUser();
  const navigate = useNavigate();
  const [data, setData] = useState(null);

  useEffect(() => {
    if (!userId) { navigate('/'); return; }
    api.getPortfolio(userId).then(setData);
  }, [userId]);

  if (!data) return <Layout><p style={{ color: 'var(--ink-soft)' }}>Loading portfolio…</p></Layout>;

  const chartData = Object.entries(data.asset_allocation_pct).map(([name, value]) => ({ name, value }));

  return (
    <Layout>
      <h1 style={{ fontSize: 27, marginBottom: 6 }}>Your Portfolio</h1>
      <p style={{ color: 'var(--ink-soft)', fontSize: 14, marginBottom: 26 }}>
        {data.holdings_count} holdings · <span className="mono">₹{data.total_invested.toLocaleString('en-IN')}</span> invested
      </p>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: 28 }}>
        <div style={{
          background: 'var(--paper-raised)', border: '1px solid var(--line)',
          borderRadius: 'var(--radius)', boxShadow: 'var(--shadow-card)', overflow: 'hidden',
        }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13.5 }}>
            <thead>
              <tr style={{ background: 'var(--paper)', textAlign: 'left' }}>
                <th style={th}>Instrument</th>
                <th style={th}>Type</th>
                <th style={th}>Action</th>
                <th style={{ ...th, textAlign: 'right' }}>Amount</th>
              </tr>
            </thead>
            <tbody>
              {data.holdings.map((h, i) => (
                <tr key={i} style={{ borderTop: '1px solid var(--line)' }}>
                  <td style={td}>{h.item.name}</td>
                  <td style={{ ...td, color: 'var(--ink-soft)' }}>{h.item_type}</td>
                  <td style={td}>
                    <span style={{
                      fontSize: 11, fontWeight: 600, padding: '2px 8px', borderRadius: 20,
                      background: h.action === 'invested' ? 'var(--emerald-soft)' : 'var(--amber-soft)',
                      color: h.action === 'invested' ? 'var(--emerald)' : 'var(--amber)',
                    }}>
                      {h.action === 'invested' ? 'One-time' : 'SIP'}
                    </span>
                  </td>
                  <td className="mono" style={{ ...td, textAlign: 'right', fontWeight: 600 }}>
                    ₹{h.amount.toLocaleString('en-IN')}
                  </td>
                </tr>
              ))}
              {data.holdings.length === 0 && (
                <tr><td style={td} colSpan={4}>No holdings yet — invest in a recommendation to get started.</td></tr>
              )}
            </tbody>
          </table>
        </div>

        <div style={{
          background: 'var(--paper-raised)', border: '1px solid var(--line)',
          borderRadius: 'var(--radius)', padding: '18px 20px', boxShadow: 'var(--shadow-card)',
        }}>
          <h3 style={{ fontSize: 15, marginBottom: 12 }}>Asset allocation</h3>
          {chartData.length > 0 ? (
            <>
              <ResponsiveContainer width="100%" height={180}>
                <PieChart>
                  <Pie data={chartData} dataKey="value" nameKey="name" innerRadius={45} outerRadius={75} paddingAngle={2}>
                    {chartData.map((_, i) => <Cell key={i} fill={PALETTE[i % PALETTE.length]} />)}
                  </Pie>
                  <Tooltip formatter={(v) => `${v}%`} />
                </PieChart>
              </ResponsiveContainer>
              <div style={{ marginTop: 8 }}>
                {chartData.map((d, i) => (
                  <div key={d.name} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 12.5, marginBottom: 6 }}>
                    <span style={{ width: 9, height: 9, borderRadius: '50%', background: PALETTE[i % PALETTE.length] }} />
                    <span style={{ flex: 1, color: 'var(--ink-soft)' }}>{d.name}</span>
                    <span className="mono">{d.value}%</span>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <p style={{ fontSize: 12.5, color: 'var(--ink-soft)' }}>Nothing invested yet.</p>
          )}
        </div>
      </div>
    </Layout>
  );
}

const th = { padding: '11px 16px', fontSize: 11.5, fontWeight: 600, color: 'var(--ink-soft)', textTransform: 'uppercase', letterSpacing: '0.03em' };
const td = { padding: '11px 16px', color: 'var(--navy-deep)' };
