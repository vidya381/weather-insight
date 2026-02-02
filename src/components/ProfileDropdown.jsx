import { useState, useRef, useEffect } from 'react';
import { IoPerson, IoLogOut, IoChevronDown, IoSettings } from 'react-icons/io5';
import './ProfileDropdown.css';

export default function ProfileDropdown({ username, onLogout, onEditProfile }) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const handleLogout = () => {
    setIsOpen(false);
    onLogout();
  };

  const handleEditProfile = () => {
    setIsOpen(false);
    if (onEditProfile) {
      onEditProfile();
    }
  };

  return (
    <div className="profile-dropdown" ref={dropdownRef}>
      <button
        className="profile-trigger"
        onClick={() => setIsOpen(!isOpen)}
      >
        <IoPerson size={18} className="user-icon" />
        <span className="user-name">{username}</span>
        <IoChevronDown
          size={16}
          className={`chevron-icon ${isOpen ? 'open' : ''}`}
        />
      </button>

      {isOpen && (
        <div className="dropdown-menu">
          <button className="dropdown-item" onClick={handleEditProfile}>
            <IoSettings size={18} />
            <span>Edit Profile</span>
          </button>
          <div className="dropdown-divider" />
          <button className="dropdown-item dropdown-item-logout" onClick={handleLogout}>
            <IoLogOut size={18} />
            <span>Logout</span>
          </button>
        </div>
      )}
    </div>
  );
}
