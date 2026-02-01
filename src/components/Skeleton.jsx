import './Skeleton.css';

export default function Skeleton({ variant = 'text', width, height, className = '' }) {
  const style = {
    width: width || '100%',
    height: height || (variant === 'text' ? '1rem' : '100%')
  };

  return (
    <div className={`skeleton skeleton-${variant} ${className}`} style={style} />
  );
}
