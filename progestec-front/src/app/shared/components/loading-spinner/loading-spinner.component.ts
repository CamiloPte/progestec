// src/app/shared/components/loading-spinner/loading-spinner.component.ts
import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

export type LoaderType = 'ring' | 'helix' | 'pulse' | 'bouncy' | 'dotted';
export type LoaderColor = 'primary' | 'secondary' | 'white';

@Component({
  selector: 'app-loading-spinner',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="loader-wrapper" [class.overlay]="overlay" [class.fullscreen]="fullscreen">
      <div class="loader-content">
        @switch (type) {
          @case ('ring') {
            <svg class="ldrs-ring" [class]="colorClass" viewBox="25 25 50 50">
              <circle cx="50" cy="50" r="20"></circle>
            </svg>
          }
          @case ('helix') {
            <div class="ldrs-helix" [class]="colorClass">
              <div class="ldrs-helix__container">
                <div class="ldrs-helix__dot"></div>
                <div class="ldrs-helix__dot"></div>
              </div>
            </div>
          }
          @case ('pulse') {
            <div class="ldrs-pulse-ring" [class]="colorClass"></div>
          }
          @case ('bouncy') {
            <div class="ldrs-bouncy" [class]="colorClass">
              <div class="ldrs-bouncy__dot"></div>
              <div class="ldrs-bouncy__dot"></div>
              <div class="ldrs-bouncy__dot"></div>
            </div>
          }
          @case ('dotted') {
            <div class="ldrs-dotted" [class]="colorClass">
              @for (i of [1,2,3,4,5,6,7,8]; track i) {
                <div class="ldrs-dotted__dot"></div>
              }
            </div>
          }
          @default {
            <div class="spinner" [class]="colorClass"></div>
          }
        }
        @if (message) {
          <p class="loader-message">{{ message }}</p>
        }
      </div>
    </div>
  `,
  styles: [`
    .loader-wrapper {
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 2rem;
    }

    .loader-wrapper.overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(255, 255, 255, 0.92);
      backdrop-filter: blur(4px);
      z-index: 9999;
      padding: 0;
    }

    .loader-wrapper.fullscreen {
      min-height: 100vh;
    }

    .loader-content {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 1rem;
    }

    .loader-message {
      color: var(--color-gray-600, #4b5563);
      font-size: 0.95rem;
      margin: 0;
      animation: fadeInUp 0.3s ease-out;
    }

    @keyframes fadeInUp {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }

    /* Color Variants */
    .color-primary { --uib-color: var(--color-primary, #1a5c3a); }
    .color-secondary { --uib-color: var(--color-secondary, #c9a227); }
    .color-white { --uib-color: #ffffff; }

    /* Ring Loader */
    .ldrs-ring {
      --uib-size: 50px;
      --uib-speed: 1.5s;
      height: var(--uib-size);
      width: var(--uib-size);
      vertical-align: middle;
      transform-origin: center;
      animation: ldrs-ring var(--uib-speed) linear infinite;
    }

    .ldrs-ring circle {
      fill: none;
      stroke: var(--uib-color, var(--color-primary, #1a5c3a));
      stroke-width: 3;
      stroke-dasharray: 1, 200;
      stroke-dashoffset: 0;
      stroke-linecap: round;
      animation: ldrs-ring-stroke var(--uib-speed) ease-in-out infinite;
    }

    @keyframes ldrs-ring {
      100% { transform: rotate(360deg); }
    }

    @keyframes ldrs-ring-stroke {
      0% { stroke-dasharray: 1, 200; stroke-dashoffset: 0; }
      50% { stroke-dasharray: 90, 200; stroke-dashoffset: -35px; }
      100% { stroke-dasharray: 90, 200; stroke-dashoffset: -125px; }
    }

    /* Helix Loader */
    .ldrs-helix {
      --uib-size: 50px;
      --uib-speed: 2s;
      display: flex;
      align-items: center;
      justify-content: center;
      height: var(--uib-size);
      width: var(--uib-size);
    }

    .ldrs-helix__container {
      animation: ldrs-helix-rotate calc(var(--uib-speed) / 2) ease-in-out infinite;
      transform-origin: center;
      width: 100%;
      height: 100%;
      position: relative;
    }

    .ldrs-helix__dot {
      position: absolute;
      width: 35%;
      aspect-ratio: 1;
      background-color: var(--uib-color, var(--color-primary, #1a5c3a));
      border-radius: 50%;
    }

    .ldrs-helix__dot:first-child {
      top: 0;
      left: 0;
      animation: ldrs-helix-first calc(var(--uib-speed) / 2) ease-in-out infinite;
    }

    .ldrs-helix__dot:last-child {
      bottom: 0;
      right: 0;
      animation: ldrs-helix-second calc(var(--uib-speed) / 2) ease-in-out infinite;
    }

    @keyframes ldrs-helix-rotate {
      0%, 100% { transform: rotate(0deg); }
      50% { transform: rotate(180deg); }
    }

    @keyframes ldrs-helix-first {
      0%, 100% { transform: scale(1); }
      50% { transform: scale(1.5); }
    }

    @keyframes ldrs-helix-second {
      0%, 100% { transform: scale(1.5); }
      50% { transform: scale(1); }
    }

    /* Pulse Ring Loader */
    .ldrs-pulse-ring {
      --uib-size: 50px;
      --uib-speed: 1.5s;
      width: var(--uib-size);
      height: var(--uib-size);
      border-radius: 50%;
      position: relative;
    }

    .ldrs-pulse-ring::before,
    .ldrs-pulse-ring::after {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      border-radius: inherit;
      border: 3px solid var(--uib-color, var(--color-primary, #1a5c3a));
      animation: ldrs-pulse var(--uib-speed) linear infinite;
    }

    .ldrs-pulse-ring::after {
      animation-delay: calc(var(--uib-speed) / -2);
    }

    @keyframes ldrs-pulse {
      0% { transform: scale(0.2); opacity: 1; }
      80%, 100% { transform: scale(1); opacity: 0; }
    }

    /* Bouncy Loader */
    .ldrs-bouncy {
      --uib-size: 50px;
      --uib-speed: 1.5s;
      display: flex;
      align-items: flex-end;
      justify-content: center;
      gap: 8px;
      height: var(--uib-size);
      width: calc(var(--uib-size) * 1.5);
    }

    .ldrs-bouncy__dot {
      flex-shrink: 0;
      width: calc(var(--uib-size) / 4);
      height: calc(var(--uib-size) / 4);
      border-radius: 50%;
      background: var(--uib-color, var(--color-primary, #1a5c3a));
      animation: ldrs-bouncy-anim var(--uib-speed) ease-in-out infinite;
    }

    .ldrs-bouncy__dot:nth-child(2) { animation-delay: calc(var(--uib-speed) * 0.12); }
    .ldrs-bouncy__dot:nth-child(3) { animation-delay: calc(var(--uib-speed) * 0.24); }

    @keyframes ldrs-bouncy-anim {
      0%, 100% { transform: translateY(0); }
      30% { transform: translateY(calc(var(--uib-size) * -0.65)); }
    }

    /* Dotted Spinner Loader */
    .ldrs-dotted {
      --uib-size: 50px;
      --uib-speed: 1.5s;
      position: relative;
      width: var(--uib-size);
      height: var(--uib-size);
    }

    .ldrs-dotted__dot {
      position: absolute;
      top: 0;
      left: 50%;
      width: 15%;
      height: 15%;
      margin-left: -7.5%;
      background-color: var(--uib-color, var(--color-secondary, #c9a227));
      border-radius: 50%;
      transform-origin: 50% calc(var(--uib-size) / 2);
      animation: ldrs-dotted-spin var(--uib-speed) linear infinite;
    }

    .ldrs-dotted__dot:nth-child(1) { animation-delay: calc(var(--uib-speed) * -0.875); }
    .ldrs-dotted__dot:nth-child(2) { animation-delay: calc(var(--uib-speed) * -0.75); }
    .ldrs-dotted__dot:nth-child(3) { animation-delay: calc(var(--uib-speed) * -0.625); }
    .ldrs-dotted__dot:nth-child(4) { animation-delay: calc(var(--uib-speed) * -0.5); }
    .ldrs-dotted__dot:nth-child(5) { animation-delay: calc(var(--uib-speed) * -0.375); }
    .ldrs-dotted__dot:nth-child(6) { animation-delay: calc(var(--uib-speed) * -0.25); }
    .ldrs-dotted__dot:nth-child(7) { animation-delay: calc(var(--uib-speed) * -0.125); }
    .ldrs-dotted__dot:nth-child(8) { animation-delay: 0s; }

    @keyframes ldrs-dotted-spin {
      0% { transform: rotate(0deg); opacity: 1; }
      100% { transform: rotate(360deg); opacity: 0.2; }
    }

    /* Basic Spinner Fallback */
    .spinner {
      width: 50px;
      height: 50px;
      border: 4px solid rgba(0, 0, 0, 0.1);
      border-top-color: var(--uib-color, var(--color-primary, #1a5c3a));
      border-radius: 50%;
      animation: spinner-spin 1s linear infinite;
    }

    @keyframes spinner-spin {
      to { transform: rotate(360deg); }
    }
  `]
})
export class LoadingSpinnerComponent {
  @Input() type: LoaderType = 'ring';
  @Input() color: LoaderColor = 'primary';
  @Input() message?: string;
  @Input() overlay = false;
  @Input() fullscreen = false;

  get colorClass(): string {
    return `color-${this.color}`;
  }
}
