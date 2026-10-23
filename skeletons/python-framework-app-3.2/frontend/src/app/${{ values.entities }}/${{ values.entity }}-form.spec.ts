import { HttpTestingController } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router, provideRouter } from '@angular/router';
import { NotificationService } from 'refresquito-angular';
import { provideRefresquitoTesting } from 'refresquito-angular/testing';
import { ADMIN } from '../roles';
import { API, ${{ values.entity }}, request } from '../testing';
import { ${{ values.entityTitle }}Form } from './${{ values.entity }}-form';

describe('${{ values.entityTitle }}Form', () => {
  let fixture: ComponentFixture<${{ values.entityTitle }}Form>;
  let navigate: jasmine.Spy;
  const el = () => fixture.nativeElement as HTMLElement;
  const errors = () => [...el().querySelectorAll('.field-error')].map((e) => e.textContent);
  const settle = async () => {
    await fixture.whenStable();
    fixture.detectChanges();
  };

  function type(control: string, value: string) {
    const input = el().querySelector(`[formControlName="${control}"]`) as HTMLInputElement;
    input.value = value;
    input.dispatchEvent(new Event(input.tagName === 'SELECT' ? 'change' : 'input'));
  }
  const submit = () => (el().querySelector('button[type=submit]') as HTMLButtonElement).click();

  async function open(id?: string) {
    TestBed.configureTestingModule({ providers: [provideRouter([]), provideRefresquitoTesting({ user: { roles: [ADMIN] } })] });
    navigate = spyOn(TestBed.inject(Router), 'navigateByUrl').and.resolveTo(true);
    spyOn(console, 'warn');
    fixture = TestBed.createComponent(${{ values.entityTitle }}Form);
    if (id) {
      fixture.componentRef.setInput('id', id);
    }
    fixture.detectChanges();
  }
  afterEach(() => TestBed.inject(HttpTestingController).verify());

  it('creates a ${{ values.entity }} and goes back to the list', async () => {
    await open();
    expect(el().querySelector('h1')?.textContent).toBe('New ${{ values.entity }}');
    type('name', 'Rex');
    type('category', 'tools');
    submit();
    const call = await request('POST', API);
    expect(call.request.body).toEqual({ name: 'Rex', category: 'tools', status: 'active', start_date: null });
    call.flush(${{ values.entity }}(1, { name: 'Rex' }));
    expect(navigate).toHaveBeenCalledWith('/${{ values.entities }}');
    expect(TestBed.inject(NotificationService).messages().map((n) => n.message)).toEqual(['Rex was saved']);
  });

  it('does not call the API with an invalid form', async () => {
    await open();
    submit();
    await settle();
    expect(errors()).toEqual(['It is required', 'It is required']);
    type('name', 'x'.repeat(81));
    await settle();
    expect(errors()[0]).toBe('It is too long');
  });

  it('shows what the API says about each field', async () => {
    await open();
    type('name', 'Rex');
    type('category', 'tools');
    type('start_date', '2999-01-01');
    submit();
    (await request('POST', API)).flush(
      { status: 422, code: 'validation_error', title: 'Unprocessable', errors: [{ field: 'start_date', message: 'Value error, it cannot be in the future' }] },
      { status: 422, statusText: 'x' },
    );
    await settle();
    expect(errors()).toEqual(['Value error, it cannot be in the future']);
    expect((el().querySelector('button[type=submit]') as HTMLButtonElement).disabled).toBeFalse();
    expect(navigate).not.toHaveBeenCalled();
  });

  it('puts a taken name next to the name', async () => {
    await open();
    type('name', 'Rex');
    type('category', 'tools');
    submit();
    (await request('POST', API)).flush(
      { status: 409, code: '${{ values.entity }}_name_taken', detail: 'There is already a ${{ values.entity }} called Rex' },
      { status: 409, statusText: 'x' },
    );
    await settle();
    expect(errors()).toEqual(['There is already a ${{ values.entity }} called Rex']);
  });

  it('loads the ${{ values.entity }} to edit and saves it with PUT', async () => {
    await open('7');
    (await request('GET', `${API}/7`)).flush(${{ values.entity }}(7, { name: 'Tom', category: 'books', status: 'pending', start_date: null }));
    await settle();
    expect(el().querySelector('h1')?.textContent).toBe('Edit ${{ values.entity }}');
    expect((el().querySelector('[formControlName="name"]') as HTMLInputElement).value).toBe('Tom');
    type('status', 'closed');
    submit();
    const call = await request('PUT', `${API}/7`);
    expect(call.request.body).toEqual({ name: 'Tom', category: 'books', status: 'closed', start_date: null });
    call.flush(${{ values.entity }}(7, { name: 'Tom' }));
    expect(navigate).toHaveBeenCalledWith('/${{ values.entities }}');
  });

  it('goes back to the list when the ${{ values.entity }} to edit does not exist', async () => {
    await open('99');
    (await request('GET', `${API}/99`)).flush({ status: 404, code: 'not_found', detail: '${{ values.entityTitle }} 99 does not exist' }, { status: 404, statusText: 'x' });
    expect(navigate).toHaveBeenCalledWith('/${{ values.entities }}');
  });
});
