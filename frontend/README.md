# ChirpNeighbors Frontend

React + TypeScript web application for bird sound identification.

## Quick Start

### Prerequisites

- Node.js 18+ (LTS recommended)
- npm or pnpm

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at http://localhost:5173

## Development

### Available Scripts

```bash
# Development server with HMR
npm run dev

# Type checking
npm run type-check

# Linting
npm run lint
npm run lint:fix

# Formatting
npm run format
npm run format:check

# Testing
npm test              # Run tests once
npm run test:watch    # Watch mode
npm run test:ui       # Test UI
npm run test:coverage # Coverage report

# Build
npm run build         # Production build
npm run preview       # Preview production build
```

### Project Structure

```
frontend/
├── src/
│   ├── components/       # React components
│   ├── pages/           # Page components
│   ├── hooks/           # Custom React hooks
│   ├── services/        # API services
│   │   └── api.ts       # Backend API client
│   ├── types/           # TypeScript types
│   │   └── index.ts     # Shared type definitions
│   ├── utils/           # Utility functions
│   ├── test/            # Test utilities
│   ├── App.tsx          # Root component
│   ├── main.tsx         # Entry point
│   └── index.css        # Global styles
├── public/              # Static assets
├── index.html           # HTML template
├── vite.config.ts       # Vite configuration
├── tsconfig.json        # TypeScript config
├── .eslintrc.cjs        # ESLint config
└── .prettierrc.json     # Prettier config
```

## Technology Stack

- **Framework**: React 18
- **Build Tool**: Vite 5
- **Language**: TypeScript
- **Testing**: Vitest + Testing Library
- **Linting**: ESLint + Prettier
- **HTTP Client**: Axios
- **Router**: React Router (ready to use)

## Code Quality

### Linting & Formatting

The project uses ESLint and Prettier with pre-commit hooks via Husky:

- **ESLint**: TypeScript, React, and React Hooks rules
- **Prettier**: Consistent code formatting
- **Pre-commit**: Runs lint-staged on commit

Commit hooks will automatically:
1. Lint and fix TypeScript/React files
2. Format all staged files
3. Prevent commits with errors

### TypeScript

Strict TypeScript configuration with:
- `strict: true`
- `noUnusedLocals: true`
- `noUnusedParameters: true`
- `noUncheckedIndexedAccess: true`

### Testing

Write tests using Vitest and Testing Library:

```typescript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import MyComponent from './MyComponent';

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(<MyComponent />);
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });
});
```

## API Integration

The frontend connects to the backend API at http://localhost:8000:

```typescript
import { api } from '@/services/api';

// Health check
const health = await api.healthCheck();

// Upload audio
const result = await api.uploadAudio(file);

// Get species
const species = await api.listSpecies();
```

API proxy is configured in `vite.config.ts` to forward `/api` requests to the backend.

## Performance Targets

- **Build time**: < 10s
- **HMR**: < 100ms
- **Test suite**: < 5s
- **Bundle size**: < 500KB (gzipped)

## Environment Variables

Create `.env` file for environment-specific configuration:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## Contributing

1. Create feature branch
2. Make changes with tests
3. Run `npm run lint:fix && npm run format`
4. Ensure `npm test` passes
5. Commit (pre-commit hooks will run)
6. Submit PR

## Browser Support

- Chrome (last 2 versions)
- Firefox (last 2 versions)
- Safari (last 2 versions)
- Edge (last 2 versions)

## License

MIT
