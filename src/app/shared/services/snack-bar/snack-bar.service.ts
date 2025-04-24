import { Injectable } from '@angular/core';
import {
  MatSnackBar,
  MatSnackBarRef,
  SimpleSnackBar,
} from '@angular/material/snack-bar';
import QualityLevel from 'videojs-contrib-quality-levels/dist/types/quality-level';

@Injectable({
  providedIn: 'root',
})
export class SnackBarService {
  constructor(private snackBar: MatSnackBar) {}

  openSnackBar(
    message: string,
    action: string = 'OK',
    duration: number = 5000
  ) {
    this.snackBar.open(message, action, {
      duration: duration,
      verticalPosition: 'bottom',
      horizontalPosition: 'center',
      panelClass: ['custom-snackbar'],
    });
  }

  showSnackBarActivateAccount() {
    this.openSnackBar('Please activate your account');
  }

  showSnackBarUserExists() {
    this.openSnackBar('This user already exists');
  }

  showSnackBarWrongCredentials() {
    this.openSnackBar('Wrong email or password');
  }

  showSnackBarRegister(): MatSnackBarRef<SimpleSnackBar> {
    return this.snackBar.open(
      'Registration successful! Please check your email.',
      'OK',
      { duration: 3000 }
    );
  }

  showSnackBarChangedVideoQuality(quality: string) {
    return this.snackBar.open(`Video quality changed to ${quality}`, 'OK', {
      duration: 3000,
    });
  }
}
