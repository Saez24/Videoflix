import { NgIf } from '@angular/common';
import { Component } from '@angular/core';
import {
  Router,
  RouterLink,
  RouterLinkActive,
  RouterModule,
  RouterOutlet,
  NavigationEnd,
} from '@angular/router';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, RouterLinkActive, RouterModule, NgIf],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss',
})
export class AppComponent {
  title = 'videoflix';
  isContentPage: boolean = false;
  showFooter = true;

  constructor(private router: Router) {
    this.router.events.subscribe((event) => {
      if (event instanceof NavigationEnd) {
        this.isContentPage = event.url.includes('/content-page'); // Passe die Route an
        this.showFooter =
          event.url !== '/legal-notice' && event.url !== '/privacy-policy';
      }
    });
  }
}
