import {
	SchemeMonochrome,
	SchemeNeutral,
	SchemeTonalSpot,
	SchemeVibrant,
	SchemeExpressive,
	SchemeFidelity,
	SchemeContent,
	SchemeRainbow,
	SchemeFruitSalad,
	argbFromHex,
	Hct,
	customColor,
	TonalPalette,
	DynamicColor,
	type DynamicScheme,
	type ColorGroup,
	hexFromArgb
} from '@material/material-color-utilities';
import { ContrastCurve } from '../dependencies/material-color-utilities/0.3.0/contrast_curve';
import { ToneDeltaPair } from '../dependencies/material-color-utilities/0.3.0/tone_delta_pair';
import flyonUIThemes from 'flyonui/src/theming/themes';
// TBD: is there even a difference between the light and dark version?
// No, not for what it's used here.
// const { light: lightFlyonUI, dark: darkFlyonUI } = flyonUIThemes;
const { dark: darkFlyonUI } = flyonUIThemes;
import Color from 'colorjs.io';

export enum Variant {
	MONOCHROME = 'Monochrome',
	NEUTRAL = 'Neutral',
	TONAL_SPOT = 'Tonal spot',
	VIBRANT = 'Vibrant',
	EXPRESSIVE = 'Expressive',
	FIDELITY = 'Fidelity',
	CONTENT = 'Content',
	RAINBOW = 'Rainbow',
	FRUIT_SALAD = 'Fruit salad'
}

// these are all the fixed colors from the DynamicScheme:
// const materialDesignColorCSSTokens= [
//     "primary", "on-primary", "primary-container", "on-primary-container",
//     "secondary", "on-secondary", "secondary-container", "on-secondary-container",
//     "tertiary", "on-tertiary", "tertiary-container", "on-tertiary-container",
//     "error", "on-error", "error-container", "on-error-container",
//     "primary-fixed", "primary-fixed-dim", "on-primary-fixed", "on-primary-fixed-variant", // avoid using those
//     "secondary-fixed", "secondary-fixed-dim", "on-secondary-fixed", "on-secondary-fixed-variant", // avoid using those
//     "tertiary-fixed", "tertiary-fixed-dim", "on-tertiary-fixed", "on-tertiary-fixed-variant", // avoid using those
//     "surface-container-lowest", "surface-container-low", "surface-container", "surface-container-high", "surface-container-highest",
//     "surface-dim", "surface", "surface-bright", // avoid using those
//     "on-surface", "on-surface-variant",
//     "outline", "outline-variant",
//     "inverse-surface", "inverse-on-surface", "inverse-primary",
//     "scrim", "shadow",
//     "neutral-palette-key-color", "neutral-variant-palette-key-color", // might be useful for mapping with FlyonUI
//     "primary-palette-key-color", "secondary-palette-key-color", "tertiary-palette-key-color", "error-palette-key-color", // avoid using those
//     "background", "on-background", // seems to be legacy
// ]
// these are all the fixed colors from the DynamicScheme:
/* prettier-ignore */
const materialDesignColors = [
    "primary", "onPrimary", "primaryContainer", "onPrimaryContainer", 
    "secondary", "onSecondary", "secondaryContainer", "onSecondaryContainer",
    "tertiary", "onTertiary", "tertiaryContainer", "onTertiaryContainer",
    "error", "onError", "errorContainer", "onErrorContainer",
    "primaryFixed", "primaryFixedDim", "onPrimaryFixed", "onPrimaryFixedVariant", // avoid using those
    "secondaryFixed", "secondaryFixedDim", "onSecondaryFixed", "onSecondaryFixedVariant", // avoid using those
    "tertiaryFixed", "tertiaryFixedDim", "onTertiaryFixed", "onTertiaryFixedVariant", // avoid using those
    "surfaceContainerLowest", "surfaceContainerLow", "surfaceContainer", "surfaceContainerHigh", "surfaceContainerHighest",
    "surfaceDim", "surface", "surfaceBright", "surfaceVariant", "surfaceTint", // avoid using those
    "onSurface", "onSurfaceVariant",
    "outline", "outlineVariant",
    "inverseSurface", "inverseOnSurface", "inversePrimary",
    "scrim", "shadow",
    "neutralPaletteKeyColor", "neutralVariantPaletteKeyColor", // might be useful for mapping with FlyonUI
    "primaryPaletteKeyColor", "secondaryPaletteKeyColor", "tertiaryPaletteKeyColor",// missing in DynamicScheme: "errorPaletteKeyColor", // avoid using those
    "background", "onBackground", // seems to be legacy
] as const;
// const materialDesignColors = materialDesignColorCSSTokens.map(token => token.replace(/-([a-z])/g, (g) => g[1].toUpperCase())) as unknown as readonly string[];
// console.log("=== lib - theming - materialDesignColorCamelCaseTokens ===");
// console.log(materialDesignColors);

// these are all the palettes with fixed hue anc chrome but varying tone from the DynamicScheme:
// const materialDesignPalettes = [
// 	'primaryPalette',
// 	'secondaryPalette',
// 	'tertiaryPalette',
// 	'errorPalette',
// 	'neutralPalette',
// 	'neutralVariantPalette'
// ] as const;

type MaterialDesignColor = Record<(typeof materialDesignColors)[number], number>;
// type MaterialDesignPalette = Record<(typeof materialDesignPalettes)[number], TonalPalette>;
type MaterialDesignPalette = {
	primaryPalette: TonalPalette;
	secondaryPalette: TonalPalette;
	tertiaryPalette: TonalPalette;
	errorPalette: TonalPalette;
	neutralPalette: TonalPalette;
	neutralVariantPalette: TonalPalette;
};
type MaterialDesignMeta = {
	contrastLevel: string | number;
	isDark: boolean;
	sourceColorArgb: number;
	sourceColorHct: Hct;
	variant: number;
};

type MaterialDesignScheme = {
	colors: MaterialDesignColor;
	palettes: MaterialDesignPalette;
	meta: MaterialDesignMeta;
};
//  MaterialDesignColor & MaterialDesignPalette & MaterialDesignMeta;

