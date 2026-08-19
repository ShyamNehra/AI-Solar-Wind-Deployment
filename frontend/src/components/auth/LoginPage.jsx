import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { loginUser, fetchMe, saveToken } from '../../api/auth';
import { useAuth } from '../../context/AuthContext';
import AuthBackground from './AuthBackground';
import Logo from '../Logo';
import './Auth.css';

const DEMO_ACCOUNTS = [
  { role: 'Administrator', username: 'shyam_nehra', handle: '@shyam_nehra', color: '#0284c7' },
  { role: 'Energy Planner', username: 'aishwarya_r', handle: '@aishwarya_r', color: '#10b981' },
  { role: 'GIS Analyst', username: 'gis_analyst', handle: '@gis_analyst', color: '#f59e0b' },
  { role: 'Project Manager', username: 'rajesh_kumar', handle: '@rajesh_kumar', color: '#a855f7' },
];

export default function LoginPage() {
  const [usernameOrEmail, setUsernameOrEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [activeQuickUser, setActiveQuickUser] = useState(null);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleLogin = async (username, pwd) => {
    setError('');
    setIsSubmitting(true);
    try {
      const tokenData = await loginUser(username, pwd);
      saveToken(tokenData.access_token);
      const userData = await fetchMe();
      login(tokenData.access_token, userData);
      navigate('/');
    } catch (err) {
      const detail = err.response?.data?.detail || 'Login failed. Please check your credentials.';
      setError(detail);
    } finally {
      setIsSubmitting(false);
      setActiveQuickUser(null);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    handleLogin(usernameOrEmail, password);
  };

  const handleQuickLogin = (username) => {
    if (!username) return;
    setActiveQuickUser(username);
    setUsernameOrEmail(username);
    setPassword('password123');
    handleLogin(username, 'password123');
  };

  return (
    <div className="auth-page">
      <AuthBackground />

      <div className="auth-card">
        {/* Brand Header */}
        <div className="auth-brand">
          <div className="auth-brand-logo-wrapper" style={{ background: 'none', border: 'none', boxShadow: 'none' }}>
            <Logo size={44} />
          </div>
          <h1>Solar & Wind Intelligence</h1>
          <p>Deployment Intelligence Platform — Sign in to continue</p>
        </div>

        {/* Error Banner */}
        {error && (
          <div className="auth-error">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <span>{error}</span>
          </div>
        )}

        {/* Login Form */}
        <form className="auth-form" onSubmit={handleSubmit}>
          {/* Username / Email */}
          <div className="auth-input-group">
            <label htmlFor="login-email">Email or Username</label>
            <div className="auth-input-wrapper">
              <span className="input-icon-prefix">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </span>
              <input
                id="login-email"
                type="text"
                className="auth-input"
                placeholder="you@organization.com"
                value={usernameOrEmail}
                onChange={(e) => setUsernameOrEmail(e.target.value)}
                required
                autoFocus
              />
            </div>
          </div>

          {/* Password */}
          <div className="auth-input-group">
            <label htmlFor="login-password">Password</label>
            <div className="auth-input-wrapper">
              <span className="input-icon-prefix">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </span>
              <input
                id="login-password"
                type={showPassword ? 'text' : 'password'}
                className="auth-input auth-input-has-suffix"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <button
                type="button"
                className="input-eye-toggle"
                onClick={() => setShowPassword(!showPassword)}
                title={showPassword ? 'Hide Password' : 'Show Password'}
              >
                {showPassword ? (
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-7 0-11-7-11-7a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 7 11 7a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24" />
                    <line x1="1" y1="1" x2="23" y2="23" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                  </svg>
                ) : (
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                )}
              </button>
            </div>
          </div>

          <button type="submit" className="auth-btn auth-btn-primary" disabled={isSubmitting} style={{ marginTop: '0.4rem' }}>
            {isSubmitting && !activeQuickUser ? (
              <>
                <span className="auth-spinner" /> Authenticating...
              </>
            ) : (
              'Sign In'
            )}
          </button>
        </form>

        {/* Quick Demo Login Section */}
        <div className="auth-divider" style={{ margin: '1.25rem 0 0.85rem 0' }}>
          <span>OR QUICK DEMO ACCESS</span>
        </div>

        <div className="quick-demo-section">
          <div className="quick-demo-grid">
            {DEMO_ACCOUNTS.map((acc) => {
              const isThisLoading = isSubmitting && activeQuickUser === acc.username;
              return (
                <button
                  key={acc.username}
                  type="button"
                  className={`quick-demo-chip ${isThisLoading ? 'loading' : ''}`}
                  onClick={() => handleQuickLogin(acc.username)}
                  disabled={isSubmitting}
                >
                  <span className="quick-demo-dot" style={{ background: acc.color }}>
                    {isThisLoading && <span className="auth-spinner" style={{ width: '8px', height: '8px', borderTopColor: '#fff' }} />}
                  </span>
                  <div className="quick-demo-info">
                    <span className="quick-demo-role">{acc.role}</span>
                    <span className="quick-demo-user">{acc.handle}</span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        <div className="auth-divider">
          <span>or</span>
        </div>

        <div className="auth-switch">
          Don't have an account? <Link to="/register">Create one now</Link>
        </div>
      </div>
    </div>
  );
}
