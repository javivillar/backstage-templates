import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { RouterLink, RouterOutlet } from '@angular/router';
import { AuthService, RqHasRole, RqNotifications } from 'refresquito-angular';
import { ADMIN, VIEWER } from './roles';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, RqNotifications, RqHasRole],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './app.html',
})
export class App {
  protected readonly auth = inject(AuthService);
  protected readonly readers = [VIEWER, ADMIN];
}
