import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { AuthService } from 'refresquito-angular';
import { ADMIN, VIEWER } from '../roles';

@Component({
  selector: 'app-home',
  imports: [RouterLink],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <section class="card hero">
      <h1>${{ values.title }}</h1>
      <p>The example application of the Refresquito frameworks: Angular, FastAPI and PostgreSQL.</p>
      @if (!auth.isLoggedIn()) {
        <button type="button" class="primary" (click)="auth.login('/${{ values.entities }}')">Sign in</button>
      } @else if (auth.hasRole(viewer, admin)) {
        <a class="button primary" routerLink="/${{ values.entities }}">See the ${{ values.entities }}</a>
      } @else {
        <p class="empty">Your user has no ${{ values.name }} role yet. Ask for <code>${{ values.name }}-viewer</code> or <code>${{ values.name }}-admin</code>.</p>
      }
    </section>
  `,
})
export class Home {
  protected readonly auth = inject(AuthService);
  protected readonly viewer = VIEWER;
  protected readonly admin = ADMIN;
}

@Component({
  selector: 'app-forbidden',
  imports: [RouterLink],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <section class="card hero">
      <h1>Not allowed</h1>
      <p>Your user does not have the role this page needs.</p>
      <a class="button" routerLink="/">Back to the start</a>
    </section>
  `,
})
export class Forbidden {}
