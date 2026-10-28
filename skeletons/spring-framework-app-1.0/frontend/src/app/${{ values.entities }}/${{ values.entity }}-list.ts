import { DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { NotificationService, RqHasRole } from 'refresquito-angular';
import { ${{ values.entityTitle }}, ${{ values.entityTitle }}Api, ${{ values.entityTitle }}Page, ${{ values.entityTitle }}Status, STATUSES } from '../api/${{ values.entities }}';
import { ADMIN } from '../roles';

@Component({
  selector: 'app-${{ values.entity }}-list',
  imports: [DatePipe, FormsModule, RouterLink, RqHasRole],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './${{ values.entity }}-list.html',
})
export class ${{ values.entityTitle }}List {
  private readonly api = inject(${{ values.entityTitle }}Api);
  private readonly notifications = inject(NotificationService);

  protected readonly admin = ADMIN;
  protected readonly statuses = STATUSES;
  protected readonly size = 10;
  protected readonly status = signal<${{ values.entityTitle }}Status | ''>('');
  protected readonly category = signal('');
  protected readonly page = signal<${{ values.entityTitle }}Page | null>(null);
  protected readonly loading = signal(false);
  protected readonly pages = computed(() => Math.max(1, Math.ceil((this.page()?.total ?? 0) / this.size)));

  constructor() {
    this.load(1);
  }

  protected load(page: number): void {
    this.loading.set(true);
    this.api.list({ page, size: this.size, status: this.status(), category: this.category() }).subscribe({
      next: (result) => {
        this.page.set(result);
        this.loading.set(false);
      },
      error: () => this.loading.set(false), // the framework already told the user
    });
  }

  protected remove(${{ values.entity }}: ${{ values.entityTitle }}): void {
    if (!confirm(`Delete ${${{ values.entity }}.name}?`)) {
      return;
    }
    this.api.remove(${{ values.entity }}.id).subscribe(() => {
      this.notifications.success(`${${{ values.entity }}.name} was deleted`);
      const current = this.page();
      // the last row of a page: go back one
      this.load(current && current.items.length === 1 && current.page > 1 ? current.page - 1 : (current?.page ?? 1));
    });
  }
}
