import { inject, Injectable } from '@angular/core';
import { ApiService } from '../api/api.service';
import { Router } from '@angular/router';

interface LoginResponse {
  ok: boolean;
  data?: {
    token: string;
    user_id: string;
    username: string;
  };
}

interface FormData {
  [key: string]: any;
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

  async logIn(formData: FormData): Promise<void> {
    console.log('Login-Daten:', formData);

    try {
      const response: LoginResponse = await this.apiService.postDataWJSON(
        this.apiService.LOGIN_URL,
        formData
      );

      if (!response.ok) {
        console.error('Login fehlgeschlagen.');
        // Optionale Fehleranzeige, z. B. Toast-Benachrichtigung
        // this.showFormErrors(['error_pw']);
      } else {
        if (response.data) {
          this.apiService.setAuthCredentials(
            response.data.token,
            response.data.user_id,
            response.data.username
          );
        }
        this.router.navigateByUrl('select-account');
      }
    } catch (error) {
      console.error('Netzwerkfehler beim Login:', error);
    }
  }

  async registration(data: FormData): Promise<void> {
    try {
      const response: LoginResponse = await this.apiService.postDataWJSON(
        this.apiService.REGISTER_URL,
        data
      );

      if (!response.ok) {
        console.error('Registrierung fehlgeschlagen:', response);
        // Hier können Fehlerdetails extrahiert und angezeigt werden
        // this.showToastMessage(true, ['Registrierungsfehler']);
      } else {
        if (response.data) {
          this.apiService.setAuthCredentials(
            response.data.token,
            response.data.user_id,
            response.data.username
          );
        }
        this.router.navigateByUrl('select-account');
      }
    } catch (error) {
      console.error('Netzwerkfehler bei der Registrierung:', error);
    }
  }
}
