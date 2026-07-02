import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import { api } from '../api';
import { useUser } from '../context/UserContext';

const RISK_LABELS = { 1: 'Low', 2: 'Low-Mod', 3: 'Moderate', 4: 'High', 5: 'Very High' };
const RISK_COLORS = { 1: 'var(--emerald)', 2: 'var(--emerald)', 3: 'var(--amber)', 4: 'var(--coral)', 5: 'var(--coral)' };

export default function Explore() {
  const { userId } = useUser();
  const navigate = useNavigate();
  const [tab, setTab] = useState('funds');
  const [funds, setFunds] = useState([]);
  const [stocks, setStocks] = useState([]);
  const [maxRisk, setMaxRisk] = useState(5);
  const [toast, setToast] = useState(null);

  useEffect(() => {
    if (!userId) { navigate('/'); return; }
    api.listFunds().then(setFunds);
    api.listStocks().then(setStocks);
  }, [userId]);

  const watchlist = async (item, itemId) => {
    await api.logInteraction({ user_id: userId, item_id: itemId, action: 'watchlisted', amount: 0 });
    setToast(`Added ${item.name} to watchlist`);
    setTimeout(() => setToast(null), 2000);
  };

  const items = (tab === 'funds' ? funds : stocks).filter((i) => i.risk_level <= maxRisk);

  return (
    <Layout>
      <h1 style={{ fontSize: 27, marginBottom: 6 }}>Explore</h1>
      <p style={{ color: 'var(--ink-soft)', fontSize: 14, marginBottom: 20 }}>
        Browse the full fund &amp; stock catalogue behind the recommender.
      </p>

      <div style={{ display: 'flex', gap: 8, marginBottom: 18, alignItems: 'center' }}>
        {['funds', 'stocks'].map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            style={{
              padding: '7px 16px', borderRadius: 20, fontSize: 13.5, fontWeight: 600,
              border: tab === t ? 'none' : '1px solid var(--line)',
              background: tab === t ? 'var(--navy)' : 'var(--paper-raised)',
              color: tab === t ? '#fff' : 'var(--ink-soft)',
              textTransform: 'capitalize',
            }}
          >
            {t}
          </button>
        ))}
        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 8 }}>
          <label style={{ fontSize: 12.5, color: 'var(--ink-soft)' }}>Max risk</label>
          <input
            type="range" min={1} max={5} value={maxRisk}
            onChange={(e) => setMaxRisk(Number(e.target.value))}
          />
          <span className="mono" style={{ fontSize: 12.5 }}>{RISK_LABELS[maxRisk]}</span>
        </div>
      </div>

      <div style={{
        display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(270px, 1fr))', gap: 12,
      }}>
        {items.map((item) => {
          const id = item.fund_id || item.stock_id;
          const isFund = !!item.fund_id;
          return (
            <div key={id} style={{
              background: 'var(--paper-raised)', border: '1px solid var(--line)',
              borderRadius: 'var(--radius)', padding: '15px 17px', boxShadow: 'var(--shadow-card)',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8 }}>
                <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--navy-deep)', lineHeight: 1.3 }}>
                  {item.name}
                </div>
                <span style={{
                  fontSize: 10.5, fontWeight: 600, padding: '2px 7px', borderRadius: 20, whiteSpace: 'nowrap',
                  background: `${RISK_COLORS[item.risk_level]}1A`, color: RISK_COLORS[item.risk_level],
                }}>
                  {RISK_LABELS[item.risk_level]}
                </span>
              </div>
              <div style={{ fontSize: 12, color: 'var(--ink-soft)', margin: '5px 0 10px' }}>
                {isFund ? item.category : `${item.sector} · ${item.market_cap_category} Cap`}
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span className="mono" style={{
                  fontSize: 14, fontWeight: 600,
                  color: item.returns_1y >= 0 ? 'var(--emerald)' : 'var(--coral)',
                }}>
                  {item.returns_1y >= 0 ? '+' : ''}{item.returns_1y}%
                </span>
                <button
                  onClick={() => watchlist(item, id)}
                  style={{
                    fontSize: 11.5, fontWeight: 500, padding: '5px 10px', borderRadius: 6,
                    border: '1px solid var(--line)', background: 'var(--paper)', color: 'var(--navy)',
                  }}
                >
                  + Watchlist
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {toast && (
        <div style={{
          position: 'fixed', bottom: 28, right: 28, background: 'var(--navy-deep)', color: '#fff',
          padding: '12px 18px', borderRadius: 8, fontSize: 13.5,
        }}>
          {toast}
        </div>
      )}
    </Layout>
  );
}
