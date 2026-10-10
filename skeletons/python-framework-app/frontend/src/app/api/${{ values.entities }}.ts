import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { ConfigService } from 'refresquito-angular';
import { Observable } from 'rxjs';
import { components } from './schema';

// the types come from the OpenAPI document of the backend (npm run gen:api)
export type ${{ values.Entity }} = components['schemas']['${{ values.Entity }}Out'];
export type ${{ values.Entity }}Input = components['schemas']['${{ values.Entity }}In'];
export type ${{ values.Entity }}Status = components['schemas']['${{ values.Entity }}Status'];
export type ${{ values.Entity }}Page = components['schemas']['Page_${{ values.Entity }}Out_'];

export const STATUSES: ${{ values.Entity }}Status[] = ['active', 'pending', 'closed'];

export interface ${{ values.Entity }}Filter {
  page?: number;
  size?: number;
  status?: ${{ values.Entity }}Status | '';
  category?: string;
}

@Injectable({ providedIn: 'root' })
export class ${{ values.Entity }}Api {
  private readonly http = inject(HttpClient);
  private readonly config = inject(ConfigService);

  private get url(): string {
    return `${this.config.apiUrl}/api/${{ values.entities }}`;
  }

  list(filter: ${{ values.Entity }}Filter = {}): Observable<${{ values.Entity }}Page> {
    const params: Record<string, string | number> = { page: filter.page ?? 1, size: filter.size ?? 10 };
    if (filter.status) {
      params['status'] = filter.status;
    }
    if (filter.category?.trim()) {
      params['category'] = filter.category.trim();
    }
    return this.http.get<${{ values.Entity }}Page>(this.url, { params });
  }

  get(id: number): Observable<${{ values.Entity }}> {
    return this.http.get<${{ values.Entity }}>(`${this.url}/${id}`);
  }

  create(${{ values.entity }}: ${{ values.Entity }}Input): Observable<${{ values.Entity }}> {
    return this.http.post<${{ values.Entity }}>(this.url, ${{ values.entity }});
  }

  update(id: number, ${{ values.entity }}: ${{ values.Entity }}Input): Observable<${{ values.Entity }}> {
    return this.http.put<${{ values.Entity }}>(`${this.url}/${id}`, ${{ values.entity }});
  }

  remove(id: number): Observable<void> {
    return this.http.delete<void>(`${this.url}/${id}`);
  }
}
