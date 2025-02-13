import { Injectable } from '@angular/core';
import {
  MatSnackBar,
  MatSnackBarRef,
  SimpleSnackBar,
} from '@angular/material/snack-bar';

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

  showSnackBarRegister(): MatSnackBarRef<SimpleSnackBar> {
    return this.snackBar.open(
      'Registration successful! Please check your email.',
      'OK',
      { duration: 3000 }
    );
  }

  showSnackBarChangedVideoQuality120P() {
    this.openSnackBar('Changed Videoquality to 120p');
  }

  showSnackBarChangedVideoQuality360P() {
    this.openSnackBar('Changed Videoquality to 360p');
  }

  showSnackBarChangedVideoQuality720P() {
    this.openSnackBar('Changed Videoquality to 720p');
  }

  showSnackBarChangedVideoQuality1080P() {
    this.openSnackBar('Changed Videoquality to 1080p');
  }
}