// interface MaterialDesignScheme {
// type MaterialDesignScheme = {
// Record<typeof materialDesignColorCamelCaseTokens[number], number>;
// Record<typeof materialDesignPalettes[number], TonalPalette> &
// [K in typeof materialDesignColorCamelCaseTokens[number]]: number;
// } & {
//     [K in typeof materialDesignPalettes[number]]: TonalPalette;
// } & {
// [K in typeof materialDesignPalettes[number]]: TonalPalette } & {
//     // ...MaterialDesignPalette
//     // MaterialDesignColor: number;
//     // primaryPalette: TonalPalette;
//     // secondaryPalette: TonalPalette;
//     // tertiaryPalette: TonalPalette;
//     // errorPalette: TonalPalette;
//     // neutralPalette: TonalPalette;
//     // neutralVariantPalette: TonalPalette;
//     contrastLevel: string;
//     isDark: boolean;
//     sourceColorArgb: number;
//     sourceColorHct: Hct;
//     variant: number;
// }

// const sampleMaterialDesignScheme: MaterialDesignScheme = {
//     // Fill in with sample data
//     primary: 0,
//     onPrimary: 0,
//     primaryContainer: 0,
//     onPrimaryContainer: 0,
//     secondary: 0,
//     onSecondary: 0,
//     secondaryContainer: 0,
//     onSecondaryContainer: 0,
//     tertiary: 0,
//     onTertiary: 0,
//     tertiaryContainer: 0,
//     onTertiaryContainer: 0,
//     error: 0,
//     onError: 0,
//     errorContainer: 0,
//     onErrorContainer: 0,
//     primaryFixed: 0,
//     primaryFixedDim: 0,
//     onPrimaryFixed: 0,
//     onPrimaryFixedVariant: 0,
//     secondaryFixed: 0,
//     secondaryFixedDim: 0,
//     onSecondaryFixed: 0,
//     onSecondaryFixedVariant: 0,
//     tertiaryFixed: 0,
//     tertiaryFixedDim: 0,
//     onTertiaryFixed: 0,
//     onTertiaryFixedVariant: 0,
//     surfaceContainerLowest: 0,
//     surfaceContainerLow: 0,
//     surfaceContainer: 0,
//     surfaceContainerHigh: 0,
//     surfaceContainerHighest: 0,
//     surfaceDim: 0,
//     surface: 0,
//     surfaceBright: 0,
//     onSurface: 0,
//     onSurfaceVariant: 0,
//     outline: 0,
//     outlineVariant: 0,
//     inverseSurface: 0,
//     inverseOnSurface: 0,
//     inversePrimary: 0,
//     scrim: 0,
//     shadow: 0,
//     neutralPaletteKeyColor: 0,
//     neutralVariantPaletteKeyColor: 0,
//     primaryPaletteKeyColor: 0,
//     secondaryPaletteKeyColor: 0,
//     tertiaryPaletteKeyColor: 0,
//     // errorPaletteKeyColor: 0,
//     background: 0,
//     onBackground: 0,
//     primaryPalette: {} as TonalPalette,
//     secondaryPalette: {} as TonalPalette,
//     tertiaryPalette: {} as TonalPalette,
//     errorPalette: {} as TonalPalette,
//     neutralPalette: {} as TonalPalette,
//     neutralVariantPalette: {} as TonalPalette,
//     contrastLevel: "0",
//     isDark: true,
//     sourceColorArgb: 0,
//     sourceColorHct: Hct.fromInt(0),
//     variant: 0,
// }
// console.log("=== lib - theming - sampleMaterialDesignScheme ===");
// console.log(sampleMaterialDesignScheme);

type CustomColors = {
	light: {
		colors: ColorGroup;
		palette: TonalPalette;
		// color: number;
		// onColor: number;
		// colorContainer: number;
		// onColorContainer: number;
		// colorPalette: TonalPalette
	};
	dark: {
		colors: ColorGroup;
		palette: TonalPalette;
		// color: number;
		// onColor: number;
		// colorContainer: number;
		// onColorContainer: number;
		// colorPalette: TonalPalette
	};
};

const additionalFlyonUIColors = ['neutral', 'info', 'success', 'warning'] as const;
const additionalFlyonUIColorsOn = additionalFlyonUIColors.map(
	(color) => `on${color.charAt(0).toUpperCase() + color.slice(1)}` as const
);
const additionalFlyonUIColorsContainer = additionalFlyonUIColors.map(
	(color) => `${color}Container` as const
);
const additionalFlyonUIColorsOnContainer = additionalFlyonUIColors.map(
	(color) => `on${color.charAt(0).toUpperCase() + color.slice(1)}Container` as const
);
/* eslint-disable @typescript-eslint/no-unused-vars */
const additionalFlyonUIColorsPalette = additionalFlyonUIColors.map(
	(color) => `${color}Palette` as const
);
/* eslint-enable @typescript-eslint/no-unused-vars */
const additionalFlyonUIColorsAll = [
	...additionalFlyonUIColors,
	...additionalFlyonUIColorsOn,
	...additionalFlyonUIColorsContainer,
	...additionalFlyonUIColorsOnContainer
];
type AdditionalFlyonUIColors = Record<(typeof additionalFlyonUIColors)[number], number>;
type AdditionalFlyonUIColorsOn = Record<(typeof additionalFlyonUIColorsOn)[number], number>;
type AdditionalFlyonUIColorsContainer = Record<
	(typeof additionalFlyonUIColorsContainer)[number],
	number
>;
type AdditionalFlyonUIColorsOnContainer = Record<
	(typeof additionalFlyonUIColorsOnContainer)[number],
	number
>;
type AdditionalFlyonUIColorsPalette = Record<
	(typeof additionalFlyonUIColorsPalette)[number],
	TonalPalette
>;
// type AdditionalFlyonUIColors = typeof additionalFlyonUIColors[number]; // creates a union type
type AdditionalFlyonUIScheme = {
	colors: AdditionalFlyonUIColors &
		AdditionalFlyonUIColorsOn &
		AdditionalFlyonUIColorsContainer &
		AdditionalFlyonUIColorsOnContainer;
	palettes: AdditionalFlyonUIColorsPalette;
};
// AdditionalFlyonUIColors &
// AdditionalFlyonUIColorsOn &
// AdditionalFlyonUIColorsContainer &
// AdditionalFlyonUIColorsOnContainer &
// AdditionalFlyonUIColorsPalette;

