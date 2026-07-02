const BUCKET_COLORS = {
  Conservative: '#0F9D74',
  Moderate: '#4E9D6B',
  Balanced: '#D98E2B',
  Growth: '#CE7A2E',
  Aggressive: '#C1523E',
};

export default function RiskGauge({ score, bucket, size = 140 }) {
  const r = size / 2 - 12;
  const cx = size / 2;
  const cy = size / 2;
  const startAngle = -220;
  const endAngle = 40;
  const angle = startAngle + (endAngle - startAngle) * score;

  const polarToCartesian = (angleDeg) => {
    const rad = (angleDeg * Math.PI) / 180;
    return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
  };

  const arcPath = (a1, a2) => {
    const p1 = polarToCartesian(a1);
    const p2 = polarToCartesian(a2);
    const largeArc = a2 - a1 > 180 ? 1 : 0;
    return `M ${p1.x} ${p1.y} A ${r} ${r} 0 ${largeArc} 1 ${p2.x} ${p2.y}`;
  };

  const needleTip = polarToCartesian(angle);
  const color = BUCKET_COLORS[bucket] || 'var(--navy)';

  return (
    <svg width={size} height={size * 0.78} viewBox={`0 0 ${size} ${size * 0.78}`}>
      <path d={arcPath(startAngle, endAngle)} stroke="var(--line)" strokeWidth={10} fill="none" strokeLinecap="round" />
      <path d={arcPath(startAngle, angle)} stroke={color} strokeWidth={10} fill="none" strokeLinecap="round" />
      <line x1={cx} y1={cy} x2={needleTip.x} y2={needleTip.y} stroke="var(--navy-deep)" strokeWidth={2} strokeLinecap="round" />
      <circle cx={cx} cy={cy} r={4.5} fill="var(--navy-deep)" />
      <text x={cx} y={cy - 20} textAnchor="middle" fontFamily="IBM Plex Mono" fontSize={20} fontWeight={600} fill="var(--navy-deep)">
        {Math.round(score * 100)}
      </text>
      <text x={cx} y={cy - 4} textAnchor="middle" fontFamily="Inter" fontSize={10} fill="var(--ink-soft)">
        RISK SCORE
      </text>
    </svg>
  );
}
