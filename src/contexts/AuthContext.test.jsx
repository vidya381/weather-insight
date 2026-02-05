import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { AuthProvider, useAuth } from './AuthContext';
import * as authAPIModule from '../api/auth';

// Mock the auth API
vi.mock('../api/auth', () => ({
  authAPI: {
    login: vi.fn(),
    register: vi.fn(),
    getCurrentUser: vi.fn(),
  },
}));

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
global.localStorage = localStorageMock;

describe('AuthContext', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorageMock.getItem.mockReturnValue(null);
  });

  it('should start with no user when no token in localStorage', () => {
    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });

    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
  });

  it('should login successfully and store token', async () => {
    const mockUser = { id: 1, username: 'testuser', email: 'test@example.com' };
    const mockToken = 'fake-jwt-token';

    authAPIModule.authAPI.login.mockResolvedValue({
      access_token: mockToken,
      user: mockUser,
    });

    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });

    let loginResult;
    await act(async () => {
      loginResult = await result.current.login('testuser', 'password123');
    });

    expect(loginResult.success).toBe(true);
    expect(result.current.user).toEqual(mockUser);
    expect(result.current.isAuthenticated).toBe(true);
    expect(localStorageMock.setItem).toHaveBeenCalledWith('token', mockToken);
  });

  it('should logout and clear token', async () => {
    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });

    // Set user first
    act(() => {
      result.current.logout();
    });

    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('token');
  });

  it('should handle login failure', async () => {
    authAPIModule.authAPI.login.mockRejectedValue({
      response: { data: { detail: 'Invalid credentials' } },
    });

    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });

    let loginResult;
    await act(async () => {
      loginResult = await result.current.login('testuser', 'wrongpassword');
    });

    expect(loginResult.success).toBe(false);
    expect(loginResult.error).toBeTruthy();
    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
  });
});
