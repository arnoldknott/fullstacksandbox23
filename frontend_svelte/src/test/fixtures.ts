/* eslint-disable no-empty-pattern */

import { argbFromHex } from '@material/material-color-utilities';
import { get } from 'svelte/store';
import { test as baseTest } from 'vitest';

import { themeStore } from '$lib/stores';
import type { AppTheme } from '$lib/theming';


export const test = baseTest
    .extend<{
        initFlyonUI: typeof import('flyonui/flyonui');
        setThemeStore: AppTheme;
    }>({
        initFlyonUI: async ({}, use) => {
            const flyonUI = await import('flyonui/flyonui');
            window.HSStaticMethods.autoInit();
            await use(flyonUI);
        },
        // TBD: should this be a mock?
        setThemeStore: async ({}, use) => {
            const previousTheme = get(themeStore);

            const error = argbFromHex('#B3261E');
            const onError = argbFromHex('#FFFFFF');
            const defaultThemeStoreValue = {
                currentMode: 'light',
                light: {
                    colors: {
                        error,
                        onError
                    }
                } as AppTheme['light'],
                dark: {
                    colors: {
                        error,
                        onError
                    }
                } as AppTheme['dark'],
                configuration: {} as AppTheme['configuration']
            } as AppTheme;
            themeStore.set(defaultThemeStoreValue);
            await use(defaultThemeStoreValue);
            themeStore.set(previousTheme);
        }
    }
);