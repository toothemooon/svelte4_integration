// Setup file for Jest tests
import '@testing-library/jest-dom';
import { jest } from '@jest/globals';

// Fix for "ReferenceError: TextEncoder is not defined" in jsdom environment
import { TextEncoder, TextDecoder } from 'util';
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;

// Mock browser localStorage for tests
const getItemMock = jest.fn();
const setItemMock = jest.fn();
const removeItemMock = jest.fn();
const clearMock = jest.fn();

global.localStorage = {
  getItem: getItemMock,
  setItem: setItemMock,
  removeItem: removeItemMock,
  clear: clearMock
};

// Mock fetch API
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({}),
  })
);

// Mock window.confirm and window.alert
global.confirm = jest.fn(() => true);
global.alert = jest.fn(); 