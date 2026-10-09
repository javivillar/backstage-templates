import { HttpTestingController, TestRequest } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { ${{ values.Entity }}, ${{ values.Entity }}Page } from './api/${{ values.entities }}';

export const API = 'http://api.test/api/${{ values.entities }}';

export function ${{ values.entity }}(id: number, fields: Partial<${{ values.Entity }}> = {}): ${{ values.Entity }} {
  return { id, name: `${{ values.Entity }} ${id}`, category: 'tools', status: 'active', start_date: '2022-05-01', created_at: '2026-10-09T10:00:00Z', created_by: 'ana', ...fields };
}

export function page(items: ${{ values.Entity }}[], total = items.length, number = 1): ${{ values.Entity }}Page {
  return { items, total, page: number, size: 10 };
}

/** The request the application just made. The token is added asynchronously, so it waits a turn first. */
export async function request(method: string, url: string): Promise<TestRequest> {
  await new Promise<void>((resolve) => setTimeout(resolve));
  return TestBed.inject(HttpTestingController).expectOne((r) => r.method === method && r.urlWithParams === url);
}
