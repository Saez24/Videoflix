import { Injectable } from '@angular/core';

export interface ApiResponse<T> {
  ok: boolean;
  status: number | string;
  data?: T;
  message?: string;
  full_msg?: any;
}

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  constructor() {}

  API_BASE_URL = 'https://videoflix-aws-backend.your-developer.com/api/';
  STATIC_BASE_URL = 'https://videoflix-aws-backend.your-developer.com';
  LOGIN_URL = 'login/';
  REGISTER_URL = 'registration/';
  PROFILE_URL = 'profiles/';
  SUB_PROFILE_URL = 'sub_profiles/';
  CONTENT_URL = 'content/videos/';

  setAuthCredentials(token: string, userId: string, email: string): void {
    localStorage.setItem('auth-token', token);
    localStorage.setItem('auth-user', email);
    localStorage.setItem('auth-user-id', userId);
  }

  removeAuthCredentials() {
    localStorage.clear();
    // localStorage.removeItem('auth-token');
    // localStorage.removeItem('auth-user');
    // localStorage.removeItem('auth-user-id');
    // localStorage.removeItem('selectedAccount');
    // localStorage.removeItem('selectedSubaccount');
  }

  getAuthToken(): string | null {
    if (typeof localStorage !== 'undefined') {
      return localStorage.getItem('auth-token');
    }
    return null;
  }

  getAuthUser() {
    return localStorage.getItem('auth-user');
  }

  getAuthUserId() {
    return localStorage.getItem('auth-user-id');
  }

  jsonToFormData(json: Record<string, any>): FormData {
    const formData = new FormData();

    const appendFormData = (data: any, parentKey: string = '') => {
      if (data && typeof data === 'object' && !(data instanceof File)) {
        Object.keys(data).forEach((key) => {
          appendFormData(data[key], parentKey ? `${parentKey}[${key}]` : key);
        });
      } else {
        formData.append(parentKey, data);
      }
    };

    appendFormData(json);
    return formData;
  }

  createHeaders(
    contentType: string = 'application/json',
    withAuth: boolean = true
  ): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': contentType,
      Accept: 'application/json',
    };

    if (withAuth) {
      // Nur Token setzen, wenn gewünscht
      const token = this.getAuthToken();
      if (token) {
        headers['Authorization'] = `Token ${token}`;
      }
    }

    return headers;
  }

  async getData(endpoint: string): Promise<ApiResponse<any>> {
    if (!endpoint) {
      return {
        ok: false,
        status: 'error',
        message: 'endpoint is required',
      };
    }
    try {
      const response = await fetch(`${this.API_BASE_URL}${endpoint}`, {
        method: 'GET',
        headers: this.createHeaders(),
      });

      const responseData = await response.json();
      // console.log('Response Data:', responseData);

      return {
        ok: response.ok,
        status: response.status,
        data: responseData,
      };
    } catch (error) {
      return {
        ok: false,
        status: 'error',
        message: 'network error',
      };
    }
  }

  async postData<T>(endpoint: string, data: any): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: this.createHeaders(),
        body: data,
      });
      const responseData = await response.json();

      return {
        ok: response.ok,
        status: response.status,
        data: responseData,
      };
    } catch (error) {
      return {
        ok: false,
        status: 'error',
        message: 'network error',
      };
    }
  }

  async postDataWJSON<T>(endpoint: string, data: any): Promise<ApiResponse<T>> {
    // console.log('Login Request Payload:', JSON.stringify(data)); // Debug Log

    const response = await fetch(`${this.API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: this.createHeaders('application/json', false), // Kein Token beim Login
      body: JSON.stringify(data),
    });

    const responseData = await response.json();
    // console.log('Response Data:', responseData); // Debug Log

    return {
      ok: response.ok,
      status: response.status,
      data: responseData,
    };
  }

  async patchDataWoFiles<T>(
    endpoint: string,
    data: any
  ): Promise<ApiResponse<T>> {
    let header = this.createHeaders();
    header['Content-Type'] = 'application/json';
    try {
      const response = await fetch(`${this.API_BASE_URL}${endpoint}`, {
        method: 'PATCH',
        headers: header,
        body: JSON.stringify(data),
      });

      const responseData = await response.json();
      return {
        ok: response.ok,
        status: response.status,
        data: responseData,
      };
    } catch (error) {
      return {
        ok: false,
        status: 'error',
        message: 'network error',
      };
    }
  }

  async patchData<T>(
    endpoint: string,
    formData: FormData
  ): Promise<ApiResponse<T>> {
    const headers = this.createHeaders();

    try {
      const response = await fetch(`${this.API_BASE_URL}${endpoint}`, {
        method: 'PATCH',
        headers: headers,
        body: formData,
      });

      const responseData = await response.json();
      return {
        ok: response.ok,
        status: response.status,
        data: responseData,
      };
    } catch (error) {
      return {
        ok: false,
        status: 'error',
        message: 'network error',
      };
    }
  }

  async deleteData(endpoint: string): Promise<ApiResponse<{}>> {
    try {
      const response = await fetch(`${this.API_BASE_URL}${endpoint}`, {
        method: 'DELETE',
        headers: this.createHeaders(),
      });

      return {
        ok: response.ok,
        status: response.status,
        data: {},
      };
    } catch (error) {
      return {
        ok: false,
        status: 'error',
        message: 'network error',
        full_msg: error,
      };
    }
  }
}
