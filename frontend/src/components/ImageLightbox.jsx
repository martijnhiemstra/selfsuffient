import { useState, useEffect, useCallback } from 'react';
import { Button } from './ui/button';
import { ChevronLeft, ChevronRight, X, Download } from 'lucide-react';

/**
 * Full-screen image lightbox with prev/next navigation, keyboard support, and thumbnail strip.
 *
 * Props:
 *  - images: Array<{ id, url, filename }> — all images to navigate through
 *  - currentIndex: number — initially selected image index
 *  - open: boolean
 *  - onClose: () => void
 *  - getImageSrc: (image) => string — function to resolve image URL (for auth tokens etc.)
 */
export const ImageLightbox = ({ images = [], currentIndex = 0, open, onClose, getImageSrc }) => {
  const [index, setIndex] = useState(currentIndex);

  useEffect(() => {
    setIndex(currentIndex);
  }, [currentIndex, open]);

  const goPrev = useCallback(() => setIndex(i => Math.max(0, i - 1)), []);
  const goNext = useCallback(() => setIndex(i => Math.min(images.length - 1, i + 1)), [images.length]);

  useEffect(() => {
    if (!open) return;
    const handleKey = (e) => {
      if (e.key === 'Escape') onClose();
      if (e.key === 'ArrowLeft') goPrev();
      if (e.key === 'ArrowRight') goNext();
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [open, onClose, goPrev, goNext]);

  // Prevent body scroll when open
  useEffect(() => {
    if (open) {
      document.body.style.overflow = 'hidden';
      return () => { document.body.style.overflow = ''; };
    }
  }, [open]);

  if (!open || images.length === 0) return null;

  const current = images[index];
  if (!current) return null;
  const src = getImageSrc ? getImageSrc(current) : current.url;

  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = src;
    link.download = current.filename || 'image';
    link.click();
  };

  return (
    <div
      className="fixed inset-0 z-50 bg-black/95 flex flex-col"
      data-testid="image-lightbox"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      {/* Top Bar */}
      <div className="flex items-center justify-between px-4 py-3 bg-gradient-to-b from-black/80 to-transparent absolute top-0 left-0 right-0 z-10">
        <span className="text-white/80 text-sm font-medium" data-testid="lightbox-counter">
          {index + 1} of {images.length}
        </span>
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="icon"
            className="text-white hover:bg-white/20"
            onClick={handleDownload}
            title="Download"
            data-testid="lightbox-download-btn"
          >
            <Download className="w-5 h-5" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="text-white hover:bg-white/20"
            onClick={onClose}
            data-testid="lightbox-close-btn"
          >
            <X className="w-5 h-5" />
          </Button>
        </div>
      </div>

      {/* Image */}
      <div className="flex-1 flex items-center justify-center p-4 pt-16 pb-4">
        <img
          src={src}
          alt={current.filename || ''}
          className="max-w-full max-h-[80vh] object-contain select-none"
          data-testid="lightbox-image"
          draggable={false}
        />
      </div>

      {/* Navigation Arrows */}
      {images.length > 1 && (
        <>
          <Button
            variant="ghost"
            size="icon"
            className="absolute left-4 top-1/2 -translate-y-1/2 w-12 h-12 rounded-full bg-black/50 text-white hover:bg-black/70 disabled:opacity-30"
            onClick={goPrev}
            disabled={index === 0}
            data-testid="lightbox-prev-btn"
          >
            <ChevronLeft className="w-8 h-8" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="absolute right-4 top-1/2 -translate-y-1/2 w-12 h-12 rounded-full bg-black/50 text-white hover:bg-black/70 disabled:opacity-30"
            onClick={goNext}
            disabled={index === images.length - 1}
            data-testid="lightbox-next-btn"
          >
            <ChevronRight className="w-8 h-8" />
          </Button>
        </>
      )}

      {/* Thumbnail Strip */}
      {images.length > 1 && (
        <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/80 to-transparent">
          <div className="flex gap-2 justify-center overflow-x-auto pb-2">
            {images.map((img, i) => (
              <button
                key={img.id}
                onClick={() => setIndex(i)}
                className={`flex-shrink-0 w-16 h-16 rounded-lg overflow-hidden border-2 transition-all ${
                  i === index
                    ? 'border-white scale-110'
                    : 'border-transparent opacity-60 hover:opacity-100'
                }`}
                data-testid={`lightbox-thumb-${i}`}
              >
                <img
                  src={getImageSrc ? getImageSrc(img) : img.url}
                  alt={img.filename || ''}
                  className="w-full h-full object-cover"
                />
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageLightbox;
