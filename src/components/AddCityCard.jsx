import './AddCityCard.css';

export default function AddCityCard({ onClick }) {
  return (
    <div className="add-city-card" onClick={onClick}>
      <div className="add-city-content">
        <div className="add-icon">+</div>
        <div className="add-text">
          <p className="add-title">Add City</p>
          <p className="add-subtitle">Add to favorites</p>
        </div>
      </div>
    </div>
  );
}
