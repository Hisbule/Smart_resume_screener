// Centralized API configuration
export const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// API endpoint helpers
export const api = {
  // Upload endpoints
  upload: () => `${API_URL}/upload`,
  
  // Ranking endpoints
  rank: () => `${API_URL}/rank`,
  
  // Candidate endpoints
  candidate: (id: string) => `${API_URL}/candidate/${id}`,
  listCandidates: (limit: number = 20) => `${API_URL}/debug/list_candidates?limit=${limit}`,
  
  // Debug endpoints
  debugIndex: () => `${API_URL}/debug/index`,
  
  // Reset endpoints
  reset: () => `${API_URL}/reset`,
};

// Helper function for fetch with error handling
export async function fetchAPI<T>(
  url: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(url, options);
  
  if (!response.ok) {
    throw new Error(`API Error: ${response.statusText}`);
  }
  
  return response.json();
}
