import { Component, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { Subject, takeUntil } from 'rxjs';
import { trigger, transition, style, animate } from '@angular/animations';

import { AuthService } from '../../core/services/auth.service';
import { UploadService } from '../../core/services/upload.service';
import { SessionResponse, UploadResult } from '../../models/upload.models';
import {
  FileDropZoneComponent,
  UploadFn,
} from '../../shared/components/file-drop-zone/file-drop-zone.component';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatSnackBarModule,
    MatProgressSpinnerModule,
    MatTooltipModule,
    FileDropZoneComponent,
  ],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss',
  animations: [
    trigger('fadeIn', [
      transition(':enter', [
        style({ opacity: 0, transform: 'translateY(16px)' }),
        animate('400ms ease-out', style({ opacity: 1, transform: 'translateY(0)' })),
      ]),
    ]),
  ],
})
export class DashboardComponent implements OnDestroy {
  user = this.authService.getUser();

  invoiceResult: UploadResult | null = null;
  gstr2bResult: UploadResult | null = null;
  session: SessionResponse | null = null;
  isStarting = false;

  invoiceUploadFn: UploadFn = (file) => this.uploadService.uploadInvoice(file);
  gstr2bUploadFn: UploadFn = (file) => this.uploadService.uploadGstr2b(file);

  private destroy$ = new Subject<void>();

  constructor(
    private authService: AuthService,
    private uploadService: UploadService,
    private router: Router,
    private snackBar: MatSnackBar,
  ) {}

  get canStart(): boolean {
    return !!this.invoiceResult && !!this.gstr2bResult && !this.isStarting;
  }

  onInvoiceUploaded(result: UploadResult) {
    this.invoiceResult = result;
    this.session = null;
  }

  onGstr2bUploaded(result: UploadResult) {
    this.gstr2bResult = result;
    this.session = null;
  }

  onUploadError(msg: string) {
    this.snackBar.open(msg, 'Dismiss', { duration: 5000, panelClass: ['snack-error'] });
  }

  startReconciliation() {
    if (!this.canStart) return;
    this.isStarting = true;

    this.uploadService
      .startReconciliation({
        invoice_temp_key: this.invoiceResult!.temp_key,
        gstr2b_temp_key: this.gstr2bResult!.temp_key,
      })
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (session) => {
          this.session = session;
          this.isStarting = false;
          // Phase 3 will navigate to: this.router.navigate(['/reconciliation', session.session_id]);
        },
        error: (err) => {
          this.isStarting = false;
          const msg = err?.error?.detail ?? 'Failed to start reconciliation';
          this.snackBar.open(msg, 'Dismiss', { duration: 5000, panelClass: ['snack-error'] });
        },
      });
  }

  logout() {
    this.authService.logout();
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
