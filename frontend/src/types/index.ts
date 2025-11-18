/**
 * Type definitions for ChirpNeighbors frontend
 */

export interface HealthCheck {
  status: string;
  checks: {
    api: string;
  };
}

export interface BirdIdentification {
  species_id: string;
  common_name: string;
  scientific_name: string;
  confidence: number;
  start_time: number;
  end_time: number;
}

export interface AudioProcessingResult {
  file_id: string;
  status: string;
  identifications: BirdIdentification[];
  audio_duration: number;
  sample_rate: number;
  processed_at: string;
}

export interface BirdSpecies {
  species_id: string;
  common_name: string;
  scientific_name: string;
  family: string;
  order: string;
  description?: string;
  habitat?: string;
  distribution?: string;
  vocalization_description?: string;
  conservation_status?: string;
  image_url?: string;
  audio_sample_url?: string;
}

export interface ApiError {
  detail: string;
}
