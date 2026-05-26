import {
  Component, EventEmitter, HostListener, Input, OnDestroy, Output
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { Subject, takeUntil } from 'rxjs';
import { DropZoneState, UploadResult } from '../../../models/upload.models';

export type UploadFn = (file: File) => import('rxjs').Observable<UploadResult>;

@Component({
  selector: 'app-file-drop-zone',
  standalone: true,
  imports: [CommonModule, MatIconModule, MatProgressBarModule],
  templateUrl: './file-drop-zone.component.html',
  styleUrl: './file-drop-zone.component.scss',
})
export class FileDropZoneComponent implements OnDestroy {
  @Input() label = 'Upload File';
  @Input() description = 'Drag & drop or click to browse';
  @Input() accept = '.xlsx,.xls';
  @Input() maxSizeMb = 10;
  @Input() uploadFn!: UploadFn;

  @Output() uploadComplete = new EventEmitter<UploadResult>();
  @Output() uploadError = new EventEmitter<string>();

  state: DropZoneState = 'idle';
  result: UploadResult | null = null;
  errorMessage = '';

  private destroy$ = new Subject<void>();

  @HostListener('dragover', ['$event'])
  onDragOver(e: DragEvent) {
    e.preventDefault();
    if (this.state !== 'uploading' && this.state !== 'success') {
      this.state = 'dragover';
    }
  }

  @HostListener('dragleave')
  onDragLeave() {
    if (this.state === 'dragover') this.state = 'idle';
  }

  @HostListener('drop', ['$event'])
  onDrop(e: DragEvent) {
    e.preventDefault();
    const file = e.dataTransfer?.files[0];
    if (file) this.processFile(file);
  }

  onFileInput(event: Event) {
    const file = (event.target as HTMLInputElement).files?.[0];
    if (file) this.processFile(file);
  }

  processFile(file: File) {
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (!['xlsx', 'xls'].includes(ext ?? '')) {
      this.setError('Only .xlsx and .xls files are accepted');
      return;
    }
    if (file.size > this.maxSizeMb * 1024 * 1024) {
      this.setError(`File exceeds ${this.maxSizeMb} MB limit`);
      return;
    }

    this.state = 'uploading';
    this.errorMessage = '';

    this.uploadFn(file)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (res) => {
          this.result = res;
          this.state = 'success';
          this.uploadComplete.emit(res);
        },
        error: (err) => {
          const msg = err?.error?.detail?.[0]?.msg ?? err?.error?.detail ?? 'Upload failed';
          this.setError(typeof msg === 'string' ? msg : JSON.stringify(msg));
          this.uploadError.emit(this.errorMessage);
        },
      });
  }

  reset() {
    this.state = 'idle';
    this.result = null;
    this.errorMessage = '';
  }

  private setError(msg: string) {
    this.state = 'error';
    this.errorMessage = msg;
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
