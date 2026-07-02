import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import RiskGauge from '../components/RiskGauge';
import { api } from '../api';
import { useUser } from '../context/UserContext';

const QUESTIONS = [
  {
    key: 'investment_horizon',
    q: 'When do you expect to need this money?',
    options: ['< 1 year', '1-3 years', '3-5 years', '5+ years'],
  },
  {
    key: 'loss_tolerance',
    q: 'If your investment dropped 15% in a month, what would you do?',
    options: [
      { label: 'Sell immediately to avoid further loss', value: 1 },
      { label: 'Sell some, hold the rest', value: 2 },
      { label: 'Hold and wait it out', value: 3 },
      { label: 'Hold, unbothered by short-term swings', value: 4 },
      { label: 'Buy more at the lower price', value: 5 },
    ],
  },
  {
    key: 'investment_goal',
    q: 'What best describes your investing goal?',
    options: ['capital protection', 'steady growth', 'wealth creation', 'aggressive growth'],
  },
];

export default function RiskQuiz() {
  const navigate = useNavigate();
  const { userId } = useUser();
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);

  const isNewUser = !userId;

  const answer = (key, value) => {
    const next = { ...answers, [key]: value };
    setAnswers(next);
    if (step < QUESTIONS.length - 1) {
      setStep(step + 1);
    } else {
      submit(next);
    }
  };

  const submit = async (finalAnswers) => {
    const payload = {
      age: 30,
      monthly_income: 60000,
      investment_horizon: finalAnswers.investment_horizon,
      loss_tolerance: finalAnswers.loss_tolerance,
      investment_goal: finalAnswers.investment_goal,
      existing_investor: !isNewUser,
    };
    const res = await api.computeRiskProfile(payload);
    setResult(res);
  };

  const content = (
    <div style={{ maxWidth: 560, margin: '0 auto' }}>
      <h1 style={{ fontSize: 27, marginBottom: 6, textAlign: 'center' }}>Risk Profile Quiz</h1>
      <p style={{ color: 'var(--ink-soft)', fontSize: 14, marginBottom: 32, textAlign: 'center' }}>
        Three quick questions calibrate your risk score, the same way SEBI-mandated
        suitability assessments work on real investing platforms.
      </p>

      {!result ? (
        <div style={{
          background: 'var(--paper-raised)', border: '1px solid var(--line)',
          borderRadius: 'var(--radius)', padding: '28px 30px', boxShadow: 'var(--shadow-card)',
        }}>
          <div style={{ fontSize: 12, color: 'var(--ink-soft)', marginBottom: 10 }}>
            Question {step + 1} of {QUESTIONS.length}
          </div>
          <div style={{ fontSize: 17, fontWeight: 600, color: 'var(--navy-deep)', marginBottom: 20 }}>
            {QUESTIONS[step].q}
          </div>
          <div style={{ display: 'grid', gap: 8 }}>
            {QUESTIONS[step].options.map((opt) => {
              const value = typeof opt === 'object' ? opt.value : opt;
              const label = typeof opt === 'object' ? opt.label : opt;
              return (
                <button
                  key={label}
                  onClick={() => answer(QUESTIONS[step].key, value)}
                  style={{
                    textAlign: 'left', padding: '12px 16px', borderRadius: 8,
                    border: '1px solid var(--line)', background: 'var(--paper)',
                    fontSize: 14, color: 'var(--navy-deep)', textTransform: 'capitalize',
                  }}
                >
                  {label}
                </button>
              );
            })}
          </div>
        </div>
      ) : (
        <div style={{
          background: 'var(--paper-raised)', border: '1px solid var(--line)',
          borderRadius: 'var(--radius)', padding: '28px 30px', boxShadow: 'var(--shadow-card)',
          textAlign: 'center',
        }}>
          <RiskGauge score={result.risk_score} bucket={result.risk_bucket} size={160} />
          <div style={{ fontSize: 21, fontWeight: 700, color: 'var(--navy-deep)', marginTop: 6, marginBottom: 8 }}>
            {result.risk_bucket} Investor
          </div>
          <p style={{ fontSize: 13.5, color: 'var(--ink-soft)', lineHeight: 1.6 }}>{result.explanation}</p>

          {isNewUser ? (
            <p style={{ fontSize: 12.5, color: 'var(--ink-soft)', marginTop: 20 }}>
              Pick a demo investor with a similar profile from the home screen to explore
              live recommendations built on this risk bucket.
            </p>
          ) : (
            <button
              onClick={() => navigate('/dashboard')}
              style={{
                marginTop: 20, padding: '10px 22px', borderRadius: 8, border: 'none',
                background: 'var(--navy)', color: '#fff', fontSize: 14, fontWeight: 600,
              }}
            >
              View updated recommendations
            </button>
          )}
        </div>
      )}
    </div>
  );

  return isNewUser
    ? <div style={{ padding: '60px 20px' }}>{content}</div>
    : <Layout>{content}</Layout>;
}
