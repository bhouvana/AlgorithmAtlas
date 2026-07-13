import type { Config } from 'tailwindcss';

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'IBM Plex Mono', 'Fira Code', 'monospace'],
        display: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        surface: { DEFAULT: '#111113', card: '#18181B', elevated: '#1C1C1F' },
        brand: { indigo: '#4F46E5', blue: '#3B82F6', purple: '#8B5CF6', cyan: '#22D3EE' },
        // Static card/panel border color (design feedback, 2026-07-13). Used
        // as `border-charcoal/10`, a barely-visible accent, not a solid
        // outline. Interactive borders that change on hover/focus (buttons,
        // nav pills, inputs) intentionally keep the layered white-opacity
        // treatment instead, since a flat color can't express that state
        // change the same way.
        charcoal: '#36454F',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease forwards',
        'slide-up': 'slideUp 0.6s ease forwards',
        'float': 'float 6s ease-in-out infinite',
        'shimmer': 'shimmer 2s linear infinite',
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: { '0%': { opacity: '0' }, '100%': { opacity: '1' } },
        slideUp: { '0%': { opacity: '0', transform: 'translateY(20px)' }, '100%': { opacity: '1', transform: 'translateY(0)' } },
        float: { '0%, 100%': { transform: 'translateY(0)' }, '50%': { transform: 'translateY(-10px)' } },
        shimmer: { '0%': { backgroundPosition: '-200% 0' }, '100%': { backgroundPosition: '200% 0' } },
      },
      boxShadow: {
        'glow-sm': '0 0 12px rgba(79,70,229,0.25)',
        'glow': '0 0 24px rgba(79,70,229,0.35)',
        'glow-lg': '0 0 48px rgba(79,70,229,0.45)',
        'card': '0 1px 0 rgba(255,255,255,0.05), 0 8px 32px rgba(0,0,0,0.4)',
        'card-hover': '0 1px 0 rgba(255,255,255,0.08), 0 20px 48px rgba(0,0,0,0.5)',
      },
    },
  },
  plugins: [],
} satisfies Config;
