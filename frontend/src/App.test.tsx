import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from './App';

describe('App', () => {
  it('renders ChirpNeighbors heading', () => {
    render(<App />);
    const heading = screen.getByText(/ChirpNeighbors/i);
    expect(heading).toBeInTheDocument();
  });

  it('renders welcome message', () => {
    render(<App />);
    const welcome = screen.getByText(/Welcome to ChirpNeighbors/i);
    expect(welcome).toBeInTheDocument();
  });

  it('renders backend health check button', () => {
    render(<App />);
    const button = screen.getByRole('button', { name: /Check Backend Health/i });
    expect(button).toBeInTheDocument();
  });

  it('renders feature list', () => {
    render(<App />);
    expect(screen.getByText(/Audio Upload & Processing/i)).toBeInTheDocument();
    expect(screen.getByText(/ML-powered Bird Identification/i)).toBeInTheDocument();
  });
});
