import {
  Component,
  ElementRef,
  Input,
  OnChanges,
  OnDestroy,
  OnInit,
  SimpleChanges,
  ViewChild,
  AfterViewInit,
} from '@angular/core';
import videojs from 'video.js';
import '@videojs/http-streaming';
import QualityLevel from 'videojs-contrib-quality-levels/dist/types/quality-level';
import { SnackBarService } from '../../shared/services/snack-bar/snack-bar.service';

@Component({
  selector: 'app-videoplayer',
  imports: [],
  templateUrl: './videoplayer.component.html',
  styleUrl: './videoplayer.component.scss',
})
export class VideoplayerComponent
  implements OnInit, OnChanges, OnDestroy, AfterViewInit
{
  @Input() videoUrl: string | null = null;
  @ViewChild('videoElement') videoElement!: ElementRef;

  private player: any;
  private qualitySelectorAdded = false;

  constructor(private snackBarService: SnackBarService) {}

  ngOnInit() {}

  ngAfterViewInit() {
    if (this.videoUrl) {
      // Small timeout to ensure DOM is ready
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
        this.initVideoPlayer(this.videoUrl);
      } else {
        this.disposePlayer();
      }
    }
  }

  ngOnDestroy() {
    this.disposePlayer();
  }

  private isSafari(): boolean {
    const ua = navigator.userAgent.toLowerCase();
    return (
      ua.indexOf('safari') !== -1 &&
      ua.indexOf('chrome') === -1 &&
      ua.indexOf('android') === -1
    );
  }

  initVideoPlayer(url: string) {
    this.disposePlayer();

    const checkDomPresence = () => {
      const videoElement = this.videoElement?.nativeElement;
      if (!videoElement || !document.body.contains(videoElement)) {
        // Try again in the next frame if not present
        requestAnimationFrame(checkDomPresence);
        return;
      }

      const isSafari = this.isSafari();

      this.player = videojs(videoElement, {
        autoplay: false,
        controls: true,
        responsive: true,
        fluid: true,
        html5: {
          vhs: {
            overrideNative: !isSafari, // Wichtig für Safari: Lasse native HLS zu
            fastQualityChange: true,
            useDevicePixelRatio: true,
          },
          nativeAudioTracks: isSafari,
          nativeVideoTracks: isSafari,
        },
        sources: [
          {
            src: url,
            type: 'application/x-mpegURL',
          },
        ],
      });

      // Events
      this.player.on('loadedmetadata', () => {
        console.log('Video metadata loaded');
        setTimeout(() => this.setupQualitySelectorWithRetry(), 500);
      });
    };
    checkDomPresence();
  }

  setupQualitySelectorWithRetry(attempt = 0) {
    const MAX_ATTEMPTS = 8; // Mehr Versuche für Safari
    const RETRY_DELAY = 800; // Längere Verzögerung

    // Stelle sicher, dass das Plugin aktiv ist
    if (!this.player.qualityLevels) {
      console.warn('Quality levels plugin not loaded');
      return;
    }

    const qualityLevels = this.player.qualityLevels();

    // Prüfe, ob qualityLevels ein gültiges Objekt ist
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

    // Mehr Debug-Informationen
    console.log(`Quality levels found: ${levelsCount}`);

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
      });

      // Label erstellen
      const label = this.getQualityLabel(level as QualityLevel);
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

        // Snackbar anzeigen
        this.snackBarService.showSnackBarChangedVideoQuality(
          this.getQualityLabel(level as QualityLevel)
        );
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
    this.qualitySelectorAdded = true;
  }

  // Hilfsfunktion für Qualitäts-Labels
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
    if (this.player) {
      this.player.dispose();
      this.player = null;
    }
  }
}
