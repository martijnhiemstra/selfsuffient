import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  const logout = useCallback(() => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  }, []);

  useEffect(() => {
    const fetchUser = async () => {
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const response = await axios.get(`${API}/auth/me`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setUser(response.data);
      } catch (error) {
        console.error('Auth error:', error);
        logout();
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, [token, logout]);

  const login = async (email, password) => {
    const response = await axios.post(`${API}/auth/login`, { email, password });
    const { access_token, user: userData } = response.data;
    
    localStorage.setItem('token', access_token);
    setToken(access_token);
    setUser(userData);
    
    return userData;
  };

  const forgotPassword = async (email) => {
    const response = await axios.post(`${API}/auth/forgot-password`, { email });
    return response.data;
  };

  const resetPassword = async (resetToken, newPassword) => {
    const response = await axios.post(`${API}/auth/reset-password`, {
      token: resetToken,
      new_password: newPassword
    });
    return response.data;
  };

  const changePassword = async (currentPassword, newPassword) => {
    const response = await axios.post(`${API}/auth/change-password`, {
      current_password: currentPassword,
      new_password: newPassword
    }, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  };

  const refreshUser = useCallback(async () => {
    if (!token) return;
    try {
      const response = await axios.get(`${API}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUser(response.data);
    } catch (error) {
      console.error('Refresh user error:', error);
    }
  }, [token]);

  const getAuthHeader = () => {
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  const value = {
    user,
    token,
    loading,
    login,
    logout,
    forgotPassword,
    resetPassword,
    changePassword,
    refreshUser,
    getAuthHeader,
    isAuthenticated: !!user,
    isAdmin: user?.is_admin || false
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
