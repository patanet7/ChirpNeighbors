import { expect, afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';

// Cleanup after each test
afterEach(() => {
  cleanup();
});

// Extend Vitest matchers if needed
// import { toHaveNoViolations } from 'jest-axe';
// expect.extend(toHaveNoViolations);
