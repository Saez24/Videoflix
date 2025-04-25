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

interface VideoProgress {
  videoId: string;
  currentTime: number;
  duration: number; // Store video duration for progress bar calculation
  title: string;
  thumbnail: string;
  videoUrl: string;
  watchedAt: number; // timestamp when last watched
  videoEnded: boolean; // Indicates if the video has ended
}

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
  private currentVideoId: string | null = null;
  private currentVideoDuration: number = 0;

  constructor(public apiService: ApiService, public authService: AuthService) {
    window.addEventListener('keydown', this.handleEscape);
  }

  videos$ = new BehaviorSubject<any[]>([]);
  thumbnails$ = new BehaviorSubject<string[]>([]);
  backgroundVideoUrl$ = new BehaviorSubject<string>('');
  continueWatchingVideos$ = new BehaviorSubject<VideoProgress[]>([]);
  private latestThumbnailsSubject = new BehaviorSubject<string[]>([]);
  private latestVideosSubject = new BehaviorSubject<any[]>([]);
  latestThumbnails$ = this.latestThumbnailsSubject.asObservable();
  categorizedVideos$ = new BehaviorSubject<{ [category: string]: any[] }>({});
  latestVideos$ = this.latestVideosSubject.asObservable();
  selectedVideoUrl$ = new BehaviorSubject<string | null>(null);
  selectedVideoData$ = new BehaviorSubject<any | null>(null);
  videoTitle: string = '';
  videoDescription: string = '';
  private videoEnded: { [id: string]: boolean } = {};

  ngOnInit() {
    this.getVideos();
    this.getThumbnails();
    this.loadContinueWatchingVideos();
    this.videos$.subscribe((videos) => {
      this.latestVideosSubject.next(videos);
    });
  }

  ngOnDestroy() {
    window.removeEventListener('keydown', this.handleEscape);
    this.saveCurrentVideoProgress();

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
        controls: false,
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
            const hlsSource = `${url}?quality=720p.m3u8`;
            this.player.src({
              src: hlsSource,
              type: 'application/x-mpegURL',
            });
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
      this.saveCurrentVideoProgress();
      this.setSelectedVideo(null, null);
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
    const videoThumbnails: { thumbnail: string; created_at: string }[] =
      response.data.map((video: any) => ({
        thumbnail: this.apiService.STATIC_BASE_URL + video.thumbnail,
        created_at: video.created_at,
      }));

    this.thumbnails$.next(
      videoThumbnails.map((item: { thumbnail: string }) => item.thumbnail)
    );
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

      const videoSource = mostViewedVideo.hls_playlist
        ? this.apiService.STATIC_BASE_URL + mostViewedVideo.hls_playlist
        : this.apiService.STATIC_BASE_URL + mostViewedVideo.video_file;

      this.videoTitle = mostViewedVideo.title;
      this.videoDescription = mostViewedVideo.description;

      this.backgroundVideoUrl$.next(videoSource);
    }
  }

  playBackgroundVideo() {
    console.log('Playing background video');
    const backgroundVideoUrl = this.backgroundVideoUrl$.getValue();
    if (backgroundVideoUrl) {
      const videos = this.videos$.getValue();
      const mostViewedVideo = videos.reduce(
        (max, video) => (video.views > max.views ? video : max),
        videos[0]
      );

      this.setSelectedVideo(backgroundVideoUrl, mostViewedVideo);
    }
  }

  setSelectedVideo(videoUrl: string | null, videoData: any | null) {
    // 1. Beim Schließen (videoUrl === null)
    if (videoUrl === null && this.currentVideoId) {
      console.log('Closing player - checking for ended video');
      if (this.videoEnded[this.currentVideoId]) {
        console.log(`Removing ended video ${this.currentVideoId}`);
        this.removeFromContinueWatching(this.currentVideoId);
        delete this.videoEnded[this.currentVideoId];
      }
      this.selectedVideoUrl$.next(null);
      this.selectedVideoData$.next(null);
      return;
    }

    // 2. Normale Videoauswahl
    this.saveCurrentVideoProgress();
    this.selectedVideoUrl$.next(videoUrl);
    this.selectedVideoData$.next(videoData);
    this.currentVideoId = videoData?.id || videoData?.videoId || null;
  }

  // Called by videoplayer component via event emitter
  onTimeUpdate(event: {
    currentTime: number;
    duration: number;
    videoEnded?: boolean;
  }) {
    if (event.videoEnded && this.currentVideoId) {
      this.videoEnded[this.currentVideoId] = true;
    }

    this.currentVideoDuration = event.duration;
    this.saveVideoProgress(event.currentTime);
  }

  private saveCurrentVideoProgress() {
    if (!this.currentVideoId) {
      return;
    }

    const videoPlayerElement = document.querySelector('app-videoplayer');
    if (!videoPlayerElement) {
      console.log('Cannot save progress - video player element not found');
      return;
    }

    const videoElement = videoPlayerElement.querySelector('video');
    if (!videoElement) {
      console.log('Cannot save progress - video element not found');
      return;
    }

    if (videoElement.currentTime > 0) {
      this.saveVideoProgress(videoElement.currentTime);
    }
  }

  saveVideoProgress(currentTime: number, videoEnded: boolean = false) {
    if (!this.currentVideoId) return;

    const videoData = this.selectedVideoData$.getValue();
    if (!videoData) return;

    const videoUrl = this.selectedVideoUrl$.getValue();
    if (!videoUrl) return;

    const progressEntry: VideoProgress = {
      videoId: this.currentVideoId,
      currentTime: videoEnded ? 0 : currentTime, // Bei Ende auf 0 setzen
      duration: this.currentVideoDuration || 0,
      title: videoData.title,
      thumbnail: this.apiService.STATIC_BASE_URL + videoData.thumbnail,
      videoUrl: videoUrl,
      watchedAt: Date.now(),
      videoEnded: videoEnded, // Neue Eigenschaft
    };

    this.updateContinueWatchingList(progressEntry);
  }

  updateContinueWatchingList(progressEntry: VideoProgress) {
    const userId = this.apiService.getAuthUserId() || 'guest';
    const continueWatchingKey = `${userId}_continue_watching`;
    let continueWatchingList: VideoProgress[] = [];

    try {
      const savedData = localStorage.getItem(continueWatchingKey);
      if (savedData) {
        continueWatchingList = JSON.parse(savedData);
      }
    } catch (error) {
      console.error('Error loading continue watching data:', error);
    }

    const existingIndex = continueWatchingList.findIndex(
      (item) => item.videoId === progressEntry.videoId
    );
    if (existingIndex !== -1) {
      continueWatchingList.splice(existingIndex, 1);
    }

    continueWatchingList.unshift(progressEntry);

    if (continueWatchingList.length > 10) {
      continueWatchingList = continueWatchingList.slice(0, 10);
    }

    localStorage.setItem(
      continueWatchingKey,
      JSON.stringify(continueWatchingList)
    );

    this.continueWatchingVideos$.next(continueWatchingList);
  }

  loadContinueWatchingVideos() {
    const userId = this.apiService.getAuthUserId() || 'guest';
    const continueWatchingKey = `${userId}_continue_watching`;

    try {
      const savedData = localStorage.getItem(continueWatchingKey);
      if (savedData) {
        const continueWatchingList: VideoProgress[] = JSON.parse(savedData);
        continueWatchingList.sort((a, b) => b.watchedAt - a.watchedAt);

        this.continueWatchingVideos$.next(continueWatchingList);
      } else {
        console.log('No continue watching data found in localStorage');
      }
    } catch (error) {
      console.error('Error loading continue watching data:', error);
      this.continueWatchingVideos$.next([]);
    }
  }

  playVideoFromProgress(progressEntry: VideoProgress) {
    // Vollständige Videodaten finden
    const allVideos = this.videos$.getValue();
    const videoData = allVideos.find((v) => v.id === progressEntry.videoId);

    if (videoData) {
      this.setSelectedVideo(progressEntry.videoUrl, videoData);
      this.selectedVideoUrl$.next(
        `${progressEntry.videoUrl}?startTime=${progressEntry.currentTime}`
      );
    } else {
      // Fallback, falls Videodaten nicht gefunden werden
      this.setSelectedVideo(progressEntry.videoUrl, {
        id: progressEntry.videoId,
        title: progressEntry.title,
        thumbnail: progressEntry.thumbnail,
      });
      this.selectedVideoUrl$.next(
        `${progressEntry.videoUrl}?startTime=${progressEntry.currentTime}`
      );
    }
  }

  async removeFromContinueWatching(videoId: string) {
    console.log(`Attempting to remove video ${videoId}`);

    const userId = this.apiService.getAuthUserId() || 'guest';
    const continueWatchingKey = `${userId}_continue_watching`;

    try {
      const savedData = localStorage.getItem(continueWatchingKey);
      if (!savedData) {
        console.log('No continue watching data found');
        return;
      }

      let continueWatchingList: VideoProgress[] = JSON.parse(savedData);
      const initialLength = continueWatchingList.length;

      // Filtere ALLE Einträge mit dieser videoId heraus (nicht nur ended)
      continueWatchingList = continueWatchingList.filter(
        (item) => item.videoId !== videoId
      );

      if (continueWatchingList.length < initialLength) {
        console.log(`Successfully removed video ${videoId}`);
        localStorage.setItem(
          continueWatchingKey,
          JSON.stringify(continueWatchingList)
        );
        this.continueWatchingVideos$.next(continueWatchingList);
      } else {
        console.log(`Video ${videoId} not found in continue watching list`);
      }
    } catch (error) {
      console.error('Error removing video:', error);
    }
  }
}
