export interface MatchedRecord {
  invoice_number: string;
  gstin: string;
  vendor_name: string;
  taxable_amount: number;
  igst: number;
  cgst: number;
  sgst: number;
  match_status: 'MATCHED' | 'AMOUNT_MISMATCH' | 'GSTIN_MISMATCH';
  raw_invoice: Record<string, unknown>;
  raw_gstr2b: Record<string, unknown> | null;
}

export interface UnmatchedRecord {
  invoice_number: string;
  gstin: string;
  mismatch_reason: string;
  missing_source: 'INVOICE' | 'GSTR2B' | 'NONE';
  amount_difference: number;
  raw_invoice: Record<string, unknown> | null;
  raw_gstr2b: Record<string, unknown> | null;
}

export interface ReconciliationSummary {
  session_id: string;
  session_name: string;
  status: string;
  total_invoice_records: number;
  total_gstr2b_records: number;
  matched_count: number;
  amount_mismatch_count: number;
  gstin_mismatch_count: number;
  only_in_invoice_count: number;
  only_in_gstr2b_count: number;
  match_percentage: number;
  total_taxable_invoice: number;
  total_taxable_gstr2b: number;
  taxable_difference: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}
