import { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Badge } from '../components/ui/badge';
import { ImageUploader } from '../components/ImageUploader';
import { ImageLightbox } from '../components/ImageLightbox';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../components/ui/dialog';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '../components/ui/alert-dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import { SimpleEditor } from '../components/SimpleEditor';
import { 
  ArrowLeft, 
  Plus, 
  Search, 
  BookOpen,
  Calendar,
  Edit,
  Trash2,
  ArrowUpDown,
  Loader2,
  Eye,
  Upload,
  Image,
  X
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';
import { format, parseISO } from 'date-fns';
import { getImageUrl, getThumbUrl } from '../utils';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const DiaryPage = () => {
  const { projectId } = useParams();
  const { token } = useAuth();
  
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('entry_datetime');
  const [sortOrder, setSortOrder] = useState('desc');
  
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingEntry, setEditingEntry] = useState(null);
  const [viewingEntry, setViewingEntry] = useState(null);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [diaryImageUploaderOpen, setDiaryImageUploaderOpen] = useState(false);
  const [lightboxOpen, setLightboxOpen] = useState(false);
  const [lightboxIndex, setLightboxIndex] = useState(0);
  
  const [formData, setFormData] = useState({
    title: '',
    story: '',
    entry_datetime: new Date().toISOString().slice(0, 16)
  });
  const [entryImages, setEntryImages] = useState([]);

  const fetchEntries = useCallback(async () => {
    try {
      const params = new URLSearchParams();
      if (search) params.append('search', search);
      params.append('sort_by', sortBy);
      params.append('sort_order', sortOrder);

      const response = await axios.get(`${API}/projects/${projectId}/diary?${params}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setEntries(response.data.entries);
    } catch (error) {
      toast.error('Failed to load diary entries');
    } finally {
      setLoading(false);
    }
  }, [projectId, token, search, sortBy, sortOrder]);

  useEffect(() => {
    fetchEntries();
  }, [fetchEntries]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.title.trim()) {
      toast.error('Title is required');
      return;
    }

    setSaving(true);
    try {
      if (editingEntry) {
        await axios.put(`${API}/projects/${projectId}/diary/${editingEntry.id}`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
        toast.success('Entry updated!');
      } else {
        const response = await axios.post(`${API}/projects/${projectId}/diary`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (entryImages.length > 0) {
          toast.info(`Uploading ${entryImages.length} image(s)...`);
          for (const img of entryImages) {
            if (img.file) {
              const fd = new FormData();
              fd.append('file', img.file);
              await axios.post(`${API}/projects/${projectId}/diary/${response.data.id}/images`, fd, {
                headers: { Authorization: `Bearer ${token}` }
              });
            }
          }
        }
        toast.success('Entry created!');
      }
      setDialogOpen(false);
      resetForm();
      fetchEntries();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to save entry');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (entryId) => {
    try {
      await axios.delete(`${API}/projects/${projectId}/diary/${entryId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Entry deleted');
      setEntries(entries.filter(e => e.id !== entryId));
    } catch (error) {
      toast.error('Failed to delete entry');
    }
  };

  const handleImageUpload = async (file) => {
    if (editingEntry) {
      setUploading(true);
      try {
        const fd = new FormData();
        fd.append('file', file);
        const response = await axios.post(
          `${API}/projects/${projectId}/diary/${editingEntry.id}/images`,
          fd,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        setEntryImages([...entryImages, response.data]);
        toast.success('Image uploaded!');
      } catch (error) {
        toast.error('Failed to upload image');
      } finally {
        setUploading(false);
      }
    } else {
      const preview = URL.createObjectURL(file);
      setEntryImages([...entryImages, { id: `temp-${Date.now()}`, file, preview, filename: file.name }]);
    }
  };

  const handleDeleteImage = async (image) => {
    if (image.file) {
      setEntryImages(entryImages.filter(i => i.id !== image.id));
      URL.revokeObjectURL(image.preview);
    } else if (editingEntry) {
      try {
        await axios.delete(
          `${API}/projects/${projectId}/diary/${editingEntry.id}/images/${image.id}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        setEntryImages(entryImages.filter(i => i.id !== image.id));
        toast.success('Image deleted');
      } catch (error) {
        toast.error('Failed to delete image');
      }
    }
  };

  const openEditDialog = (entry) => {
    setEditingEntry(entry);
    setFormData({
      title: entry.title,
      story: entry.story,
      entry_datetime: entry.entry_datetime.slice(0, 16)
    });
    setEntryImages(entry.images || []);
    setDialogOpen(true);
  };

  const resetForm = () => {
    setEditingEntry(null);
    setFormData({
      title: '',
      story: '',
      entry_datetime: new Date().toISOString().slice(0, 16)
    });
    entryImages.forEach(img => {
      if (img.preview) URL.revokeObjectURL(img.preview);
    });
    setEntryImages([]);
  };

  return (
    <div className="p-6 md:p-12 lg:p-16" data-testid="diary-page">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <Link to={`/projects/${projectId}`}>
          <Button variant="ghost" size="icon">
            <ArrowLeft className="w-5 h-5" />
          </Button>
        </Link>
        <div className="flex-1">
          <h1 className="text-3xl font-display font-bold tracking-tight">Diary</h1>
          <p className="text-muted-foreground">Document your daily progress</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={(open) => { setDialogOpen(open); if (!open) resetForm(); }}>
          <DialogTrigger asChild>
            <Button className="rounded-full gap-2" data-testid="create-diary-entry">
              <Plus className="w-4 h-4" />
              New Entry
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-2xl max-h-[90vh] overflow-y-auto">
            <form onSubmit={handleSubmit}>
              <DialogHeader>
                <DialogTitle className="font-display">
                  {editingEntry ? 'Edit Entry' : 'New Diary Entry'}
                </DialogTitle>
                <DialogDescription>
                  Record your thoughts and progress
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="title">Title</Label>
                    <Input
                      id="title"
                      value={formData.title}
                      onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                      placeholder="Entry title"
                      data-testid="diary-title-input"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="datetime">Date & Time</Label>
                    <Input
                      id="datetime"
                      type="datetime-local"
                      value={formData.entry_datetime}
                      onChange={(e) => setFormData({ ...formData, entry_datetime: e.target.value })}
                      data-testid="diary-datetime-input"
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Story</Label>
                  <SimpleEditor
                    content={formData.story}
                    onChange={(html) => setFormData({ ...formData, story: html })}
                    placeholder="Write your diary entry..."
                  />
                </div>

                {/* Image Attachments */}
                <div className="space-y-2">
                  <Label>Images</Label>
                  <div className="border border-input rounded-lg p-4">
                    {entryImages.length > 0 && (
                      <div className="grid grid-cols-3 gap-2 mb-4">
                        {entryImages.map((image) => (
                          <div key={image.id} className="relative group aspect-square">
                            <img
                              src={image.preview || getImageUrl(image.url, token)}
                              alt={image.filename}
                              className="w-full h-full object-cover rounded-lg"
                            />
                            <Button
                              type="button"
                              variant="destructive"
                              size="icon"
                              className="absolute top-1 right-1 h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity"
                              onClick={() => handleDeleteImage(image)}
                            >
                              <X className="w-3 h-3" />
                            </Button>
                          </div>
                        ))}
                      </div>
                    )}
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => setDiaryImageUploaderOpen(true)}
                      disabled={uploading}
                      className="w-full"
                    >
                      {uploading ? (
                        <Loader2 className="w-4 h-4 animate-spin mr-2" />
                      ) : (
                        <Upload className="w-4 h-4 mr-2" />
                      )}
                      Add Image
                    </Button>
                  </div>
                </div>
              </div>
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={saving} data-testid="save-diary-entry">
                  {saving && <Loader2 className="w-4 h-4 animate-spin mr-2" />}
                  {editingEntry ? 'Save Changes' : 'Create Entry'}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Search entries..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
            data-testid="search-diary"
          />
        </div>
        <div className="flex gap-2">
          <Select value={sortBy} onValueChange={setSortBy}>
            <SelectTrigger className="w-[160px]">
              <SelectValue placeholder="Sort by" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="entry_datetime">Date</SelectItem>
              <SelectItem value="title">Title</SelectItem>
              <SelectItem value="created_at">Created</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline" size="icon" onClick={() => setSortOrder(s => s === 'desc' ? 'asc' : 'desc')}>
            <ArrowUpDown className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Entries List */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
        </div>
      ) : entries.length === 0 ? (
        <Card className="border border-border/50">
          <CardContent className="py-12 text-center">
            <BookOpen className="w-16 h-16 mx-auto text-muted-foreground/30 mb-4" />
            <h3 className="text-xl font-display font-semibold mb-2">No Diary Entries Yet</h3>
            <p className="text-muted-foreground mb-6">Start documenting your journey</p>
            <Button onClick={() => setDialogOpen(true)} className="rounded-full gap-2">
              <Plus className="w-4 h-4" />
              Create First Entry
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {entries.map((entry) => (
            <Card 
              key={entry.id} 
              className="border border-border/50 hover:shadow-md transition-all"
              data-testid={`diary-entry-${entry.id}`}
            >
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <CardTitle className="font-display text-lg">{entry.title}</CardTitle>
                      {entry.images?.length > 0 && (
                        <Badge variant="outline" className="gap-1">
                          <Image className="w-3 h-3" /> {entry.images.length}
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground font-mono-data flex items-center gap-2 mt-1">
                      <Calendar className="w-4 h-4" />
                      {format(parseISO(entry.entry_datetime), 'PPp')}
                    </p>
                  </div>
                  <div className="flex gap-1">
                    <Button 
                      variant="ghost" 
                      size="icon"
                      onClick={() => setViewingEntry(entry)}
                      data-testid={`view-entry-${entry.id}`}
                    >
                      <Eye className="w-4 h-4" />
                    </Button>
                    <Button 
                      variant="ghost" 
                      size="icon"
                      onClick={() => openEditDialog(entry)}
                      data-testid={`edit-entry-${entry.id}`}
                    >
                      <Edit className="w-4 h-4" />
                    </Button>
                    <AlertDialog>
                      <AlertDialogTrigger asChild>
                        <Button variant="ghost" size="icon" className="text-destructive">
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </AlertDialogTrigger>
                      <AlertDialogContent>
                        <AlertDialogHeader>
                          <AlertDialogTitle>Delete Entry?</AlertDialogTitle>
                          <AlertDialogDescription>
                            This will permanently delete this diary entry and all its images.
                          </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                          <AlertDialogCancel>Cancel</AlertDialogCancel>
                          <AlertDialogAction 
                            onClick={() => handleDelete(entry.id)}
                            className="bg-destructive text-destructive-foreground"
                          >
                            Delete
                          </AlertDialogAction>
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div 
                  className="prose-content text-muted-foreground line-clamp-3"
                  dangerouslySetInnerHTML={{ __html: entry.story || '<p>No content</p>' }}
                />
                {entry.images?.length > 0 && (
                  <div className="flex gap-2 mt-3 overflow-x-auto">
                    {entry.images.slice(0, 4).map((img) => (
                      <img
                        key={img.id}
                        src={getThumbUrl(img.url, token)}
                        alt={img.filename}
                        className="w-16 h-16 object-cover rounded-lg flex-shrink-0"
                      />
                    ))}
                    {entry.images.length > 4 && (
                      <div className="w-16 h-16 bg-muted rounded-lg flex items-center justify-center flex-shrink-0">
                        <span className="text-sm text-muted-foreground">+{entry.images.length - 4}</span>
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* View Entry Dialog */}
      <Dialog open={!!viewingEntry} onOpenChange={(open) => !open && setViewingEntry(null)}>
        <DialogContent className="sm:max-w-2xl max-h-[90vh] overflow-y-auto">
          {viewingEntry && (
            <>
              <DialogHeader>
                <DialogTitle className="font-display text-2xl">{viewingEntry.title}</DialogTitle>
                <p className="text-sm text-muted-foreground font-mono-data">
                  {format(parseISO(viewingEntry.entry_datetime), 'PPPp')}
                </p>
              </DialogHeader>
              <div 
                className="prose-content py-4"
                dangerouslySetInnerHTML={{ __html: viewingEntry.story || '<p>No content</p>' }}
              />
              {viewingEntry.images?.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-muted-foreground">Attached Images</h4>
                  <div className="grid grid-cols-2 gap-2">
                    {viewingEntry.images.map((img, idx) => (
                      <img
                        key={img.id}
                        src={getImageUrl(img.url, token)}
                        alt={img.filename}
                        className="w-full rounded-lg cursor-pointer hover:opacity-90 transition-opacity"
                        onClick={() => { setLightboxIndex(idx); setLightboxOpen(true); }}
                        data-testid={`diary-image-${img.id}`}
                      />
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </DialogContent>
      </Dialog>

      <ImageUploader
        open={diaryImageUploaderOpen}
        onClose={() => setDiaryImageUploaderOpen(false)}
        onUpload={handleImageUpload}
        mode="free"
        maxWidth={1600}
        title="Upload Diary Image"
      />

      {viewingEntry?.images?.length > 0 && (
        <ImageLightbox
          images={viewingEntry.images}
          currentIndex={lightboxIndex}
          open={lightboxOpen}
          onClose={() => setLightboxOpen(false)}
          getImageSrc={(img) => getImageUrl(img.url, token)}
        />
      )}
    </div>
  );
};

export default DiaryPage;