// TBD: check how to do all the containers programmatically for providing the container classes (extensions of FlyonUI to match Material Design)
// TBD: Map matched colors to both class names, e.g. onPrimary primary-container becomes a class definition of ".on-primary, .primary-container"
// Material design tokens become FlyonUI variables (both technically CSS variables)
const flyonUIVariablesMaterialDesignMapping = new Map([
	// default FlyonUI tokens:
	['primary', 'p'],
	['onPrimary', 'pc'],
	['secondary', 's'],
	['onSecondary', 'sc'],
	['tertiary', 'a'], // accent
	['onTertiary', 'ac'],
	['neutral', 'n'],
	['onNeutral', 'nc'],
	['info', 'in'],
	['onInfo', 'inc'],
	['success', 'su'],
	['onSuccess', 'suc'],
	['warning', 'wa'],
	['onWarning', 'wac'],
	['error', 'er'],
	['onError', 'erc'],
	['surfaceContainerLowest', 'b1'],
	['surfaceContainer', 'b2'],
	['surfaceContainerHighest', 'b3'],
	['onSurface', 'bc'],
	['shadow', 'bs'],
	// extension from material design to flyonUI:
	// Foreground extensions:
	['primaryContainer', 'pcontainer'],
	['onPrimaryContainer', 'pcontainercontent'],
	['secondaryContainer', 'scontainer'],
	['onSecondaryContainer', 'scontainercontent'],
	// Background and other extensions:
	['inversePrimary', 'ip'],
	['surfaceTint', 'st'],
	// TBD: add tertiary -> accent, netral, info, success, warning, error containers
	// Avoid using those colors:
	['primaryFixed', 'pf'],
	['primaryFixedDim', 'pfdim'],
	['onPrimaryFixed', 'pfcontent'],
	['onPrimaryFixedVariant', 'pfvariantcontent'],
	['secondaryFixed', 'sf'],
	['secondaryFixedDim', 'sfdim'],
	['onSecondaryFixed', 'sfcontent'],
	['onSecondaryFixedVariant', 'sfvariantcontent'],
	['tertiaryFixed', 'af'],
	['tertiaryFixedDim', 'afdim'],
	['onTertiaryFixed', 'afcontent'],
	['onTertiaryFixedVariant', 'afvariantcontent']
]);

// add missing material design tokens as utility classes for flyonUI
// with both material design and flyonUI syntax:
export const extendingFlyonUIwithAdditionalMaterialDesignColors = new Map([
	['primaryContainer', 'primary-container'],
	['onPrimaryContainer', 'primary-container-content'],
	['secondaryContainer', 'secondary-container'],
	['onSecondaryContainer', 'secondary-container-content'],
	['tertiaryContainer', 'accent-container'],
	['onTertiaryContainer', 'accent-container-content'],
	['neutralContainer', 'neutral-container'],
	['onNeutralContainer', 'neutral-container-content'],
	['errorContainer', 'error-container'],
	['onErrorContainer', 'error-container-content'],
	['warningContainer', 'warning-container'],
	['onWarningContainer', 'warning-container-content'],
	['successContainer', 'success-container'],
	['onSuccessContainer', 'success-container-content'],
	['infoContainer', 'info-container'],
	['onInfoContainer', 'info-container-content'],
	['surfaceContainerLow', 'base-50'],
	['surfaceContainerHigh', 'base-150'],
	['outline', 'outline'],
	['outlineVariant', 'outline-variant'],
	['inverseSurface', 'inverse-surface'],
	['inverseOnSurface', 'inverse-surface-content'],
	['inversePrimary', 'inverse-primary'],
	['scrim', 'scrim'],
	['background', 'background'],
	['onBackground', 'background-content'],
	['neutralPaletteKeyColor', 'neutral-palette-key-color'],
	['neutralVariantPaletteKeyColor', 'neutral-variant-palette-key-color'],
	['primaryPaletteKeyColor', 'primary-palette-key-color'],
	['secondaryPaletteKeyColor', 'secondary-palette-key-color'],
	['tertiaryPaletteKeyColor', 'accent-palette-key-color'],
	['primaryFixed', 'primary-fixed'],
	['primaryFixedDim', 'primary-fixed-dim'],
	['onPrimaryFixed', 'primary-fixed-content'],
	['onPrimaryFixedVariant', 'primary-fixed-variant-content'],
	['secondaryFixed', 'secondary-fixed'],
	['secondaryFixedDim', 'secondary-fixed-dim'],
	['onSecondaryFixed', 'secondary-fixed-content'],
	['onSecondaryFixedVariant', 'secondary-fixed-variant-content'],
	['tertiaryFixed', 'accent-fixed'],
	['tertiaryFixedDim', 'accent-fixed-dim'],
	['onTertiaryFixed', 'accent-fixed-content'],
	['onTertiaryFixedVariant', 'accent-fixed-variant-content'],
	['surfaceDim', 'surface-dim'],
	['surface', 'surface'],
	['surfaceBright', 'surface-bright'],
	['surfaceVariant', 'surface-variant'],
	['surfaceTint', 'surface-tint']
]);

export interface ColorConfig {
	sourceColor: string;
	variant: Variant;
	contrast: number;
}

// interface AppColorSchemeForMode extends DynamicScheme {
//     // note: neutralPalette and neutralVariantPalette already exist in DynamicScheme!
//     // TBD: decide wether to use tehe neutral colors from Material or from FlyonUI!
//     readonly neutralPalette: TonalPalette;
//     readonly infoPalette: TonalPalette;
//     readonly successPalette: TonalPalette;
//     readonly warningPalette: TonalPalette;
//     get neutral(): number
//     get onNeutral(): number
//     get neutralContainer(): number
//     get onNeutralContainer(): number
//     get info(): number
//     get onInfo(): number
//     get infoContainer(): number
//     get onInfoContainer(): number
//     get success(): number
//     get onSuccess(): number
//     get successContainer(): number
//     get onSuccessContainer(): number
//     get warning(): number
//     get onWarning(): number
//     get warningContainer(): number
//     get onWarningContainer(): number
// }

export const appColors = [...materialDesignColors, ...additionalFlyonUIColorsAll] as const;
type AppColorSchemeForMode = MaterialDesignScheme & AdditionalFlyonUIScheme;

