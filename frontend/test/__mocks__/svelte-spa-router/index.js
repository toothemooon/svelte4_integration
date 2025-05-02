import { jest } from '@jest/globals';
import { writable } from 'svelte/store';

export const push = jest.fn();
export const pop = jest.fn();
export const replace = jest.fn();
export const link = jest.fn();

// Create a writable store for location that can be subscribed to
export const location = writable('/post/1'); 