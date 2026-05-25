import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { RoutePersistenceService } from './core/services/route-persistence.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected readonly title = signal('progestec-front');

  constructor(private routePersistence: RoutePersistenceService) {}
}