// const sampleAppColorSchemeForMode: AppColorSchemeForMode = {
//     // Fill in with sample data
//     primary: 0,
//     onPrimary: 0,
//     primaryContainer: 0,
//     onPrimaryContainer: 0,
//     secondary: 0,
//     onSecondary: 0,
//     secondaryContainer: 0,
//     onSecondaryContainer: 0,
//     tertiary: 0,
//     onTertiary: 0,
//     tertiaryContainer: 0,
//     onTertiaryContainer: 0,
//     error: 0,
//     onError: 0,
//     errorContainer: 0,
//     onErrorContainer: 0,
//     primaryFixed: 0,
//     primaryFixedDim: 0,
//     onPrimaryFixed: 0,
//     onPrimaryFixedVariant: 0,
//     secondaryFixed: 0,
//     secondaryFixedDim: 0,
//     onSecondaryFixed: 0,
//     onSecondaryFixedVariant: 0,
//     tertiaryFixed: 0,
//     tertiaryFixedDim: 0,
//     onTertiaryFixed: 0,
//     onTertiaryFixedVariant: 0,
//     surfaceContainerLowest: 0,
//     surfaceContainerLow: 0,
//     surfaceContainer: 0,
//     surfaceContainerHigh: 0,
//     surfaceContainerHighest: 0,
//     surfaceDim: 0,
//     surface: 0,
//     surfaceBright: 0,
//     onSurface: 0,
//     onSurfaceVariant: 0,
//     outline: 0,
//     outlineVariant: 0,
//     inverseSurface: 0,
//     inverseOnSurface: 0,
//     inversePrimary: 0,
//     scrim: 0,
//     shadow: 0,
//     neutralPaletteKeyColor: 0,
//     neutralVariantPaletteKeyColor: 0,
//     primaryPaletteKeyColor: 0,
//     secondaryPaletteKeyColor: 0,
//     tertiaryPaletteKeyColor: 0,
//     // errorPaletteKeyColor: 0,
//     background: 0,
//     onBackground: 0,
//     primaryPalette: {} as TonalPalette,
//     secondaryPalette: {} as TonalPalette,
//     tertiaryPalette: {} as TonalPalette,
//     errorPalette: {} as TonalPalette,
//     neutralPalette: {} as TonalPalette,
//     neutralVariantPalette: {} as TonalPalette,
//     contrastLevel: '',
//     isDark: false,
//     sourceColorArgb: 0,
//     sourceColorHct: {} as Hct,
//     variant: 0,
//     neutral: 0,
//     onNeutral: 0,
//     neutralContainer: 0,
//     onNeutralContainer: 0,
//     info: 0,
//     onInfo: 0,
//     infoContainer: 0,
//     onInfoContainer: 0,
//     success: 0,
//     onSuccess: 0,
//     successContainer: 0,
//     onSuccessContainer: 0,
//     warning: 0,
//     onWarning: 0,
//     warningContainer: 0,
//     onWarningContainer: 0,
//     infoPalette: {} as TonalPalette,
//     successPalette: {} as TonalPalette,
//     warningPalette: {} as TonalPalette,
// };

// console.log("=== lib - theming - sampleAppColorSchemeForMode ===");
// console.log(sampleAppColorSchemeForMode);

export interface AppColors {
	light: AppColorSchemeForMode;
	dark: AppColorSchemeForMode;
}

export interface AppTheme {
	configuration: ColorConfig;
	currentMode: 'light' | 'dark';
	light: AppColorSchemeForMode;
	dark: AppColorSchemeForMode;
	// fonts: AppFonts;
	// styles: AppStyles;
}

class Colorization {
	sourceColor: {
		hex: string;
		argb: number;
		hct: Hct;
	};
	variant: Variant;
	contrast: number;
	isFidelity: boolean = false;
	isMonochrome: boolean = false;

	constructor(sourceColorHex: string, variant: Variant, contrast: number) {
		this.sourceColor = {
			hex: sourceColorHex,
			argb: argbFromHex(sourceColorHex),
			hct: Hct.fromInt(argbFromHex(sourceColorHex))
		};
		this.variant = variant;
		this.contrast = contrast;
		this.isFidelity = variant === Variant.FIDELITY || variant === Variant.CONTENT;
		this.isMonochrome = variant === Variant.MONOCHROME;
	}

	private createMaterialSchemes(
		sourceColor: Hct = this.sourceColor.hct,
		variant: Variant = this.variant,
		contrast: number = this.contrast
	): { light: DynamicScheme; dark: DynamicScheme } {
		let lightScheme: DynamicScheme;
		let darkScheme: DynamicScheme;
		switch (variant) {
			case Variant.MONOCHROME:
				lightScheme = new SchemeMonochrome(sourceColor, false, contrast);
				darkScheme = new SchemeMonochrome(sourceColor, true, contrast);
				break;
			case Variant.NEUTRAL:
				lightScheme = new SchemeNeutral(sourceColor, false, contrast);
				darkScheme = new SchemeNeutral(sourceColor, true, contrast);
				break;
			case Variant.TONAL_SPOT:
				lightScheme = new SchemeTonalSpot(sourceColor, false, contrast);
				darkScheme = new SchemeTonalSpot(sourceColor, true, contrast);
				break;
			case Variant.VIBRANT:
				lightScheme = new SchemeVibrant(sourceColor, false, contrast);
				darkScheme = new SchemeVibrant(sourceColor, true, contrast);
				break;
			case Variant.EXPRESSIVE:
				lightScheme = new SchemeExpressive(sourceColor, false, contrast);
				darkScheme = new SchemeExpressive(sourceColor, true, contrast);
				break;
			case Variant.FIDELITY:
				lightScheme = new SchemeFidelity(sourceColor, false, contrast);
				darkScheme = new SchemeFidelity(sourceColor, true, contrast);
				break;
			case Variant.CONTENT:
				lightScheme = new SchemeContent(sourceColor, false, contrast);
				darkScheme = new SchemeContent(sourceColor, true, contrast);
				break;
			case Variant.RAINBOW:
				lightScheme = new SchemeRainbow(sourceColor, false, contrast);
				darkScheme = new SchemeRainbow(sourceColor, true, contrast);
				break;
			case Variant.FRUIT_SALAD:
				lightScheme = new SchemeFruitSalad(sourceColor, false, contrast);
				darkScheme = new SchemeFruitSalad(sourceColor, true, contrast);
				break;
			default:
				throw new Error('Unsupported variant');
		}
		return { light: lightScheme, dark: darkScheme };
	}

