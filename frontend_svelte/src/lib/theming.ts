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
    contrastLevel: string;
    isDark: boolean;
    sourceColorArgb: number;
    sourceColorHct: Hct;
    variant: number;
}

type MaterialDesignScheme = MaterialDesignColor & MaterialDesignPalette & MaterialDesignMeta;

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

    const sampleMaterialDesignScheme: MaterialDesignScheme = {
        // Fill in with sample data
        primary: 0,
        onPrimary: 0,
        primaryContainer: 0,
        onPrimaryContainer: 0,
        secondary: 0,
        onSecondary: 0,
        secondaryContainer: 0,
        onSecondaryContainer: 0,
        tertiary: 0,
        onTertiary: 0,
        tertiaryContainer: 0,
        onTertiaryContainer: 0,
        error: 0,
        onError: 0,
        errorContainer: 0,
        onErrorContainer: 0,
        primaryFixed: 0,
        primaryFixedDim: 0,
        onPrimaryFixed: 0,
        onPrimaryFixedVariant: 0,
        secondaryFixed: 0,
        secondaryFixedDim: 0,
        onSecondaryFixed: 0,
        onSecondaryFixedVariant: 0,
        tertiaryFixed: 0,
        tertiaryFixedDim: 0,
        onTertiaryFixed: 0,
        onTertiaryFixedVariant: 0,
        surfaceContainerLowest: 0,
        surfaceContainerLow: 0,
        surfaceContainer: 0,
        surfaceContainerHigh: 0,
        surfaceContainerHighest: 0,
        surfaceDim: 0,
        surface: 0,
        surfaceBright: 0,
        onSurface: 0,
        onSurfaceVariant: 0,
        outline: 0,
        outlineVariant: 0,
        inverseSurface: 0,
        inverseOnSurface: 0,
        inversePrimary: 0,
        scrim: 0,
        shadow: 0,
        neutralPaletteKeyColor: 0,
        neutralVariantPaletteKeyColor: 0,
        primaryPaletteKeyColor: 0,
        secondaryPaletteKeyColor: 0,
        tertiaryPaletteKeyColor: 0,
        // errorPaletteKeyColor: 0,
        background: 0,
        onBackground: 0,
        primaryPalette: {} as TonalPalette,
        secondaryPalette: {} as TonalPalette,
        tertiaryPalette: {} as TonalPalette,
        errorPalette: {} as TonalPalette,
        neutralPalette: {} as TonalPalette,
        neutralVariantPalette: {} as TonalPalette,
        contrastLevel: "0",
        isDark: true,
        sourceColorArgb: 0,
        sourceColorHct: Hct.fromInt(0),
        variant: 0,
    }
// console.log("=== lib - theming - sampleMaterialDesignScheme ===");
// console.log(sampleMaterialDesignScheme);

type CustomColors = {
    light: {
        color: number;
        onColor: number;
        colorContainer: number;
        onColorContainer: number;
        colorPalette: TonalPalette
    },
    dark: {
        color: number;
        onColor: number;
        colorContainer: number;
        onColorContainer: number;
        colorPalette: TonalPalette
    },
}


