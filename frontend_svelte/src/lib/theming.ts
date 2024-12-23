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
    type DynamicScheme,
    type ColorGroup,
    hexFromArgb,
} from "@material/material-color-utilities";
import flyonUIThemes from 'flyonui/src/theming/themes';
const { light: lightFlyonUI, dark: darkFlyonUI } = flyonUIThemes;

export enum Variant {
    MONOCHROME = "Monochrome",
    NEUTRAL = "Neutral",
    TONAL_SPOT = "Tonal spot",
    VIBRANT = "Vibrant",
    EXPRESSIVE = "Expressive",
    FIDELITY = "Fidelity",
    CONTENT = "Content",
    RAINBOW = "Rainbow",
    FRUIT_SALAD = "Fruit salad",
    }

// these are all the fixed colors from the DynamicScheme:
/* eslint-disable */
/* prettier-ignore */
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
const materialDesignColors = [
    "primary", "onPrimary", "primaryContainer", "onPrimaryContainer", 
    "secondary", "onSecondary", "secondaryContainer", "onSecondaryContainer",
    "tertiary", "onTertiary", "tertiaryContainer", "onTertiaryContainer",
    "error", "onError", "errorContainer", "onErrorContainer",
    "primaryFixed", "primaryFixedDim", "onPrimaryFixed", "onPrimaryFixedVariant", // avoid using those
    "secondaryFixed", "secondaryFixedDim", "onSecondaryFixed", "onSecondaryFixedVariant", // avoid using those
    "tertiaryFixed", "tertiaryFixedDim", "onTertiaryFixed", "onTertiaryFixedVariant", // avoid using those
    "surfaceContainerLowest", "surfaceContainerLow", "surfaceContainer", "surfaceContainerHigh", "surfaceContainerHighest",
    "surfaceDim", "surface", "surfaceBright", // avoid using those
    "onSurface", "onSurfaceVariant",
    "outline", "outlineVariant",
    "inverseSurface", "inverseOnSurface", "inversePrimary",
    "scrim", "shadow",
    "neutralPaletteKeyColor", "neutralVariantPaletteKeyColor", // might be useful for mapping with FlyonUI
    "primaryPaletteKeyColor", "secondaryPaletteKeyColor", "tertiaryPaletteKeyColor",// missing in DynamicScheme: "errorPaletteKeyColor", // avoid using those
    "background", "onBackground", // seems to be legacy
] as const;
/* eslint enable */
// const materialDesignColors = materialDesignColorCSSTokens.map(token => token.replace(/-([a-z])/g, (g) => g[1].toUpperCase())) as unknown as readonly string[];
// console.log("=== lib - theming - materialDesignColorCamelCaseTokens ===");
// console.log(materialDesignColors);


// these are all the palettes with fixed hue anc chrome but varying tone from the DynamicScheme:
const materialDesignPalettes = [
    "primaryPalette", "secondaryPalette", "tertiaryPalette", "errorPalette", "neutralPalette", "neutralVariantPalette"
] as const;

type MaterialDesignColor = Record<typeof materialDesignColors[number], number>;
type MaterialDesignPalette = Record<typeof materialDesignPalettes[number], TonalPalette>;
type MaterialDesignMeta = {
    contrastLevel: string | number;
    isDark: boolean;
    sourceColorArgb: number;
    sourceColorHct: Hct;
    variant: number;
}

type MaterialDesignScheme = {
    colors: MaterialDesignColor;
    palettes: MaterialDesignPalette;
    meta: MaterialDesignMeta;
}
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
        colors: ColorGroup
        palette: TonalPalette
        // color: number;
        // onColor: number;
        // colorContainer: number;
        // onColorContainer: number;
        // colorPalette: TonalPalette
    },
    dark: {
        colors: ColorGroup
        palette: TonalPalette
        // color: number;
        // onColor: number;
        // colorContainer: number;
        // onColorContainer: number;
        // colorPalette: TonalPalette
    },
}