	// Color: #a6ff00; variant: content & fidelity; contrast: 0 is buggy
	private createCustomColors(color: string, colorName: string): CustomColors {
		const colorNameCapitalized = colorName.charAt(0).toUpperCase() + colorName.slice(1);
		// mixing with the primary color of the app scheme:
		// TBD: consider creating warning and success as a fixed tonal palette
		// with TonalPalette.fromHueAndChrome(hue, chroma) - error has parameters 25, 84!
		// potentially fix to yellow-ish and greeen-ish color?
		const colorGroup = customColor(this.sourceColor.argb, {
			value: argbFromHex(color),
			name: colorName,
			blend: true
		});
		const customColorHct = {
			light: Hct.fromInt(colorGroup.light.color),
			dark: Hct.fromInt(colorGroup.dark.color)
		};
		// using the mixed color as input:
		const schemeLight = this.createMaterialSchemes(customColorHct.light).light;
		const schemeDark = this.createMaterialSchemes(customColorHct.dark).dark;
		// // using the input color as primary color - colors are pretty disconnected  - so don't use this:
		// const schemeLight = this.createMaterialSchemes(Hct.fromInt(argbFromHex(color))).light;
		// const schemeDark = this.createMaterialSchemes(Hct.fromInt(argbFromHex(color))).dark;

		const surfaceContainerHighestLight = DynamicColor.fromPalette({
			name: 'surfaceContainerHighestLight',
			palette: (schemeLight) => schemeLight.neutralPalette,
			tone: (schemeLight) => new ContrastCurve(90, 90, 84, 80).get(schemeLight.contrastLevel),
			isBackground: true
		});

		const customPrimaryLight = DynamicColor.fromPalette({
			name: colorName,
			palette: (schemeLight) => schemeLight.primaryPalette,
			tone: (_schemeLight) => (this.isMonochrome ? 0 : 40),
			// consider using options from primary instead of error"
			background: (_schemeLight) => surfaceContainerHighestLight, //MaterialDynamicColors.highestSurface(schemeLight),
			contrastCurve: new ContrastCurve(3, 4.5, 7, 7),
			toneDeltaPair: (_schemeLight) =>
				new ToneDeltaPair(customPrimaryContainerLight, customPrimaryLight, 10, 'nearer', false)
		});
		const customOnPrimaryLight = DynamicColor.fromPalette({
			name: `on${colorNameCapitalized}`,
			palette: (schemeLight) => schemeLight.primaryPalette,
			tone: (_schemeLight) => (this.isMonochrome ? 10 : 20),
			// consider using options from primary instead of error"
			background: (_schemeLight) => customPrimaryLight, //MaterialDynamicColors.primary,
			contrastCurve: new ContrastCurve(4.5, 7, 11, 21)
		});
		const customPrimaryContainerLight = DynamicColor.fromPalette({
			name: `${colorName}Container`,
			palette: (schemeLight) => schemeLight.primaryPalette,
			tone: (_schemeLight) =>
				this.isFidelity ? customColorHct.dark.tone : this.isMonochrome ? 25 : 90,
			isBackground: true,
			// consider using options from primary instead of error"
			background: (_schemeLight) => surfaceContainerHighestLight, // MaterialDynamicColors.highestSurface(schemeLight),
			contrastCurve: new ContrastCurve(1, 1, 3, 4.5),
			toneDeltaPair: (_schemeLight) =>
				new ToneDeltaPair(customPrimaryContainerLight, customPrimaryLight, 10, 'nearer', false)
		});
		const customOnPrimaryContainerLight = DynamicColor.fromPalette({
			name: `on${colorNameCapitalized}Container`,
			palette: (schemeLight) => schemeLight.primaryPalette,
			tone: (_schemeLight) =>
				this.isFidelity
					? DynamicColor.foregroundTone(customPrimaryContainerLight.tone(schemeLight), 4.5)
					: this.isMonochrome
						? 100
						: 30,
			// consider using options from primary instead of error"
			background: (_schemeLight) => customPrimaryContainerLight, //MaterialDynamicColors.primaryContainer,
			contrastCurve: new ContrastCurve(3, 4.5, 7, 11)
		});

		const surfaceContainerHighestDark = DynamicColor.fromPalette({
			name: 'surfaceContainerHighestDark',
			palette: (schemeDark) => schemeDark.neutralPalette,
			tone: (schemeDark) => new ContrastCurve(22, 22, 26, 30).get(schemeDark.contrastLevel), // for light: new ContrastCurve(90, 90, 84, 80).get(s.contrastLevel),
			isBackground: true
		});

		const customPrimaryDark = DynamicColor.fromPalette({
			name: colorName,
			palette: (schemeDark) => schemeDark.primaryPalette,
			tone: (_schemeDark) => (this.isMonochrome ? 100 : 80),
			// consider using options from primary instead of error"
			background: (_schemeDark) => surfaceContainerHighestDark, //MaterialDynamicColors.highestSurface(schemeDark),//
			contrastCurve: new ContrastCurve(3, 4.5, 7, 7),
			toneDeltaPair: (_schemeDark) =>
				new ToneDeltaPair(customPrimaryContainerDark, customPrimaryDark, 10, 'nearer', false)
		});
		const customOnPrimaryDark = DynamicColor.fromPalette({
			name: `on${colorName}`,
			palette: (schemeDark) => schemeDark.primaryPalette,
			tone: (_schemeDark) => (this.isMonochrome ? 90 : 100), // from error // consider making 90 in Monochrome!
			// consider using options from primary instead of error"
			background: (_schemeDark) => customPrimaryDark, // MaterialDynamicColors.primary,
			contrastCurve: new ContrastCurve(4.5, 7, 11, 21)
		});
		const customPrimaryContainerDark = DynamicColor.fromPalette({
			name: `${colorName}Container`,
			palette: (schemeDark) => schemeDark.primaryPalette,
			tone: (_schemeDark) =>
				this.isFidelity ? customColorHct.dark.tone : this.isMonochrome ? 85 : 30, // this.sourceColor.hct.tone,//
			isBackground: true,
			// consider using options from primary instead of error"
			background: (_schemeDark) => surfaceContainerHighestDark, //MaterialDynamicColors.highestSurface(schemeDark),//
			contrastCurve: new ContrastCurve(1, 1, 3, 4.5), // new ContrastCurve(1, 4.5, 7, 11),// new ContrastCurve(3, 4.5, 7, 7),
			toneDeltaPair: (_schemeDark) =>
				new ToneDeltaPair(customPrimaryContainerDark, customPrimaryDark, 10, 'nearer', false)
		});
		const customOnPrimaryContainerDark = DynamicColor.fromPalette({
			name: `on${colorNameCapitalized}Container`,
			palette: (schemeDark) => schemeDark.primaryPalette,
			// tone: (schemeDark) => this.isMonochrome ? 0 : 90,
			tone: (schemeDark) =>
				this.isFidelity
					? DynamicColor.foregroundTone(customPrimaryContainerDark.tone(schemeDark), 4.5)
					: this.isMonochrome
						? 0
						: 90,
			// consider using options from primary instead of error"
			background: (_schemeDark) => customPrimaryContainerDark, //MaterialDynamicColors.primaryContainer,
			contrastCurve: new ContrastCurve(3, 4.5, 7, 11)
		});
		// // before applying dynamic colors to custom colors:
		// const lightPalette = TonalPalette.fromInt(colorGroup.light.color);
		// const darkPalette = TonalPalette.fromInt(colorGroup.dark.color);
		// after applying dynamic colors to custom colors:
		const lightPalette = schemeLight.primaryPalette;
		const darkPalette = schemeDark.primaryPalette;
		const light = {
			/// / before applying dynamic colors to custom colors:
			// colors: colorGroup.light,
			colors: {
				color: customPrimaryLight.getArgb(schemeLight),
				onColor: customOnPrimaryLight.getArgb(schemeLight),
				colorContainer: customPrimaryContainerLight.getArgb(schemeLight),
				onColorContainer: customOnPrimaryContainerLight.getArgb(schemeLight)
			},
			palette: lightPalette
		};
		const dark = {
			// // before applying dynamic colors to custom colors:
			// colors: colorGroup.dark,
			colors: {
				color: customPrimaryDark.getArgb(schemeDark),
				onColor: customOnPrimaryDark.getArgb(schemeDark),
				colorContainer: customPrimaryContainerDark.getArgb(schemeDark),
				onColorContainer: customOnPrimaryContainerDark.getArgb(schemeDark)
			},
			palette: darkPalette
		};
		// light.colors.color = customPrimaryLight.getArgb(schemeLight);
		// dark.colors.color = customPrimaryDark.getArgb(schemeDark);
		// light.colors.onColor = customOnPrimaryLight.getArgb(schemeLight);
		// dark.colors.onColor = customOnPrimaryDark.getArgb(schemeDark);
		// light.colors.colorContainer = customPrimaryContainerLight.getArgb(schemeLight);
		// dark.colors.colorContainer = customPrimaryContainerDark.getArgb(schemeDark);
		// light.colors.onColorContainer = customOnPrimaryContainerLight.getArgb(schemeLight);
		// dark.colors.onColorContainer = customOnPrimaryContainerDark.getArgb(schemeDark);

		return {
			light: light,
			dark: dark
		};
	}

