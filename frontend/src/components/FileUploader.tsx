import type { ChangeEvent } from "react";

interface Props {
  onFileSelected: (file: File) => void;
  loading: boolean;
  acceptedTypes?: string;
}

export function FileUploader({ onFileSelected, loading, acceptedTypes = ".xlsx,.xlsm" }: Props) {
  const handleChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      onFileSelected(file);
    }
  };

  return (
    <div className="upload-panel">
      <div>
        <h1 className="section-title">Upload a Qivalon Export</h1>
        <p className="stat-label">
          Drop the macro-enabled workbook (.xlsm) or a standard Excel file (.xlsx). We will replicate the
          in-sheet logic, recompute the macro outputs, and render decision-ready insights.
        </p>
      </div>
      <div>
        <label className="upload-label">
          {loading ? "Analyzing…" : "Select Workbook"}
          <input
            type="file"
            accept={acceptedTypes}
            onChange={handleChange}
            disabled={loading}
          />
        </label>
      </div>
    </div>
  );
}

