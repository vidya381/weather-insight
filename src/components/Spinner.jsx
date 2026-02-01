import './Spinner.css';

export default function Spinner({ size = 'medium', text }) {
  return (
    <div className="spinner-container">
      <div className={`spinner spinner-${size}`} />
      {text && <p className="spinner-text">{text}</p>}
    </div>
  );
}
