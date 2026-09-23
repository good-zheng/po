import * as matchers from '@testing-library/react-native/matchers';

expect.extend(matchers);

const mockSecureStoreData = new Map<string, string>();

jest.mock('expo-secure-store', () => ({
  deleteItemAsync: jest.fn(async (key: string) => {
    mockSecureStoreData.delete(key);
  }),
  getItemAsync: jest.fn(
    async (key: string) => mockSecureStoreData.get(key) ?? null,
  ),
  setItemAsync: jest.fn(async (key: string, value: string) => {
    mockSecureStoreData.set(key, value);
  }),
}));

beforeEach(() => {
  mockSecureStoreData.clear();
});
