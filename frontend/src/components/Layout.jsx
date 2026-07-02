import { NavLink, useNavigate } from 'react-router-dom';
import { LayoutGrid, Compass, Wallet, SlidersHorizontal, LogOut, TrendingUp } from 'lucide-react';
import { useUser } from '../context/UserContext';

const navItems = [
  { to: '/dashboard', label: 'Recommendations', icon: LayoutGrid },
  { to: '/explore', label: 'Explore', icon: Compass },
  { to: '/portfolio', label: 'Portfolio', icon: Wallet },
  { to: '/risk-quiz', label: 'Risk Profile', icon: SlidersHorizontal },
];

export default function Layout({ children }) {
  const { user, setUserId } = useUser();
  const navigate = useNavigate();

  const switchUser = () => {
    setUserId(null);
    navigate('/');
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <aside style={{
        width: 236,
        background: 'var(--navy-deep)',
        color: '#EDEFF5',
        padding: '28px 18px',
        display: 'flex',
        flexDirection: 'column',
        position: 'sticky',
        top: 0,
        height: '100vh',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 9, padding: '0 8px 32px' }}>
          <TrendingUp size={22} color="var(--emerald)" strokeWidth={2.4} />
          <span className="display" style={{ color: '#fff', fontSize: 21 }}>FundWise</span>
        </div>

        <nav style={{ display: 'flex', flexDirection: 'column', gap: 3, flex: 1 }}>
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              style={({ isActive }) => ({
                display: 'flex',
                alignItems: 'center',
                gap: 11,
                padding: '10px 12px',
                borderRadius: 8,
                fontSize: 14.5,
                fontWeight: 500,
                color: isActive ? '#fff' : '#AEB5C9',
                background: isActive ? 'rgba(255,255,255,0.08)' : 'transparent',
                transition: 'background 0.15s, color 0.15s',
              })}
            >
              <Icon size={17} strokeWidth={2} />
              {label}
            </NavLink>
          ))}
        </nav>

        {user && (
          <div style={{ borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: 16, marginTop: 16 }}>
            <div style={{ fontSize: 13, color: '#8B92A8', marginBottom: 2 }}>Investing as</div>
            <div style={{ fontSize: 14.5, fontWeight: 600, color: '#fff', marginBottom: 2 }}>{user.name}</div>
            <div style={{ fontSize: 12.5, color: 'var(--emerald)', marginBottom: 14 }}>{user.risk_bucket} investor</div>
            <button
              onClick={switchUser}
              style={{
                display: 'flex', alignItems: 'center', gap: 7,
                background: 'transparent', border: '1px solid rgba(255,255,255,0.15)',
                color: '#C4C9D9', borderRadius: 7, padding: '7px 10px', fontSize: 13,
                width: '100%',
              }}
            >
              <LogOut size={14} /> Switch investor
            </button>
          </div>
        )}
      </aside>

      <main style={{ flex: 1, padding: '36px 44px', maxWidth: 1180 }}>
        {children}
      </main>
    </div>
  );
}
