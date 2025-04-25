import {
  Component,
  ElementRef,
  Input,
  OnChanges,
  OnDestroy,
  SimpleChanges,
  ViewChild,
  AfterViewInit,
  Output,
  EventEmitter,
} from '@angular/core';
import videojs from 'video.js';
import '@videojs/http-streaming';
import QualityLevel from 'videojs-contrib-quality-levels/dist/types/quality-level';
import { SnackBarService } from '../../shared/services/snack-bar/snack-bar.service';
import { VideoJsPlayerOptions } from '../../shared/types/video-player.types';

@Component({
  selector: 'app-videoplayer',
  imports: [],
  templateUrl: './videoplayer.component.html',
  styleUrl: './videoplayer.component.scss',
})
export class VideoplayerComponent
  implements OnChanges, OnDestroy, AfterViewInit
{
  @Input() videoUrl: string | null = null;
  @ViewChild('videoElement') videoElement!: ElementRef;
  @Output() timeUpdate = new EventEmitter<{
    currentTime: number;
    duration: number;
    videoEnded?: boolean;
  }>();

  private player: any;
  private qualitySelectorAdded = false;
  private isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
  private progressUpdateInterval: any;
  private startTime: number = 0;

  constructor(private snackBarService: SnackBarService) {}

  ngAfterViewInit() {
    if (this.videoUrl) {
      setTimeout(() => {
        this.initVideoPlayer(this.videoUrl!);
      }, 0);
    }
  }

  ngOnChanges(changes: SimpleChanges) {
    if (
      changes['videoUrl'] &&
      changes['videoUrl'].currentValue !== changes['videoUrl'].previousValue
    ) {
      if (this.videoUrl) {
        this.parseStartTimeFromUrl(this.videoUrl);
        this.disposePlayer();
        this.initVideoPlayer(this.videoUrl);
      } else {
        this.disposePlayer();
      }
    }
  }

  ngOnDestroy() {
    this.disposePlayer();
    this.clearProgressInterval();
  }

  private parseStartTimeFromUrl(url: string): number {
    try {
      const urlObj = typeof url === 'string' ? new URL(url) : url;
      const startTimeParams = urlObj.searchParams.getAll('startTime');
      const startTimeParam =
        startTimeParams.length > 0
          ? startTimeParams[startTimeParams.length - 1]
          : null;

      const startTime = startTimeParam ? parseFloat(startTimeParam) : 0;
      return startTime;
    } catch (e) {
      console.warn('Error parsing URL:', e);

      const regex = /[?&]startTime=([^&]+)/g;
      let match;
      let lastMatch;

      while ((match = regex.exec(url)) !== null) {
        lastMatch = match;
      }

      return lastMatch ? parseFloat(lastMatch[1]) : 0;
    }
  }

  initVideoPlayer(url: string) {
    this.checkDomPresence(url);
  }

  private checkDomPresence(url: string) {
    const videoElement = this.videoElement?.nativeElement;
    if (!videoElement || !document.body.contains(videoElement)) {
      requestAnimationFrame(() => this.checkDomPresence(url));
      return;
    }
    this.initializePlayer(url, videoElement);
  }

  private initializePlayer(url: string, videoElement: HTMLVideoElement) {
    this.startTime = this.parseStartTimeFromUrl(url);

    this.player = videojs(videoElement, this.getPlayerOptions(url));

    this.setupPlayerReadyHandler();
    this.setupPlayerEventHandlers();
    this.setupSafariSpecificHandlers();
    this.setupProgressTracking();
  }

  private getPlayerOptions(url: string): VideoJsPlayerOptions {
    return {
      autoplay: false,
      controls: true,
      responsive: true,
      fluid: true,
      html5: {
        vhs: {
          overrideNative: !this.isSafari,
          fastQualityChange: true,
          useDevicePixelRatio: true,
        },
        nativeAudioTracks: this.isSafari,
        nativeVideoTracks: this.isSafari,
      },
      sources: [
        {
          src: url.split('?')[0],
          type: 'application/x-mpegURL',
        },
      ],
    };
  }

  private setupPlayerReadyHandler() {
    this.player.ready(() => {
      if (this.startTime > 0) {
        this.player.currentTime(this.startTime);
        this.startTime = 0; // WICHTIG: Zurücksetzen nach Gebrauch
      }
    });
  }

  private setupPlayerEventHandlers() {
    const handleTimeUpdate = () => {
      if (this.startTime > 0) {
        this.player.currentTime(this.startTime);
        const initialDelay = this.isSafari ? 1500 : 500;
        setTimeout(() => this.setupQualitySelectorWithRetry(), initialDelay);
      }
    };

    this.player.on('loadedmetadata', () => {
      if (this.startTime > 0) {
        this.player.currentTime(this.startTime);
        this.startTime = 0;
      }
      this.setupQualitySelectorWithRetry();
    });

    this.player.on('play', () => {
      if (this.startTime > 0) {
        this.player.currentTime(this.startTime);
        this.startTime = 0;
      }
      this.setupQualitySelectorWithRetry();
    });

    this.player.on('ended', () => {
      this.timeUpdate.emit({
        currentTime: this.player.duration(),
        duration: this.player.duration(),
        videoEnded: true,
      });
    });
  }

  private setupSafariSpecificHandlers() {
    if (!this.isSafari) return;

    this.player.on('seeked', () => {
      const ct = this.player.currentTime();
      if (ct >= this.player.duration() - 1) {
        this.timeUpdate.emit({
          currentTime: this.player.duration(),
          duration: this.player.duration(),
        });
      }
    });

    this.player.on('timeupdate', () => {
      const currentTime = this.player.currentTime();
      const duration = this.player.duration();

      if (duration && currentTime && duration - currentTime < 0.5) {
        console.log('Manual end detection');
        this.timeUpdate.emit({
          currentTime: duration,
          duration: duration,
        });
      }
    });
  }

  formatTime(seconds: number): string {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds < 10 ? '0' : ''}${remainingSeconds}`;
  }

  setupProgressTracking() {
    this.clearProgressInterval();
    this.progressUpdateInterval = setInterval(() => {
      if (this.player && !this.player.paused()) {
        const currentTime = this.player.currentTime();
        const duration = this.player.duration();
        this.timeUpdate.emit({ currentTime, duration });
      }
    }, 5000);

    if (this.player) {
      this.player.on('pause', () => {
        const currentTime = this.player.currentTime();
        const duration = this.player.duration();
        this.timeUpdate.emit({ currentTime, duration });
      });

      this.player.on('seeked', () => {
        const currentTime = this.player.currentTime();
        const duration = this.player.duration();
        this.timeUpdate.emit({ currentTime, duration });
      });

      this.player.on('loadedmetadata', () => {
        const currentTime = this.player.currentTime();
        const duration = this.player.duration();
        this.timeUpdate.emit({ currentTime, duration });
      });
    }
  }

  clearProgressInterval() {
    if (this.progressUpdateInterval) {
      clearInterval(this.progressUpdateInterval);
      this.progressUpdateInterval = null;
    }
  }

  setupQualitySelectorWithRetry(attempt = 0) {
    const MAX_ATTEMPTS = 8;
    const RETRY_DELAY = 800;

    if (!this.player.qualityLevels) {
      console.warn('Quality levels plugin not loaded');
      return;
    }

    const qualityLevels = this.player.qualityLevels();

    if (!qualityLevels || typeof qualityLevels.length === 'undefined') {
      console.warn('Quality levels not properly initialized');

      if (attempt < MAX_ATTEMPTS) {
        console.log(`Retry attempt ${attempt + 1} of ${MAX_ATTEMPTS}`);
        setTimeout(() => {
          this.setupQualitySelectorWithRetry(attempt + 1);
        }, RETRY_DELAY);
      }
      return;
    }

    const levelsCount = qualityLevels.length;

    if (levelsCount > 0) {
      this.setupQualitySelector();
    } else if (attempt < MAX_ATTEMPTS) {
      console.log(
        `No quality levels found yet. Retry attempt ${
          attempt + 1
        } of ${MAX_ATTEMPTS}`
      );
      setTimeout(() => {
        this.setupQualitySelectorWithRetry(attempt + 1);
      }, RETRY_DELAY);
    } else {
      console.warn('No quality levels available after retries');
    }
  }

  setupQualitySelector() {
    if (this.qualitySelectorAdded) return;

    const qualityLevels = this.player.qualityLevels();
    const levelsArray = Array.from(qualityLevels);
    const MenuButton = videojs.getComponent('MenuButton');
    const qualityMenuButton = new MenuButton(this.player, {
      className: 'vjs-quality-selector',
    });

    const icon = videojs.dom.createEl('span', {
      className: 'vjs-icon-quality',
      innerHTML: '&#x2699;',
    });
    qualityMenuButton.el().appendChild(icon);

    const Menu = videojs.getComponent('Menu');
    const qualityMenu = new Menu(this.player);
    const activeIndex = levelsArray.findIndex(
      (level) => (level as QualityLevel).enabled_
    );

    levelsArray.forEach((level, index) => {
      const MenuItem = videojs.getComponent('MenuItem');
      const menuItem = new MenuItem(this.player, {
        className: 'vjs-menu-item-selectable',
      });

      const label = this.getQualityLabel(level as QualityLevel);
      const labelEl = videojs.dom.createEl('div', {
        className: 'vjs-menu-item-text',
        textContent: label,
      });
      menuItem.el().appendChild(labelEl);

      if (index === activeIndex) {
        menuItem.addClass('vjs-selected');
      }

      menuItem.on('click', () => {
        levelsArray.forEach((_, i) => {
          qualityLevels[i].enabled = i === index;
        });
        qualityMenu.children().forEach((item: any) => {
          item.removeClass('vjs-selected');
        });
        menuItem.addClass('vjs-selected');

        this.snackBarService.showSnackBarChangedVideoQuality(
          this.getQualityLabel(level as QualityLevel)
        );
      });

      qualityMenu.addChild(menuItem);
    });

    qualityMenuButton.addChild(qualityMenu);

    const controlBar = this.player.controlBar;
    controlBar.addChild(
      qualityMenuButton,
      {},
      controlBar.children().length - 2
    );
    this.qualitySelectorAdded = true;
  }

  getQualityLabel(level: QualityLevel): string {
    if (!level) return 'Auto';
    const height = level.height;
    if (!height) return 'Auto';
    if (height >= 1080) return '1080p';
    if (height >= 720) return '720p';
    if (height >= 480) return '480p';
    return `${height}p`;
  }

  disposePlayer() {
    // Emit final time update before dispose
    if (this.player) {
      const currentTime = this.player.currentTime();
      const duration = this.player.duration();
      if (currentTime > 0) {
        this.timeUpdate.emit({ currentTime, duration });
      }

      this.clearProgressInterval();
      this.player.dispose();
      this.player = null;
      this.qualitySelectorAdded = false;
    }
  }
}
