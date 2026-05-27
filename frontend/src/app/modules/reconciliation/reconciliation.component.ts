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
  MatchedRecord, PaginatedResponse, ReconciliationSummary, UnmatchedRecord,
} from '../../models/reconciliation.models';

const STATUS_BADGE_MAP: Record<string, string> = {
  MATCHED: 'badge-matched',
  AMOUNT_MISMATCH: 'badge-mismatch',
  GSTIN_MISMATCH: 'badge-gstin',
};

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
  readonly pageSize = 20;
  matchedSearch = '';
  unmatchedSearch = '';
  matchStatusFilter = '';
  missingSourceFilter = '';

  protected readonly Math = Math;

  private destroy$ = new Subject<void>();

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private auth: AuthService,
    private reconcSvc: ReconciliationService,
    private snackBar: MatSnackBar,
  ) {}

  ngOnInit(): void {
    this.sessionId = this.route.snapshot.paramMap.get('sessionId') ?? '';
    this.loadSummary();
  }

  loadSummary(): void {
    this.isLoading = true;
    this.reconcSvc.getSummary(this.sessionId)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (s) => {
          this.summary = s;
          this.isLoading = false;
          this.loadMatched();
          this.loadUnmatched();
        },
        error: () => {
          // Summary not found — session hasn't been run yet, trigger reconciliation now
          this.reconcSvc.run(this.sessionId)
            .pipe(takeUntil(this.destroy$))
            .subscribe({
              next: (s) => {
                this.summary = s;
                this.isLoading = false;
                this.loadMatched();
                this.loadUnmatched();
              },
              error: (err) => {
                this.isLoading = false;
                const msg = err?.error?.detail ?? 'Failed to run reconciliation';
                this.snackBar.open(msg, 'Dismiss', { duration: 5000 });
              },
            });
        },
      });
  }

  loadMatched(): void {
    this.reconcSvc
      .getMatched(this.sessionId, this.matchedPage, this.pageSize, this.matchedSearch, this.matchStatusFilter)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (d) => (this.matchedData = d),
        error: () => this.snackBar.open('Failed to load matched records', 'Dismiss', { duration: 3000 }),
      });
  }

  loadUnmatched(): void {
    this.reconcSvc
      .getUnmatched(this.sessionId, this.unmatchedPage, this.pageSize, this.unmatchedSearch, this.missingSourceFilter)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (d) => (this.unmatchedData = d),
        error: () => this.snackBar.open('Failed to load unmatched records', 'Dismiss', { duration: 3000 }),
      });
  }

  onMatchedSearch(): void { this.matchedPage = 1; this.loadMatched(); }
  onUnmatchedSearch(): void { this.unmatchedPage = 1; this.loadUnmatched(); }

  setMatchedPage(p: number): void { this.matchedPage = p; this.loadMatched(); }
  setUnmatchedPage(p: number): void { this.unmatchedPage = p; this.loadUnmatched(); }

  get matchedTotalPages(): number { return Math.ceil((this.matchedData?.total ?? 0) / this.pageSize); }
  get unmatchedTotalPages(): number { return Math.ceil((this.unmatchedData?.total ?? 0) / this.pageSize); }

  get matchedPageRange(): number[] {
    return Array.from({ length: this.matchedTotalPages }, (_, i) => i + 1);
  }

  get unmatchedPageRange(): number[] {
    return Array.from({ length: this.unmatchedTotalPages }, (_, i) => i + 1);
  }

  exportExcel(): void {
    this.reconcSvc.exportExcel(this.sessionId)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (blob) => {
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `reconciliation_${this.sessionId.slice(0, 8)}.xlsx`;
          a.click();
          URL.revokeObjectURL(url);
        },
        error: () => this.snackBar.open('Export failed', 'Dismiss', { duration: 3000 }),
      });
  }

  getStatusClass(status: string): string {
    return STATUS_BADGE_MAP[status] ?? 'badge-default';
  }

  getMissingSourceClass(src: string): string {
    if (src === 'GSTR2B') return 'badge-only-inv';
    if (src === 'INVOICE') return 'badge-only-g2b';
    return 'badge-mismatch';
  }

  goBack(): void { this.router.navigate(['/dashboard']); }
  logout(): void { this.auth.logout(); }

  ngOnDestroy(): void { this.destroy$.next(); this.destroy$.complete(); }
}
