// src/app/auth/login/login.component.ts
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  FormBuilder,
  FormGroup,
  Validators,
  ReactiveFormsModule,
} from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { RoutePersistenceService } from '../../core/services/route-persistence.service';
import { PermissionService } from '../../core/services/permission.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css'],
})
export class LoginComponent {
  form: FormGroup;
  loading = false;
  errorMessage: string | null = null;

  // para el footer
  currentYear = new Date().getFullYear();
  // para mostrar/ocultar contraseña
  hidePassword = true;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router,
    private routePersistence: RoutePersistenceService,
    private permissionService: PermissionService
  ) {
    this.form = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required]],
    });
  }

  submit(): void {
    this.errorMessage = null;

    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const { email, password } = this.form.value;
    this.loading = true;

    this.authService.login(email, password).subscribe({
      next: (loginResponse) => {
        // Si debe cambiar contraseña, redirigir directamente
        if (loginResponse.must_change_password) {
          this.loading = false;
          this.router.navigate(['/change-password']);
          return;
        }

        this.authService.loadCurrentUser().subscribe({
          next: (user) => {
            this.loading = false;
            // Redirigir a clientes a su portal dedicado
            if (user && this.permissionService.isClient(user)) {
              this.router.navigate(['/client/dashboard']);
            } else {
              const targetRoute =
                this.routePersistence.getStoredRoute() ?? '/inicio';
              this.router.navigateByUrl(targetRoute);
            }
          },
          error: (err: unknown) => {
            console.error('Error cargando /auth/me', err);
            this.loading = false;
            this.errorMessage =
              'No se pudo obtener la información del usuario.';
          },
        });
      },
      error: (err: unknown) => {
        console.error('Login error', err);
        this.loading = false;
        this.errorMessage = 'El email o la contraseña son incorrectos.';
      },
    });
  }

  hasError(controlName: string, error: string): boolean {
    const control = this.form.get(controlName);
    return !!control && control.touched && control.hasError(error);
  }

  togglePassword(): void {
    this.hidePassword = !this.hidePassword;
  }
}
