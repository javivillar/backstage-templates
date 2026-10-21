import { ChangeDetectionStrategy, Component, inject, input, OnInit, signal } from '@angular/core';
import { NonNullableFormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { NotificationService, RqHttpError } from 'refresquito-angular';
import { ${{ values.entityTitle }}Api, ${{ values.entityTitle }}Input, ${{ values.entityTitle }}Status, STATUSES } from '../api/${{ values.entities }}';

@Component({
  selector: 'app-${{ values.entity }}-form',
  imports: [ReactiveFormsModule, RouterLink],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './${{ values.entity }}-form.html',
})
export class ${{ values.entityTitle }}Form implements OnInit {
  /** Route parameter: the ${{ values.entity }} to edit; without it, a new one. */
  readonly id = input<string>();

  private readonly api = inject(${{ values.entityTitle }}Api);
  private readonly router = inject(Router);
  private readonly notifications = inject(NotificationService);

  protected readonly statuses = STATUSES;
  protected readonly saving = signal(false);
  /** What the API said about each field. */
  protected readonly fieldErrors = signal<Record<string, string>>({});
  protected readonly form = inject(NonNullableFormBuilder).group({
    name: ['', [Validators.required, Validators.maxLength(80)]],
    category: ['', [Validators.required, Validators.maxLength(40)]],
    status: ['active' as ${{ values.entityTitle }}Status],
    start_date: [''],
  });

  ngOnInit(): void {
    const id = this.id();
    if (id) {
      this.api.get(Number(id)).subscribe({
        next: (${{ values.entity }}) => this.form.setValue({ name: ${{ values.entity }}.name, category: ${{ values.entity }}.category, status: ${{ values.entity }}.status, start_date: ${{ values.entity }}.start_date ?? '' }),
        error: () => this.router.navigateByUrl('/${{ values.entities }}'),
      });
    }
  }

  protected save(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const value = this.form.getRawValue();
    const ${{ values.entity }}: ${{ values.entityTitle }}Input = { ...value, start_date: value.start_date || null };
    const id = this.id();
    this.saving.set(true);
    this.fieldErrors.set({});
    (id ? this.api.update(Number(id), ${{ values.entity }}) : this.api.create(${{ values.entity }})).subscribe({
      next: (saved) => {
        this.notifications.success(`${saved.name} was saved`);
        this.router.navigateByUrl('/${{ values.entities }}');
      },
      error: (error: RqHttpError) => {
        this.saving.set(false);
        this.fieldErrors.set(error.code === '${{ values.entity }}_name_taken' ? { name: error.message } : error.fieldErrors);
      },
    });
  }

  protected problem(field: 'name' | 'category' | 'status' | 'start_date'): string | null {
    const fromApi = this.fieldErrors()[field];
    if (fromApi) {
      return fromApi;
    }
    const control = this.form.controls[field];
    if (!control.touched || control.valid) {
      return null;
    }
    return control.hasError('required') ? 'It is required' : 'It is too long';
  }
}
