import { Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTabsModule } from '@angular/material/tabs';
import { MatChipsModule } from '@angular/material/chips';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { trigger, transition, style, animate } from '@angular/animations';
import { Subject, takeUntil } from 'rxjs';

import { AuthService } from '../../core/services/auth.service';
import { ReconciliationService } from '../../core/services/reconciliation.service';
import {
  MatchedRecord, PaginatedResponse, ReconciliationSummary, UnmatchedRecord
} from '../../models/reconciliation.models';

@Component({
  selector: 'app-reconciliation',
  standalone: true,
  imports: [
    CommonModule, FormsModule,
    MatButtonModule, MatIconModule, MatTabsModule,
    MatChipsModule, MatTooltipModule,
    MatProgressSpinnerModule, MatSnackBarModule,
  ],
  templateUrl: './reconciliation.component.html',
  styleUrl: './reconciliation.component.scss',
  animations: [
    trigger('fadeIn', [
      transition(':enter', [
        style({ opacity: 0, transform: 'translateY(16px)' }),
        animate('350ms ease-out', style({ opacity: 1, transform: 'translateY(0)' })),
      ]),
    ]),
  ],
})
export class ReconciliationComponent implements OnInit, OnDestroy {
  sessionId = '';
  user = this.auth.getUser();

  summary: ReconciliationSummary | null = null;
  matchedData: PaginatedResponse<MatchedRecord> | null = null;
  unmatchedData: PaginatedResponse<UnmatchedRecord> | null = null;

  isLoading = true;
  activeTab: 'matched' | 'unmatched' = 'matched';

  matchedPage = 1;
  unmatchedPage = 1;
  pageSize = 20;
  matchedSearch = '';
  unmatchedSearch = '';
  matchStatusFilter = '';
  missingSourceFilter = '';

  private destroy$ = new Subject<void>();

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private auth: AuthService,
    private reconcSvc: ReconciliationService,
    private snackBar: MatSnackBar,
  ) {}

  ngOnInit() {
    this.sessionId = this.route.snapshot.paramMap.get('sessionId') ?? '';
    this.loadSummary();
  }

  loadSummary() {
    this.isLoading = true;
    this.reconcSvc.getSummary(this.sessionId)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (s) => { this.summary = s; this.isLoading = false; this.loadMatched(); this.loadUnmatched(); },
        error: () => {
          // Session exists but hasn't been run yet — run it now
          this.reconcSvc.run(this.sessionId)
            .pipe(takeUntil(this.destroy$))
            .subscribe({
              next: (s) => { this.summary = s; this.isLoading = false; this.loadMatched(); this.loadUnmatched(); },
              error: (err) => {
                this.isLoading = false;
                this.snackBar.open(err?.error?.detail ?? 'Failed to run reconciliation', 'Dismiss', { duration: 5000 });
              },
            });
        },
      });
  }

  loadMatched() {
    this.reconcSvc.getMatched(this.sessionId, this.matchedPage, this.pageSize, this.matchedSearch, this.matchStatusFilter)
      .pipe(takeUntil(this.destroy$))
      .subscribe({ next: (d) => this.matchedData = d });
  }

  loadUnmatched() {
    this.reconcSvc.getUnmatched(this.sessionId, this.unmatchedPage, this.pageSize, this.unmatchedSearch, this.missingSourceFilter)
      .pipe(takeUntil(this.destroy$))
      .subscribe({ next: (d) => this.unmatchedData = d });
  }

  onMatchedSearch() { this.matchedPage = 1; this.loadMatched(); }
  onUnmatchedSearch() { this.unmatchedPage = 1; this.loadUnmatched(); }

  setMatchedPage(p: number) { this.matchedPage = p; this.loadMatched(); }
  setUnmatchedPage(p: number) { this.unmatchedPage = p; this.loadUnmatched(); }

  matchedTotalPages(): number { return Math.ceil((this.matchedData?.total ?? 0) / this.pageSize); }
  unmatchedTotalPages(): number { return Math.ceil((this.unmatchedData?.total ?? 0) / this.pageSize); }
  minVal(a: number, b: number): number { return Math.min(a, b); }

  pageRange(total: number): number[] {
    return Array.from({ length: total }, (_, i) => i + 1);
  }

  exportExcel() {
    const url = this.reconcSvc.getExportUrl(this.sessionId);
    const token = this.auth.getAccessToken();
    // Use fetch with auth header then trigger download
    fetch(url, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.blob())
      .then(blob => {
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = `reconciliation_${this.sessionId.slice(0, 8)}.xlsx`;
        a.click();
        URL.revokeObjectURL(a.href);
      })
      .catch(() => this.snackBar.open('Export failed', 'Dismiss', { duration: 3000 }));
  }

  getStatusClass(status: string): string {
    const map: Record<string, string> = {
      MATCHED: 'badge-matched',
      AMOUNT_MISMATCH: 'badge-mismatch',
      GSTIN_MISMATCH: 'badge-gstin',
    };
    return map[status] ?? 'badge-default';
  }

  getMissingSourceClass(src: string): string {
    if (src === 'GSTR2B') return 'badge-only-inv';
    if (src === 'INVOICE') return 'badge-only-g2b';
    return 'badge-mismatch';
  }

  goBack() { this.router.navigate(['/dashboard']); }
  logout() { this.auth.logout(); }

  ngOnDestroy() { this.destroy$.next(); this.destroy$.complete(); }
}
