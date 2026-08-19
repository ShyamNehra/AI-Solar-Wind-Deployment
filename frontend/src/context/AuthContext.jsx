import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { fetchMe, saveToken, getToken, clearToken } from '../api/auth';

const AuthContext = createContext(null);

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within <AuthProvider>');
  return ctx;
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Attempt to load user from existing JWT in localStorage on mount
  const refreshUser = useCallback(async () => {
    const token = getToken();
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      const userData = await fetchMe();
      setUser(userData);
    } catch {
      // Token expired or invalid
      clearToken();
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  const login = useCallback((token, userData) => {
    saveToken(token);
    setUser(userData);
  }, []);

  const logout = useCallback(() => {
    clearToken();
    setUser(null);
  }, []);

  const isAuthenticated = !!user;

  const hasRole = useCallback((roleName) => {
    if (!user) return false;
    if (user.role === 'administrator') return true; // Admin has all roles
    return user.role === roleName;
  }, [user]);

  // Map backend role enum values to display labels
  const getRoleLabel = useCallback((role) => {
    const labels = {
      renewable_energy_planner: 'Renewable Energy Planner',
      gis_analyst: 'GIS Analyst',
      project_manager: 'Project Manager',
      administrator: 'Administrator',
    };
    return labels[role] || role;
  }, []);

  const value = {
    user,
    loading,
    isAuthenticated,
    login,
    logout,
    refreshUser,
    hasRole,
    getRoleLabel,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
