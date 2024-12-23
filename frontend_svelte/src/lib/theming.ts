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
import { on } from "svelte/events";
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

export interface ColorConfig {
    sourceColor: string;
    variant: Variant;
    contrast: number;
}

interface AppColorSchemeForMode extends DynamicScheme {
    // note: neutralPalette and neutralVariantPalette already exist in DynamicScheme!
    // TBD: decide wether to use tehe neutral colors from Material or from FlyonUI!
    readonly neutralPalette: TonalPalette;
    readonly infoPalette: TonalPalette;
    readonly successPalette: TonalPalette;
    readonly warningPalette: TonalPalette;
    get neutral(): number
    get onNeutral(): number
    get neutralContainer(): number
    get onNeutralContainer(): number
    get info(): number
    get onInfo(): number
    get infoContainer(): number
    get onInfoContainer(): number
    get success(): number
    get onSuccess(): number
    get successContainer(): number
    get onSuccessContainer(): number
    get warning(): number
    get onWarning(): number
    get warningContainer(): number
    get onWarningContainer(): number
}

type FlyonAddition = {
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

    private createFlyonUIadditions( sourceColor: number, flyonUIcolor: string, colorName: string): FlyonAddition  {
        const colorGroup = customColor(sourceColor, {value: argbFromHex(flyonUIcolor), name: `flyonui-${colorName}`, blend: true});
        const lightPalette = TonalPalette.fromInt(colorGroup.light.color);
        // console.log("=== lib - theming - createFlyonUIadditions - lightPalette ===");
        // console.log(lightPalette);
        const darkPalette = TonalPalette.fromInt(colorGroup.dark.color);
        const light = {
            ...colorGroup.light,
            ...lightPalette
        }
        const dark = {
            ...colorGroup.dark,
            ...darkPalette
        }

        // Object.defineProperty(light, colorName, { get: () => colorGroup.light.color });
        // Object.defineProperty(light, `on${capitalizedColorName}`, { get: () => colorGroup.light.onColor });
        // Object.defineProperty(light, `${colorName}Container`, { get: () => colorGroup.light.colorContainer });
        // Object.defineProperty(light, `on${capitalizedColorName}Container`, { get: () => colorGroup.light.onColorContainer });
        // Object.defineProperty(light, `${colorName}Palette}`,  lightPalette );
        // Object.defineProperty(dark, colorName, { get: () => colorGroup.dark.color });
        // Object.defineProperty(dark, `on${capitalizedColorName}`, { get: () => colorGroup.dark.onColor });
        // Object.defineProperty(dark, `${colorName}Container`, { get: () => colorGroup.dark.colorContainer });
        // Object.defineProperty(dark, `on${capitalizedColorName}Container`, { get: () => colorGroup.dark.onColorContainer });
        // Object.defineProperty(dark, `${colorName}Palette}`,  darkPalette );

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
        console.log("=== lib - theming - createAppColors - lightMaterial ===");
        console.log(lightMaterial);
        const neutralFromFlyonUI = this.createFlyonUIadditions(sourceColorArgb, lightFlyonUI.neutral, 'neutral');
        const infoFromFlyonUI = this.createFlyonUIadditions(sourceColorArgb, lightFlyonUI.info, 'info');
        const successFromFlyonUI = this.createFlyonUIadditions(sourceColorArgb, lightFlyonUI.success, 'success');
        const warningFromFlyonUI = this.createFlyonUIadditions(sourceColorArgb, lightFlyonUI.warning, 'warning');
        // console.log("=== lib - theming - createAppColors - neutralFromFlyonUI ===");
        // console.log(neutralFromFlyonUI.light);
        const light = {
            ...lightMaterial,
            primary: lightMaterial.primary,
            onPrimary: lightMaterial.onPrimary,
            primaryContainer: lightMaterial.primaryContainer,
            onPrimaryContainer: lightMaterial.onPrimaryContainer,
            secondary: lightMaterial.secondary,
            onSecondary: lightMaterial.onSecondary,
            secondaryContainer: lightMaterial.secondaryContainer,
            onSecondaryContainer: lightMaterial.onSecondaryContainer,
            tertiary: lightMaterial.tertiary,
            onTertiary: lightMaterial.onTertiary,
            tertiaryContainer: lightMaterial.tertiaryContainer,
            onTertiaryContainer: lightMaterial.onTertiaryContainer,
            error: lightMaterial.error,
            onError: lightMaterial.onError,
            errorContainer: lightMaterial.errorContainer,
            onErrorContainer: lightMaterial.onErrorContainer,
            primaryFixed: lightMaterial.primaryFixed,
            primaryFixedDim: lightMaterial.primaryFixedDim,
            onPrimaryFixed: lightMaterial.onPrimaryFixed,
            onPrimaryFixedVariant: lightMaterial.onPrimaryFixedVariant,
            secondaryFixed: lightMaterial.secondaryFixed,
            secondaryFixedDim: lightMaterial.secondaryFixedDim,
            onSecondaryFixed: lightMaterial.onSecondaryFixed,
            onSecondaryFixedVariant: lightMaterial.onSecondaryFixedVariant,
            tertiaryFixed: lightMaterial.tertiaryFixed,
            tertiaryFixedDim: lightMaterial.tertiaryFixedDim,
            onTertiaryFixed: lightMaterial.onTertiaryFixed,
            onTertiaryFixedVariant: lightMaterial.onTertiaryFixedVariant,
            surfaceContainerLowest: lightMaterial.surfaceContainerLowest,
            surfaceContainerLow: lightMaterial.surfaceContainerLow,
            surfaceContainer: lightMaterial.surfaceContainer,
            surfaceContainerHigh: lightMaterial.surfaceContainerHigh,
            surfaceContainerHighest: lightMaterial.surfaceContainerHighest,

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
        const dark = {
            ...darkMaterial,
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

        // console.log("=== lib - theming - createAppColors - light ===");
        // console.log(light);

        return {
            light: light,
            dark: dark
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
        console.log("=== lib - theming - createMaterialSchemeFrom ===");
        const colorization = new Colorization(colorConfig.sourceColor, colorConfig.variant, colorConfig.contrast);
        return colorization.createAppColors(colorConfig);
    }


}