const additionalFlyonUIColors = [ "neutral", "info", "success", "warning" ] as const;
const additionalFlyonUIColorsOn = additionalFlyonUIColors.map(color => `on${color.charAt(0).toUpperCase() + color.slice(1)}` as const);
const additionalFlyonUIColorsContainer = additionalFlyonUIColors.map(color => `${color}Container` as const);
const additionalFlyonUIColorsOnContainer = additionalFlyonUIColors.map(color => `on${color.charAt(0).toUpperCase() + color.slice(1)}Container` as const);
const additionalFlyonUIColorsPalette = additionalFlyonUIColors.map(color => `${color}Palette` as const);
const additionalFlyonUIColorsAll = [
    ...additionalFlyonUIColors,
    ...additionalFlyonUIColorsOn,
    ...additionalFlyonUIColorsContainer,
    ...additionalFlyonUIColorsOnContainer
];
type AdditionalFlyonUIColors = Record<typeof additionalFlyonUIColors[number], number>;
type AdditionalFlyonUIColorsOn = Record<typeof additionalFlyonUIColorsOn[number], number>;
type AdditionalFlyonUIColorsContainer = Record<typeof additionalFlyonUIColorsContainer[number], number>;
type AdditionalFlyonUIColorsOnContainer = Record<typeof additionalFlyonUIColorsOnContainer[number], number>;
type AdditionalFlyonUIColorsPalette = Record<typeof additionalFlyonUIColorsPalette[number], TonalPalette>;
// type AdditionalFlyonUIColors = typeof additionalFlyonUIColors[number]; // creates a union type
type AdditionalFlyonUIScheme = {
    colors: AdditionalFlyonUIColors & AdditionalFlyonUIColorsOn & AdditionalFlyonUIColorsContainer & AdditionalFlyonUIColorsOnContainer;
    palettes: AdditionalFlyonUIColorsPalette;
}
    // AdditionalFlyonUIColors &
    // AdditionalFlyonUIColorsOn &
    // AdditionalFlyonUIColorsContainer &
    // AdditionalFlyonUIColorsOnContainer &
    // AdditionalFlyonUIColorsPalette;


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

export const appColorNames = [ ...materialDesignColors, ...additionalFlyonUIColorsAll ] as const;
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

class Colorization {
    sourceColor: string;
    variant: Variant;
    contrast: number;

    constructor(sourceColor: string, variant: Variant, contrast: number) {
        this.sourceColor = sourceColor;
        this.variant = variant;
        this.contrast = contrast;
    }

    private createMaterialSchemes( sourceColor: Hct, variant: Variant, contrast: number): { light: DynamicScheme, dark: DynamicScheme } {
        let lightScheme: DynamicScheme;
        let darkScheme: DynamicScheme;
        switch (variant) {
            case Variant.MONOCHROME:
                lightScheme = new SchemeMonochrome(sourceColor, false, contrast);
                darkScheme = new SchemeMonochrome(sourceColor, true, contrast);
                break
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
                throw new Error("Unsupported variant");
        }
        return { light: lightScheme, dark: darkScheme };
    }

    private createCustomColors( sourceColor: number, flyonUIcolor: string, colorName: string): CustomColors {
        const colorGroup = customColor(sourceColor, {value: argbFromHex(flyonUIcolor), name: colorName, blend: true});
        const lightPalette = TonalPalette.fromInt(colorGroup.light.color);
        const darkPalette = TonalPalette.fromInt(colorGroup.dark.color);
        const light = {
            colors: colorGroup.light,
            palette: lightPalette
        }
        const dark = {
            colors: colorGroup.dark,
            palette: darkPalette
        }

        return {
            light: light,
            dark: dark,
        }
    }

