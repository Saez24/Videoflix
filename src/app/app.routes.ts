import { Routes } from '@angular/router';
import { StartPageComponent } from './start-page/start-page.component';
import { SignUpComponent } from './login/sign-up/sign-up.component';
import { ResetPasswordComponent } from './login/restore-account/reset-password/reset-password.component';
import { SendEmailComponent } from './login/restore-account/send-email/send-email.component';
import { SignInComponent } from './login/sign-in/sign-in.component';
import { PrivacyPolicyComponent } from './shared/legal-pages/privacy-policy/privacy-policy.component';
import { LegalNoticeComponent } from './shared/legal-pages/legal-notice/legal-notice.component';
import { ContentPageComponent } from './content-page/content-page.component';

export const routes: Routes = [
  {
    path: '',
    component: StartPageComponent,
  },

  { path: 'sign-up', component: SignUpComponent },
  { path: 'reset-password', component: ResetPasswordComponent },
  { path: 'send-mail', component: SendEmailComponent },
  { path: 'sign-in', component: SignInComponent },
  { path: 'privacy-policy', component: PrivacyPolicyComponent },
  { path: 'legal-notice', component: LegalNoticeComponent },
  { path: 'content-page', component: ContentPageComponent },
];
