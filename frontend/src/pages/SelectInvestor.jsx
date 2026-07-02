import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { TrendingUp } from 'lucide-react';
import { api } from '../api';
import { useUser } from '../context/UserContext';

const BUCKET_COLORS = {
  Conservative: '#0F9D74', Moderate: '#4E9D6B', Balanced: '#D98E2B',
  Growth: '#CE7A2E', Aggressive: '#C1523E',
};

export default function SelectInvestor() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const { setUserId } = useUser();
  const navigate = useNavigate();

  useEffect(() => {
    api.listUsers().then((u) => {
      setUsers(u.slice(0, 12));
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const pick = (id) => {
    setUserId(id);
    navigate('/dashboard');
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 40 }}>
      <div style={{ maxWidth: 780, width: '100%' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8, justifyContent: 'center' }}>
          <TrendingUp size={26} color="var(--emerald)" strokeWidth={2.4} />
          <span className="display" style={{ fontSize: 28 }}>FundWise</span>
        </div>
        <p style={{ textAlign: 'center', color: 'var(--ink-soft)', marginBottom: 36, fontSize: 15 }}>
          A hybrid recommendation engine for mutual funds &amp; stocks.
          Pick a demo investor to see personalized picks — or take the risk quiz to build a new profile.
        </p>

        {loading ? (
          <p style={{ textAlign: 'center', color: 'var(--ink-soft)' }}>Loading investor profiles…</p>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
            {users.map((u) => (
              <button
                key={u.user_id}
                onClick={() => pick(u.user_id)}
                style={{
                  textAlign: 'left', padding: '14px 16px', borderRadius: 10,
                  border: '1px solid var(--line)', background: 'var(--paper-raised)',
                  boxShadow: 'var(--shadow-card)', cursor: 'pointer',
                }}
              >
                <div style={{ fontWeight: 600, fontSize: 14.5, color: 'var(--navy-deep)', marginBottom: 3 }}>{u.name}</div>
                <div style={{ fontSize: 12, color: 'var(--ink-soft)', marginBottom: 8 }}>
                  {u.age} yrs · {u.occupation}
                </div>
                <span style={{
                  fontSize: 11, fontWeight: 600, padding: '2px 8px', borderRadius: 20,
                  background: `${BUCKET_COLORS[u.risk_bucket]}1A`, color: BUCKET_COLORS[u.risk_bucket],
                }}>
                  {u.risk_bucket}
                </span>
              </button>
            ))}
          </div>
        )}

        <p style={{ textAlign: 'center', marginTop: 28 }}>
          <a href="#" onClick={(e) => { e.preventDefault(); navigate('/risk-quiz-new'); }}
             style={{ fontSize: 13.5, color: 'var(--navy)', fontWeight: 600, borderBottom: '1px solid var(--navy)' }}>
            Or build a fresh risk profile →
          </a>
        </p>
      </div>
    </div>
  );
}
