import { Component } from 'react';
import './ErrorBoundary.css';

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.href = '/dashboard';
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <div className="error-boundary-content">
            <h1>Something went wrong</h1>
            <p>We encountered an unexpected error. This has been logged.</p>
            {this.state.error?.message && (
              <div className="error-details">
                <code>{this.state.error.message}</code>
              </div>
            )}
            <button onClick={this.handleReset} className="error-boundary-btn">
              Return to Dashboard
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
