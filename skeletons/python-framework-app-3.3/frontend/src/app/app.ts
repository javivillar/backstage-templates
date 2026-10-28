import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { ConfigService, RqNavItem, RqShell } from 'refresquito-angular';
import { ADMIN, VIEWER } from './roles';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RqShell],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './app.html',
})
export class App {
  /** The stage of this deployment (config.json, `stage`): shown next to the name, none in pro. */
  protected readonly stage = stageOf(inject(ConfigService));
  protected readonly nav: RqNavItem[] = [
    { label: '${{ values.entitiesTitle }}', link: '/${{ values.entities }}', icon: 'collection', roles: [VIEWER, ADMIN] },
{%- if values.processes %}
    { label: 'My tasks', link: '/tasks', icon: 'check2-square', roles: [VIEWER, ADMIN] },
{%- endif %}
{%- if values.dashboards %}
    { label: 'Dashboard', link: '/dashboard', icon: 'bar-chart', section: 'Analysis', roles: [VIEWER, ADMIN] },
{%- endif %}
{%- if values.flows %}
    { label: 'Flows', link: '/flows', icon: 'activity', section: 'Analysis', roles: [VIEWER, ADMIN] },
{%- endif %}
  ];
}

function stageOf(config: ConfigService): string | null {
  try {
    const stage = config.config()['stage'];
    return typeof stage === 'string' && stage !== 'pro' ? stage : null;
  } catch {
    return null;
  }
}
