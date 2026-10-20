import { DatePipe } from '@angular/common';
import { HttpTestingController } from '@angular/common/http/testing';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { RouterLink, provideRouter } from '@angular/router';
import { RqHasRole } from 'refresquito-angular';
import { provideRefresquitoTesting } from 'refresquito-angular/testing';
import { ADMIN } from '../roles';
import { API, ${{ values.entity }}, request } from '../testing';
import { ${{ values.entityTitle }}Detail } from './${{ values.entity }}-detail';

describe('${{ values.entityTitle }}Detail', () => {
  it('shows the ${{ values.entity }} (each platform block has its own component and test)', async () => {
    TestBed.configureTestingModule({ providers: [provideRouter([]), provideRefresquitoTesting({ user: { roles: [ADMIN] } })] });
    TestBed.overrideComponent(${{ values.entityTitle }}Detail, { set: { imports: [DatePipe, RouterLink, RqHasRole], schemas: [NO_ERRORS_SCHEMA] } });
    const fixture = TestBed.createComponent(${{ values.entityTitle }}Detail);
    fixture.componentRef.setInput('id', '7');
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Loading');
    (await request('GET', `${API}/7`)).flush(${{ values.entity }}(7, { name: 'Rex', category: 'tools' }));
    await fixture.whenStable();
    fixture.detectChanges();
    const el = fixture.nativeElement as HTMLElement;
    expect(el.querySelector('h1')?.textContent).toBe('Rex');
    expect(el.textContent).toContain('tools');
    expect(el.querySelector('a.button')?.getAttribute('href')).toBe('/${{ values.entities }}/7/edit');
    TestBed.inject(HttpTestingController).verify();
  });
});