	public createAppColors(): AppColors {
		const { light: lightMaterial, dark: darkMaterial } = this.createMaterialSchemes();
		// those 4 colors are the same in lightFlyonUI and darkFlyonUI
		// so no need for two inputs here - the colors are differentiated by Material Design Dynamic Colors:
		const neutralFromFlyonUI = this.createCustomColors(darkFlyonUI.neutral, 'flyonui-neutral');
		const infoFromFlyonUI = this.createCustomColors(darkFlyonUI.info, 'flyonui-info');
		const successFromFlyonUI = this.createCustomColors(darkFlyonUI.success, 'flyonui-success');
		const warningFromFlyonUI = this.createCustomColors(darkFlyonUI.warning, 'flyonui-warning');
		let light: {
			colors: Partial<AppColorSchemeForMode['colors']>;
			palettes: Partial<AppColorSchemeForMode['palettes']>;
			meta: Partial<AppColorSchemeForMode['meta']>;
		} = { colors: {}, palettes: {}, meta: {} };
		let dark: {
			colors: Partial<AppColorSchemeForMode['colors']>;
			palettes: Partial<AppColorSchemeForMode['palettes']>;
			meta: Partial<AppColorSchemeForMode['meta']>;
		} = { colors: {}, palettes: {}, meta: {} };
		// Assigning the MaterialDesign colors first:
		materialDesignColors.forEach((token) => {
			const keyDynamicScheme = token as keyof DynamicScheme;
			light.colors[token] = lightMaterial[keyDynamicScheme] as number;
			dark.colors[token] = darkMaterial[keyDynamicScheme] as number;
		});
		// Adding the FlyonUI colors, palettes and meta data:
		light = {
			colors: {
				...light.colors,
				neutral: neutralFromFlyonUI.light.colors.color,
				onNeutral: neutralFromFlyonUI.light.colors.onColor,
				neutralContainer: neutralFromFlyonUI.light.colors.colorContainer,
				onNeutralContainer: neutralFromFlyonUI.light.colors.onColorContainer,
				info: infoFromFlyonUI.light.colors.color,
				onInfo: infoFromFlyonUI.light.colors.onColor,
				infoContainer: infoFromFlyonUI.light.colors.colorContainer,
				onInfoContainer: infoFromFlyonUI.light.colors.onColorContainer,
				success: successFromFlyonUI.light.colors.color,
				onSuccess: successFromFlyonUI.light.colors.onColor,
				successContainer: successFromFlyonUI.light.colors.colorContainer,
				onSuccessContainer: successFromFlyonUI.light.colors.onColorContainer,
				warning: warningFromFlyonUI.light.colors.color,
				onWarning: warningFromFlyonUI.light.colors.onColor,
				warningContainer: warningFromFlyonUI.light.colors.colorContainer,
				onWarningContainer: warningFromFlyonUI.light.colors.onColorContainer
			},
			palettes: {
				primaryPalette: lightMaterial.primaryPalette,
				secondaryPalette: lightMaterial.secondaryPalette,
				tertiaryPalette: lightMaterial.tertiaryPalette,
				// decide here which neutral palette to use, make sure colors gets the right one, too
				// neutralPalette: lightMaterial.neutralPalette,
				neutralVariantPalette: lightMaterial.neutralVariantPalette,
				errorPalette: lightMaterial.errorPalette,
				neutralPalette: neutralFromFlyonUI.light.palette,
				infoPalette: infoFromFlyonUI.light.palette,
				successPalette: successFromFlyonUI.light.palette,
				warningPalette: warningFromFlyonUI.light.palette
			},
			meta: {
				contrastLevel: lightMaterial.contrastLevel,
				isDark: lightMaterial.isDark,
				sourceColorArgb: lightMaterial.sourceColorArgb,
				sourceColorHct: lightMaterial.sourceColorHct,
				variant: lightMaterial.variant
			}
		};

		dark = {
			colors: {
				...dark.colors,
				neutral: neutralFromFlyonUI.dark.colors.color,
				onNeutral: neutralFromFlyonUI.dark.colors.onColor,
				neutralContainer: neutralFromFlyonUI.dark.colors.colorContainer,
				onNeutralContainer: neutralFromFlyonUI.dark.colors.onColorContainer,
				info: infoFromFlyonUI.dark.colors.color,
				onInfo: infoFromFlyonUI.dark.colors.onColor,
				infoContainer: infoFromFlyonUI.dark.colors.colorContainer,
				onInfoContainer: infoFromFlyonUI.dark.colors.onColorContainer,
				success: successFromFlyonUI.dark.colors.color,
				onSuccess: successFromFlyonUI.dark.colors.onColor,
				successContainer: successFromFlyonUI.dark.colors.colorContainer,
				onSuccessContainer: successFromFlyonUI.dark.colors.onColorContainer,
				warning: warningFromFlyonUI.dark.colors.color,
				onWarning: warningFromFlyonUI.dark.colors.onColor,
				warningContainer: warningFromFlyonUI.dark.colors.colorContainer,
				onWarningContainer: warningFromFlyonUI.dark.colors.onColorContainer
			},
			palettes: {
				primaryPalette: darkMaterial.primaryPalette,
				secondaryPalette: darkMaterial.secondaryPalette,
				tertiaryPalette: darkMaterial.tertiaryPalette,
				// decide here which neutral palette to use, make sure colors gets the right one, too
				// neutralPalette: darkMaterial.neutralPalette,
				neutralVariantPalette: darkMaterial.neutralVariantPalette,
				errorPalette: darkMaterial.errorPalette,
				neutralPalette: neutralFromFlyonUI.dark.palette,
				infoPalette: infoFromFlyonUI.dark.palette,
				successPalette: successFromFlyonUI.dark.palette,
				warningPalette: warningFromFlyonUI.dark.palette
			},
			meta: {
				contrastLevel: darkMaterial.contrastLevel,
				isDark: darkMaterial.isDark,
				sourceColorArgb: darkMaterial.sourceColorArgb,
				sourceColorHct: darkMaterial.sourceColorHct,
				variant: darkMaterial.variant
			}
		};

		return {
			light: light as AppColorSchemeForMode,
			dark: dark as AppColorSchemeForMode
		};
	}
}

