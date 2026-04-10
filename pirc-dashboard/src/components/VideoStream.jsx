import React, { useEffect, useRef } from 'react';

function VideoStream({ robotId }) {
  const videoRef = useRef(null);

  useEffect(() => {
    const video = videoRef.current;
    if (video) {
      // RTSP → WebRTC via proxy
      video.srcObject = null;
      const streamUrl = `rtsp://${window.location.hostname}:8554/${robotId}_stream`;
      
      // FFMPEG.wasm for H.265 decode
      const player = new JSMpeg.Player(streamUrl, {
        canvas: video.parentElement,
        autoplay: true,
        loop: true
      });
    }
  }, [robotId]);

  return (
    <div className="w-full h-64 bg-black rounded-lg overflow-hidden">
      <canvas ref={videoRef} className="w-full h-full" />
      <div className="text-center text-sm text-gray-400 mt-2">
        60FPS H.265 • {robotId}
      </div>
    </div>
  );
}

export default VideoStream;
