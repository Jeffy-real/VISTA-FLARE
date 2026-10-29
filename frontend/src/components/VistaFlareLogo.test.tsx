import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { VistaFlareLogo } from './VistaFlareLogo';

describe('VistaFlareLogo', () => {
  it('renders full logo by default with correct asset and accessible alt', () => {
    render(<VistaFlareLogo />);
    const img = screen.getByRole('img');
    expect(img).toHaveAttribute('src', '/vista-flare-logo.png');
    expect(img).toHaveAttribute('alt', 'Vista Flare');
    expect(img).toHaveAttribute('height', '36');
  });

  it('renders icon variant with standalone icon asset', () => {
    render(<VistaFlareLogo variant="icon" size="sm" />);
    const img = screen.getByRole('img');
    expect(img).toHaveAttribute('src', '/vista-flare-icon.png');
    expect(img).toHaveAttribute('alt', 'Vista Flare symbol');
    expect(img).toHaveAttribute('height', '28');
  });

  it('renders wordmark variant with official typography', () => {
    render(<VistaFlareLogo variant="wordmark" size="lg" />);
    const img = screen.getByRole('img');
    expect(img).toHaveAttribute('src', '/vista-flare-wordmark.png');
    expect(img).toHaveAttribute('alt', 'VISTA FLARE');
    expect(img).toHaveAttribute('height', '38');
  });

  it('renders stacked variant with vertical layout', () => {
    render(<VistaFlareLogo variant="stacked" size={60} />);
    const img = screen.getByRole('img');
    expect(img).toHaveAttribute('src', '/vista-flare-logo-stacked.png');
    expect(img).toHaveAttribute('height', '60');
  });

  it('supports custom alt text and className', () => {
    render(<VistaFlareLogo alt="Custom Brand Label" className="custom-logo" />);
    const img = screen.getByRole('img');
    expect(img).toHaveAttribute('alt', 'Custom Brand Label');
    expect(img).toHaveClass('custom-logo');
  });
});

