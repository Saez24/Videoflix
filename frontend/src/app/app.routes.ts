import { Routes } from '@angular/router';
import { StartPageComponent } from './start-page/start-page.component';
import { SignUpComponent } from './login/sign-up/sign-up.component';
import { ResetPasswordComponent } from './login/restore-account/reset-password/reset-password.component';
import { SignInComponent } from './login/sign-in/sign-in.component';
import { PrivacyPolicyComponent } from './shared/legal-pages/privacy-policy/privacy-policy.component';
import { LegalNoticeComponent } from './shared/legal-pages/legal-notice/legal-notice.component';
import { ContentPageComponent } from './content-page/content-page.component';
import { EmailVerificationComponent } from './login/sign-up/email-verification/email-verification.component';
import { authGuard } from './auth.guard';
import { ResetPasswordConfirmComponent } from './login/restore-account/reset-password-confirm/reset-password-confirm.component';

export const routes: Routes = [
  {
    path: '',
    component: StartPageComponent,
  },

  { path: 'sign-up', component: SignUpComponent },
  { path: 'reset-password', component: ResetPasswordComponent },
  {
    path: 'password-reset-confirm/:uidb64/:token',
    component: ResetPasswordConfirmComponent,
  },
  { path: 'sign-in', component: SignInComponent },
  { path: 'privacy-policy', component: PrivacyPolicyComponent },
  { path: 'legal-notice', component: LegalNoticeComponent },
  {
    path: 'content-page',
    component: ContentPageComponent,
    canActivate: [authGuard],
  },
  {
    path: 'verify-email/:uidb64/:token',
    component: EmailVerificationComponent,
  },
];
