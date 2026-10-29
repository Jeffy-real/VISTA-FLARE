import type { ImgHTMLAttributes } from 'react';

export type LogoVariant = 'full' | 'icon' | 'wordmark' | 'stacked';
export type LogoSizePreset = 'sm' | 'md' | 'lg' | 'xl';

export interface VistaFlareLogoProps extends Omit<ImgHTMLAttributes<HTMLImageElement>, 'size' | 'src'> {
  /**
   * Logo variant:
   * - 'full': Horizontal official logo with navy-blue V-symbol and VISTA FLARE wordmark
   * - 'icon': Genuine standalone V-symbol (navy, electric blue, and teal accents)
   * - 'wordmark': Authentic VISTA FLARE typography without symbol
   * - 'stacked': Vertical layout with centered symbol above wordmark
   */
  variant?: LogoVariant;
  /** Size preset ('sm' | 'md' | 'lg' | 'xl') or a numeric height in pixels */
  size?: LogoSizePreset | number;
  /** Accessible alternative text. Defaults to appropriate brand description */
  alt?: string;
  /** Optional class name */
  className?: string;
}

interface VariantMetadata {
  src: string;
  intrinsicWidth: number;
  intrinsicHeight: number;
  aspectRatio: number;
  defaultAlt: string;
  heightPresets: Record<LogoSizePreset, number>;
}

const VARIANTS: Record<LogoVariant, VariantMetadata> = {
  full: {
    src: '/vista-flare-logo.png',
    intrinsicWidth: 1721,
    intrinsicHeight: 627,
    aspectRatio: 1721 / 627, // ~2.745
    defaultAlt: 'Vista Flare',
    heightPresets: { sm: 28, md: 36, lg: 48, xl: 64 },
  },
  icon: {
    src: '/vista-flare-icon.png',
    intrinsicWidth: 1407,
    intrinsicHeight: 1381,
    aspectRatio: 1407 / 1381, // ~1.019
    defaultAlt: 'Vista Flare symbol',
    heightPresets: { sm: 28, md: 36, lg: 44, xl: 56 },
  },
  wordmark: {
    src: '/vista-flare-wordmark.png',
    intrinsicWidth: 1709,
    intrinsicHeight: 527,
    aspectRatio: 1709 / 527, // ~3.243
    defaultAlt: 'VISTA FLARE',
    heightPresets: { sm: 22, md: 28, lg: 38, xl: 50 },
  },
  stacked: {
    src: '/vista-flare-logo-stacked.png',
    intrinsicWidth: 1760,
    intrinsicHeight: 1394,
    aspectRatio: 1760 / 1394, // ~1.263
    defaultAlt: 'Vista Flare',
    heightPresets: { sm: 48, md: 64, lg: 84, xl: 112 },
  },
};

export function VistaFlareLogo({
  variant = 'full',
  size = 'md',
  alt,
  className = '',
  style,
  ...rest
}: VistaFlareLogoProps) {
  const meta = VARIANTS[variant] || VARIANTS.full;
  const targetHeight = typeof size === 'number' ? size : meta.heightPresets[size] || meta.heightPresets.md;
  const calculatedWidth = Math.round(targetHeight * meta.aspectRatio);

  return (
    <img
      src={meta.src}
      width={calculatedWidth}
      height={targetHeight}
      alt={alt ?? meta.defaultAlt}
      decoding="async"
      loading="eager"
      className={`inline-block object-contain select-none ${className}`}
      style={{
        aspectRatio: `${meta.intrinsicWidth} / ${meta.intrinsicHeight}`,
        maxWidth: '100%',
        height: 'auto',
        maxHeight: `${targetHeight}px`,
        ...style,
      }}
      {...rest}
    />
  );
}

export default VistaFlareLogo;

