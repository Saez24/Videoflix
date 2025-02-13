import { inject, Injectable } from '@angular/core';
import { ApiService, ApiResponse } from '../api/api.service';
import { Router } from '@angular/router';
import { SnackBarService } from '../snack-bar/snack-bar.service';

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
  snackBarService = inject(SnackBarService);

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

    // console.log(data);

    if (response.ok && response.data) {
      if (!response.data.is_active) {
        // console.error('Account ist noch nicht aktiviert.');
        this.snackBarService.showSnackBarActivateAccount();
        return {
          ok: false,
          status: response.status,
          message:
            'Please activate your account. Check your email for the activation link.',
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
      // console.log('Registrierung erfolgreich:', response.data);
      this.snackBarService
        .showSnackBarRegister()
        .afterDismissed()
        .subscribe(() => {
          this.router.navigateByUrl('sign-in'); // Weiterleiten nach Schließen der Snackbar
        });
    } else {
      console.error('Registration failed:', response.message);
      // Hier evtl. eine Fehlermeldung anzeigen
    }
  }
}
