import { HttpTestingController } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { NotificationService } from 'refresquito-angular';
import { provideRefresquitoTesting } from 'refresquito-angular/testing';
import { ADMIN, VIEWER } from '../roles';
import { API, page, ${{ values.entity }}, request } from '../testing';
import { ${{ values.Entity }}List } from './${{ values.entity }}-list';

describe('${{ values.Entity }}List', () => {
  let fixture: ComponentFixture<${{ values.Entity }}List>;
  const el = () => fixture.nativeElement as HTMLElement;
  const rows = () => [...el().querySelectorAll('tbody tr')].map((r) => r.querySelector('td')?.textContent);
  const settle = async () => {
    await fixture.whenStable();
    fixture.detectChanges();
  };

  async function open(role: string, first = page([${{ values.entity }}(1, { name: 'Ada' }), ${{ values.entity }}(2, { name: 'Rex', status: 'closed' })])) {
    TestBed.configureTestingModule({ providers: [provideRouter([]), provideRefresquitoTesting({ user: { roles: [role] } })] });
    fixture = TestBed.createComponent(${{ values.Entity }}List);
    (await request('GET', `${API}?page=1&size=10`)).flush(first);
    await settle();
  }
  afterEach(() => TestBed.inject(HttpTestingController).verify());

  it('lists the ${{ values.entities }} of the first page', async () => {
    await open(VIEWER);
    expect(rows()).toEqual(['Ada', 'Rex']);
    expect(el().querySelector('.status-closed')?.textContent).toBe('closed');
    expect(el().querySelector('.pager span')?.textContent).toContain('Page 1 of 1 · 2 ${{ values.entities }}');
  });

  it('shows the actions that write only to an admin', async () => {
    await open(VIEWER);
    expect(el().querySelector('a[href="/${{ values.entities }}/new"]')).toBeNull();
    expect(el().querySelector('td.actions button')).toBeNull();
    TestBed.resetTestingModule();
    await open(ADMIN);
    expect(el().querySelector('a[href="/${{ values.entities }}/new"]')).not.toBeNull();
    expect(el().querySelectorAll('td.actions button').length).toBe(2);
    expect(el().querySelector('td.actions a')?.getAttribute('href')).toBe('/${{ values.entities }}/1/edit');
  });

  it('says so when nothing matches', async () => {
    await open(VIEWER, page([]));
    expect(el().querySelector('.empty')?.textContent).toContain('No ${{ values.entities }} match');
  });

  it('filters by status and category from the first page', async () => {
    await open(VIEWER);
    const status = el().querySelector('select') as HTMLSelectElement;
    status.value = 'closed';
    status.dispatchEvent(new Event('change'));
    (await request('GET', `${API}?page=1&size=10&status=closed`)).flush(page([${{ values.entity }}(2, { name: 'Rex' })]));
    const category = el().querySelector('input') as HTMLInputElement;
    category.value = ' cat ';
    category.dispatchEvent(new Event('input'));
    (el().querySelector('.filters button') as HTMLButtonElement).click();
    (await request('GET', `${API}?page=1&size=10&status=closed&category=cat`)).flush(page([]));
    await settle();
    expect(rows()).toEqual([]);
  });

  it('moves between pages', async () => {
    await open(VIEWER, page([${{ values.entity }}(1)], 25));
    const [previous, next] = [...el().querySelectorAll('.pager button')] as HTMLButtonElement[];
    expect(previous.disabled).toBeTrue();
    expect(el().querySelector('.pager span')?.textContent).toContain('Page 1 of 3');
    next.click();
    (await request('GET', `${API}?page=2&size=10`)).flush(page([${{ values.entity }}(11)], 25, 2));
    await settle();
    expect(rows()).toEqual(['${{ values.Entity }} 11']);
  });

  it('deletes after asking, and reloads', async () => {
    await open(ADMIN, page([${{ values.entity }}(21, { name: 'Last' })], 21, 3));
    const ask = spyOn(window, 'confirm').and.returnValue(false);
    const button = el().querySelector('td.actions button') as HTMLButtonElement;
    button.click();
    expect(ask).toHaveBeenCalledWith('Delete Last?');
    ask.and.returnValue(true);
    button.click();
    (await request('DELETE', `${API}/21`)).flush(null);
    // it was the only row of page 3: back to page 2
    (await request('GET', `${API}?page=2&size=10`)).flush(page([${{ values.entity }}(11)], 20, 2));
    await settle();
    expect(TestBed.inject(NotificationService).messages().map((n) => n.message)).toEqual(['Last was deleted']);
  });

  it('stops loading when the list fails; the framework tells the user', async () => {
    TestBed.configureTestingModule({ providers: [provideRouter([]), provideRefresquitoTesting({ user: { roles: [VIEWER] } })] });
    spyOn(console, 'warn');
    fixture = TestBed.createComponent(${{ values.Entity }}List);
    (await request('GET', `${API}?page=1&size=10`)).flush({ status: 500, code: 'internal_error', detail: 'Unexpected error', request_id: 'r-1' }, { status: 500, statusText: 'x' });
    await settle();
    expect(el().querySelector('.empty')).toBeNull();
    expect(TestBed.inject(NotificationService).messages()[0]).toEqual(jasmine.objectContaining({ kind: 'error', reference: 'r-1' }));
  });
});
