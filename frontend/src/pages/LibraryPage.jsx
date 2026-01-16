import { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Card, CardContent } from '../components/ui/card';
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
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '../components/ui/breadcrumb';
import { RichTextEditor } from '../components/RichTextEditor';
import { 
  ArrowLeft, 
  Plus, 
  Search, 
  Library as LibraryIcon,
  Folder,
  FolderPlus,
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

export const LibraryPage = () => {
  const { projectId } = useParams();
  const { token } = useAuth();
  
  const [folders, setFolders] = useState([]);
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentFolder, setCurrentFolder] = useState(null);
  const [breadcrumbs, setBreadcrumbs] = useState([]);
  const [search, setSearch] = useState('');
  const [sortOrder, setSortOrder] = useState('desc');
  
  const [folderDialogOpen, setFolderDialogOpen] = useState(false);
  const [entryDialogOpen, setEntryDialogOpen] = useState(false);
  const [editingEntry, setEditingEntry] = useState(null);
  const [viewingEntry, setViewingEntry] = useState(null);
  
  const [newFolderName, setNewFolderName] = useState('');
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    is_public: false
  });
  const [saving, setSaving] = useState(false);

  const fetchContents = useCallback(async () => {
    try {
      const params = new URLSearchParams();
      if (currentFolder) params.append('folder_id', currentFolder);
      if (search) params.append('search', search);
      params.append('sort_order', sortOrder);

      const response = await axios.get(`${API}/projects/${projectId}/library?${params}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setFolders(response.data.folders);
      setEntries(response.data.entries);
    } catch (error) {
      toast.error('Failed to load library');
    } finally {
      setLoading(false);
    }
  }, [projectId, token, currentFolder, search, sortOrder]);

  useEffect(() => {
    fetchContents();
  }, [fetchContents]);

  const navigateToFolder = (folderId) => {
    setCurrentFolder(folderId);
    setLoading(true);
  };

  const handleCreateFolder = async (e) => {
    e.preventDefault();
    if (!newFolderName.trim()) {
      toast.error('Folder name is required');
      return;
    }

    setSaving(true);
    try {
      await axios.post(`${API}/projects/${projectId}/library/folders`, {
        name: newFolderName,
        parent_id: currentFolder
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Folder created!');
      setFolderDialogOpen(false);
      setNewFolderName('');
      fetchContents();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create folder');
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteFolder = async (folderId) => {
    try {
      await axios.delete(`${API}/projects/${projectId}/library/folders/${folderId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Folder deleted');
      fetchContents();
    } catch (error) {
      toast.error('Failed to delete folder');
    }
  };

  const handleSubmitEntry = async (e) => {
    e.preventDefault();
    if (!formData.title.trim()) {
      toast.error('Title is required');
      return;
    }

    setSaving(true);
    try {
      if (editingEntry) {
        await axios.put(`${API}/projects/${projectId}/library/entries/${editingEntry.id}`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
        toast.success('Entry updated!');
      } else {
        await axios.post(`${API}/projects/${projectId}/library/entries`, {
          ...formData,
          folder_id: currentFolder
        }, {
          headers: { Authorization: `Bearer ${token}` }
        });
        toast.success('Entry created!');
      }
      setEntryDialogOpen(false);
      resetEntryForm();
      fetchContents();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to save entry');
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteEntry = async (entryId) => {
    try {
      await axios.delete(`${API}/projects/${projectId}/library/entries/${entryId}`, {
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
    setEntryDialogOpen(true);
  };

  const resetEntryForm = () => {
    setEditingEntry(null);
    setFormData({ title: '', description: '', is_public: false });
  };

  return (
    <div className="p-6 md:p-12 lg:p-16" data-testid="library-page">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <Link to={`/projects/${projectId}`}>
          <Button variant="ghost" size="icon">
            <ArrowLeft className="w-5 h-5" />
          </Button>
        </Link>
        <div className="flex-1">
          <h1 className="text-3xl font-display font-bold tracking-tight">Library</h1>
          <p className="text-muted-foreground">Store your experiences and knowledge</p>
        </div>
        <div className="flex gap-2">
          <Dialog open={folderDialogOpen} onOpenChange={setFolderDialogOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" className="gap-2" data-testid="create-library-folder">
                <FolderPlus className="w-4 h-4" />
                New Folder
              </Button>
            </DialogTrigger>
            <DialogContent>
              <form onSubmit={handleCreateFolder}>
                <DialogHeader>
                  <DialogTitle>Create Folder</DialogTitle>
                </DialogHeader>
                <div className="py-4">
                  <Label htmlFor="folderName">Folder Name</Label>
                  <Input
                    id="folderName"
                    value={newFolderName}
                    onChange={(e) => setNewFolderName(e.target.value)}
                    placeholder="Enter folder name"
                  />
                </div>
                <DialogFooter>
                  <Button type="button" variant="outline" onClick={() => setFolderDialogOpen(false)}>Cancel</Button>
                  <Button type="submit" disabled={saving}>
                    {saving && <Loader2 className="w-4 h-4 animate-spin mr-2" />}
                    Create
                  </Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
          
          <Dialog open={entryDialogOpen} onOpenChange={(open) => { setEntryDialogOpen(open); if (!open) resetEntryForm(); }}>
            <DialogTrigger asChild>
              <Button className="rounded-full gap-2" data-testid="create-library-entry">
                <Plus className="w-4 h-4" />
                New Entry
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-2xl max-h-[90vh] overflow-y-auto">
              <form onSubmit={handleSubmitEntry}>
                <DialogHeader>
                  <DialogTitle className="font-display">
                    {editingEntry ? 'Edit Entry' : 'New Library Entry'}
                  </DialogTitle>
                  <DialogDescription>Document your experiences</DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label htmlFor="title">Title</Label>
                    <Input
                      id="title"
                      value={formData.title}
                      onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                      placeholder="Entry title"
                      data-testid="library-title-input"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Description</Label>
                    <RichTextEditor
                      content={formData.description}
                      onChange={(html) => setFormData({ ...formData, description: html })}
                      placeholder="Write your experience..."
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label htmlFor="public">Make Public</Label>
                      <p className="text-sm text-muted-foreground">Visible to others</p>
                    </div>
                    <Switch
                      id="public"
                      checked={formData.is_public}
                      onCheckedChange={(checked) => setFormData({ ...formData, is_public: checked })}
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button type="button" variant="outline" onClick={() => setEntryDialogOpen(false)}>Cancel</Button>
                  <Button type="submit" disabled={saving} data-testid="save-library-entry">
                    {saving && <Loader2 className="w-4 h-4 animate-spin mr-2" />}
                    {editingEntry ? 'Save Changes' : 'Create Entry'}
                  </Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Breadcrumbs */}
      {currentFolder && (
        <Breadcrumb className="mb-4">
          <BreadcrumbList>
            <BreadcrumbItem>
              <BreadcrumbLink 
                onClick={() => navigateToFolder(null)} 
                className="cursor-pointer hover:text-primary"
              >
                Library
              </BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbItem>
              <BreadcrumbPage>Current Folder</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
      )}

      {/* Search */}
      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Search..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
        </div>
        <Button variant="outline" size="icon" onClick={() => setSortOrder(s => s === 'desc' ? 'asc' : 'desc')}>
          <ArrowUpDown className="w-4 h-4" />
        </Button>
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
        </div>
      ) : folders.length === 0 && entries.length === 0 ? (
        <Card className="border border-border/50">
          <CardContent className="py-12 text-center">
            <LibraryIcon className="w-16 h-16 mx-auto text-muted-foreground/30 mb-4" />
            <h3 className="text-xl font-display font-semibold mb-2">Empty Library</h3>
            <p className="text-muted-foreground mb-6">Start building your knowledge base</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {/* Folders */}
          {folders.length > 0 && (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-6">
              {folders.map((folder) => (
                <Card 
                  key={folder.id}
                  className="border border-border/50 cursor-pointer hover:shadow-md transition-all group"
                  onClick={() => navigateToFolder(folder.id)}
                  data-testid={`library-folder-${folder.id}`}
                >
                  <CardContent className="p-4 text-center relative">
                    <Folder className="w-10 h-10 mx-auto text-primary mb-2" />
                    <p className="font-medium truncate text-sm">{folder.name}</p>
                    <AlertDialog>
                      <AlertDialogTrigger asChild>
                        <Button 
                          variant="ghost" 
                          size="icon"
                          className="absolute top-1 right-1 opacity-0 group-hover:opacity-100 h-6 w-6"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <Trash2 className="w-3 h-3 text-destructive" />
                        </Button>
                      </AlertDialogTrigger>
                      <AlertDialogContent onClick={(e) => e.stopPropagation()}>
                        <AlertDialogHeader>
                          <AlertDialogTitle>Delete Folder?</AlertDialogTitle>
                          <AlertDialogDescription>This will delete the folder and all contents.</AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                          <AlertDialogCancel>Cancel</AlertDialogCancel>
                          <AlertDialogAction onClick={() => handleDeleteFolder(folder.id)} className="bg-destructive">
                            Delete
                          </AlertDialogAction>
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {/* Entries */}
          {entries.map((entry) => (
            <Card 
              key={entry.id} 
              className="border border-border/50 hover:shadow-md transition-all"
              data-testid={`library-entry-${entry.id}`}
            >
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <FileText className="w-4 h-4 text-primary" />
                      <h3 className="font-display font-semibold">{entry.title}</h3>
                      {entry.is_public ? (
                        <Badge variant="default" className="gap-1 text-xs">
                          <Globe className="w-3 h-3" /> Public
                        </Badge>
                      ) : (
                        <Badge variant="secondary" className="gap-1 text-xs">
                          <Lock className="w-3 h-3" /> Private
                        </Badge>
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground font-mono-data mb-2">
                      {format(parseISO(entry.created_at), 'PP')} • {entry.views} views
                    </p>
                    <div 
                      className="prose-content text-muted-foreground text-sm line-clamp-2"
                      dangerouslySetInnerHTML={{ __html: entry.description || '<p>No content</p>' }}
                    />
                  </div>
                  <div className="flex gap-1 ml-4">
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
                          <AlertDialogTitle>Delete Entry?</AlertDialogTitle>
                          <AlertDialogDescription>This will permanently delete this entry.</AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                          <AlertDialogCancel>Cancel</AlertDialogCancel>
                          <AlertDialogAction onClick={() => handleDeleteEntry(entry.id)} className="bg-destructive">
                            Delete
                          </AlertDialogAction>
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                  </div>
                </div>
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

export default LibraryPage;
