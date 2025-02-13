import { NgIf } from '@angular/common';
import { AfterViewInit, Component, OnInit } from '@angular/core';
import {
  ActivatedRoute,
  Router,
  RouterLink,
  RouterLinkActive,
  RouterModule,
} from '@angular/router';
import { ApiService } from '../../../shared/services/api/api.service';

@Component({
  selector: 'app-email-verification',
  imports: [NgIf, RouterLink, RouterLinkActive, RouterModule],
  templateUrl: './email-verification.component.html',
  styleUrl: './email-verification.component.scss',
})
export class EmailVerificationComponent implements OnInit {
  message = 'Email is being verified...';
  success = false;
  API_BASE_URL = '';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private apiService: ApiService
  ) {}

  ngOnInit() {
    this.API_BASE_URL = this.apiService.API_BASE_URL;
    this.verifyEmail();
  }
  async verifyEmail() {
    const uidb64 = this.route.snapshot.paramMap.get('uidb64');
    const token = this.route.snapshot.paramMap.get('token');

    if (uidb64 && token) {
      await fetch(
        `http://127.0.0.1:8000/api/registration/verify/${uidb64}/${token}/`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        }
      )
        .then((response) => response.json())
        .then((data) => {
          if (data.message) {
            this.message =
              'Email successfully verified! You will be redirected...';
            this.success = true;
          } else {
            this.message = 'Error during verification: ' + data.error;
          }

          // Nach 3 Sekunden weiterleiten
          setTimeout(() => {
            this.router.navigate(['/sign-in']); // Zielseite nach der Bestätigung
          }, 3000);
        })
        .catch(() => {
          this.message = 'There was a problem with the verification.';
        });
    } else {
      this.message = 'Invalid confirmation link.';
    }
  }
}
