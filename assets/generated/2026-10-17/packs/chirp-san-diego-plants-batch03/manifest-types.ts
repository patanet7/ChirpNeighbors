export type Vec2 = [number, number];
export type Bounds = [number, number, number, number];
export interface SourceAsset { id:string; path:string; sha256:string; size:Vec2; alpha128_bbox:Bounds; bottom_anchor_estimate:Vec2; partial_alpha_fraction:number; }
export interface Species { id:string; name:string; form?:string; states:Record<string,string>; references:string[]; }
export interface RegistrationMeasurement { overlay_alpha128_over_base_fraction:number; lower10_percent_overlay_max_alpha:number; lower10_percent_composite_identical_rgba_fraction:number; note:string; }
export interface PlantManifest { version:number; region:string[]; status:string; counts:{generated_originals:number;candidate_sources:number;species:number;composited_states:number}; assets:SourceAsset[]; species:Species[]; registration:Record<string,RegistrationMeasurement>; world_assumptions:Record<string,Vec2|string>; anchors:Record<string,Vec2|string>; wind:{implemented:boolean;proposal:string}; animation:{implemented:boolean;preview:string}; qa:string[]; rights:string; }
