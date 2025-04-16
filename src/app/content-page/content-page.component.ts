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
    console.log(response.data);
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
    console.log('Selected Video:', videoUrl);
  }

  initVideoPlayer(url: string) {
    const videoElement = document.getElementById(
      'videoPlayer'
    ) as HTMLVideoElement;
    if (!videoElement) return;

    this.disposePlayer(); // vorherigen Player entfernen

    this.player = videojs(videoElement, {
      autoplay: false,
      controls: true,
      responsive: true,
      fluid: true,
      sources: [
        {
          src: url,
          type: 'application/x-mpegURL', // für HLS (m3u8)
        },
      ],
    });
  }

  disposePlayer() {
    if (this.player) {
      this.player.dispose();
      this.player = null;
    }
  }
}
