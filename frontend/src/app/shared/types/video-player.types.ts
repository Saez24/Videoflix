export interface VideoJsPlayerOptions {
  autoplay?: boolean;
  controls?: boolean;
  responsive?: boolean;
  fluid?: boolean;
  html5?: {
    vhs?: {
      overrideNative?: boolean;
      fastQualityChange?: boolean;
      useDevicePixelRatio?: boolean;
    };
    nativeAudioTracks?: boolean;
    nativeVideoTracks?: boolean;
  };
  sources?: Array<{
    src: string;
    type: string;
  }>;
}
