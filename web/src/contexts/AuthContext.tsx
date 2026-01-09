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
      // 验证令牌是否有效，但设置较短的超时时间
      validateTokenWithTimeout(token, 3000); // 3秒超时
    } else {
      // 没有令牌，直接设置为未认证状态
      setIsAuthenticated(false);
      setUser(null);
      setLoading(false);
    }
  }, []);

  const validateTokenWithTimeout = async (token: string, timeoutMs: number) => {
    // 创建一个超时Promise
    const timeoutPromise = new Promise((_, reject) => {
      setTimeout(() => reject(new Error('Token validation timeout')), timeoutMs);
    });

    try {
      // 并行执行令牌验证和超时Promise
      await Promise.race([
        validateToken(token),
        timeoutPromise
      ]);
    } catch (error) {
      console.error('Token validation failed or timed out:', error);
      // 令牌无效或超时，清除本地存储
      localStorage.removeItem('authToken');
      setIsAuthenticated(false);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const validateToken = async (token: string) => {
    try {
      // 尝试调用一个需要身份验证的API来验证令牌
      const response = await axios.get('http://localhost:5000/api/status', {
        timeout: 2000, // 2秒请求超时
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.data.success) {
        setIsAuthenticated(true);
        setUser('admin'); // 在实际应用中，可以从令牌中解析用户信息
      } else {
        // 令牌无效，清除本地存储
        localStorage.removeItem('authToken');
        setIsAuthenticated(false);
        setUser(null);
      }
    } catch (error) {
      console.error('Token validation failed:', error);
      // 令牌无效或后端不可达，清除本地存储
      localStorage.removeItem('authToken');
      setIsAuthenticated(false);
      setUser(null);
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
      {!loading ? children : (
        <div style={{ padding: '20px', textAlign: 'center' }}>
          <h2>正在验证登录状态...</h2>
          <p>如果长时间加载，请检查后端服务是否正常运行</p>
        </div>
      )}
    </AuthContext.Provider>
  );
};