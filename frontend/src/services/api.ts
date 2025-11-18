/**
 * API service for communicating with ChirpNeighbors backend
 */

import axios, { AxiosInstance } from 'axios';
import type {
  HealthCheck,
  AudioProcessingResult,
  BirdSpecies,
  BirdIdentification,
} from '@/types';

class ApiService {
  private client: AxiosInstance;

  constructor(baseURL: string = '/api/v1') {
    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // Health check
  async healthCheck(): Promise<HealthCheck> {
    const response = await this.client.get<HealthCheck>('/health');
    return response.data;
  }

  // Audio endpoints
  async uploadAudio(file: File): Promise<{ file_id: string; status: string }> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post('/audio/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  }

  async processAudio(fileId: string): Promise<{ status: string; progress: number }> {
    const response = await this.client.get(`/audio/process/${fileId}`);
    return response.data;
  }

  async getResults(fileId: string): Promise<AudioProcessingResult> {
    const response = await this.client.get<AudioProcessingResult>(`/audio/results/${fileId}`);
    return response.data;
  }

  // Bird species endpoints
  async listSpecies(): Promise<{ species: BirdSpecies[]; total: number }> {
    const response = await this.client.get('/birds/species');
    return response.data;
  }

  async getSpecies(speciesId: string): Promise<BirdSpecies> {
    const response = await this.client.get<BirdSpecies>(`/birds/species/${speciesId}`);
    return response.data;
  }

  async searchSpecies(query: string): Promise<{ results: BirdSpecies[]; query: string }> {
    const response = await this.client.get('/birds/search', {
      params: { q: query },
    });
    return response.data;
  }
}

// Export singleton instance
export const api = new ApiService();
export default api;
