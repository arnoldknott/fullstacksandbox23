import { describe, it, expect, afterEach } from 'vitest';
import { render, screen, cleanup } from '@testing-library/svelte';
import UserForm from './UserForm.svelte';

afterEach(() => cleanup());

describe('Register form', () => {
	it.todo('should have an email, password  and name field', () => {
		render(UserForm, { type: 'signup' });
		// const name = screen.queryByLabelText('Full name');
		// const email = screen.queryByLabelText('Email address');
		// const password = screen.queryByLabelText('Password');

		// expect(name).toBeTruthy();
		// expect(email).toBeTruthy();
		// expect(password).toBeTruthy();
		const name = screen.queryByText('Full name');
		const email = screen.queryByText('Email address');
		const password = screen.queryByText('Password');

		expect(name).toContain('Full name');
		expect(email).toContain('Email address');
		expect(password).toContain('Password');
	});
	it.todo('should have a register button', async () => {
		render(UserForm, { type: 'signup' });
		const register = screen.getByRole('button');
		expect(register.innerHTML).toContain('Sign up');
	});
});

describe('Login form', () => {
	it.todo('should have an email, password and no name field', () => {
		render(UserForm);
		const name = screen.queryByLabelText('Full name');
		const email = screen.queryByLabelText('Email address');
		const password = screen.queryByLabelText('Password');

		expect(name).toBeFalsy();
		expect(email).toBeTruthy();
		expect(password).toBeTruthy();
	});
	it.todo('should have a login button', () => {
		render(UserForm);
		const register = screen.getByRole('button');
		expect(register.innerHTML).toContain('Log in');
	});
});
