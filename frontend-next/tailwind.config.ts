import type { Config } from 'tailwindcss';

export default {
  darkMode: ['class'],
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        background: '#0b1020',
        foreground: '#e6ebff',
        card: '#111833',
        border: '#1f2a4d',
        primary: '#5b8cff',
        'primary-foreground': '#ffffff',
        muted: '#9fb0e6',
        danger: '#ff5d73',
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
      },
    },
  },
  plugins: [],
} satisfies Config;
