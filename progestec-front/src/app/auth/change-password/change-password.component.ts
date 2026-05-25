import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule, AbstractControl, ValidationErrors } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-change-password',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './change-password.component.html',
})
export class ChangePasswordComponent {
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);
  private router = inject(Router);

  form: FormGroup;
  loading = false;
  error = '';
  success = false;
  showPassword = false;
  showConfirmPassword = false;
  currentYear = new Date().getFullYear();

  constructor() {
    this.form = this.fb.group({
      newPassword: ['', [Validators.required, Validators.minLength(6)]],
      confirmPassword: ['', [Validators.required]],
    }, { validators: this.passwordMatchValidator });
  }

  passwordMatchValidator(control: AbstractControl): ValidationErrors | null {
    const password = control.get('newPassword');
    const confirmPassword = control.get('confirmPassword');
    
    if (password && confirmPassword && password.value !== confirmPassword.value) {
      return { passwordMismatch: true };
    }
    return null;
  }

  toggleShowPassword(): void {
    this.showPassword = !this.showPassword;
  }

  toggleShowConfirmPassword(): void {
    this.showConfirmPassword = !this.showConfirmPassword;
  }

  onSubmit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.loading = true;
    this.error = '';

    const { newPassword } = this.form.value;

    this.authService.setPassword(newPassword).subscribe({
      next: () => {
        this.success = true;
        this.loading = false;
        
        // Redirigir después de 2 segundos
        setTimeout(() => {
          // Cargar usuario actualizado y redirigir
          this.authService.loadCurrentUser().subscribe({
            next: (user) => {
              if (user.role_name === 'CLIENT') {
                this.router.navigate(['/client']);
              } else {
                this.router.navigate(['/']);
              }
            },
            error: () => {
              this.router.navigate(['/']);
            }
          });
        }, 2000);
      },
      error: (err) => {
        this.loading = false;
        this.error = err.error?.detail || 'Error al cambiar la contraseña';
      }
    });
  }

  get f() {
    return this.form.controls;
  }
}
