import { Component } from '@angular/core';
import {
  RouterLink,
  RouterLinkActive,
  RouterModule,
  Router,
} from '@angular/router';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-start-page',
  imports: [RouterLink, RouterLinkActive, RouterModule, FormsModule],
  templateUrl: './start-page.component.html',
  styleUrl: './start-page.component.scss',
})
export class StartPageComponent {
  email: string = '';

  constructor(private router: Router) {}

  navigateToSignUp() {
    this.router.navigate(['/sign-up'], {
      queryParams: { email: this.email },
    });
  }
}
