module.exports = {
  preset: 'jest-expo',
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '\\.css$': '<rootDir>/jest/css-mock.js',
  },
  setupFilesAfterEnv: ['<rootDir>/jest.setup.ts'],
};
