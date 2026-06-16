import '@testing-library/jest-dom/vitest';

import { WebSocket } from 'ws';
globalThis.WebSocket = WebSocket;