// export interface StylingConfig {}

// class Styling {}

// export interface TypographyConfig {}

// class Typography {}

export class Theming {
	// colorConfiguration: ColorConfig;
	// stylingConfiguration: StylingConfig;
	// typographyConfiguration: TypographyConfig;

	// constructor(colorConfiguration: ColorConfig, stylingConfiguration: StylingConfig, typographyConfiguration: TypographyConfig) {
	//     this.colorConfiguration = colorConfiguration;
	//     this.stylingConfiguration = stylingConfiguration;
	//     this.typographyConfiguration = typographyConfiguration;
	// }
	// constructor(colorConfiguration: ColorConfig) {
	//     this.colorConfiguration = colorConfiguration
	// }
	constructor() {}

	// works:
	// public manipulateContrast(contrast: number): number {
	//     const tenFoldContrast = contrast * 10;
	//     console.log("=== lib - theming - Manipulating contrast - tenFoldContrast ===");
	//     console.log(tenFoldContrast);
	//     return tenFoldContrast
	// }

	// Note, where this is called, the document needs to be available
	// so don't call on server in server side rendering scenarios!
	public applyTheme(
		colorConfig: ColorConfig,
		mode: 'light' | 'dark',
		targetElement: HTMLElement = document.documentElement
	): AppTheme {
		const colorization = new Colorization(
			colorConfig.sourceColor,
			colorConfig.variant,
			colorConfig.contrast
		);
		const colorScheme = colorization.createAppColors();
		const colors = mode === 'dark' ? colorScheme.dark.colors : colorScheme.light.colors;
		this.applyMaterialTokens(colors, targetElement);
		this.applyFlyonUITokens(colors, targetElement);
		// Theming.addStyle(`.btn-inverse-primary`, [
		// 	// "--btn-color: var(--md-sys-color-inverse-primary);"
		// 	"--btn-color: #535a92;"
		// ]);
		// extendingFlyonUIwithAdditionalMaterialDesignColors.forEach(
		// 	(utilityClass, materialDesignToken) => {
		// 		// const tokenKebabCase = materialDesignToken.replace(/([a-z])([A-Z])/g, '$1-$2').toLowerCase();
		// 		const materialTokenKey = materialDesignToken as keyof typeof colors;
		// 		const colorHex = hexFromArgb(colors[materialTokenKey])
		// 		// TBD: consider using --tw-classes, wherever applicable to enable opacity and Tailwind CSS compatibility
		// 		Theming.addStyle(`.bg-${utilityClass}`, [
		// 			`background-color: ${colorHex};`
		// 		]);
		// 		Theming.addStyle(`.text-${utilityClass}`, [
		// 			`color: ${colorHex};`
		// 		]);

		// 		// TBD: consider applying variables instead of colors and don't reapply when the color is changed. only the variable changes!
		// 		// // remove - takes so much computation - add when needed:
		// 		// // TBD: check .ring
		// 		// Theming.addStyle(`.fill-${utilityClass}`, [
		// 		// 	`fill: ${colorHex};`
		// 		// ]);
		// 		// Theming.addStyle(`.caret-${utilityClass}`, [
		// 		// 	`caret-color: ${colorHex};`
		// 		// ]);
		// 		// Theming.addStyle(`.stroke-${utilityClass}`, [
		// 		// 	`stroke: ${colorHex};`
		// 		// ]);
		// 		// Theming.addStyle(`.border-${utilityClass}`, [
		// 		// 	`border-color: ${colorHex};`
		// 		// ]);
		// 		// Theming.addStyle(`.accent-${utilityClass}`, [
		// 		// 	`accent-color: ${colorHex};`
		// 		// ]);
		// 		// // TBD: check shadow!
		// 		// // TBD: check possibilities for applying opacity to those colors!
		// 		// Theming.addStyle(`.accent-${utilityClass}`, [
		// 		// 	`accent-color: ${colorHex};`
		// 		// ]);
		// 		// Theming.addStyle(`.decoration-${utilityClass}`, [
		// 		// 	`text-decoration-color: ${colorHex};`
		// 		// ]);

		// 		// TBD: causes trouble on all browsers on iPad
		// 		// Theming.addStyle(`.placeholder:text-${utilityClass}`, [
		// 		// 	`color: ${colorHex};`
		// 		// ]);
		// 		// TBD: check .ring-offset
		// 	}
		// );
		return {
			configuration: colorConfig,
			currentMode: mode,
			...colorScheme
		};
	}

