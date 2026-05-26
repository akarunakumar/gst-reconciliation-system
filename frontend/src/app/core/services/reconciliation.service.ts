import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  MatchedRecord, PaginatedResponse, ReconciliationSummary, UnmatchedRecord
} from '../../models/reconciliation.models';

@Injectable({ providedIn: 'root' })
export class ReconciliationService {
  private readonly base = environment.apiUrl;

  constructor(private http: HttpClient) {}

  run(sessionId: string): Observable<ReconciliationSummary> {
    return this.http.post<ReconciliationSummary>(`${this.base}/reconciliation/run/${sessionId}`, {});
  }

  getSummary(sessionId: string): Observable<ReconciliationSummary> {
    return this.http.get<ReconciliationSummary>(`${this.base}/reconciliation/summary/${sessionId}`);
  }

  getMatched(sessionId: string, page = 1, pageSize = 20, search = '', matchStatus = ''): Observable<PaginatedResponse<MatchedRecord>> {
    let params = new HttpParams().set('page', page).set('page_size', pageSize);
    if (search) params = params.set('search', search);
    if (matchStatus) params = params.set('match_status', matchStatus);
    return this.http.get<PaginatedResponse<MatchedRecord>>(`${this.base}/reconciliation/matched/${sessionId}`, { params });
  }

  getUnmatched(sessionId: string, page = 1, pageSize = 20, search = '', missingSource = ''): Observable<PaginatedResponse<UnmatchedRecord>> {
    let params = new HttpParams().set('page', page).set('page_size', pageSize);
    if (search) params = params.set('search', search);
    if (missingSource) params = params.set('missing_source', missingSource);
    return this.http.get<PaginatedResponse<UnmatchedRecord>>(`${this.base}/reconciliation/unmatched/${sessionId}`, { params });
  }

  getExportUrl(sessionId: string): string {
    return `${this.base}/reconciliation/export/${sessionId}`;
  }
}
