import { useState } from 'react';
import { IoClose, IoPerson, IoMail, IoLockClosed, IoCheckmark } from 'react-icons/io5';
import { authAPI } from '../api/auth';
import './ProfileEditModal.css';

export default function ProfileEditModal({ user, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    username: user?.username || '',
    email: user?.email || '',
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showPasswordFields, setShowPasswordFields] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setError('');
    setSuccess('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    // Validate password change if attempting
    if (showPasswordFields) {
      if (!formData.currentPassword) {
        setError('Current password is required to change password');
        return;
      }
      if (!formData.newPassword) {
        setError('New password is required');
        return;
      }
      if (formData.newPassword.length < 8) {
        setError('New password must be at least 8 characters');
        return;
      }
      if (formData.newPassword !== formData.confirmPassword) {
        setError('New passwords do not match');
        return;
      }
    }

    // Build update data
    const updateData = {};
    if (formData.username !== user.username) {
      updateData.username = formData.username;
    }
    if (formData.email !== user.email) {
      updateData.email = formData.email;
    }
    if (showPasswordFields && formData.newPassword) {
      updateData.current_password = formData.currentPassword;
      updateData.new_password = formData.newPassword;
    }

    // Check if anything changed
    if (Object.keys(updateData).length === 0) {
      setError('No changes to save');
      return;
    }

    setLoading(true);
    try {
      const updatedUser = await authAPI.updateProfile(updateData);
      setSuccess('Profile updated successfully!');

      // Call success callback to update parent component
      if (onSuccess) {
        onSuccess(updatedUser);
      }

      // Close modal after 1.5 seconds
      setTimeout(() => {
        onClose();
      }, 1500);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Edit Profile</h2>
          <button className="modal-close-btn" onClick={onClose}>
            <IoClose size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="profile-edit-form">
          {error && (
            <div className="form-message form-error">
              {error}
            </div>
          )}

          {success && (
            <div className="form-message form-success">
              <IoCheckmark size={20} />
              {success}
            </div>
          )}

          {/* Username Field */}
          <div className="form-group">
            <label htmlFor="username">
              <IoPerson size={18} />
              Username
            </label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              minLength={3}
              maxLength={50}
              required
            />
          </div>

          {/* Email Field */}
          <div className="form-group">
            <label htmlFor="email">
              <IoMail size={18} />
              Email
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>

          {/* Password Change Section */}
          <div className="password-change-section">
            <button
              type="button"
              className="toggle-password-btn"
              onClick={() => setShowPasswordFields(!showPasswordFields)}
            >
              <IoLockClosed size={18} />
              {showPasswordFields ? 'Cancel Password Change' : 'Change Password'}
            </button>

            {showPasswordFields && (
              <>
                <div className="form-group">
                  <label htmlFor="currentPassword">Current Password</label>
                  <input
                    type="password"
                    id="currentPassword"
                    name="currentPassword"
                    value={formData.currentPassword}
                    onChange={handleChange}
                    placeholder="Enter current password"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="newPassword">New Password</label>
                  <input
                    type="password"
                    id="newPassword"
                    name="newPassword"
                    value={formData.newPassword}
                    onChange={handleChange}
                    minLength={8}
                    placeholder="Enter new password (min 8 characters)"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="confirmPassword">Confirm New Password</label>
                  <input
                    type="password"
                    id="confirmPassword"
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    placeholder="Confirm new password"
                  />
                </div>
              </>
            )}
          </div>

          {/* Form Actions */}
          <div className="form-actions">
            <button
              type="button"
              className="btn-cancel"
              onClick={onClose}
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn-save"
              disabled={loading}
            >
              {loading ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
