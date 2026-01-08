import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

interface AuthContextType {
  isAuthenticated: boolean;
  user: string | null;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 检查本地存储中的令牌
    const token = localStorage.getItem('authToken');
    if (token) {
      // 验证令牌是否有效
      validateToken(token);
    } else {
      setLoading(false);
    }
  }, []);

  const validateToken = async (token: string) => {
    try {
      // 尝试调用一个需要身份验证的API来验证令牌
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      const response = await axios.get('http://localhost:5000/api/status');
      if (response.data.success) {
        setIsAuthenticated(true);
        setUser('admin'); // 在实际应用中，可以从令牌中解析用户信息
      } else {
        // 令牌无效，清除本地存储
        localStorage.removeItem('authToken');
        delete axios.defaults.headers.common['Authorization'];
      }
    } catch (error) {
      console.error('Token validation failed:', error);
      localStorage.removeItem('authToken');
      delete axios.defaults.headers.common['Authorization'];
    } finally {
      setLoading(false);
    }
  };

  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      const response = await axios.post('http://localhost:5000/api/login', {
        username,
        password
      });

      if (response.data.success) {
        const { token } = response.data;
        // 将令牌存储在本地存储中
        localStorage.setItem('authToken', token);
        // 设置axios默认头部
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        
        setIsAuthenticated(true);
        setUser(username);
        return true;
      } else {
        return false;
      }
    } catch (error) {
      console.error('Login failed:', error);
      return false;
    }
  };

  const logout = () => {
    // 清除本地存储中的令牌
    localStorage.removeItem('authToken');
    delete axios.defaults.headers.common['Authorization'];
    
    setIsAuthenticated(false);
    setUser(null);
  };

  const value = {
    isAuthenticated,
    user,
    login,
    logout,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading ? children : <div>Loading...</div>}
    </AuthContext.Provider>
  );
};