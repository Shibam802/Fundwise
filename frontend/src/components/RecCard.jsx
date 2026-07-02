import { useState } from 'react';
import { TrendingUp, TrendingDown, Info } from 'lucide-react';

const RISK_LABELS = { 1: 'Low', 2: 'Low-Mod', 3: 'Moderate', 4: 'High', 5: 'Very High' };
const RISK_COLORS = { 1: 'var(--emerald)', 2: 'var(--emerald)', 3: 'var(--amber)', 4: 'var(--coral)', 5: 'var(--coral)' };

export default function RecCard({ rec, onAction }) {
  const [expanded, setExpanded] = useState(false);
  const item = rec.item;
  const isFund = !!item.fund_id;
  const ret = item.returns_1y;

  return (
    <div style={{
      background: 'var(--paper-raised)',
      border: '1px solid var(--line)',
      borderRadius: 'var(--radius)',
      padding: '18px 20px',
      boxShadow: 'var(--shadow-card)',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 12 }}>
        <div>
          <div style={{ fontSize: 15.5, fontWeight: 600, color: 'var(--navy-deep)', marginBottom: 3 }}>
            {item.name}
          </div>
          <div style={{ fontSize: 12.5, color: 'var(--ink-soft)' }}>
            {isFund ? item.category : `${item.sector} · ${item.market_cap_category} Cap`}
            {isFund && ` · ${item.amc}`}
          </div>
        </div>
        <span style={{
          fontSize: 11, fontWeight: 600, padding: '3px 9px', borderRadius: 20,
          background: `${RISK_COLORS[item.risk_level]}1A`, color: RISK_COLORS[item.risk_level],
          whiteSpace: 'nowrap',
        }}>
          {RISK_LABELS[item.risk_level]} risk
        </span>
      </div>

      <div style={{ display: 'flex', alignItems: 'baseline', gap: 18, marginTop: 14 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
          {ret >= 0 ? <TrendingUp size={15} color="var(--emerald)" /> : <TrendingDown size={15} color="var(--coral)" />}
          <span className="mono" style={{ fontSize: 16, fontWeight: 600, color: ret >= 0 ? 'var(--emerald)' : 'var(--coral)' }}>
            {ret >= 0 ? '+' : ''}{ret}%
          </span>
          <span style={{ fontSize: 12, color: 'var(--ink-soft)' }}>1Y return</span>
        </div>
        {isFund && (
          <div style={{ fontSize: 12.5, color: 'var(--ink-soft)' }}>
            Expense: <span className="mono">{item.expense_ratio}%</span>
          </div>
        )}
      </div>

      <div style={{
        marginTop: 13, padding: '9px 12px', background: 'var(--paper)',
        borderRadius: 7, fontSize: 12.5, color: 'var(--ink-soft)', lineHeight: 1.5,
      }}>
        {rec.explanation}
      </div>

      <div style={{ marginTop: 10, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <button
          onClick={() => setExpanded(!expanded)}
          style={{
            display: 'flex', alignItems: 'center', gap: 5, background: 'none', border: 'none',
            color: 'var(--navy)', fontSize: 12, fontWeight: 500, padding: 0,
          }}
        >
          <Info size={12} /> {expanded ? 'Hide' : 'Show'} match breakdown
        </button>

        <div style={{ display: 'flex', gap: 8 }}>
          <button
            onClick={() => onAction(item, isFund ? item.fund_id : item.stock_id, 'watchlisted')}
            style={{
              fontSize: 12.5, fontWeight: 500, padding: '6px 12px', borderRadius: 7,
              border: '1px solid var(--line)', background: 'var(--paper-raised)', color: 'var(--navy)',
            }}
          >
            Watchlist
          </button>
          <button
            onClick={() => onAction(item, isFund ? item.fund_id : item.stock_id, 'invested')}
            style={{
              fontSize: 12.5, fontWeight: 600, padding: '6px 14px', borderRadius: 7,
              border: 'none', background: 'var(--navy)', color: '#fff',
            }}
          >
            Invest
          </button>
        </div>
      </div>

      {expanded && (
        <div style={{ marginTop: 12, paddingTop: 12, borderTop: '1px dashed var(--line)' }}>
          <ScoreBar label="Content-based fit" value={rec.content_score} color="var(--navy)" />
          <ScoreBar label="Collaborative fit (similar investors)" value={rec.collab_score} color="var(--emerald)" />
          <div style={{ fontSize: 11.5, color: 'var(--ink-soft)', marginTop: 8 }}>
            Blend weight this session: <span className="mono">{Math.round(rec.alpha_used * 100)}%</span> content-based,{' '}
            <span className="mono">{Math.round((1 - rec.alpha_used) * 100)}%</span> collaborative
            &nbsp;· risk-fit multiplier <span className="mono">{rec.risk_fit_multiplier}</span>
          </div>
        </div>
      )}
    </div>
  );
}

function ScoreBar({ label, value, color }) {
  return (
    <div style={{ marginBottom: 8 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11.5, color: 'var(--ink-soft)', marginBottom: 3 }}>
        <span>{label}</span>
        <span className="mono">{Math.round(value * 100)}%</span>
      </div>
      <div style={{ height: 5, background: 'var(--line)', borderRadius: 3, overflow: 'hidden' }}>
        <div style={{ width: `${value * 100}%`, height: '100%', background: color, borderRadius: 3 }} />
      </div>
    </div>
  );
}
