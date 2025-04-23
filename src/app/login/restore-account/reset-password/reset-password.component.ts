import { Component, signal } from '@angular/core';
import {
  FormControl,
  Validators,
  FormsModule,
  ReactiveFormsModule,
} from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatCardModule } from '@angular/material/card';
import { RouterLink } from '@angular/router';
import { ApiService } from '../../../shared/services/api/api.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-reset-password',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    FormsModule,
    ReactiveFormsModule,
    RouterLink,
  ],
  templateUrl: './reset-password.component.html',
  styleUrls: ['./reset-password.component.scss'],
})
export class ResetPasswordComponent {
  email = new FormControl('', [Validators.required, Validators.email]);
  errorMessage = signal('');
  requestSent = signal(false);
  isLoading = signal(false);

  constructor(private apiService: ApiService) {}

  updateErrorMessage() {
    if (this.email.hasError('required')) {
      this.errorMessage.set('You must enter a value');
    } else if (this.email.hasError('email')) {
      this.errorMessage.set('Not a valid email');
    } else {
      this.errorMessage.set('');
    }
  }

  async sendResetEmail() {
    if (this.email.invalid) return;

    this.isLoading.set(true);
    try {
      const response = await fetch(
        `${this.apiService.API_BASE_URL}password-reset/request/`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: this.email.value }),
        }
      );

      const data = await response.json();
      if (response.ok) {
        this.requestSent.set(true);
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
