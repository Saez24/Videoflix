import {
  ChangeDetectionStrategy,
  Component,
  OnInit,
  AfterViewInit,
  OnDestroy,
} from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { RouterLink, RouterLinkActive, RouterModule } from '@angular/router';
import { ApiService } from '../shared/services/api/api.service';
import { AsyncPipe, KeyValuePipe, NgFor, NgIf } from '@angular/common';
import { CapitalizePipe } from '../shared/pipes/capitalize.pipe';
import { AuthService } from '../shared/services/authentication/auth.service';
import { BehaviorSubject } from 'rxjs';
import videojs from 'video.js';
import qualityLevels from 'videojs-contrib-quality-levels';
import QualityLevel from 'videojs-contrib-quality-levels/dist/types/quality-level';

@Component({
  selector: 'app-content-page',
  imports: [
    MatIconModule,
    RouterLink,
    RouterLinkActive,
    RouterModule,
    NgIf,
    NgFor,
    CapitalizePipe,
    AsyncPipe,
    KeyValuePipe,
  ],
  templateUrl: './content-page.component.html',
  styleUrl: './content-page.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ContentPageComponent implements OnInit, AfterViewInit, OnDestroy {
  private player: any;
  constructor(public apiService: ApiService, public authService: AuthService) {
    window.addEventListener('keydown', this.handleEscape);
  }

  videos$ = new BehaviorSubject<any[]>([]);
  thumbnails$ = new BehaviorSubject<string[]>([]);
  backgroundVideoUrl$ = new BehaviorSubject<string>('');
  private latestThumbnailsSubject = new BehaviorSubject<string[]>([]);
  latestThumbnails$ = this.latestThumbnailsSubject.asObservable();
  categorizedVideos$ = new BehaviorSubject<{ [category: string]: any[] }>({});
  selectedVideoUrl$ = new BehaviorSubject<string | null>(null);

  ngOnInit() {
    this.getVideos();
    this.getThumbnails();
  }

  ngAfterViewInit() {
    this.selectedVideoUrl$.subscribe((url) => {
      if (url) {
        setTimeout(() => this.initVideoPlayer(url), 0); // sicherstellen, dass DOM fertig
      } else {
        this.disposePlayer();
      }
    });
  }

  ngOnDestroy() {
    this.disposePlayer();
    window.removeEventListener('keydown', this.handleEscape);
  }

  handleEscape = (event: KeyboardEvent) => {
    if (event.key === 'Escape') {
      this.setSelectedVideo(null);
    }
  };

  async getVideos() {
    const response = await this.apiService.getData(this.apiService.CONTENT_URL);

    this.videos$.next(response.data);
    this.groupVideosByCategory(response.data);
    this.setBackgroundVideo(response.data);
  }

  getCategories(): string[] {
    return Object.keys(this.categorizedVideos$);
  }

  groupVideosByCategory(videos: any[]) {
    const categorizedVideos: { [category: string]: any[] } = {};

    videos.forEach((video) => {
      const category = video.category;
      if (category) {
        if (!categorizedVideos[category]) {
          categorizedVideos[category] = [];
        }
        categorizedVideos[category].push(video);
      }
    });

    this.categorizedVideos$.next(categorizedVideos);
  }

  async getThumbnails() {
    const response = await this.apiService.getData(this.apiService.CONTENT_URL);
    const thumbnails = response.data.map(
      (video: any) => this.apiService.STATIC_BASE_URL + video.thumbnail
    );
    this.thumbnails$.next(thumbnails);
    this.getLatestVideoThumbnails(thumbnails);
  }

  getLatestVideoThumbnails(thumbnails: any[]) {
    const sortedThumbnails = thumbnails
      .filter((video) => video.created_at) // Entfernt Objekte ohne created_at
      .sort(
        (a, b) =>
          new Date(b.created_at || 0).getTime() -
          new Date(a.created_at || 0).getTime()
      )
      .slice(0, 6);

    this.latestThumbnailsSubject.next(sortedThumbnails);
  }

  setBackgroundVideo(videos: any[]) {
    if (videos.length > 0) {
      const mostViewedVideo = videos.reduce(
        (max, video) => (video.views > max.views ? video : max),
        videos[0]
      );
      this.backgroundVideoUrl$.next(
        this.apiService.STATIC_BASE_URL + mostViewedVideo.video_file
      );
    }
  }

  setSelectedVideo(videoUrl: string | null) {
    this.selectedVideoUrl$.next(videoUrl);
  }

  initVideoPlayer(url: string) {
    this.disposePlayer();

    const videoElement = document.getElementById(
      'videoPlayer'
    ) as HTMLVideoElement;
    if (!videoElement) return;

    this.player = videojs(videoElement, {
      autoplay: false,
      controls: true,
      responsive: true,
      fluid: true,
      html5: {
        vhs: {
          overrideNative: true,
        },
      },
      sources: [
        {
          src: url,
          type: 'application/x-mpegURL',
        },
      ],
    });

    // Warte auf das 'loadedmetadata' Event
    this.player.on('loadedmetadata', () => {
      this.setupQualitySelectorWithRetry();
    });
  }

  setupQualitySelectorWithRetry(attempt = 0) {
    const MAX_ATTEMPTS = 5;
    const RETRY_DELAY = 500;

    const qualityLevels = this.player.qualityLevels();
    const levelsArray = Array.from(qualityLevels) as QualityLevel[];

    if (levelsArray.length > 0) {
      this.setupQualitySelector();
    } else if (attempt < MAX_ATTEMPTS) {
      setTimeout(() => {
        this.setupQualitySelectorWithRetry(attempt + 1);
      }, RETRY_DELAY);
    } else {
      console.warn('No quality levels available after retries', qualityLevels);
    }
  }

  setupQualitySelector() {
    const qualityLevels = this.player.qualityLevels();
    const levelsArray = Array.from(qualityLevels);

    // Erstelle das Menü
    const MenuButton = videojs.getComponent('MenuButton');
    const qualityMenuButton = new MenuButton(this.player, {
      className: 'vjs-quality-selector',
    });

    // Custom Icon hinzufügen
    const icon = videojs.dom.createEl('span', {
      className: 'vjs-icon-quality',
      innerHTML: '&#x2699;', // Zahnrad-Icon
    });
    qualityMenuButton.el().appendChild(icon);

    const Menu = videojs.getComponent('Menu');
    const qualityMenu = new Menu(this.player);

    // Finde die aktuell aktive Qualitätsstufe
    const activeIndex = levelsArray.findIndex(
      (level) => (level as QualityLevel).enabled_
    );

    levelsArray.forEach((level, index) => {
      const MenuItem = videojs.getComponent('MenuItem');
      const menuItem = new MenuItem(this.player, {
        className: 'vjs-menu-item-selectable',
        // selectable: true, // Removed as it's not recognized
      });

      // Label erstellen
      const label = this.getQualityLabel(level);
      const labelEl = videojs.dom.createEl('div', {
        className: 'vjs-menu-item-text',
        textContent: label,
      });
      menuItem.el().appendChild(labelEl);

      // Aktive Stufe markieren
      if (index === activeIndex) {
        menuItem.addClass('vjs-selected');
      }

      menuItem.on('click', () => {
        // Alle Stufen deaktivieren
        levelsArray.forEach((_, i) => {
          qualityLevels[i].enabled = i === index;
        });
        // UI aktualisieren
        qualityMenu.children().forEach((item: any) => {
          item.removeClass('vjs-selected');
        });
        menuItem.addClass('vjs-selected');
      });

      qualityMenu.addChild(menuItem);
    });

    // Menü zum Button hinzufügen
    qualityMenuButton.addChild(qualityMenu);

    // Button zur ControlBar hinzufügen
    const controlBar = this.player.controlBar;
    controlBar.addChild(
      qualityMenuButton,
      {},
      controlBar.children().length - 2
    );
  }

  // Hilfsfunktion für Qualitäts-Labels
  private getQualityLabel(level: any): string {
    if (level.height >= 1080) return '1080p (HD)';
    if (level.height >= 720) return '720p (HD)';
    if (level.height >= 480) return '480p';

    // Fallback für andere Fälle
    return `${level.height}p (${Math.round(level.bandwidth / 1000)}kbps)`;
  }

  disposePlayer() {
    if (this.player) {
      this.player.dispose();
      this.player = null;
    }
  }
}
