import { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../api';

const UserContext = createContext(null);

export function UserProvider({ children }) {
  const [userId, setUserId] = useState(() => localStorage.getItem('fw_user_id') || null);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!userId) {
      setUser(null);
      return;
    }
    setLoading(true);
    api.getUser(userId)
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
    localStorage.setItem('fw_user_id', userId);
  }, [userId]);

  return (
    <UserContext.Provider value={{ userId, setUserId, user, setUser, loading }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  return useContext(UserContext);
}
