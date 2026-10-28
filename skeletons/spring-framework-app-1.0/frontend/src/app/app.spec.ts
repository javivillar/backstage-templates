import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { FakeAuthService, provideRefresquitoTesting } from 'refresquito-angular/testing';
import { App } from './app';
import { Forbidden, Home } from './pages/home';
import { ADMIN, VIEWER } from './roles';

describe('App', () => {
  async function render<T>(component: new () => T, user: { name?: string; roles: string[] } | null) {
    TestBed.configureTestingModule({ providers: [provideRouter([]), provideRefresquitoTesting({ user })] });
    const fixture = TestBed.createComponent(component);
    await fixture.whenStable();
    fixture.detectChanges();
    return { fixture, el: fixture.nativeElement as HTMLElement, auth: TestBed.inject(FakeAuthService) };
  }

  it('offers to sign in when nobody is', async () => {
    const { el, auth } = await render(App, null);
    expect(el.querySelector('.rq-shell-link')).toBeNull();
    (el.querySelector('.btn-rq-header') as HTMLButtonElement).click();
    expect(auth.logins.length).toBe(1);
  });

  it('shows the user, the menu of its role and signs out', async () => {
    const { el, auth } = await render(App, { name: 'Ana García', roles: [VIEWER] });
    expect(el.querySelector('.rq-shell-user-name')?.textContent).toBe('Ana García');
    expect(el.querySelector('.rq-shell-link')?.getAttribute('href')).toBe('/${{ values.entities }}');
    (el.querySelector('.btn-rq-header') as HTMLButtonElement).click();
    expect(auth.logouts).toBe(1);
  });

  it('home: sign in, go to the ${{ values.entities }}, or explain the missing role', async () => {
    let page = await render(Home, null);
    (page.el.querySelector('button') as HTMLButtonElement).click();
    expect(page.auth.logins).toEqual(['/${{ values.entities }}']);
    TestBed.resetTestingModule();
    page = await render(Home, { roles: [ADMIN] });
    expect(page.el.querySelector('a')?.getAttribute('href')).toBe('/${{ values.entities }}');
    TestBed.resetTestingModule();
    page = await render(Home, { roles: ['something-else'] });
    expect(page.el.querySelector('.empty')?.textContent).toContain('${{ values.name }}-viewer');
  });

  it('forbidden page links back to the start', async () => {
    const { el } = await render(Forbidden, { roles: [] });
    expect(el.querySelector('a')?.getAttribute('href')).toBe('/');
  });
});
