import { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Switch } from '../components/ui/switch';
import { Badge } from '../components/ui/badge';
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
import { RichTextEditor } from '../components/RichTextEditor';
import { 
  ArrowLeft, 
  Plus, 
  Search, 
  FileText,
  Edit,
  Trash2,
  ArrowUpDown,
  Loader2,
  Eye,
  Globe,
  Lock
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';
import { format, parseISO } from 'date-fns';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const BlogPage = () => {
  const { projectId } = useParams();
  const { token } = useAuth();
  
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState('desc');
  
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingEntry, setEditingEntry] = useState(null);
  const [viewingEntry, setViewingEntry] = useState(null);
  const [saving, setSaving] = useState(false);
  
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    is_public: false
  });

  const fetchEntries = useCallback(async () => {
    try {
      const params = new URLSearchParams();
      if (search) params.append('search', search);
      params.append('sort_by', sortBy);
      params.append('sort_order', sortOrder);

      const response = await axios.get(`${API}/projects/${projectId}/blog?${params}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setEntries(response.data.entries);
    } catch (error) {
      toast.error('Failed to load blog entries');
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
        await axios.put(`${API}/projects/${projectId}/blog/${editingEntry.id}`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
        toast.success('Entry updated!');
      } else {
        await axios.post(`${API}/projects/${projectId}/blog`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
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
      await axios.delete(`${API}/projects/${projectId}/blog/${entryId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Entry deleted');
      setEntries(entries.filter(e => e.id !== entryId));
    } catch (error) {
      toast.error('Failed to delete entry');
    }
  };

  const openEditDialog = (entry) => {
    setEditingEntry(entry);
    setFormData({
      title: entry.title,
      description: entry.description,
      is_public: entry.is_public
    });
    setDialogOpen(true);
  };

  const resetForm = () => {
    setEditingEntry(null);
    setFormData({ title: '', description: '', is_public: false });
  };

  return (
    <div className="p-6 md:p-12 lg:p-16" data-testid="blog-page">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <Link to={`/projects/${projectId}`}>
          <Button variant="ghost" size="icon">
            <ArrowLeft className="w-5 h-5" />
          </Button>
        </Link>
        <div className="flex-1">
          <h1 className="text-3xl font-display font-bold tracking-tight">Blog</h1>
          <p className="text-muted-foreground">Share updates with the world</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={(open) => { setDialogOpen(open); if (!open) resetForm(); }}>
          <DialogTrigger asChild>
            <Button className="rounded-full gap-2" data-testid="create-blog-entry">
              <Plus className="w-4 h-4" />
              New Post
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-2xl max-h-[90vh] overflow-y-auto">
            <form onSubmit={handleSubmit}>
              <DialogHeader>
                <DialogTitle className="font-display">
                  {editingEntry ? 'Edit Post' : 'New Blog Post'}
                </DialogTitle>
                <DialogDescription>
                  Share your experiences and knowledge
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="title">Title</Label>
                  <Input
                    id="title"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    placeholder="Post title"
                    data-testid="blog-title-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label>Content</Label>
                  <RichTextEditor
                    content={formData.description}
                    onChange={(html) => setFormData({ ...formData, description: html })}
                    placeholder="Write your blog post..."
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="public">Make Public</Label>
                    <p className="text-sm text-muted-foreground">Visible on the public blog</p>
                  </div>
                  <Switch
                    id="public"
                    checked={formData.is_public}
                    onCheckedChange={(checked) => setFormData({ ...formData, is_public: checked })}
                    data-testid="blog-public-switch"
                  />
                </div>
              </div>
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button>
                <Button type="submit" disabled={saving} data-testid="save-blog-entry">
                  {saving && <Loader2 className="w-4 h-4 animate-spin mr-2" />}
                  {editingEntry ? 'Save Changes' : 'Publish'}
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
            placeholder="Search posts..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
        </div>
        <div className="flex gap-2">
          <Select value={sortBy} onValueChange={setSortBy}>
            <SelectTrigger className="w-[140px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="created_at">Date</SelectItem>
              <SelectItem value="title">Title</SelectItem>
              <SelectItem value="views">Views</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline" size="icon" onClick={() => setSortOrder(s => s === 'desc' ? 'asc' : 'desc')}>
            <ArrowUpDown className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Entries */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
        </div>
      ) : entries.length === 0 ? (
        <Card className="border border-border/50">
          <CardContent className="py-12 text-center">
            <FileText className="w-16 h-16 mx-auto text-muted-foreground/30 mb-4" />
            <h3 className="text-xl font-display font-semibold mb-2">No Blog Posts Yet</h3>
            <p className="text-muted-foreground mb-6">Share your journey with the world</p>
            <Button onClick={() => setDialogOpen(true)} className="rounded-full gap-2">
              <Plus className="w-4 h-4" />
              Create First Post
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {entries.map((entry) => (
            <Card 
              key={entry.id} 
              className="border border-border/50 hover:shadow-md transition-all"
              data-testid={`blog-entry-${entry.id}`}
            >
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <CardTitle className="font-display text-lg">{entry.title}</CardTitle>
                      {entry.is_public ? (
                        <Badge variant="default" className="gap-1">
                          <Globe className="w-3 h-3" /> Public
                        </Badge>
                      ) : (
                        <Badge variant="secondary" className="gap-1">
                          <Lock className="w-3 h-3" /> Private
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground font-mono-data flex items-center gap-4">
                      <span>{format(parseISO(entry.created_at), 'PP')}</span>
                      <span className="flex items-center gap-1">
                        <Eye className="w-3 h-3" /> {entry.views} views
                      </span>
                    </p>
                  </div>
                  <div className="flex gap-1">
                    <Button variant="ghost" size="icon" onClick={() => setViewingEntry(entry)}>
                      <Eye className="w-4 h-4" />
                    </Button>
                    <Button variant="ghost" size="icon" onClick={() => openEditDialog(entry)}>
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
                          <AlertDialogTitle>Delete Post?</AlertDialogTitle>
                          <AlertDialogDescription>This will permanently delete this blog post.</AlertDialogDescription>
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
                  dangerouslySetInnerHTML={{ __html: entry.description || '<p>No content</p>' }}
                />
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* View Dialog */}
      <Dialog open={!!viewingEntry} onOpenChange={(open) => !open && setViewingEntry(null)}>
        <DialogContent className="sm:max-w-2xl max-h-[90vh] overflow-y-auto">
          {viewingEntry && (
            <>
              <DialogHeader>
                <div className="flex items-center gap-2">
                  <DialogTitle className="font-display text-2xl">{viewingEntry.title}</DialogTitle>
                  {viewingEntry.is_public ? (
                    <Badge variant="default"><Globe className="w-3 h-3 mr-1" /> Public</Badge>
                  ) : (
                    <Badge variant="secondary"><Lock className="w-3 h-3 mr-1" /> Private</Badge>
                  )}
                </div>
                <p className="text-sm text-muted-foreground">
                  {format(parseISO(viewingEntry.created_at), 'PPPp')} • {viewingEntry.views} views
                </p>
              </DialogHeader>
              <div 
                className="prose-content py-4"
                dangerouslySetInnerHTML={{ __html: viewingEntry.description || '<p>No content</p>' }}
              />
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default BlogPage;
