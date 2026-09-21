import { describe, expect, it } from 'vitest';
import access from './access';

describe('access', () => {
  it('should return canAdmin true when user role is admin', () => {
    const initialState = {
      currentUser: {
        id: '1',
        nickname: 'Admin User',
        role: 'admin',
      },
    };

    const result = access(initialState);

    expect(result.canAdmin).toBe(true);
    expect(result.canSuperAdmin).toBe(false);
  });

  it('should return canSuperAdmin true when user role is superadmin', () => {
    const initialState = {
      currentUser: {
        id: '0',
        nickname: 'Super Admin',
        role: 'superadmin',
      },
    };

    const result = access(initialState);

    expect(result.canSuperAdmin).toBe(true);
    expect(result.canAdmin).toBe(true);
  });

  it('should return canAdmin false when user role is user', () => {
    const initialState = {
      currentUser: {
        id: '2',
        nickname: 'Regular User',
        role: 'user',
      },
    };

    const result = access(initialState);

    expect(result.canAdmin).toBe(false);
    expect(result.canUser).toBe(true);
  });

  it('should return canAdmin false when user role is undefined', () => {
    const initialState = {
      currentUser: {
        id: '3',
        nickname: 'Guest User',
      },
    };

    const result = access(initialState);

    expect(result.canAdmin).toBe(false);
  });

  it('should return canUser false when currentUser is undefined', () => {
    const initialState = {
      currentUser: undefined,
    };

    const result = access(initialState);

    expect(result.canUser).toBe(false);
  });

  it('should return canUser false when initialState is undefined', () => {
    const result = access(undefined);

    expect(result.canUser).toBe(false);
  });
});