const additionalFlyonUIColors = [ "neutral", "info", "success", "warning" ] as const;
const additionalFlyonUIColorsOn = additionalFlyonUIColors.map(color => `on${color.charAt(0).toUpperCase() + color.slice(1)}` as const);
const additionalFlyonUIColorsContainer = additionalFlyonUIColors.map(color => `${color}Container` as const);
const additionalFlyonUIColorsOnContainer = additionalFlyonUIColors.map(color => `on${color.charAt(0).toUpperCase() + color.slice(1)}Container` as const);
const additionalFlyonUIColorsPalette = additionalFlyonUIColors.map(color => `${color}Palette` as const);
type AdditionalFlyonUIColors = Record<typeof additionalFlyonUIColors[number], number>;
type AdditionalFlyonUIColorsOn = Record<typeof additionalFlyonUIColorsOn[number], number>;
type AdditionalFlyonUIColorsContainer = Record<typeof additionalFlyonUIColorsContainer[number], number>;
type AdditionalFlyonUIColorsOnContainer = Record<typeof additionalFlyonUIColorsOnContainer[number], number>;
type AdditionalFlyonUIColorsPalette = Record<typeof additionalFlyonUIColorsPalette[number], TonalPalette>;
// type AdditionalFlyonUIColors = typeof additionalFlyonUIColors[number]; // creates a union type
type AdditionalFlyonUIScheme = 
    AdditionalFlyonUIColors &
    AdditionalFlyonUIColorsOn &
    AdditionalFlyonUIColorsContainer &
    AdditionalFlyonUIColorsOnContainer &
    AdditionalFlyonUIColorsPalette;


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
        // console.log("=== lib - theming - createMaterialSchemes ===");
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
        console.log("=== lib - theming - createMaterialSchemes - lightScheme ===");
        console.log(lightScheme);
        return { light: lightScheme, dark: darkScheme };
    }

    private createCustomColors( sourceColor: number, flyonUIcolor: string, colorName: string): CustomColors {
        const colorGroup = customColor(sourceColor, {value: argbFromHex(flyonUIcolor), name: colorName, blend: true});
        const lightPalette = TonalPalette.fromInt(colorGroup.light.color);
        // console.log("=== lib - theming - createFlyonUIadditions - lightPalette ===");
        // console.log(lightPalette);
        const darkPalette = TonalPalette.fromInt(colorGroup.dark.color);
        const light = {
            ...colorGroup.light,
            colorPalette: lightPalette
        }
        const dark = {
            ...colorGroup.dark,
            colorPalette: darkPalette
        }

        // console.log("=== lib - theming - createFlyonUIadditions - light ===");
        // console.log(light);
        return {
            light: light,
            dark: dark,
        }
    }

    public createAppColors( colorConfig: ColorConfig):  AppColors {
        // console.log("=== lib - theming - createMaterialSchemeFrom ===");
        const sourceColorArgb = argbFromHex(colorConfig.sourceColor);
        const sourceColorHct = Hct.fromInt(sourceColorArgb);
        const { light: lightMaterial, dark: darkMaterial } = this.createMaterialSchemes(sourceColorHct, colorConfig.variant, colorConfig.contrast);
        const neutralFromFlyonUI = this.createCustomColors(sourceColorArgb, lightFlyonUI.neutral, 'flyonui-neutral');
        const infoFromFlyonUI = this.createCustomColors(sourceColorArgb, lightFlyonUI.info, 'flyonui-info');
        const successFromFlyonUI = this.createCustomColors(sourceColorArgb, lightFlyonUI.success, 'flyonui-success');
        const warningFromFlyonUI = this.createCustomColors(sourceColorArgb, lightFlyonUI.warning, 'flyonui-warning');
        // console.log("=== lib - theming - createAppColors - neutralFromFlyonUI ===");
        // console.log(neutralFromFlyonUI.light);
        const light: { [key: string]: any } = {
            ...lightMaterial,// materialDesignPalettes and contrastLevel, isDark, sourceColorArgb, sourceColorHct, and variant
            neutral: neutralFromFlyonUI.light.color,
            onNeutral: neutralFromFlyonUI.light.onColor,
            neutralContainer: neutralFromFlyonUI.light.colorContainer,
            onNeutralContainer: neutralFromFlyonUI.light.onColorContainer,
            neutralPalette: neutralFromFlyonUI.light.colorPalette,
            info: infoFromFlyonUI.light.color,
            onInfo: infoFromFlyonUI.light.onColor,
            infoContainer: infoFromFlyonUI.light.colorContainer,
            onInfoContainer: infoFromFlyonUI.light.onColorContainer,
            infoPalette: infoFromFlyonUI.light.colorPalette,
            success: successFromFlyonUI.light.color,
            onSuccess: successFromFlyonUI.light.onColor,
            successContainer: successFromFlyonUI.light.colorContainer,
            onSuccessContainer: successFromFlyonUI.light.onColorContainer,
            successPalette: successFromFlyonUI.light.colorPalette,
            warning: warningFromFlyonUI.light.color,
            onWarning: warningFromFlyonUI.light.onColor,
            warningContainer: warningFromFlyonUI.light.colorContainer,
            onWarningContainer: warningFromFlyonUI.light.onColorContainer,
            warningPalette: warningFromFlyonUI.light.colorPalette,
        }
    
        const dark: { [key: string]: any } = {
            ...darkMaterial,// materialDesignPalettes and contrastLevel, isDark, sourceColorArgb, sourceColorHct, and variant
            neutral: neutralFromFlyonUI.dark.color,
            onNeutral: neutralFromFlyonUI.dark.onColor,
            neutralContainer: neutralFromFlyonUI.dark.colorContainer,
            onNeutralContainer: neutralFromFlyonUI.dark.onColorContainer,
            neutralPalette: neutralFromFlyonUI.dark.colorPalette,
            info: infoFromFlyonUI.dark.color,
            onInfo: infoFromFlyonUI.dark.onColor,
            infoContainer: infoFromFlyonUI.dark.colorContainer,
            onInfoContainer: infoFromFlyonUI.dark.onColorContainer,
            infoPalette: infoFromFlyonUI.dark.colorPalette,
            success: successFromFlyonUI.dark.color,
            onSuccess: successFromFlyonUI.dark.onColor,
            successContainer: successFromFlyonUI.dark.colorContainer,
            onSuccessContainer: successFromFlyonUI.dark.onColorContainer,
            successPalette: successFromFlyonUI.dark.colorPalette,
            warning: warningFromFlyonUI.dark.color,
            onWarning: warningFromFlyonUI.dark.onColor,
            warningContainer: warningFromFlyonUI.dark.colorContainer,
            onWarningContainer: warningFromFlyonUI.dark.onColorContainer,
            warningPalette: warningFromFlyonUI.dark.colorPalette,
        }
        materialDesignColors.forEach(token => {
            // const keyMaterialDesignColor = token as keyof MaterialDesignColor;
            const keyDynamicScheme = token as keyof DynamicScheme;
            light[token] = lightMaterial[keyDynamicScheme];
            dark[token] = darkMaterial[keyDynamicScheme];
            // Object.defineProperty(light, token, { value: lightMaterial[key] });
            // Object.defineProperty(dark, token, { value: darkMaterial[key] });
        });

        console.log("=== lib - theming - createAppColors - light ===");
        console.log(light);

        return {
            // maybe return the colors, the palettes and meta data separately?
            // like that: light: { colors: light, palettes: lightPalettes, meta: lightMeta }
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

    public createScheme( colorConfig: ColorConfig ):  AppColors {
        const colorization = new Colorization(colorConfig.sourceColor, colorConfig.variant, colorConfig.contrast);
        return colorization.createAppColors(colorConfig);
    }

    public applyMaterialTokens( appColors: AppColors): void {
        const materialDesignColorsKebabCase = materialDesignColors.map(token => token.replace(/([a-z])([A-Z])/g, '$1-$2').toLowerCase());
    }


}
