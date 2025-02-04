import { ChangeDetectionStrategy, Component } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-legal-notice',
  imports: [MatIconModule],
  templateUrl: './legal-notice.component.html',
  styleUrl: './legal-notice.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LegalNoticeComponent {}
