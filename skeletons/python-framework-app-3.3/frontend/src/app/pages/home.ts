import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { AuthService } from 'refresquito-angular';
import { ADMIN, VIEWER } from '../roles';

@Component({
  selector: 'app-home',
  imports: [RouterLink],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <section class="card text-center py-5 px-4">
      <div class="mx-auto mb-3 ${{ values.entity }}-avatar"><i class="bi bi-grid-3x3-gap-fill" aria-hidden="true"></i></div>
      <h1 class="fw-bold">${{ values.title }}</h1>
      <p class="text-body-secondary mb-4">The example application of the Refresquito frameworks: Angular, FastAPI and PostgreSQL.</p>
      @if (!auth.isLoggedIn()) {
        <div><button type="button" class="btn btn-primary btn-lg" (click)="auth.login('/${{ values.entities }}')">Sign in</button></div>
      } @else if (auth.hasRole(viewer, admin)) {
        <div><a class="btn btn-primary btn-lg" routerLink="/${{ values.entities }}">See the ${{ values.entities }}</a></div>
      } @else {
        <p class="empty alert alert-warning d-inline-block mb-0">Your user has no ${{ values.name }} role yet. Ask for <code>${{ values.name }}-viewer</code> or <code>${{ values.name }}-admin</code>.</p>
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
    <section class="card text-center py-5 px-4">
      <h1 class="fw-bold"><i class="bi bi-shield-lock me-2" aria-hidden="true"></i>Not allowed</h1>
      <p class="text-body-secondary">Your user does not have the role this page needs.</p>
      <div><a class="btn btn-outline-secondary" routerLink="/">Back to the start</a></div>
    </section>
  `,
})
export class Forbidden {}
