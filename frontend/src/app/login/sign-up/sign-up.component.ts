import {
  Component,
  ChangeDetectionStrategy,
  signal,
  OnInit,
} from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import {
  FormControl,
  FormsModule,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { merge } from 'rxjs';
import { MatCheckboxModule } from '@angular/material/checkbox';
import {
  RouterLink,
  RouterLinkActive,
  RouterModule,
  ActivatedRoute,
} from '@angular/router';
import { AuthService } from '../../shared/services/authentication/auth.service';

@Component({
  selector: 'app-sign-up',
  imports: [
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    FormsModule,
    ReactiveFormsModule,
    MatIconModule,
    MatButtonModule,
    MatCheckboxModule,
    RouterLink,
    RouterLinkActive,
    RouterModule,
  ],
  templateUrl: './sign-up.component.html',
  styleUrl: './sign-up.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SignUpComponent implements OnInit {
  readonly email = new FormControl('', [Validators.required, Validators.email]);
  readonly password = new FormControl('', [Validators.required]);
  readonly repeated_password = new FormControl('', [Validators.required]);
  errorMessage = signal('');
  hide = signal(true);

  constructor(public authService: AuthService, private route: ActivatedRoute) {
    merge(this.email.statusChanges, this.email.valueChanges)
      .pipe(takeUntilDestroyed())
      .subscribe(() => this.updateErrorMessage());
  }

  ngOnInit() {
    // Lese die E-Mail-Adresse aus den Query-Parametern
    this.route.queryParams.subscribe((params) => {
      if (params['email']) {
        this.email.setValue(params['email']);
        // Validierung auslösen
        this.updateErrorMessage();
      }
    });
  }

  isFormValid(): boolean {
    const passwordsMatch = this.password.value === this.repeated_password.value;

    return (
      this.email.valid &&
      this.password.valid &&
      this.repeated_password.valid &&
      passwordsMatch
    );
  }

  clickEvent(event: MouseEvent) {
    this.hide.set(!this.hide());
    event.stopPropagation();
  }

  updateErrorMessage() {
    if (this.email.hasError('required')) {
      this.errorMessage.set('You must enter a value');
    } else if (this.email.hasError('email')) {
      this.errorMessage.set('Not a valid email');
    } else {
      this.errorMessage.set('');
    }
  }
}
