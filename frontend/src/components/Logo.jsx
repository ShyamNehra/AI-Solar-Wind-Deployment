import React from 'react';

export default function Logo({ size = 32, className = '' }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 32 32"
      width={size}
      height={size}
      className={className}
      fill="none"
      style={{ display: 'inline-block', verticalAlign: 'middle', borderRadius: '8px' }}
    >
      <rect width="32" height="32" rx="8" fill="#0F172A" />
      {/* Minimal Sun */}
      <circle cx="11" cy="11" r="4.5" fill="#F59E0B" />
      {/* Minimal Wind Swoosh Lines */}
      <path d="M6 21C11 21 16 16 26 9" stroke="#3B82F6" strokeWidth="2.5" strokeLinecap="round" />
      <path d="M10 25C14 25 18 21 25 15" stroke="#60A5FA" strokeWidth="1.75" strokeLinecap="round" opacity="0.75" />
    </svg>
  );
}
