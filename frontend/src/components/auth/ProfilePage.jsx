import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { updateProfile } from '../../api/auth';
import './Auth.css';

export default function ProfilePage({ isOpen, onClose }) {
  const { user, logout, refreshUser, getRoleLabel } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    full_name: user?.full_name || '',
    organization: user?.organization || '',
    organization_id: user?.organization_id || '1001',
    bio: user?.bio || '',
  });
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (user && isOpen) {
      setForm({
        full_name: user.full_name || '',
        organization: user.organization || '',
        organization_id: user.organization_id || '1001',
        bio: user.bio || '',
      });
      setMessage('');
    }
  }, [user, isOpen]);

  if (!isOpen || !user) return null;

  const initials = (user.full_name || user.username || 'U')
    .split(' ')
    .map((w) => w[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);

  const handleSave = async () => {
    setSaving(true);
    setMessage('');
    try {
      await updateProfile(form);
      await refreshUser();
      setMessage('Profile updated successfully!');
    } catch (err) {
      setMessage('Failed to update profile.');
    } finally {
      setSaving(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="profile-overlay" onClick={onClose}>
      <div className="profile-modal" onClick={(e) => e.stopPropagation()}>
        <button
          type="button"
          className="profile-close-btn"
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '14px',
            right: '14px',
            background: '#ffffff',
            border: '1px solid #cbd5e1',
            borderRadius: '50%',
            width: '28px',
            height: '28px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '0.85rem',
            fontWeight: 'bold',
            color: '#64748b',
            cursor: 'pointer',
            zIndex: 10,
            boxShadow: '0 2px 6px rgba(0,0,0,0.08)',
            transition: 'all 0.2s ease',
          }}
          title="Close Profile Window"
        >
          ✕
        </button>
        <div className="profile-header">
          <div className="profile-avatar-lg">{initials}</div>
          <div className="profile-meta">
            <h2>{user.full_name || user.username}</h2>
            <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap', marginTop: '0.2rem' }}>
              <span className="role-badge">{getRoleLabel(user.role)}</span>
              <span className="role-badge" style={{ background: '#f0fdf4', color: '#166534', border: '1px solid #bbf7d0', fontFamily: 'monospace', fontWeight: 800 }}>
                Team Code: #{user.organization_id || '1001'}
              </span>
            </div>
            <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.35rem', fontWeight: 500 }}>
              @{user.username} · {user.email}
            </div>
          </div>
        </div>

        <div className="profile-form">
          <div className="auth-input-group">
            <label>Full Name</label>
            <input
              type="text"
              className="profile-input"
              value={form.full_name}
              onChange={(e) => setForm({ ...form, full_name: e.target.value })}
              placeholder="Your full name"
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
            <div className="auth-input-group">
              <label>Organization / Company</label>
              <input
                type="text"
                className="profile-input"
                value={form.organization}
                onChange={(e) => setForm({ ...form, organization: e.target.value })}
                placeholder="Company name"
              />
            </div>

            <div className="auth-input-group">
              <label>Team Workspace Code</label>
              <input
                type="text"
                className="profile-input"
                style={{ fontFamily: 'monospace', fontWeight: 700 }}
                value={form.organization_id}
                onChange={(e) => setForm({ ...form, organization_id: e.target.value })}
                placeholder="4-digit team code"
                maxLength={10}
              />
            </div>
          </div>

          <div className="auth-input-group">
            <label>Bio</label>
            <textarea
              className="profile-textarea"
              value={form.bio}
              onChange={(e) => setForm({ ...form, bio: e.target.value })}
              placeholder="Brief description of your expertise..."
              rows={2}
            />
          </div>

          <div className="profile-footer-info">
            <span>Joined: {new Date(user.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })}</span>
          </div>

          {message && (
            <div className={message.includes('success') ? 'auth-success' : 'auth-error'}>
              {message}
            </div>
          )}

          <div className="profile-actions">
            <button
              className="profile-btn profile-btn-logout"
              style={{ background: '#fef2f2', border: '1px solid #fecaca', color: '#dc2626', fontWeight: 700 }}
              onClick={handleLogout}
            >
              Logout
            </button>
            <button className="profile-btn profile-btn-save" onClick={handleSave} disabled={saving}>
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
