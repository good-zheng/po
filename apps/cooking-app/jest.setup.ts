import AsyncStorage from '@react-native-async-storage/async-storage';
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

jest.mock('@react-native-async-storage/async-storage', () =>
  require('@react-native-async-storage/async-storage/jest'),
);

jest.mock('expo-speech', () => ({
  speak: jest.fn(),
  stop: jest.fn(),
}));

beforeEach(() => {
  mockSecureStoreData.clear();
  void AsyncStorage.clear();
});
