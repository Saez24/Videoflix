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

  isLoggedIn(): boolean {
    return !!this.getAuthToken(); // Beispiel: Überprüft, ob ein Token existiert
  }

  private getAuthToken(): string | null {
    // Beispiel: Token aus dem lokalen Speicher abrufen
    return localStorage.getItem('auth-token');
  }

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
    } else {
      this.snackBarService.showSnackBarWrongCredentials();
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
      // Registrierung erfolgreich
      this.snackBarService
        .showSnackBarRegister()
        .afterDismissed()
        .subscribe(() => {
          this.router.navigateByUrl('sign-in');
        });
    } else {
      // Überprüfen Sie responseData auf Fehlermeldungen
      const errorData = response.data as any; // Da bei Fehlern das Format anders sein könnte

      if (errorData && typeof errorData === 'object') {
        // Django sendet oft Fehler als Objekt mit Feldnamen als Schlüssel
        if (errorData.password && Array.isArray(errorData.password)) {
          // Prüfen auf verschiedene bekannte Fehlermeldungen
          const passwordErrors = errorData.password;

          if (passwordErrors.some((err: string) => err.includes('common'))) {
            this.snackBarService.showSnackBarCommonPassword();
            return;
          }
        }

        if (errorData.email && Array.isArray(errorData.email)) {
          const emailErrors = errorData.email;

          if (
            emailErrors.some((err: string) => err.includes('already in use'))
          ) {
            this.snackBarService.showSnackBarUserExists();
            return;
          }
        }
      }

      // Fallback für unbekannte Fehler
      this.snackBarService.showSnackBarError('Registration failed');
    }
  }
}
