import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { RouterLink, RouterLinkActive, RouterModule } from '@angular/router';
import { ApiService } from '../shared/services/api/api.service';
import { AsyncPipe, KeyValuePipe, NgFor, NgIf } from '@angular/common';
import { CapitalizePipe } from '../shared/pipes/capitalize.pipe';
import { AuthService } from '../shared/services/authentication/auth.service';
import { BehaviorSubject, Observable } from 'rxjs';

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
export class ContentPageComponent implements OnInit {
  constructor(public apiService: ApiService, public authService: AuthService) {}

  videos$ = new BehaviorSubject<any[]>([]);
  thumbnails$ = new BehaviorSubject<string[]>([]);
  backgroundVideoUrl$ = new BehaviorSubject<string>('');
  private latestThumbnailsSubject = new BehaviorSubject<string[]>([]);
  latestThumbnails$ = this.latestThumbnailsSubject.asObservable();
  categorizedVideos$ = new BehaviorSubject<{ [category: string]: any[] }>({});
  selectedVideoUrl$ = new BehaviorSubject<string | null>(null);
  currentQuality = '720p'; // Standardqualität
  selectedVideo: string | null = null; // Das aktuell ausgewählte Video
  showQualityMenu = false; // Steuerung der Sichtbarkeit des Qualitätsmenüs
  availableQualities: ('360p' | '720p' | '1080p')[] = ['360p', '720p', '1080p'];

  // Hier definierst du die Videoquellen für jede Qualität
  qualitySources: { [key in '360p' | '720p' | '1080p']: string } = {
    '360p': 'path_to_video_360p.mp4',
    '720p': 'path_to_video_720p.mp4',
    '1080p': 'path_to_video_1080p.mp4',
  };

  ngOnInit() {
    this.getVideos();
    this.getThumbnails();
  }

  // ngAfterViewInit() {
  //   // this.apiService.getAuthUser();
  //   // this.apiService.getAuthUserId();
  //   this.getVideos();
  //   this.getThumbnails();
  // }

  async getVideos() {
    const response = await this.apiService.getData('content/');
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
    const response = await this.apiService.getData('content/');
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

  // Methode zum Setzen des ausgewählten Videos
  setSelectedVideo(videoUrl: string | null) {
    this.selectedVideoUrl$.next(videoUrl);
  }

  // Methode zum Wechseln der Qualität
  changeQuality(quality: '360p' | '720p' | '1080p') {
    this.currentQuality = quality;
    this.selectedVideo = this.qualitySources[quality];
    this.showQualityMenu = false; // Menü ausblenden nach Auswahl
  }

  // Methode zum Öffnen und Schließen des Qualitätsmenüs
  toggleQualityMenu() {
    this.showQualityMenu = !this.showQualityMenu;
  }

  // Methode zum Schließen des Video-Overlays
}
