import React from 'react';
import './Auth.css';

export default function AuthBackground() {
  return (
    <div className="auth-background-container">
      {/* 100% Vector SVG Background */}
      <svg 
        className="vector-background"
        viewBox="0 0 1440 900" 
        preserveAspectRatio="xMidYMax slice"
        fill="none" 
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          {/* Sky Gradient */}
          <linearGradient id="skyGrad" x1="50%" y1="0%" x2="50%" y2="100%">
            <stop offset="0%" stopColor="#0a0f1d" />
            <stop offset="50%" stopColor="#111827" />
            <stop offset="100%" stopColor="#1e293b" />
          </linearGradient>

          {/* Sun/Energy Source Glow */}
          <radialGradient id="energyGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#38bdf8" stopOpacity="0.25" />
            <stop offset="50%" stopColor="#0ea5e9" stopOpacity="0.08" />
            <stop offset="100%" stopColor="#0c4a6e" stopOpacity="0" />
          </radialGradient>

          {/* Solar Panel Gloss */}
          <linearGradient id="panelGloss" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#0284c7" />
            <stop offset="100%" stopColor="#0f172a" />
          </linearGradient>

          {/* Windmill Blade Shape */}
          <path id="blade" d="M -1.5,0 L -2.5,-45 C -2.5,-50 2.5,-50 2.5,-45 L 1.5,0 Z" fill="#e2e8f0" opacity="0.95" />
        </defs>

        {/* 1. Sky */}
        <rect width="1440" height="900" fill="url(#skyGrad)" />

        {/* 2. Abstract Pulsing Solar Energy Source */}
        <g transform="translate(1080, 250)">
          <circle cx="0" cy="0" r="180" fill="url(#energyGlow)" className="energy-ring-pulse" />
          <circle cx="0" cy="0" r="110" fill="url(#energyGlow)" className="energy-ring-pulse-delayed" />
          <circle cx="0" cy="0" r="6" fill="#38bdf8" opacity="0.8" />
        </g>

        {/* 3. Subtle Vector Wind Currents */}
        <path 
          className="wind-current" 
          d="M -100,180 Q 300,100 700,240 T 1500,200" 
          stroke="rgba(56, 189, 248, 0.12)" 
          strokeWidth="2" 
          strokeDasharray="25 40" 
          fill="none" 
        />
        <path 
          className="wind-current" 
          d="M -100,320 Q 400,280 800,360 T 1500,300" 
          stroke="rgba(16, 185, 129, 0.08)" 
          strokeWidth="1.5" 
          strokeDasharray="15 35" 
          fill="none" 
          style={{ animationDelay: '-4s', animationDuration: '22s' }}
        />
        <path 
          className="wind-current" 
          d="M -100,480 Q 200,420 750,520 T 1500,460" 
          stroke="rgba(56, 189, 248, 0.08)" 
          strokeWidth="1.8" 
          strokeDasharray="30 45" 
          fill="none" 
          style={{ animationDelay: '-8s', animationDuration: '16s' }}
        />

        {/* 4. Layered Abstract Vector Hills */}
        
        {/* Far Hills (Deep Navy) */}
        <path 
          d="M 0,560 Q 380,480 720,590 T 1440,510 L 1440,900 L 0,900 Z" 
          fill="#111625" 
          stroke="#1e293b"
          strokeWidth="0.5"
        />

        {/* Far Windmills */}
        <g transform="translate(240, 510) scale(0.45)">
          <line x1="0" y1="0" x2="0" y2="80" stroke="#475569" strokeWidth="2.5" />
          <g className="spinning-rotor" style={{ animationDuration: '5s' }}>
            <circle cx="0" cy="0" r="2.5" fill="#f1f5f9" />
            <use href="#blade" />
            <use href="#blade" transform="rotate(120)" />
            <use href="#blade" transform="rotate(240)" />
          </g>
        </g>
        <g transform="translate(1080, 520) scale(0.4)">
          <line x1="0" y1="0" x2="0" y2="80" stroke="#475569" strokeWidth="2.5" />
          <g className="spinning-rotor" style={{ animationDuration: '6s' }}>
            <circle cx="0" cy="0" r="2.5" fill="#f1f5f9" />
            <use href="#blade" />
            <use href="#blade" transform="rotate(120)" />
            <use href="#blade" transform="rotate(240)" />
          </g>
        </g>

        {/* Mid Hills (Deep Slate Blue) */}
        <path 
          d="M 0,640 Q 420,560 920,680 T 1440,630 L 1440,900 L 0,900 Z" 
          fill="#161e33" 
          stroke="#334155"
          strokeWidth="0.5"
        />

        {/* Mid Windmills */}
        <g transform="translate(140, 580) scale(0.7)">
          <line x1="0" y1="0" x2="0" y2="100" stroke="#64748b" strokeWidth="3" />
          <g className="spinning-rotor" style={{ animationDuration: '4s' }}>
            <circle cx="0" cy="0" r="3.5" fill="#f8fafc" />
            <use href="#blade" />
            <use href="#blade" transform="rotate(120)" />
            <use href="#blade" transform="rotate(240)" />
          </g>
        </g>
        <g transform="translate(1160, 605) scale(0.6)">
          <line x1="0" y1="0" x2="0" y2="100" stroke="#64748b" strokeWidth="3" />
          <g className="spinning-rotor" style={{ animationDuration: '4.8s' }}>
            <circle cx="0" cy="0" r="3.5" fill="#f8fafc" />
            <use href="#blade" />
            <use href="#blade" transform="rotate(120)" />
            <use href="#blade" transform="rotate(240)" />
          </g>
        </g>
        <g transform="translate(1280, 595) scale(0.65)">
          <line x1="0" y1="0" x2="0" y2="100" stroke="#64748b" strokeWidth="3" />
          <g className="spinning-rotor" style={{ animationDuration: '3.5s' }}>
            <circle cx="0" cy="0" r="3.5" fill="#f8fafc" />
            <use href="#blade" />
            <use href="#blade" transform="rotate(120)" />
            <use href="#blade" transform="rotate(240)" />
          </g>
        </g>

        {/* Near Hills (Slate Gray-Blue) */}
        <path 
          d="M 0,730 Q 520,670 1020,760 T 1440,740 L 1440,900 L 0,900 Z" 
          fill="#1e294b" 
          stroke="#475569"
          strokeWidth="0.5"
        />

        {/* Near Windmills */}
        <g transform="translate(220, 665) scale(0.95)">
          <line x1="0" y1="0" x2="0" y2="120" stroke="#94a3b8" strokeWidth="3.5" />
          <g className="spinning-rotor" style={{ animationDuration: '3.2s' }}>
            <circle cx="0" cy="0" r="4.5" fill="#ffffff" />
            <use href="#blade" />
            <use href="#blade" transform="rotate(120)" />
            <use href="#blade" transform="rotate(240)" />
          </g>
        </g>
        <g transform="translate(1120, 700) scale(0.85)">
          <line x1="0" y1="0" x2="0" y2="120" stroke="#94a3b8" strokeWidth="3.5" />
          <g className="spinning-rotor" style={{ animationDuration: '4.2s' }}>
            <circle cx="0" cy="0" r="4.5" fill="#ffffff" />
            <use href="#blade" />
            <use href="#blade" transform="rotate(120)" />
            <use href="#blade" transform="rotate(240)" />
          </g>
        </g>

        {/* 5. Abstract Vector Solar Panel Fields on Near Hillside */}
        <g transform="translate(900, 735) rotate(-5) skewX(-15) scale(0.85)">
          {/* Sub-grid 1 */}
          <polygon points="0,30 80,0 160,25 60,65" fill="url(#panelGloss)" stroke="#0ea5e9" strokeWidth="1" />
          <line x1="40" y1="15" x2="110" y2="45" stroke="#38bdf8" strokeWidth="0.5" />
          <line x1="80" y1="0" x2="60" y2="65" stroke="#38bdf8" strokeWidth="0.5" />
          <line x1="40" y1="15" x2="20" y2="47" stroke="#38bdf8" strokeWidth="0.5" />
          <line x1="120" y1="10" x2="110" y2="45" stroke="#38bdf8" strokeWidth="0.5" />
        </g>
        <g transform="translate(100, 770) rotate(12) skewX(20) scale(0.9)">
          <polygon points="0,20 60,0 120,15 50,45" fill="url(#panelGloss)" stroke="#0ea5e9" strokeWidth="1" />
          <line x1="30" y1="10" x2="85" y2="30" stroke="#38bdf8" strokeWidth="0.5" />
          <line x1="60" y1="0" x2="50" y2="45" stroke="#38bdf8" strokeWidth="0.5" />
        </g>
      </svg>
    </div>
  );
}
