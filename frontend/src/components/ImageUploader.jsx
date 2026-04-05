import { useState, useRef, useCallback } from 'react';
import ReactCrop from 'react-image-crop';
import 'react-image-crop/dist/ReactCrop.css';
import imageCompression from 'browser-image-compression';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from './ui/dialog';
import { Button } from './ui/button';
import { Loader2, Upload, Crop, Check, X, ImageIcon } from 'lucide-react';

/**
 * Centralized image uploader with crop + resize + compress.
 *
 * Props:
 *  - open: boolean
 *  - onClose: () => void
 *  - onUpload: (processedFile: File) => Promise<void>  — called with the final file
 *  - mode: 'cover' | 'free'
 *      cover = forced 3:2 aspect crop (project covers)
 *      free  = optional free-form crop (gallery, blog, library)
 *  - maxWidth: number (default 1920)
 *  - title: string (dialog title)
 */
export const ImageUploader = ({ open, onClose, onUpload, mode = 'free', maxWidth = 1920, title = 'Upload Image' }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [crop, setCrop] = useState(undefined);
  const [completedCrop, setCompletedCrop] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [step, setStep] = useState('select'); // select, crop, uploading
  const imgRef = useRef(null);
  const fileInputRef = useRef(null);

  const reset = () => {
    setSelectedFile(null);
    setPreview(null);
    setCrop(undefined);
    setCompletedCrop(null);
    setStep('select');
    setUploading(false);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleClose = () => {
    reset();
    onClose();
  };

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!file.type.startsWith('image/')) {
      return;
    }
    setSelectedFile(file);
    const reader = new FileReader();
    reader.onload = () => {
      setPreview(reader.result);
      setStep('crop');
    };
    reader.readAsDataURL(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (!file || !file.type.startsWith('image/')) return;
    setSelectedFile(file);
    const reader = new FileReader();
    reader.onload = () => {
      setPreview(reader.result);
      setStep('crop');
    };
    reader.readAsDataURL(file);
  };

  const onImageLoad = useCallback((e) => {
    imgRef.current = e.currentTarget;
    const { width, height } = e.currentTarget;
    if (mode === 'cover') {
      // Force 3:2 aspect ratio, centered
      const aspect = 3 / 2;
      let cropW, cropH;
      if (width / height > aspect) {
        cropH = height;
        cropW = height * aspect;
      } else {
        cropW = width;
        cropH = width / aspect;
      }
      setCrop({
        unit: 'px',
        x: (width - cropW) / 2,
        y: (height - cropH) / 2,
        width: cropW,
        height: cropH,
      });
    }
  }, [mode]);

  const getCroppedCanvas = () => {
    const image = imgRef.current;
    if (!image || !completedCrop) return null;

    const canvas = document.createElement('canvas');
    const scaleX = image.naturalWidth / image.width;
    const scaleY = image.naturalHeight / image.height;

    const cropX = completedCrop.x * scaleX;
    const cropY = completedCrop.y * scaleY;
    const cropW = completedCrop.width * scaleX;
    const cropH = completedCrop.height * scaleY;

    canvas.width = cropW;
    canvas.height = cropH;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(image, cropX, cropY, cropW, cropH, 0, 0, cropW, cropH);
    return canvas;
  };

  const processAndUpload = async (useCrop) => {
    setUploading(true);
    setStep('uploading');

    try {
      let blob;

      if (useCrop && completedCrop && completedCrop.width > 0 && completedCrop.height > 0) {
        const canvas = getCroppedCanvas();
        if (!canvas) { setUploading(false); setStep('crop'); return; }
        blob = await new Promise((resolve) => canvas.toBlob(resolve, 'image/jpeg', 0.92));
      } else {
        blob = selectedFile;
      }

      // Compress + resize
      const options = {
        maxWidthOrHeight: maxWidth,
        maxSizeMB: 2,
        useWebWorker: true,
        fileType: 'image/jpeg',
        initialQuality: 0.82,
      };

      const compressed = await imageCompression(new File([blob], selectedFile.name, { type: blob.type || 'image/jpeg' }), options);
      const finalFile = new File([compressed], selectedFile.name.replace(/\.[^.]+$/, '.jpg'), { type: 'image/jpeg' });

      await onUpload(finalFile);
      handleClose();
    } catch (err) {
      console.error('Image processing error:', err);
      setUploading(false);
      setStep('crop');
    }
  };

  return (
    <Dialog open={open} onOpenChange={(o) => !o && handleClose()}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <ImageIcon className="w-5 h-5" />
            {title}
          </DialogTitle>
          <DialogDescription>
            {mode === 'cover'
              ? 'Select and crop your image to a 3:2 aspect ratio'
              : 'Select an image. You can optionally crop before uploading.'}
          </DialogDescription>
        </DialogHeader>

        {/* Step: Select */}
        {step === 'select' && (
          <div
            className="border-2 border-dashed rounded-lg p-8 text-center cursor-pointer hover:border-primary/50 transition-colors"
            onClick={() => fileInputRef.current?.click()}
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
            data-testid="image-drop-zone"
          >
            <Upload className="w-10 h-10 mx-auto text-muted-foreground mb-3" />
            <p className="font-medium">Click or drag an image here</p>
            <p className="text-sm text-muted-foreground mt-1">JPEG, PNG, GIF, WEBP</p>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              className="hidden"
              data-testid="image-file-input"
            />
          </div>
        )}

        {/* Step: Crop */}
        {step === 'crop' && preview && (
          <div className="space-y-4">
            <div className="max-h-[400px] overflow-auto rounded-lg bg-muted/30 flex items-center justify-center">
              <ReactCrop
                crop={crop}
                onChange={(c) => setCrop(c)}
                onComplete={(c) => setCompletedCrop(c)}
                aspect={mode === 'cover' ? 3 / 2 : undefined}
                data-testid="image-crop-area"
              >
                <img
                  src={preview}
                  alt="Preview"
                  onLoad={onImageLoad}
                  style={{ maxHeight: '400px', maxWidth: '100%' }}
                />
              </ReactCrop>
            </div>
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span>
                {mode === 'cover' ? 'Drag to adjust the 3:2 crop area' : 'Drag to select a crop area (optional)'}
              </span>
              {completedCrop && completedCrop.width > 0 && (
                <span>{Math.round(completedCrop.width)}x{Math.round(completedCrop.height)}px</span>
              )}
            </div>
          </div>
        )}

        {/* Step: Uploading */}
        {step === 'uploading' && (
          <div className="flex flex-col items-center gap-4 py-8" data-testid="image-uploading">
            <Loader2 className="w-10 h-10 animate-spin text-primary" />
            <p className="text-sm text-muted-foreground">Processing and uploading...</p>
          </div>
        )}

        {step === 'crop' && (
          <DialogFooter className="flex gap-2 sm:gap-2">
            <Button variant="outline" onClick={handleClose} disabled={uploading}>
              <X className="w-4 h-4 mr-2" />Cancel
            </Button>
            {mode !== 'cover' && (
              <Button
                variant="secondary"
                onClick={() => processAndUpload(false)}
                disabled={uploading}
                data-testid="upload-skip-crop-btn"
              >
                <Upload className="w-4 h-4 mr-2" />Upload without crop
              </Button>
            )}
            <Button
              onClick={() => processAndUpload(true)}
              disabled={uploading || !completedCrop || completedCrop.width === 0}
              data-testid="upload-with-crop-btn"
            >
              {uploading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Crop className="w-4 h-4 mr-2" />}
              {mode === 'cover' ? 'Crop & Upload' : 'Crop & Upload'}
            </Button>
          </DialogFooter>
        )}
      </DialogContent>
    </Dialog>
  );
};

export default ImageUploader;
