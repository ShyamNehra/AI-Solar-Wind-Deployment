import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import './Auth.css';

export default function ProtectedRoute({ children, allowedRoles }) {
  const { isAuthenticated, loading, user } = useAuth();

  // Show loading spinner while checking auth state
  if (loading) {
    return (
      <div className="auth-loading-page">
        <div className="auth-loading-spinner-lg" />
        <span>Loading workspace...</span>
      </div>
    );
  }

  // Not authenticated → redirect to login
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Check role restriction if specified
  if (allowedRoles && allowedRoles.length > 0) {
    const userRole = user?.role;
    const isAdmin = userRole === 'administrator';
    if (!isAdmin && !allowedRoles.includes(userRole)) {
      return <Navigate to="/" replace />;
    }
  }

  return children;
}
