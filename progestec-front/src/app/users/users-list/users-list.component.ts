import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { UserService } from '../../core/services/user.service';
import { UserReadMinimal, UserCreate, UserUpdate } from '../../core/models/user';
import { AuthenticatedLayoutComponent } from '../../core/layouts/authenticated-layout.component';

interface Role {
  id: number;
  name: string;
  label: string;
}

@Component({
  selector: 'app-users-list',
  standalone: true,
  imports: [CommonModule, FormsModule, AuthenticatedLayoutComponent],
  templateUrl: './users-list.component.html',
  styleUrl: './users-list.component.css'
})
export class UsersListComponent implements OnInit {
  private userService = inject(UserService);

  users: UserReadMinimal[] = [];
  filteredUsers: UserReadMinimal[] = [];
  loading = true;
  error = '';

  // Filtros
  searchTerm = '';
  selectedRole = '';

  // Modales
  showCreateModal = false;
  showEditModal = false;
  showViewModal = false;
  showDeleteModal = false;

  // Usuario seleccionado
  selectedUser: UserReadMinimal | null = null;

  // Formulario
  formData = {
    full_name: '',
    email: '',
    password: '',
    phone: '',
    identification: '',
    identification_type: 'CC',
    role_id: 4 // CLIENT por defecto
  };

  // Roles disponibles
  roles: Role[] = [
    { id: 1, name: 'ADMIN', label: 'Administrador' },
    { id: 2, name: 'ADVISOR', label: 'Asesor' },
    { id: 3, name: 'TECHNICIAN', label: 'Técnico' },
    { id: 4, name: 'CLIENT', label: 'Cliente' },
    { id: 5, name: 'COURIER', label: 'Mensajero' }
  ];

  identificationTypes = [
    { value: 'CC', label: 'Cédula' },
    { value: 'CE', label: 'Cédula Extranjería' },
    { value: 'NIT', label: 'NIT' },
    { value: 'PAS', label: 'Pasaporte' },
    { value: 'TI', label: 'Tarjeta Identidad' }
  ];

  submitting = false;

  ngOnInit(): void {
    this.loadUsers();
  }

  loadUsers(): void {
    this.loading = true;
    this.error = '';

    this.userService.listUsers().subscribe({
      next: (users) => {
        this.users = users;
        this.applyFilters();
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Error al cargar los usuarios';
        this.loading = false;
        console.error(err);
      }
    });
  }

  applyFilters(): void {
    let result = [...this.users];

    // Filtro por rol
    if (this.selectedRole) {
      result = result.filter(u => u.role_name === this.selectedRole);
    }

    // Filtro por búsqueda
    if (this.searchTerm.trim()) {
      const term = this.searchTerm.toLowerCase();
      result = result.filter(u =>
        u.full_name?.toLowerCase().includes(term) ||
        u.email?.toLowerCase().includes(term) ||
        u.phone?.includes(term) ||
        u.identification?.includes(term)
      );
    }

    this.filteredUsers = result;
  }

  // Modales
  openCreateModal(): void {
    this.resetForm();
    this.showCreateModal = true;
  }

  openEditModal(user: UserReadMinimal): void {
    this.selectedUser = user;
    this.formData = {
      full_name: user.full_name || '',
      email: user.email || '',
      password: '',
      phone: user.phone || '',
      identification: user.identification || '',
      identification_type: user.identification_type || 'CC',
      role_id: user.role_id || 4
    };
    this.showEditModal = true;
  }

  openViewModal(user: UserReadMinimal): void {
    this.selectedUser = user;
    this.showViewModal = true;
  }

  openDeleteModal(user: UserReadMinimal): void {
    this.selectedUser = user;
    this.showDeleteModal = true;
  }

  closeModals(): void {
    this.showCreateModal = false;
    this.showEditModal = false;
    this.showViewModal = false;
    this.showDeleteModal = false;
    this.selectedUser = null;
  }

  resetForm(): void {
    this.formData = {
      full_name: '',
      email: '',
      password: '',
      phone: '',
      identification: '',
      identification_type: 'CC',
      role_id: 4
    };
  }

  // CRUD
  createUser(): void {
    if (!this.formData.full_name || !this.formData.email || !this.formData.password) {
      return;
    }

    this.submitting = true;

    const createData: UserCreate = {
      full_name: this.formData.full_name,
      email: this.formData.email,
      password: this.formData.password,
      phone: this.formData.phone,
      identification: this.formData.identification,
      identification_type: this.formData.identification_type,
      role_id: this.formData.role_id
    };

    this.userService.createUser(createData).subscribe({
      next: () => {
        this.closeModals();
        this.loadUsers();
        this.submitting = false;
      },
      error: (err) => {
        console.error(err);
        this.submitting = false;
      }
    });
  }

  updateUser(): void {
    if (!this.selectedUser) return;

    this.submitting = true;

    const updateData: UserUpdate = {
      full_name: this.formData.full_name,
      phone: this.formData.phone,
      identification_type: this.formData.identification_type,
      role_id: this.formData.role_id
    };

    this.userService.updateUser(this.selectedUser.id, updateData).subscribe({
      next: () => {
        this.closeModals();
        this.loadUsers();
        this.submitting = false;
      },
      error: (err) => {
        console.error(err);
        this.submitting = false;
      }
    });
  }

  deleteUser(): void {
    if (!this.selectedUser) return;

    this.submitting = true;

    this.userService.changeUserState(this.selectedUser.id, 0).subscribe({
      next: () => {
        this.closeModals();
        this.loadUsers();
        this.submitting = false;
      },
      error: (err) => {
        console.error(err);
        this.submitting = false;
      }
    });
  }

  // Helpers
  getRoleBadgeClass(roleName: string | null | undefined): string {
    const classes: Record<string, string> = {
      'ADMIN': 'badge-danger',
      'ADVISOR': 'badge-purple',
      'TECHNICIAN': 'badge-info',
      'CLIENT': 'badge-success',
      'COURIER': 'badge-warning'
    };
    return classes[roleName || ''] || 'badge-secondary';
  }

  getRoleLabel(roleName: string | null | undefined): string {
    if (!roleName) return 'Sin rol';
    const role = this.roles.find(r => r.name === roleName);
    return role?.label || roleName;
  }

  getIdentificationTypeLabel(type: string | null | undefined): string {
    if (!type) return 'N/A';
    const t = this.identificationTypes.find(i => i.value === type);
    return t?.label || type;
  }

  formatDate(dateStr: string | null | undefined): string {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr);
    return date.toLocaleDateString('es-CO', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  }

  getUserInitials(name: string | null | undefined): string {
    if (!name) return '?';
    return name.split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase();
  }
}