    public createAppColors( colorConfig: ColorConfig):  AppColors {
        const sourceColorArgb = argbFromHex(colorConfig.sourceColor);
        const sourceColorHct = Hct.fromInt(sourceColorArgb);
        const { light: lightMaterial, dark: darkMaterial } = this.createMaterialSchemes(sourceColorHct, colorConfig.variant, colorConfig.contrast);
        const neutralFromFlyonUI = this.createCustomColors(sourceColorArgb, lightFlyonUI.neutral, 'flyonui-neutral');
        const infoFromFlyonUI = this.createCustomColors(sourceColorArgb, lightFlyonUI.info, 'flyonui-info');
        const successFromFlyonUI = this.createCustomColors(sourceColorArgb, lightFlyonUI.success, 'flyonui-success');
        const warningFromFlyonUI = this.createCustomColors(sourceColorArgb, lightFlyonUI.warning, 'flyonui-warning');
        let light: { [key: string]: any }= { colors: {} }
        let dark: { [key: string]: any }= { colors: {} }
        // Assigning the MaterialDesign colors first:
        materialDesignColors.forEach(token => {
            const keyDynamicScheme = token as keyof DynamicScheme;
            light.colors[token] = lightMaterial[keyDynamicScheme];
            dark.colors[token] = darkMaterial[keyDynamicScheme];
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
                onWarningContainer: warningFromFlyonUI.light.colors.onColorContainer,
            },
            palettes:{
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
                warningPalette: warningFromFlyonUI.light.palette,
            },
            meta: {
                contrastLevel: lightMaterial.contrastLevel,
                isDark: lightMaterial.isDark,
                sourceColorArgb: lightMaterial.sourceColorArgb,
                sourceColorHct: lightMaterial.sourceColorHct,
                variant: lightMaterial.variant,
            }
        }
    
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
                onWarningContainer: warningFromFlyonUI.dark.colors.onColorContainer,
            },
            palettes:{
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
                warningPalette: warningFromFlyonUI.dark.palette,
            },
            meta: {
                contrastLevel: darkMaterial.contrastLevel,
                isDark: darkMaterial.isDark,
                sourceColorArgb: darkMaterial.sourceColorArgb,
                sourceColorHct: darkMaterial.sourceColorHct,
                variant: darkMaterial.variant,
            }
        }

        return {
            light: light as AppColorSchemeForMode,
            dark: dark as AppColorSchemeForMode
        };
    }

    private convertMaterialArgbToOklch( argbColor: number): string {
        console.log("=== lib - theming - convertMaterialArgbToOklch ===");
        console.log(argbColor);
        return "convertedColor"
    }
}


export interface StylingConfig {
}

class Styling {}


export interface TypographyConfig {
}

class Typography {}

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

    public applyTheme( colorConfig: ColorConfig, mode: "light" | "dark", targetElement: HTMLElement ):  AppColors {
        const colorization = new Colorization(colorConfig.sourceColor, colorConfig.variant, colorConfig.contrast);
        const colorScheme = colorization.createAppColors(colorConfig);
        this.applyMaterialTokens(colorScheme, mode, targetElement);
        return colorScheme;
    }

    public applyMaterialTokens( appColors: AppColors, mode: "light" | "dark", targetElement: HTMLElement): void {
        const colors = mode === "dark" ? appColors.dark.colors : appColors.light.colors;
        console.log("=== lib - theming - applyMaterialTokens - colors[warning] ===");
        console.log(hexFromArgb(colors.warning));
        console.log("=== lib - theming - applyMaterialTokens - colors[onWarning] ===");
        console.log(hexFromArgb(colors.onWarning));
        console.log("=== lib - theming - applyMaterialTokens - colors[warningContainer] ===");
        console.log(hexFromArgb(colors.warningContainer));
        console.log("=== lib - theming - applyMaterialTokens - colors[onWarningContainer] ===");
        console.log(hexFromArgb(colors.onWarningContainer));
        appColorNames.forEach(token => {
            const tokenKebabCase = token.replace(/([a-z])([A-Z])/g, '$1-$2').toLowerCase();
            targetElement.style.setProperty(`--md-sys-color-${tokenKebabCase}`, hexFromArgb(colors[token]))
        });
        targetElement.style.backgroundColor = hexFromArgb(colors['background']);
    }


}
