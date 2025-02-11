import { inject, Injectable } from '@angular/core';
import { ApiService, ApiResponse } from '../api/api.service';
import { Router } from '@angular/router';

interface LoginResponse {
  token: string;
  user_id: string;
  email: string;
  is_active: boolean;
}

interface RegistrationResponse {
  id: number;
  email: string;
}

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  router = inject(Router);
  apiService = inject(ApiService);

  constructor() {}

  logOut() {
    this.apiService.removeAuthCredentials();
    this.router.navigateByUrl('');
  }

  async logIn(data: {
    email: string;
    password: string;
  }): Promise<ApiResponse<LoginResponse>> {
    const response = await this.apiService.postDataWJSON<LoginResponse>(
      this.apiService.LOGIN_URL,
      data
    );

    console.log(data);

    if (response.ok && response.data) {
      if (!response.data.is_active) {
        console.error('Account ist noch nicht aktiviert.');
        return {
          ok: false,
          status: response.status,
          message:
            'Bitte bestätige zuerst deine E-Mail-Adresse, bevor du dich einloggst.',
        };
      }

      this.apiService.setAuthCredentials(
        response.data.token,
        response.data.user_id,
        response.data.email
      );
      this.router.navigateByUrl('content-page');
    }

    return response;
  }

  async register(data: {
    email: string;
    password: string;
    repeated_password: string;
  }) {
    const response = await this.apiService.postDataWJSON<RegistrationResponse>(
      this.apiService.REGISTER_URL,
      data
    );

    if (response.ok) {
      console.log('Registrierung erfolgreich:', response.data);
      this.router.navigateByUrl('sign-in');
    } else {
      console.error('Registrierung fehlgeschlagen:', response.message);
      // Hier evtl. eine Fehlermeldung anzeigen
    }
  }
}
