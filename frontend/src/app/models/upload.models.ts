export interface UploadResult {
  filename: string;
  row_count: number;
  columns: string[];
  preview: Record<string, unknown>[];
  temp_key: string;
  warnings: string[];
  sheets: string[];
}

export interface StartReconciliationRequest {
  invoice_temp_key: string;
  gstr2b_temp_key: string;
  session_name?: string;
}

export interface SessionResponse {
  session_id: string;
  status: string;
  invoice_row_count: number;
  gstr2b_row_count: number;
  message: string;
}

export type DropZoneState = 'idle' | 'dragover' | 'uploading' | 'success' | 'error';
