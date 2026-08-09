import { writable } from 'svelte/store';

import type { AppTheme } from './theming';

export const themeStore = writable<AppTheme>({} as AppTheme);