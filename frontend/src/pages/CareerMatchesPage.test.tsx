import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { CareerMatchesPage } from './CareerMatchesPage';

describe('CareerMatchesPage score semantics', () => {
  const baseProps = {
    recommendations: [{ rank: 1, role: 'Platform Engineer', score: 1 }],
    selectedSkills: [{ name: 'Python', level: 'advanced' as const }],
    onSelectRole: vi.fn(),
    onExploreJobs: vi.fn(),
    onReset: vi.fn(),
    savedRoles: [],
    onToggleSavedRole: vi.fn(),
  };

  it('does not label fallback classifier scores as ANN Softmax probabilities', () => {
    render(<CareerMatchesPage {...baseProps} model="sklearn" />);

    expect(screen.getByText('Fallback classifier score')).toBeInTheDocument();
    expect(screen.getAllByText(/configured scikit-learn fallback classifier/i)).toHaveLength(2);
    expect(screen.queryByText(/normalized Softmax probability output from the ANN model/i)).not.toBeInTheDocument();
  });

  it('uses ANN Softmax wording only for TensorFlow predictions', () => {
    render(<CareerMatchesPage {...baseProps} model="tensorflow" />);

    expect(screen.getByText('ANN Softmax score')).toBeInTheDocument();
    expect(screen.getAllByText(/ANN Softmax outputs/i)).toHaveLength(2);
  });
});
