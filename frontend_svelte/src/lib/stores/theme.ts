import { writable } from 'svelte/store';

import type { AppTheme } from '../theming';

// TBD: consider converting this store into a state inside theming.ts and export it for global reactivity.

const theme = writable<AppTheme>({} as AppTheme);
export default theme;
