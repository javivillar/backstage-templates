import { DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject, input, numberAttribute, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { RqHasRole } from 'refresquito-angular';
import { ${{ values.entityTitle }}, ${{ values.entityTitle }}Api } from '../api/${{ values.entities }}';
import { ADMIN } from '../roles';
{%- if (values.sites | length) > 0 %}
import { ${{ values.entityTitle }}Documents } from './${{ values.entity }}-documents';
{%- endif %}
{%- if (values.buckets | length) > 0 %}
import { ${{ values.entityTitle }}Files } from './${{ values.entity }}-files';
{%- endif %}
{%- if values.processes %}
import { ${{ values.entityTitle }}Review } from './${{ values.entity }}-review';
{%- endif %}
{%- if values.flows %}
import { ${{ values.entityTitle }}Welcome } from './${{ values.entity }}-welcome';
{%- endif %}

/** A ${{ values.entity }}, and what the ${{ values.name }} keeps of it in the platform blocks it declares (one component each). */
@Component({
  selector: 'app-${{ values.entity }}-detail',
  imports: [
    DatePipe,
    RouterLink,
    RqHasRole,
{%- if values.processes %}
    ${{ values.entityTitle }}Review, // block processes
{%- endif %}
{%- if values.flows %}
    ${{ values.entityTitle }}Welcome, // block flows
{%- endif %}
{%- if (values.buckets | length) > 0 %}
    ${{ values.entityTitle }}Files, // block s3
{%- endif %}
{%- if (values.sites | length) > 0 %}
    ${{ values.entityTitle }}Documents, // block dms
{%- endif %}
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './${{ values.entity }}-detail.html',
})
export class ${{ values.entityTitle }}Detail {
  /** From the route: ${{ values.entities }}/:id */
  readonly id = input.required({ transform: numberAttribute });
  private readonly api = inject(${{ values.entityTitle }}Api);

  protected readonly admin = ADMIN;
  protected readonly ${{ values.entity }} = signal<${{ values.entityTitle }} | null>(null);

  ngOnInit(): void {
    this.api.get(this.id()).subscribe((${{ values.entity }}) => this.${{ values.entity }}.set(${{ values.entity }}));
  }
}
