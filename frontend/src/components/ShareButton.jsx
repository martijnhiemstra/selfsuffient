import { useState } from 'react';
import { Button } from './ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from './ui/dropdown-menu';
import { Share2, Twitter, Facebook, Linkedin, Copy, Check, Mail } from 'lucide-react';
import { toast } from 'sonner';

/**
 * Social sharing component for projects, blogs, and library entries
 */
export const ShareButton = ({ 
  title, 
  description, 
  url,
  className = "",
  variant = "outline",
  size = "sm"
}) => {
  const [copied, setCopied] = useState(false);
  
  // Get the full URL to share
  const shareUrl = url || (typeof window !== 'undefined' ? window.location.href : '');
  
  // Clean description for sharing (remove HTML)
  const cleanDescription = description?.replace(/<[^>]*>/g, '').slice(0, 200) || '';
  
  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      toast.success('Link copied to clipboard!');
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      toast.error('Failed to copy link');
    }
  };
  
  const shareToTwitter = () => {
    const text = `${title}${cleanDescription ? ' - ' + cleanDescription : ''}`;
    const twitterUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(shareUrl)}`;
    window.open(twitterUrl, '_blank', 'width=600,height=400');
  };
  
  const shareToFacebook = () => {
    const facebookUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}`;
    window.open(facebookUrl, '_blank', 'width=600,height=400');
  };
  
  const shareToLinkedin = () => {
    const linkedinUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl)}`;
    window.open(linkedinUrl, '_blank', 'width=600,height=400');
  };
  
  const shareViaEmail = () => {
    const subject = encodeURIComponent(title || 'Check this out!');
    const body = encodeURIComponent(`${cleanDescription}\n\n${shareUrl}`);
    window.location.href = `mailto:?subject=${subject}&body=${body}`;
  };
  
  const handleNativeShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: title,
          text: cleanDescription,
          url: shareUrl,
        });
      } catch (err) {
        if (err.name !== 'AbortError') {
          console.error('Error sharing:', err);
        }
      }
    }
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button 
          variant={variant} 
          size={size} 
          className={`gap-2 ${className}`}
          data-testid="share-button"
        >
          <Share2 className="w-4 h-4" />
          Share
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48">
        {typeof navigator !== 'undefined' && navigator.share && (
          <>
            <DropdownMenuItem onClick={handleNativeShare} data-testid="share-native">
              <Share2 className="w-4 h-4 mr-2" />
              Share...
            </DropdownMenuItem>
            <DropdownMenuSeparator />
          </>
        )}
        <DropdownMenuItem onClick={shareToTwitter} data-testid="share-twitter">
          <Twitter className="w-4 h-4 mr-2" />
          Twitter / X
        </DropdownMenuItem>
        <DropdownMenuItem onClick={shareToFacebook} data-testid="share-facebook">
          <Facebook className="w-4 h-4 mr-2" />
          Facebook
        </DropdownMenuItem>
        <DropdownMenuItem onClick={shareToLinkedin} data-testid="share-linkedin">
          <Linkedin className="w-4 h-4 mr-2" />
          LinkedIn
        </DropdownMenuItem>
        <DropdownMenuItem onClick={shareViaEmail} data-testid="share-email">
          <Mail className="w-4 h-4 mr-2" />
          Email
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={handleCopyLink} data-testid="share-copy-link">
          {copied ? (
            <Check className="w-4 h-4 mr-2 text-green-500" />
          ) : (
            <Copy className="w-4 h-4 mr-2" />
          )}
          {copied ? 'Copied!' : 'Copy Link'}
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

/**
 * Inline share icons for compact display
 */
export const ShareIcons = ({ title, description, url, className = "" }) => {
  const [copied, setCopied] = useState(false);
  const shareUrl = url || (typeof window !== 'undefined' ? window.location.href : '');
  const cleanDescription = description?.replace(/<[^>]*>/g, '').slice(0, 200) || '';

  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      toast.success('Link copied!');
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      toast.error('Failed to copy link');
    }
  };

  const shareToTwitter = () => {
    const text = `${title}${cleanDescription ? ' - ' + cleanDescription : ''}`;
    const twitterUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(shareUrl)}`;
    window.open(twitterUrl, '_blank', 'width=600,height=400');
  };

  const shareToFacebook = () => {
    const facebookUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}`;
    window.open(facebookUrl, '_blank', 'width=600,height=400');
  };

  return (
    <div className={`flex items-center gap-1 ${className}`}>
      <Button
        variant="ghost"
        size="icon"
        className="h-8 w-8"
        onClick={shareToTwitter}
        title="Share on Twitter"
        data-testid="share-icon-twitter"
      >
        <Twitter className="w-4 h-4" />
      </Button>
      <Button
        variant="ghost"
        size="icon"
        className="h-8 w-8"
        onClick={shareToFacebook}
        title="Share on Facebook"
        data-testid="share-icon-facebook"
      >
        <Facebook className="w-4 h-4" />
      </Button>
      <Button
        variant="ghost"
        size="icon"
        className="h-8 w-8"
        onClick={handleCopyLink}
        title={copied ? 'Copied!' : 'Copy link'}
        data-testid="share-icon-copy"
      >
        {copied ? (
          <Check className="w-4 h-4 text-green-500" />
        ) : (
          <Copy className="w-4 h-4" />
        )}
      </Button>
    </div>
  );
};
