import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import RiskGauge from '../components/RiskGauge';
import RecCard from '../components/RecCard';
import { api } from '../api';
import { useUser } from '../context/UserContext';

export default function Dashboard() {
  const { userId, user } = useUser();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [similar, setSimilar] = useState([]);
  const [toast, setToast] = useState(null);

  useEffect(() => {
    if (!userId) { navigate('/'); return; }
    api.getRecommendations(userId, 8).then(setData);
    api.getSimilarInvestors(userId, 4).then(setSimilar);
  }, [userId]);

  const handleAction = async (item, itemId, action) => {
    const amount = action === 'invested' ? 5000 : 0;
    await api.logInteraction({ user_id: userId, item_id: itemId, action, amount });
    setToast(`${action === 'invested' ? 'Invested in' : 'Added to watchlist:'} ${item.name}`);
    setTimeout(() => setToast(null), 2500);
    api.getRecommendations(userId, 8).then(setData);
  };

  if (!user || !data) return <Layout><p style={{ color: 'var(--ink-soft)' }}>Loading your picks…</p></Layout>;

  return (
    <Layout>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 28 }}>
        <div>
          <h1 style={{ fontSize: 27, marginBottom: 4 }}>Recommended for {user.name.split(' ')[0]}</h1>
          <p style={{ color: 'var(--ink-soft)', fontSize: 14 }}>
            Blended from {data.n_history_items} past interactions using content + collaborative signals.
          </p>
        </div>
        <div style={{ textAlign: 'center' }}>
          <RiskGauge score={user.risk_score} bucket={user.risk_bucket} size={130} />
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: 28 }}>
        <div style={{ display: 'grid', gap: 14 }}>
          {data.recommendations.map((rec) => (
            <RecCard key={rec.item_id} rec={rec} onAction={handleAction} />
          ))}
        </div>

        <aside>
          <div style={{
            background: 'var(--paper-raised)', border: '1px solid var(--line)',
            borderRadius: 'var(--radius)', padding: '18px 20px', boxShadow: 'var(--shadow-card)',
          }}>
            <h3 style={{ fontSize: 15, marginBottom: 4 }}>Investors like you</h3>
            <p style={{ fontSize: 12, color: 'var(--ink-soft)', marginBottom: 14 }}>
              Closest taste-vectors from the collaborative model
            </p>
            {similar.map((s) => (
              <div key={s.user.user_id} style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                padding: '9px 0', borderTop: '1px solid var(--line)', fontSize: 13,
              }}>
                <div>
                  <div style={{ fontWeight: 500, color: 'var(--navy-deep)' }}>{s.user.name}</div>
                  <div style={{ fontSize: 11.5, color: 'var(--ink-soft)' }}>{s.user.risk_bucket}</div>
                </div>
                <span className="mono" style={{ fontSize: 12, color: 'var(--emerald)' }}>
                  {Math.round(s.similarity * 100)}%
                </span>
              </div>
            ))}
          </div>

          <div style={{
            marginTop: 16, background: 'var(--amber-soft)', borderRadius: 'var(--radius)',
            padding: '16px 18px', fontSize: 12.5, color: '#7A5417', lineHeight: 1.55,
          }}>
            <strong>How this works:</strong> new investors lean on content-based matching
            (risk profile + category fit). As you invest and watchlist more, the engine
            shifts weight toward collaborative signals from similar investors.
          </div>
        </aside>
      </div>

      {toast && (
        <div style={{
          position: 'fixed', bottom: 28, right: 28, background: 'var(--navy-deep)', color: '#fff',
          padding: '12px 18px', borderRadius: 8, fontSize: 13.5, boxShadow: '0 8px 24px rgba(0,0,0,0.2)',
        }}>
          {toast}
        </div>
      )}
    </Layout>
  );
}
