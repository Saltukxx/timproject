import { useState } from "react";
import axios from "axios";
import type { AnalysisResponse } from "../types";

interface UploadState {
  loading: boolean;
  error: string | null;
  data: AnalysisResponse | null;
}

function normaliseBaseUrl(baseUrl: string | undefined | null) {
  if (!baseUrl) return undefined;
  const trimmed = baseUrl.trim();
  if (!trimmed) return undefined;
  if (trimmed === "%VITE_API_BASE_URL%") return undefined;
  return trimmed.endsWith("/") ? trimmed.slice(0, -1) : trimmed;
}

function resolveApiBaseUrl() {
  const fromEnv = normaliseBaseUrl(import.meta.env.VITE_API_BASE_URL);
  if (fromEnv) return fromEnv;

  const fromWindow = normaliseBaseUrl(window.__MAEVA_API_BASE__);
  if (fromWindow) return fromWindow;

  // Default to relative /api for setups that proxy API calls through the static host.
  return "/api";
}

const apiClient = axios.create({
  baseURL: resolveApiBaseUrl()
});

export function useAnalysis() {
  const [state, setState] = useState<UploadState>({
    loading: false,
    error: null,
    data: null
  });

  const upload = async (file: File) => {
    setState({ loading: true, error: null, data: null });
    try {
      const formData = new FormData();
      formData.append("file", file);
      const response = await apiClient.post<AnalysisResponse>("/api/analyze", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      setState({ loading: false, error: null, data: response.data });
    } catch (error) {
      console.error(error);
      const message = error instanceof Error ? error.message : "Analysis failed";
      setState({ loading: false, error: message, data: null });
    }
  };

  return { ...state, upload };
}
