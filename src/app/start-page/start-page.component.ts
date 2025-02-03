import { Component } from '@angular/core';
import {
  Router,
  RouterLink,
  RouterLinkActive,
  RouterModule,
} from '@angular/router';

@Component({
  selector: 'app-start-page',
  imports: [RouterLink, RouterLinkActive, RouterModule],
  templateUrl: './start-page.component.html',
  styleUrl: './start-page.component.scss',
})
export class StartPageComponent {}
