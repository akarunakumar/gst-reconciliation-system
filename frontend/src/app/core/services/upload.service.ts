import { Injectable } from '@angular/core';
import { HttpClient, HttpEventType, HttpRequest } from '@angular/common/http';
import { Observable, map, filter } from 'rxjs';
import { environment } from '../../../environments/environment';
import { SessionResponse, StartReconciliationRequest, UploadResult } from '../../models/upload.models';

@Injectable({ providedIn: 'root' })
export class UploadService {
  private readonly apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  uploadInvoice(file: File): Observable<UploadResult> {
    return this._upload(file, `${this.apiUrl}/upload/invoices`);
  }

  uploadGstr2b(file: File): Observable<UploadResult> {
    return this._upload(file, `${this.apiUrl}/upload/gstr2b`);
  }

  startReconciliation(req: StartReconciliationRequest): Observable<SessionResponse> {
    return this.http.post<SessionResponse>(`${this.apiUrl}/upload/start`, req);
  }

  private _upload(file: File, url: string): Observable<UploadResult> {
    const formData = new FormData();
    formData.append('file', file, file.name);
    const req = new HttpRequest('POST', url, formData, { reportProgress: true });
    return this.http.request<UploadResult>(req).pipe(
      filter((e) => e.type === HttpEventType.Response),
      map((e: any) => e.body as UploadResult)
    );
  }
}
