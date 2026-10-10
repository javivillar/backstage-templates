import { Routes } from '@angular/router';
import { authGuard } from 'refresquito-angular';
import { Forbidden, Home } from './pages/home';
import { ${{ values.Entity }}Form } from './${{ values.entities }}/${{ values.entity }}-form';
import { ${{ values.Entity }}List } from './${{ values.entities }}/${{ values.entity }}-list';
import { ADMIN, VIEWER } from './roles';

export const routes: Routes = [
  { path: '', component: Home, title: '${{ values.title }}' },
  { path: '${{ values.entities }}', component: ${{ values.Entity }}List, title: '${{ values.Entities }}', canActivate: [authGuard], data: { roles: [VIEWER, ADMIN] } },
  { path: '${{ values.entities }}/new', component: ${{ values.Entity }}Form, title: 'New ${{ values.entity }}', canActivate: [authGuard], data: { roles: [ADMIN] } },
  { path: '${{ values.entities }}/:id/edit', component: ${{ values.Entity }}Form, title: 'Edit ${{ values.entity }}', canActivate: [authGuard], data: { roles: [ADMIN] } },
  { path: 'forbidden', component: Forbidden, title: 'Not allowed' },
  { path: '**', redirectTo: '' },
];
