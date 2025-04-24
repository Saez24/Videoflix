import {
  ChangeDetectionStrategy,
  Component,
  OnInit,
  OnDestroy,
  ElementRef,
  ViewChild,
} from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { RouterLink, RouterLinkActive, RouterModule } from '@angular/router';
import { ApiService } from '../shared/services/api/api.service';
import { AsyncPipe, KeyValuePipe, NgFor, NgIf } from '@angular/common';
import { CapitalizePipe } from '../shared/pipes/capitalize.pipe';
import { AuthService } from '../shared/services/authentication/auth.service';
import { BehaviorSubject, Subscription } from 'rxjs';
import { VideoplayerComponent } from './videoplayer/videoplayer.component';
import videojs from 'video.js';

@Component({
  selector: 'app-content-page',
  standalone: true,
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
    VideoplayerComponent,
  ],
  templateUrl: './content-page.component.html',
  styleUrl: './content-page.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ContentPageComponent implements OnInit, OnDestroy {
  @ViewChild('myVideo') myVideo!: ElementRef;

  private player: any;
  private backgroundVideoSubscription: Subscription | null = null;
  constructor(public apiService: ApiService, public authService: AuthService) {
    window.addEventListener('keydown', this.handleEscape);
  }

  videos$ = new BehaviorSubject<any[]>([]);
  thumbnails$ = new BehaviorSubject<string[]>([]);
  backgroundVideoUrl$ = new BehaviorSubject<string>('');
  private latestThumbnailsSubject = new BehaviorSubject<string[]>([]);
  private latestVideosSubject = new BehaviorSubject<any[]>([]);
  latestThumbnails$ = this.latestThumbnailsSubject.asObservable();
  categorizedVideos$ = new BehaviorSubject<{ [category: string]: any[] }>({});
  latestVideos$ = this.latestVideosSubject.asObservable();
  selectedVideoUrl$ = new BehaviorSubject<string | null>(null);

  ngOnInit() {
    this.getVideos();
    this.getThumbnails();
    this.videos$.subscribe((videos) => {
      this.latestVideosSubject.next(videos);
    });
  }

  ngOnDestroy() {
    window.removeEventListener('keydown', this.handleEscape);

    // Clean up Video.js player
    if (this.player) {
      this.player.dispose();
    }

    if (this.backgroundVideoSubscription) {
      this.backgroundVideoSubscription.unsubscribe();
    }
  }

  ngAfterViewInit() {
    // Initialize the Video.js player
    if (this.myVideo) {
      this.player = videojs(this.myVideo.nativeElement, {
        controls: true,
        autoplay: false,
        loop: true,
        muted: true,
        playsinline: true,
        preload: 'auto',
      });

      // Subscribe to changes in the backgroundVideoUrl$
      this.backgroundVideoSubscription = this.backgroundVideoUrl$.subscribe(
        (url) => {
          if (url && this.player) {
            // Set the source to 720p.m3u8 specifically
            const hlsSource = `${url}?quality=720p.m3u8`;
            this.player.src({
              src: hlsSource,
              type: 'application/x-mpegURL',
            });

            // Give the player a moment to load the new source
            setTimeout(() => {
              this.player.load();
              this.player.play().catch((error: unknown) => {
                console.error('Error playing video:', error);
              });
            }, 100);
          }
        }
      );
    }
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
    // Speichere vollständige Video-Objekte oder zumindest Thumbnail + created_at
    const videoThumbnails: { thumbnail: string; created_at: string }[] =
      response.data.map((video: any) => ({
        thumbnail: this.apiService.STATIC_BASE_URL + video.thumbnail,
        created_at: video.created_at,
      }));

    this.thumbnails$.next(
      videoThumbnails.map((item: { thumbnail: string }) => item.thumbnail)
    ); // Nur URLs für thumbnails$
    this.getLatestVideoThumbnails(videoThumbnails); // Vollständige Objekte für die Sortierung
  }

  getLatestVideoThumbnails(videoThumbnails: any[]) {
    const sortedThumbnails = videoThumbnails
      .filter((item) => item.created_at) // Jetzt funktioniert das
      .sort(
        (a, b) =>
          new Date(b.created_at || 0).getTime() -
          new Date(a.created_at || 0).getTime()
      )
      .slice(0, 6)
      .map((item) => item.thumbnail); // Konvertiere zurück zu String-URLs

    this.latestThumbnailsSubject.next(sortedThumbnails);
  }

  setBackgroundVideo(videos: any[]) {
    if (videos.length > 0) {
      const mostViewedVideo = videos.reduce(
        (max, video) => (video.views > max.views ? video : max),
        videos[0]
      );

      // Verwende HLS-Playlist statt der Original-Videodatei
      const videoSource = mostViewedVideo.hls_playlist
        ? this.apiService.STATIC_BASE_URL + mostViewedVideo.hls_playlist
        : this.apiService.STATIC_BASE_URL + mostViewedVideo.video_file;

      this.backgroundVideoUrl$.next(videoSource);
    }
  }

  setSelectedVideo(videoUrl: string | null) {
    this.selectedVideoUrl$.next(videoUrl);
  }
}
