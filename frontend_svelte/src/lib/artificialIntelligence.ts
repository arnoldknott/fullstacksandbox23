export enum Model {
	// TBD: replace with actual model names:
	MODEL1 = 'Model 1',
	MODEL2 = 'Model 2',
	MODEL3 = 'Model 3'
}

export interface ArtificialIntelligenceConfig {
	enabled: boolean;
	model: Model;
	temperature: number;
}