	private static createStyleElementInDocument(styleElementId: string): HTMLStyleElement {
		let styleElement = document.getElementById(styleElementId) as HTMLStyleElement;
		if (!styleElement) {
			styleElement = document.createElement('style');
			styleElement.setAttribute('type', 'text/css');
			styleElement.setAttribute('id', styleElementId);
		}
		document.head.appendChild(styleElement);
		return styleElement;
	}

	static rgbFromHex = (hex: string) => {
		const hexValue = hex.replace('#', '');
		const r = parseInt(hexValue.substring(0, 2), 16);
		const g = parseInt(hexValue.substring(2, 4), 16);
		const b = parseInt(hexValue.substring(4, 6), 16);
		console.log(`Converted hex ${hex} to rgb ${r} ${g} ${b}`);
		return `${r} ${g} ${b}`;
	};

	private applyMaterialTokens(
		colors: AppColors['dark']['colors'] | AppColors['light']['colors'],
		targetElement: HTMLElement
	): void {
		if (targetElement === document.documentElement) {
			const styleElementId = 'md_sys_dynamic_color_tokens';
			let styles = '';
			console.log('=== lib - theming - applyMaterialTokens ===');
			appColors.forEach((token) => {
				const tokenKebabCase = token.replace(/([a-z])([A-Z])/g, '$1-$2').toLowerCase();
				styles += `--md-sys-color-${tokenKebabCase}: ${hexFromArgb(colors[token])};\n`;
				styles += `--md-rgb-color-${tokenKebabCase}: ${Theming.rgbFromHex(hexFromArgb(colors[token]))};\n`;
				// console.log(tokenKebabCase)
				// console.log(Theming.rgbFromHex(hexFromArgb(colors[token])))
			});
			const styleElement = Theming.createStyleElementInDocument(styleElementId);
			styleElement.textContent = `:root {\n${styles}}`;
			// document.head.appendChild(styleElement);
		} else {
			appColors.forEach((token) => {
				const tokenKebabCase = token.replace(/([a-z])([A-Z])/g, '$1-$2').toLowerCase();
				targetElement.style.setProperty(
					`--md-sys-color-${tokenKebabCase}`,
					hexFromArgb(colors[token])
				);
			});
		}
		targetElement.style.backgroundColor = hexFromArgb(colors['background']);
	}

	// consider moving to Colorization and add the instance of Colorization to the Theming class
	private oklchFromArgb(argbColor: number): string {
		const hctColor = Hct.fromInt(argbColor);
		const colorJs = new Color('hct', [hctColor.hue, hctColor.chroma, hctColor.tone]);
		return colorJs.to('oklch').coords.join(' ');
	}

	static addStyle(styleName: string, styles: string[]): void {
		const styleElement = Theming.createStyleElementInDocument('utility_classes');

		let rules = `${styleName} {\n`;
		styles.forEach((style) => {
			rules += `    ${style}\n`;
		});
		rules += '}';

		// check if pseudoelement :root already exists in styleElement
		const rootStartIndex = styleElement.textContent?.indexOf(':root {') ?? -1;
		const rootEndIndex = styleElement.textContent?.lastIndexOf('}') ?? -1;

		if (rootStartIndex !== -1 && rootEndIndex !== -1) {
			// Check if the rules already exist
			const rulesStartIndex = styleElement.textContent?.indexOf(rules);
			if (rulesStartIndex === -1) {
				// Insert styles before the closing }
				const beforeRoot = styleElement.textContent?.substring(0, rootEndIndex);
				const afterRoot = styleElement.textContent?.substring(rootEndIndex);
				styleElement.textContent = `${beforeRoot}\n${rules}\n${afterRoot}`;
			}
		} else {
			// If :root is not found, create it
			styleElement.textContent += `\n:root {\n${rules}\n}`;
		}
	}

	// static addBackgroundUtilityClass( name: string, backgroundColor: string[]): void {
	//     Theming.addStyle(`bg-${name}`, [`background-color: ${backgroundColor}`]);
	// }

	// static addFillUtilityClass( name: string, fill: string[]): void {
	//     Theming.addStyle(`fill-${name}`, [`fill: ${fill}`]);
	// }

	// TBD: might not be necessary any more, when refactored into Tailwind variables!
	private applyFlyonUITokens(
		colors: AppColors['dark']['colors'] | AppColors['light']['colors'],
		targetElement: HTMLElement
	): void {
		if (targetElement === document.documentElement) {
			const styleElementId = 'flyonUI_variables';
			let styles = '';
			// match tokens from material design to flyonUI tokens:
			flyonUIVariablesMaterialDesignMapping.forEach((flyonUIVariable, materialDesignToken) => {
				const materialTokenKey = materialDesignToken as keyof typeof colors;
				const oklchColor = this.oklchFromArgb(colors[materialTokenKey]);
				styles += `--${flyonUIVariable}: ${oklchColor};\n`;
				// styles += `.bg-${materialDesignToken} {background-color: ${hexFromArgb(colors[materialTokenKey])}};\n`;
				// styles += `.text-${materialDesignToken} {color: ${hexFromArgb(colors[materialTokenKey])}};\n`;
			});
			const styleElement = Theming.createStyleElementInDocument(styleElementId);
			styleElement.textContent = `:root {\n${styles}}`;
			// document.head.appendChild(styleElement);
		} else {
			flyonUIVariablesMaterialDesignMapping.forEach((flyonUIVariable, materialDesignToken) => {
				const oklchColor = this.oklchFromArgb(colors[materialDesignToken as keyof typeof colors]);
				targetElement.style.setProperty(`--${flyonUIVariable}`, oklchColor);
				// TBD: also set the classes as property on the targetElement?
			});
		}
	}
}
