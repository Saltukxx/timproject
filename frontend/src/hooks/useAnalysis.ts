import { useState } from "react";
import axios from "axios";
import type { AnalysisResponse } from "../types";

interface UploadState {
  loading: boolean;
  error: string | null;
  data: AnalysisResponse | null;
}

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
      const response = await axios.post<AnalysisResponse>("/api/analyze", formData, {
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

