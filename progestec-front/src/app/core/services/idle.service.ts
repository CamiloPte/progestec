import { Injectable, NgZone, Inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { BehaviorSubject, fromEvent, merge, Subscription, timer } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class IdleService {
  private idleWarningMs = 14 * 60 * 1000; // 14 minutos
  private idleLogoutMs = 15 * 60 * 1000;  // 15 minutos

  private warning$ = new BehaviorSubject<boolean>(false);
  warningState$ = this.warning$.asObservable();

  private timersSub?: Subscription;
  private eventsSub?: Subscription;
  private isBrowser = false;

  constructor(private zone: NgZone, @Inject(PLATFORM_ID) platformId: Object) {
    this.isBrowser = isPlatformBrowser(platformId);
    if (this.isBrowser) {
      this.startListening();
    }
  }

  private startListening(): void {
    if (!this.isBrowser) {
      return;
    }

    const userEvents = merge(
      fromEvent(window, 'mousemove'),
      fromEvent(window, 'mousedown'),
      fromEvent(window, 'keydown'),
      fromEvent(window, 'scroll'),
      fromEvent(window, 'touchstart')
    );

    this.zone.runOutsideAngular(() => {
      this.eventsSub = userEvents.subscribe(() => this.resetTimers());
    });

    this.resetTimers();
  }

  resetTimers(): void {
    if (!this.isBrowser) {
      return;
    }

    this.timersSub?.unsubscribe();
    this.warning$.next(false);

    this.zone.runOutsideAngular(() => {
      const warnTimer = timer(this.idleWarningMs);
      const logoutTimer = timer(this.idleLogoutMs);

      this.timersSub = new Subscription();

      this.timersSub.add(
        warnTimer.subscribe(() => this.zone.run(() => this.warning$.next(true)))
      );
      this.timersSub.add(
        logoutTimer.subscribe(() => this.zone.run(() => this.warning$.next(false)))
      );
    });
  }

  stop(): void {
    if (!this.isBrowser) {
      return;
    }

    this.timersSub?.unsubscribe();
    this.eventsSub?.unsubscribe();
    this.warning$.next(false);
  }
}
