

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

class Colorization {}


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


    public manipulateContrast(contrast: number): number {
        const tenFoldContrast = contrast * 10;
        console.log("=== lib - theming - Manipulating contrast - tenFoldContrast ===");
        console.log(tenFoldContrast);
        return tenFoldContrast
    }
}
