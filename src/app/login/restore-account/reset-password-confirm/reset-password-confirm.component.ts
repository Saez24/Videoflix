import { Component, OnInit, signal } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { ApiService } from '../../../shared/services/api/api.service';
import {
  FormControl,
  FormsModule,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';

@Component({
  selector: 'app-reset-password-confirm',
  standalone: true,
  imports: [
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    FormsModule,
    ReactiveFormsModule,
    MatButtonModule,
    RouterLink,
  ],
  templateUrl: './reset-password-confirm.component.html',
  styleUrls: ['./reset-password-confirm.component.scss'],
})
export class ResetPasswordConfirmComponent implements OnInit {
  password = new FormControl('', [
    Validators.required,
    Validators.minLength(8),
  ]);
  confirmPassword = new FormControl('', [Validators.required]);
  errorMessage = signal('');
  success = signal(false);
  isLoading = signal(false);
  uidb64 = '';
  token = '';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private apiService: ApiService
  ) {}

  ngOnInit() {
    this.route.params.subscribe((params) => {
      this.uidb64 = params['uidb64'];
      this.token = params['token'];
    });
  }

  updateErrorMessage() {
    if (this.password.hasError('required')) {
      this.errorMessage.set('Password is required');
    } else if (this.password.hasError('minlength')) {
      this.errorMessage.set('Password must be at least 8 characters');
    } else {
      this.errorMessage.set('');
    }
  }

  async resetPassword() {
    if (this.password.invalid || this.confirmPassword.invalid) return;
    if (this.password.value !== this.confirmPassword.value) {
      this.errorMessage.set('Passwords do not match');
      return;
    }

    this.isLoading.set(true);
    try {
      const response = await fetch(
        `${this.apiService.API_BASE_URL}password-reset/confirm/${this.uidb64}/${this.token}/`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ password: this.password.value }),
        }
      );

      const data = await response.json();
      if (response.ok) {
        this.success.set(true);
        setTimeout(() => {
          this.router.navigate(['/sign-in']);
        }, 3000);
      } else {
        this.errorMessage.set(data.error || 'An error occurred');
      }
    } catch (error) {
      this.errorMessage.set('There was a problem with the request');
    } finally {
      this.isLoading.set(false);
    }
  }
}
