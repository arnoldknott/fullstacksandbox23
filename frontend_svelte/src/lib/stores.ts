import { writable } from 'svelte/store';
import type { AppTheme } from './theming';

export const themeStore = writable<AppTheme>({} as AppTheme);

export const count = writable<number>(0);
