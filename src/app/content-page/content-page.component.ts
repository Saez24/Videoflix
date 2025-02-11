import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { RouterLink, RouterLinkActive, RouterModule } from '@angular/router';
import { ApiService } from '../shared/services/api/api.service';
import { NgFor, NgIf } from '@angular/common';
import { CapitalizePipe } from '../shared/pipes/capitalize.pipe';
import { AuthService } from '../shared/services/authentication/auth.service';

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
  ],
  templateUrl: './content-page.component.html',
  styleUrl: './content-page.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ContentPageComponent implements OnInit {
  constructor(public apiService: ApiService, public authService: AuthService) {}
  videos: any[] = [];
  thumbnails: any[] = [];
  backgroundVideoUrl: string = '';
  latestVideos: any[] = [];
  latestTumbnails: any[] = [];
  categorizedVideos: { [category: string]: any[] } = {};

  ngOnInit() {
    // this.apiService.getAuthUser();
    // this.apiService.getAuthUserId();
    this.getVideos();
    this.getThumbnails();
  }

  getVideos() {
    this.apiService.getData('content/').then((response) => {
      this.videos = response.data;
      console.log('Videos:', this.videos);
      this.groupVideosByCategory();
      this.setBackgroundVideo();
    });
  }

  getCategories(): string[] {
    return Object.keys(this.categorizedVideos);
  }

  groupVideosByCategory() {
    this.categorizedVideos = {};

    this.videos.forEach((video) => {
      const category = video.category; // Verwenden der einzelnen Kategorie als String

      if (category) {
        // Sicherstellen, dass die Kategorie existiert
        if (!this.categorizedVideos[category]) {
          this.categorizedVideos[category] = [];
        }
        this.categorizedVideos[category].push(video);
      }
    });

    console.log('Categorized Videos:', this.categorizedVideos);
  }

  getThumbnails() {
    this.apiService.getData('content/').then((response) => {
      // Korrekt die URLs der Thumbnails extrahieren
      this.thumbnails = response.data.map(
        (video: any) => this.apiService.STATIC_BASE_URL + video.thumbnail
      );
      console.log('Thumbnails:', this.thumbnails);
      this.getLatestVideoThumbnails();
    });
  }

  getLatestVideoThumbnails() {
    this.latestTumbnails = this.thumbnails
      .sort(
        (a, b) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      )
      .slice(0, 6); // Die neuesten 6 Videos
    console.log('Latest Tumbnails:', this.latestTumbnails);
  }

  setBackgroundVideo() {
    if (this.videos.length > 0) {
      const mostViewedVideo = this.videos.reduce(
        (max, video) => (video.views > max.views ? video : max),
        this.videos[0]
      );

      this.backgroundVideoUrl =
        this.apiService.STATIC_BASE_URL + mostViewedVideo.video_file;
      console.log('Most Viewed Video:', this.backgroundVideoUrl);
    }
  }
}
