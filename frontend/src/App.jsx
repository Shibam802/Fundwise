import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { UserProvider } from './context/UserContext';
import SelectInvestor from './pages/SelectInvestor';
import Dashboard from './pages/Dashboard';
import Explore from './pages/Explore';
import Portfolio from './pages/Portfolio';
import RiskQuiz from './pages/RiskQuiz';

export default function App() {
  return (
    <UserProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<SelectInvestor />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/explore" element={<Explore />} />
          <Route path="/portfolio" element={<Portfolio />} />
          <Route path="/risk-quiz" element={<RiskQuiz />} />
          <Route path="/risk-quiz-new" element={<RiskQuiz />} />
        </Routes>
      </BrowserRouter>
    </UserProvider>
  );
}
