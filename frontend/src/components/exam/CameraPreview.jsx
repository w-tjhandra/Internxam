import { useEffect, useRef } from "react";

export const CameraPreview = ({ stream }) => {
  const ref = useRef(null);
  useEffect(() => {
    if (ref.current && stream) ref.current.srcObject = stream;
  }, [stream]);
  return (
    <div className="relative border border-zinc-200 bg-zinc-950" data-testid="camera-preview-box">
      <video ref={ref} autoPlay muted playsInline className="w-full aspect-video object-cover" />
      <div className="absolute top-1.5 left-1.5 flex items-center gap-1.5 bg-black/70 px-2 py-0.5">
        <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />
        <span className="text-[10px] font-medium text-white uppercase tracking-wider">Sesi Diawasi</span>
      </div>
    </div>
  );
};
