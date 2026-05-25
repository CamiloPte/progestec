import { Component, OnInit, Inject } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators, FormsModule } from '@angular/forms';
import { forkJoin, Subject } from 'rxjs';
import { debounceTime, distinctUntilChanged } from 'rxjs/operators';
import { HttpErrorResponse } from '@angular/common/http';

import { TicketService } from '../../core/services/ticket.service';
import { DeviceService } from '../../core/services/device.service';
import { UserService } from '../../core/services/user.service';
import { AuthenticatedLayoutComponent } from '../../core/layouts/authenticated-layout.component';
import { AuthService } from '../../core/services/auth.service';
import { CatalogService } from '../../core/services/catalog.service';

import { DeviceReadMinimal } from '../../core/models/device';
import { UserReadMinimal } from '../../core/models/user';
import { CatalogManufacturer, CatalogModel, CatalogVariant } from '../../core/models/catalog';
import { PLATFORM_ID } from '@angular/core';

@Component({
  selector: 'app-ticket-create',
  standalone: true,
  imports: [CommonModule, RouterModule, ReactiveFormsModule, FormsModule, AuthenticatedLayoutComponent],
  templateUrl: './ticket-create.component.html',
  styleUrls: ['./ticket-create.component.css'],
})
export class TicketCreateComponent implements OnInit {
  form: FormGroup;
  clientSearch = '';
  deviceSearch = '';
  loading = false;
  saving = false;
  error: string | null = null;
  searchingClient = false;
  searchingDevice = false;
  creatingClient = false;
  creatingDevice = false;

  clients: UserReadMinimal[] = [];
  filteredClients: UserReadMinimal[] = [];
  devices: DeviceReadMinimal[] = [];
  filteredDevices: DeviceReadMinimal[] = [];
  technicians: UserReadMinimal[] = [];
  manufacturers: CatalogManufacturer[] = [];
  models: CatalogModel[] = [];
  variants: CatalogVariant[] = [];

  selectedManufacturerId: number | null = null;
  selectedModelId: number | null = null;
  selectedVariant: CatalogVariant | null = null;

  selectedClient: UserReadMinimal | null = null;
  selectedDevice: DeviceReadMinimal | null = null;

  showClientModal = false;
  showDeviceModal = false;
  showClientSearchModal = false;
  showDeviceSearchModal = false;
  clientSearchModalQuery = '';
  deviceSearchModalQuery = '';
  newClientForm: FormGroup;
  newDeviceForm: FormGroup;
  deviceFile: File | null = null;

  // Subjects para debounce
  private clientSearchSubject = new Subject<string>();
  private deviceSearchSubject = new Subject<string>();
  private isBrowser = false;

