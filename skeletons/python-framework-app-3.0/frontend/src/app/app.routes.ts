import { Routes } from '@angular/router';
import { authGuard } from 'refresquito-angular';
import { Forbidden, Home } from './pages/home';
{%- if values.processes %}
import { Tasks } from './pages/tasks';
{%- endif %}
import { ${{ values.entityTitle }}Detail } from './${{ values.entities }}/${{ values.entity }}-detail';
import { ${{ values.entityTitle }}Form } from './${{ values.entities }}/${{ values.entity }}-form';
import { ${{ values.entityTitle }}List } from './${{ values.entities }}/${{ values.entity }}-list';
import { ADMIN, VIEWER } from './roles';

export const routes: Routes = [
  { path: '', component: Home, title: '${{ values.title }}' },
  { path: '${{ values.entities }}', component: ${{ values.entityTitle }}List, title: '${{ values.entitiesTitle }}', canActivate: [authGuard], data: { roles: [VIEWER, ADMIN] } },
  { path: '${{ values.entities }}/new', component: ${{ values.entityTitle }}Form, title: 'New ${{ values.entity }}', canActivate: [authGuard], data: { roles: [ADMIN] } },
  { path: '${{ values.entities }}/:id/edit', component: ${{ values.entityTitle }}Form, title: 'Edit ${{ values.entity }}', canActivate: [authGuard], data: { roles: [ADMIN] } },
  { path: '${{ values.entities }}/:id', component: ${{ values.entityTitle }}Detail, title: '${{ values.entityTitle }}', canActivate: [authGuard], data: { roles: [VIEWER, ADMIN] } },
{%- if values.processes %}
  // block processes: the tasks of the user
  { path: 'tasks', component: Tasks, title: 'My tasks', canActivate: [authGuard], data: { roles: [VIEWER, ADMIN] } },
{%- endif %}
  { path: 'forbidden', component: Forbidden, title: 'Not allowed' },
  { path: '**', redirectTo: '' },
];
