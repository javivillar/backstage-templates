import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { ConfigService } from 'refresquito-angular';
import { Observable } from 'rxjs';
import { components } from './schema';

// the types come from the OpenAPI document of the backend (npm run gen:api)
export type ${{ values.entityTitle }} = components['schemas']['${{ values.entityTitle }}Out'];
export type ${{ values.entityTitle }}Input = components['schemas']['${{ values.entityTitle }}In'];
export type ${{ values.entityTitle }}Status = components['schemas']['${{ values.entityTitle }}Status'];
export type ${{ values.entityTitle }}Page = components['schemas']['Page_${{ values.entityTitle }}Out_'];

export const STATUSES: ${{ values.entityTitle }}Status[] = ['active', 'pending', 'closed'];

export interface ${{ values.entityTitle }}Filter {
  page?: number;
  size?: number;
  status?: ${{ values.entityTitle }}Status | '';
  category?: string;
}

@Injectable({ providedIn: 'root' })
export class ${{ values.entityTitle }}Api {
  private readonly http = inject(HttpClient);
  private readonly config = inject(ConfigService);

  private get url(): string {
    return `${this.config.apiUrl}/api/${{ values.entities }}`;
  }

  list(filter: ${{ values.entityTitle }}Filter = {}): Observable<${{ values.entityTitle }}Page> {
    const params: Record<string, string | number> = { page: filter.page ?? 1, size: filter.size ?? 10 };
    if (filter.status) {
      params['status'] = filter.status;
    }
    if (filter.category?.trim()) {
      params['category'] = filter.category.trim();
    }
    return this.http.get<${{ values.entityTitle }}Page>(this.url, { params });
  }

  get(id: number): Observable<${{ values.entityTitle }}> {
    return this.http.get<${{ values.entityTitle }}>(`${this.url}/${id}`);
  }

  create(${{ values.entity }}: ${{ values.entityTitle }}Input): Observable<${{ values.entityTitle }}> {
    return this.http.post<${{ values.entityTitle }}>(this.url, ${{ values.entity }});
  }

  update(id: number, ${{ values.entity }}: ${{ values.entityTitle }}Input): Observable<${{ values.entityTitle }}> {
    return this.http.put<${{ values.entityTitle }}>(`${this.url}/${id}`, ${{ values.entity }});
  }

  remove(id: number): Observable<void> {
    return this.http.delete<void>(`${this.url}/${id}`);
  }
}