  constructor(
    private fb: FormBuilder,
    private ticketService: TicketService,
    private deviceService: DeviceService,
    private userService: UserService,
    private authService: AuthService,
    private catalogService: CatalogService,
    private router: Router,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {
    this.form = this.fb.group({
      failure_desc: ['', Validators.required],
      diagnosis: [''],
      cost_estimate: [''],
      assignee_user_id: [null],
    });

    this.newClientForm = this.fb.group({
      full_name: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      phone: [''],
      identification: ['', Validators.required],
      identification_type: ['', Validators.required],
    });

    this.newDeviceForm = this.fb.group({
      manufacturer_id: [null, Validators.required],
      model_id: [null, Validators.required],
      variant_id: [null, Validators.required],
      type: ['', Validators.required],
      serial: [''],
      imei: [''],
      brand: ['', Validators.required],
      model: ['', Validators.required],
      notes: [''],
    });
  }

  ngOnInit(): void {
    this.isBrowser = isPlatformBrowser(this.platformId);
    if (!this.isBrowser) {
      return;
    }

    if (!this.authService.isAuthenticated()) {
      this.router.navigate(['/login']);
      return;
    }
    this.loadLookups();
    this.loadManufacturers();

    // Configurar debounce para búsqueda de clientes
    this.clientSearchSubject
      .pipe(debounceTime(300), distinctUntilChanged())
      .subscribe((query) => {
        this.clientSearchModalQuery = query;
        if (query.trim().length >= 2) {
          this.performClientSearch();
        } else {
          this.filteredClients = [];
        }
      });

    // Configurar debounce para búsqueda de dispositivos
    this.deviceSearchSubject
      .pipe(debounceTime(300), distinctUntilChanged())
      .subscribe((query) => {
        this.deviceSearchModalQuery = query;
        if (query.trim().length >= 2) {
          this.performDeviceSearch();
        } else {
          this.filteredDevices = [];
        }
      });
  }

  private loadLookups(): void {
    if (!this.isBrowser) {
      return;
    }
    this.loading = true;
    this.userService.listTechnicians().subscribe({
      next: (technicians) => {
        this.technicians = technicians;
      },
      error: (err) => {
        console.error('Error cargando técnicos', err);
        if (err instanceof HttpErrorResponse && err.status === 401) {
          this.authService.logout();
          this.loading = false;
          this.router.navigate(['/login']);
          return;
        }
        this.error = 'No se pudieron cargar los técnicos.';
      },
      complete: () => {
        this.loading = false;
      },
    });
  }

  // -------------------- selección cliente --------------------
  onSearchClients(): void {
    if (!this.isBrowser) {
      return;
    }
    this.searchingClient = true;
    this.userService.listClients().subscribe({
      next: (clients) => {
        this.clients = clients;
        this.filterClients();
      },
      error: (err) => {
        console.error('Error cargando clientes', err);
        if (err instanceof HttpErrorResponse && err.status === 401) {
          this.authService.logout();
          this.router.navigate(['/login']);
          return;
        }
        this.error = 'No se pudieron cargar los clientes.';
        this.searchingClient = false;
      },
      complete: () => {
        this.searchingClient = false;
      },
    });
  }

  filterClients(): void {
    // si aún no hemos cargado clientes, dispara la búsqueda
    const searchQuery = this.showClientSearchModal ? this.clientSearchModalQuery : this.clientSearch;
    if (!this.clients.length && !this.searchingClient && searchQuery.trim().length > 0) {
      this.onSearchClients();
      return;
    }
    const q = searchQuery.toLowerCase().trim();
    this.filteredClients = this.clients.filter((c) => {
      return (
        (c.full_name || '').toLowerCase().includes(q) ||
        (c.email || '').toLowerCase().includes(q) ||
        (c.identification || '').toLowerCase().includes(q)
      );
    });
  }

  selectClient(client: UserReadMinimal): void {
    this.selectedClient = client;
    this.clientSearch = client.full_name;
    this.loadDevicesForClient(client.id);
    this.filteredClients = [];
    this.clientSearchModalQuery = '';
  }

  clearClientSelection(): void {
    this.selectedClient = null;
    this.clientSearch = '';
    this.filteredClients = this.clients;
    this.selectedDevice = null;
    this.filteredDevices = this.devices;
  }

  // Modal de búsqueda de cliente
  openClientSearchModal(): void {
    this.clientSearchModalQuery = this.clientSearch || '';
    this.showClientSearchModal = true;
    if (this.clientSearchModalQuery) {
      this.onSearchClients();
    }
  }

  closeClientSearchModal(): void {
    this.showClientSearchModal = false;
    this.clientSearchModalQuery = '';
  }

  onClientSearchInput(): void {
    this.clientSearchSubject.next(this.clientSearchModalQuery);
  }

 performClientSearch(): void {
    if (!this.isBrowser) {
      return;
    }
    if (!this.clients.length) {
      this.onSearchClients();
    } else {
      this.filterClients();
    }
  }

  selectClientFromModal(client: UserReadMinimal): void {
    this.selectClient(client);
    this.closeClientSearchModal();
  }

  // Modal de búsqueda de dispositivo
  openDeviceSearchModal(): void {
    if (!this.selectedClient) {
      this.error = 'Primero selecciona o crea un cliente.';
      return;
    }
    this.deviceSearchModalQuery = this.deviceSearch || '';
    this.showDeviceSearchModal = true;
    if (this.deviceSearchModalQuery) {
      this.onSearchDevices();
    }
  }

  closeDeviceSearchModal(): void {
    this.showDeviceSearchModal = false;
    this.deviceSearchModalQuery = '';
  }

  onDeviceSearchInput(): void {
    this.deviceSearchSubject.next(this.deviceSearchModalQuery);
  }

  performDeviceSearch(): void {
    if (!this.isBrowser) {
      return;
    }
    if (!this.devices.length) {
      this.onSearchDevices();
    } else {
      this.filterDevices();
    }
  }

  selectDeviceFromModal(device: DeviceReadMinimal): void {
    this.selectDevice(device);
    this.closeDeviceSearchModal();
  }

  openClientModal(): void {
    this.newClientForm.reset();
    this.showClientModal = true;
  }

  closeClientModal(): void {
    this.showClientModal = false;
  }

  saveNewClient(): void {
    if (!this.isBrowser) {
      return;
    }
    if (this.newClientForm.invalid) {
      this.newClientForm.markAllAsTouched();
      return;
    }
    this.creatingClient = true;
    this.error = null;
    const payload = this.newClientForm.value;
    this.userService.quickCreateClient(payload).subscribe({
      next: (client) => {
        this.creatingClient = false;
        this.clients = [client, ...this.clients];
        this.filteredClients = this.clients;
        this.selectClient(client);
        this.showClientModal = false;
      },
      error: (err) => {
        console.error('No se pudo crear el cliente', err);
        this.error = 'No se pudo crear el cliente. Intenta de nuevo.';
        this.creatingClient = false;
      },
    });
  }

  // -------------------- selección dispositivo --------------------
  onSearchDevices(): void {
    if (!this.isBrowser) {
      return;
    }
    this.searchingDevice = true;
    const load$ = this.selectedClient
      ? this.deviceService.listDevicesByClient(this.selectedClient.id)
      : this.deviceService.listDevices();
    load$.subscribe({
      next: (devices) => {
        this.devices = devices;
        this.filterDevices();
      },
      error: (err) => {
        console.error('Error cargando dispositivos', err);
        this.devices = [];
        this.filteredDevices = [];
        this.searchingDevice = false;
      },
      complete: () => (this.searchingDevice = false),
    });
  }

  filterDevices(): void {
    const searchQuery = this.showDeviceSearchModal ? this.deviceSearchModalQuery : this.deviceSearch;
    if (!this.devices.length && !this.searchingDevice && searchQuery.trim().length > 0) {
      this.onSearchDevices();
      return;
    }
    const q = searchQuery.toLowerCase().trim();
    this.filteredDevices = this.devices.filter((d) => {
      return (
        (d.brand || '').toLowerCase().includes(q) ||
        (d.model || '').toLowerCase().includes(q) ||
        (d.serial || '').toLowerCase().includes(q) ||
        (d.imei || '').toLowerCase().includes(q) ||
        (d.type || '').toLowerCase().includes(q)
      );
    });
  }

  selectDevice(device: DeviceReadMinimal): void {
    this.selectedDevice = device;
    this.deviceSearch = device.serial || device.imei || `${device.brand} ${device.model}`;
    this.filteredDevices = [];
    this.deviceSearchModalQuery = '';
  }

  clearDeviceSelection(): void {
    this.selectedDevice = null;
    this.deviceSearch = '';
    this.filteredDevices = this.devices;
  }

  openDeviceModal(): void {
    if (!this.selectedClient) {
      this.error = 'Primero selecciona o crea un cliente.';
      return;
    }
    this.newDeviceForm.reset();
    this.deviceFile = null;
    this.showDeviceModal = true;
  }

  closeDeviceModal(): void {
    this.showDeviceModal = false;
  }

  onDeviceFileChange(event: any): void {
    const file = event.target.files?.[0];
    this.deviceFile = file || null;
  }

  saveNewDevice(): void {
    if (!this.isBrowser) {
      return;
    }
    if (!this.selectedClient) {
      this.error = 'Primero selecciona un cliente.';
      return;
    }
    if (this.newDeviceForm.invalid) {
      this.newDeviceForm.markAllAsTouched();
      return;
    }
    this.creatingDevice = true;
    this.error = null;
    const payload = {
      owner_user_id: this.selectedClient.id,
      type: this.newDeviceForm.value.type,
      brand: this.newDeviceForm.value.brand,
      model: this.newDeviceForm.value.model,
      serial: this.newDeviceForm.value.serial,
      imei: this.newDeviceForm.value.imei,
      notes: this.newDeviceForm.value.notes,
      intake_photo_file: this.deviceFile,
      catalog_manufacturer_id: this.newDeviceForm.value.manufacturer_id,
      catalog_model_id: this.newDeviceForm.value.model_id,
      catalog_variant_id: this.newDeviceForm.value.variant_id,
    };
    this.deviceService.quickCreateDevice(payload).subscribe({
      next: (device) => {
        this.creatingDevice = false;
        this.devices = [device, ...this.devices];
        this.filteredDevices = this.devices;
        this.selectDevice(device);
        this.showDeviceModal = false;
      },
      error: (err) => {
        console.error('No se pudo crear el dispositivo', err);
        this.error = 'No se pudo crear el dispositivo. Intenta de nuevo.';
        this.creatingDevice = false;
      },
    });
  }

  private loadDevicesForClient(clientId: number): void {
    if (!this.isBrowser) {
      return;
    }
    this.searchingDevice = true;
    this.deviceService.listDevicesByClient(clientId).subscribe({
      next: (devices) => {
        this.devices = devices;
        this.filteredDevices = devices;
      },
      error: (err) => {
        console.error('Error cargando dispositivos del cliente', err);
        this.devices = [];
        this.filteredDevices = [];
        this.searchingDevice = false;
      },
      complete: () => (this.searchingDevice = false),
    });
  }

  // -------------------- catálogo dinámico --------------------
  private loadManufacturers(): void {
    if (!this.isBrowser) {
      return;
    }
    this.catalogService.getManufacturers().subscribe({
      next: (data) => {
        this.manufacturers = data;
      },
      error: (err) => {
        console.error('Error cargando fabricantes', err);
      },
    });
  }

  onManufacturerChange(manufacturerId: number | null): void {
    if (!this.isBrowser) {
      return;
    }
    this.selectedManufacturerId = manufacturerId;
    this.models = [];
    this.variants = [];
    this.selectedModelId = null;
    this.selectedVariant = null;
    this.newDeviceForm.patchValue({
      model_id: null,
      variant_id: null,
      brand: '',
      model: '',
      type: '',
    });
    if (manufacturerId) {
      this.catalogService.getModels(manufacturerId).subscribe({
        next: (models) => {
          this.models = models;
        },
        error: (err) => console.error('Error cargando modelos', err),
      });
    }
  }

  onModelChange(modelId: number | null): void {
    if (!this.isBrowser) {
      return;
    }
    this.selectedModelId = modelId;
    this.variants = [];
    this.selectedVariant = null;
    this.newDeviceForm.patchValue({
      variant_id: null,
      model: '',
      type: '',
    });
    if (modelId) {
      const currentModel = this.models.find((m) => m.id === modelId);
      if (currentModel) {
        this.newDeviceForm.patchValue({
          model: currentModel.name,
          type: currentModel.category || '',
        });
      }
      this.catalogService.getVariants(modelId).subscribe({
        next: (variants) => {
          this.variants = variants;
        },
        error: (err) => console.error('Error cargando variantes', err),
      });
    }
  }

  onVariantChange(variantId: number | null): void {
    if (!variantId) {
      this.selectedVariant = null;
      return;
    }
    const variant = this.variants.find((v) => v.id === variantId) || null;
    this.selectedVariant = variant;
    if (variant) {
      this.newDeviceForm.patchValue({
        variant_id: variant.id,
      });
      // Aseguramos que brand/model reflejen la selección actual
      const currentModel = this.models.find((m) => m.id === variant.model_id);
      const manufacturer = this.manufacturers.find((f) => f.id === this.selectedManufacturerId);
      this.newDeviceForm.patchValue({
        brand: manufacturer?.name || this.newDeviceForm.value.brand,
        model: currentModel?.name || this.newDeviceForm.value.model,
        type: currentModel?.category || this.newDeviceForm.value.type,
      });
    }
  }

  submit(): void {
    if (this.form.invalid || !this.selectedClient || !this.selectedDevice) {
      this.form.markAllAsTouched();
      if (!this.selectedClient) {
        this.error = 'Selecciona o crea un cliente.';
      } else if (!this.selectedDevice) {
        this.error = 'Selecciona o crea un dispositivo.';
      }
      return;
    }

    this.error = null;
    this.saving = true;

    const costEstimateRaw = this.form.value.cost_estimate;
    const costEstimate =
      costEstimateRaw === null || costEstimateRaw === undefined || costEstimateRaw === ''
        ? null
        : Number(costEstimateRaw);

    const payload = {
      tracking_code: `TKT-${Date.now()}`,
      device_id: this.selectedDevice.id,
      failure_desc: this.form.value.failure_desc,
      diagnosis: this.form.value.diagnosis,
      cost_estimate: costEstimate,
      assignee_user_id: this.form.value.assignee_user_id || null,
      status_id: 1,
      intake_at: new Date().toISOString(),
    };

    this.ticketService.createTicket(payload).subscribe({
      next: (ticket) => {
        this.saving = false;
        this.router.navigate(['/tickets', ticket.id]);
      },
      error: (err) => {
        console.error('Error creando ticket', err);
        this.saving = false;
        this.error = 'No se pudo crear el ticket. Intenta nuevamente.';
      },
    });
  }
}
