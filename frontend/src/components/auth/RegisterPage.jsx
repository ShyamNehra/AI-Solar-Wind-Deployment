import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { registerUser, loginUser, fetchMe, saveToken, checkWorkspaceAvailability } from '../../api/auth';
import { useAuth } from '../../context/AuthContext';
import AuthBackground from './AuthBackground';
import Logo from '../Logo';
import './Auth.css';

const ROLE_OPTIONS = [
  { value: 'renewable_energy_planner', label: 'Renewable Energy Planner' },
  { value: 'gis_analyst', label: 'GIS Analyst' },
  { value: 'project_manager', label: 'Project Manager' },
  { value: 'administrator', label: 'Administrator' },
];

export default function RegisterPage() {
  const [form, setForm] = useState({
    email: '',
    username: '',
    password: '',
    full_name: '',
    organization: 'Infosys Energy Division',
    organization_id: '', // Empty initially — no prefill
    workspace_mode: 'create', // 'create' or 'join'
    role: 'renewable_energy_planner',
  });

  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const [workspaceCheck, setWorkspaceCheck] = useState({
    checking: false,
    status: null,
    message: ''
  });

  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const set = (field) => (e) => {
    let val = e.target.value;
    if (field === 'organization_id') {
      val = val.replace(/\D/g, '').slice(0, 4);
    }
    setForm((prev) => ({ ...prev, [field]: val }));
  };

  // Real-time 4-digit code verification timer
  useEffect(() => {
    const code = (form.organization_id || '').trim();
    if (!code || code.length < 4) {
      setWorkspaceCheck({ checking: false, status: null, message: '' });
      return;
    }

    setWorkspaceCheck({ checking: true, status: 'checking', message: 'Checking...' });
    const timer = setTimeout(async () => {
      try {
        const res = await checkWorkspaceAvailability(code);
        if (form.workspace_mode === 'create') {
          if (res.available_for_creation) {
            setWorkspaceCheck({ checking: false, status: 'available', message: '✓ Available' });
          } else {
            setWorkspaceCheck({ checking: false, status: 'taken', message: '✕ Taken' });
          }
        } else {
          if (res.exists) {
            setWorkspaceCheck({ checking: false, status: 'found', message: '✓ Verified' });
          } else {
            setWorkspaceCheck({ checking: false, status: 'not_found', message: '✕ Invalid' });
          }
        }
      } catch {
        setWorkspaceCheck({ checking: false, status: null, message: 'Verification error' });
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [form.organization_id, form.workspace_mode]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (form.password.length < 6) {
      setError('Password must be at least 6 characters long.');
      return;
    }

    if (form.password !== confirmPassword) {
      setError('Passwords do not match. Please check both fields.');
      return;
    }

    if (form.organization_id.length !== 4) {
      setError('Team Code must be exactly 4 numeric digits.');
      return;
    }

    if (form.workspace_mode === 'create' && workspaceCheck.status === 'taken') {
      setError(`Team code '${form.organization_id}' is already taken. Please enter another 4-digit code.`);
      return;
    }

    if (form.workspace_mode === 'join' && workspaceCheck.status === 'not_found') {
      setError(`Team code '${form.organization_id}' was not found. Verify the code with your lead.`);
      return;
    }

    setIsSubmitting(true);
    try {
      await registerUser(form);
      const tokenData = await loginUser(form.email, form.password, form.organization_id);
      saveToken(tokenData.access_token);
      const userData = await fetchMe();
      login(tokenData.access_token, userData);
      navigate('/');
    } catch (err) {
      const detail = err.response?.data?.detail || 'Registration failed. Please try again.';
      setError(detail);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="auth-page">
      <AuthBackground />

      <div className="auth-card auth-card-wide">
        {/* Header */}
        <div className="auth-brand">
          <div className="auth-brand-logo-wrapper" style={{ background: 'none', border: 'none', boxShadow: 'none' }}>
            <Logo size={44} />
          </div>
          <h1>Create Account</h1>
          <p>Join the Solar & Wind Intelligence Platform</p>
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

        <form className="auth-form" onSubmit={handleSubmit}>
          {/* Workspace Mode Switcher & 4-Digit Code Row */}
          <div className="auth-input-group">
            <label>Team Workspace</label>

            <div className="workspace-mode-pills" style={{ marginBottom: '0.4rem' }}>
              <button
                type="button"
                className={`mode-pill-btn ${form.workspace_mode === 'create' ? 'active' : ''}`}
                onClick={() => setForm(prev => ({ ...prev, workspace_mode: 'create', organization_id: '' }))}
              >
                Create Team Code
              </button>
              <button
                type="button"
                className={`mode-pill-btn ${form.workspace_mode === 'join' ? 'active' : ''}`}
                onClick={() => setForm(prev => ({ ...prev, workspace_mode: 'join', organization_id: '' }))}
              >
                Join Existing Team
              </button>
            </div>

            <div className="auth-input-wrapper">
              <span className="input-icon-prefix">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                  <path d="M7 11V7a5 5 0 0110 0v4" />
                </svg>
              </span>
              <input
                type="text"
                className={`auth-input team-code-input ${workspaceCheck.message ? 'auth-input-has-status' : ''}`}
                placeholder="Enter 4-digit code"
                maxLength={4}
                value={form.organization_id}
                onChange={set('organization_id')}
                required
              />
              {workspaceCheck.message && (
                <span className={`input-status-suffix ${workspaceCheck.status || ''}`}>
                  {workspaceCheck.message}
                </span>
              )}
            </div>
          </div>

          {/* Full Name & Username */}
          <div className="auth-input-row">
            <div className="auth-input-group">
              <label htmlFor="reg-name">Full Name</label>
              <div className="auth-input-wrapper">
                <span className="input-icon-prefix">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </span>
                <input
                  id="reg-name"
                  type="text"
                  className="auth-input"
                  placeholder="Full Name"
                  value={form.full_name}
                  onChange={set('full_name')}
                  required
                />
              </div>
            </div>

            <div className="auth-input-group">
              <label htmlFor="reg-username">Username</label>
              <div className="auth-input-wrapper">
                <span className="input-icon-prefix">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="4" />
                    <path d="M16 8v5a3 3 0 006 0v-1a10 10 0 10-3.92 7.94" />
                  </svg>
                </span>
                <input
                  id="reg-username"
                  type="text"
                  className="auth-input"
                  placeholder="username"
                  value={form.username}
                  onChange={set('username')}
                  required
                />
              </div>
            </div>
          </div>

          {/* Email Address */}
          <div className="auth-input-group">
            <label htmlFor="reg-email">Email Address</label>
            <div className="auth-input-wrapper">
              <span className="input-icon-prefix">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </span>
              <input
                id="reg-email"
                type="email"
                className="auth-input"
                placeholder="you@organization.com"
                value={form.email}
                onChange={set('email')}
                required
              />
            </div>
          </div>

          {/* Password & Confirm Password */}
          <div className="auth-input-row">
            <div className="auth-input-group">
              <label htmlFor="reg-password">Password</label>
              <div className="auth-input-wrapper">
                <span className="input-icon-prefix">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                </span>
                <input
                  id="reg-password"
                  type={showPassword ? 'text' : 'password'}
                  className="auth-input auth-input-has-suffix"
                  placeholder="Password"
                  value={form.password}
                  onChange={set('password')}
                  required
                  minLength={6}
                />
                <button
                  type="button"
                  className="input-eye-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                  title={showPassword ? 'Hide Password' : 'Show Password'}
                >
                  {showPassword ? (
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-7 0-11-7-11-7a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 7 11 7a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24" />
                      <line x1="1" y1="1" x2="23" y2="23" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                    </svg>
                  ) : (
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  )}
                </button>
              </div>
            </div>

            <div className="auth-input-group">
              <label htmlFor="reg-confirm-password">Confirm Password</label>
              <div className="auth-input-wrapper">
                <span className="input-icon-prefix">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </span>
                <input
                  id="reg-confirm-password"
                  type={showConfirmPassword ? 'text' : 'password'}
                  className="auth-input auth-input-has-suffix"
                  placeholder="Confirm Password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  minLength={6}
                />
                <button
                  type="button"
                  className="input-eye-toggle"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  title={showConfirmPassword ? 'Hide Password' : 'Show Password'}
                >
                  {showConfirmPassword ? (
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-7 0-11-7-11-7a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 7 11 7a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24" />
                      <line x1="1" y1="1" x2="23" y2="23" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                    </svg>
                  ) : (
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Role Select */}
          <div className="auth-input-group">
            <label htmlFor="reg-role">Workspace Role</label>
            <div className="auth-input-wrapper">
              <span className="input-icon-prefix">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </span>
              <select
                id="reg-role"
                className="auth-select"
                value={form.role}
                onChange={set('role')}
              >
                {ROLE_OPTIONS.map((r) => (
                  <option key={r.value} value={r.value}>{r.label}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            className="auth-btn auth-btn-primary"
            disabled={isSubmitting || workspaceCheck.status === 'taken' || workspaceCheck.status === 'not_found'}
            style={{ marginTop: '0.3rem' }}
          >
            {isSubmitting ? (
              <>
                <span className="auth-spinner" /> Creating Account...
              </>
            ) : (
              'Create Account'
            )}
          </button>
        </form>

        <div className="auth-switch">
          Already have an account? <Link to="/login">Sign in</Link>
        </div>
      </div>
    </div>
  );
}
