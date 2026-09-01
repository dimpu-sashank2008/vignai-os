import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import client from '../api/client';
import { User, LoginCredentials, LoginResponse, ChangePasswordPayload, ChangePasswordResponse } from '../types';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<User>;
  changePassword: (payload: ChangePasswordPayload) => Promise<User>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    try {
      const stored = localStorage.getItem('vignex_user');
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  });
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('vignex_token'));
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('vignex_token');
      if (storedToken) {
        try {
          const response = await client.get<User>('/auth/me', {
            headers: { Authorization: `Bearer ${storedToken}` },
          });
          const validUser = response.data;
          setUser(validUser);
          setToken(storedToken);
          localStorage.setItem('vignex_user', JSON.stringify(validUser));
        } catch {
          localStorage.removeItem('vignex_token');
          localStorage.removeItem('vignex_user');
          setToken(null);
          setUser(null);
        }
      } else {
        localStorage.removeItem('vignex_user');
        setUser(null);
        setToken(null);
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = useCallback(async (credentials: LoginCredentials): Promise<User> => {
    const response = await client.post<LoginResponse>('/auth/login', credentials);
    const { access_token, user: loggedInUser } = response.data;

    localStorage.setItem('vignex_token', access_token);
    localStorage.setItem('vignex_user', JSON.stringify(loggedInUser));

    setToken(access_token);
    setUser(loggedInUser);

    return loggedInUser;
  }, []);

  const changePassword = useCallback(async (payload: ChangePasswordPayload): Promise<User> => {
    const response = await client.post<ChangePasswordResponse>('/auth/change-password', payload);
    const { access_token, user: updatedUser } = response.data;

    localStorage.setItem('vignex_token', access_token);
    localStorage.setItem('vignex_user', JSON.stringify(updatedUser));

    setToken(access_token);
    setUser(updatedUser);

    return updatedUser;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('vignex_token');
    localStorage.removeItem('vignex_user');
    setToken(null);
    setUser(null);
    navigate('/login');
  }, [navigate]);

  const isAuthenticated = !!token && !!user;

  return (
    <AuthContext.Provider value={{ user, token, isAuthenticated, isLoading, login, changePassword, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
