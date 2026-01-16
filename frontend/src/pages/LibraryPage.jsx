import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useSortPreference } from '../hooks/useSortPreference';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Switch } from '../components/ui/switch';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
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
} from '../components/ui/alert-dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import { Badge } from '../components/ui/badge';
import { 
  Plus, 
  FolderPlus,
  Folder,
  FolderOpen,
  FileText,
  Search,
  ArrowUpDown,
  Trash2,
  Edit,
  Loader2,
  ChevronRight,
  Home,
  Globe,
  Lock,
  Eye
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';
import RichTextEditor from '../components/RichTextEditor';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const LibraryPage = () => {
  const { projectId } = useParams();
  const { token } = useAuth();
  
  const [folders, setFolders] = useState([]);
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentFolderId, setCurrentFolderId] = useState(null);
  const [breadcrumbs, setBreadcrumbs] = useState([]);
  const [search, setSearch] = useState('');
  const [sortPreference, setSortPreference] = useSortPreference('library', { sortBy: 'created_at', sortOrder: 'desc' });
  
  const [folderDialogOpen, setFolderDialogOpen] = useState(false);
  const [entryDialogOpen, setEntryDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [folderName, setFolderName] = useState('');
  const [itemToDelete, setItemToDelete] = useState(null);
  const [editingEntry, setEditingEntry] = useState(null);
  
  const [entryForm, setEntryForm] = useState({
    title: '',
    description: '',
    is_public: false
  });

  const fetchLibrary = useCallback(async () => {
    try {
      let url = `${API}/projects/${projectId}/library?sort_by=${sortPreference.sortBy}&sort_order=${sortPreference.sortOrder}`;
      if (currentFolderId) url += `&folder_id=${currentFolderId}`;
      if (search) url += `&search=${encodeURIComponent(search)}`;
      
      const response = await axios.get(url, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setFolders(response.data.folders || []);
      setEntries(response.data.entries || []);
    } catch (error) {
      toast.error('Failed to load library');
    } finally {
      setLoading(false);
    }
  }, [projectId, token, currentFolderId, search, sortPreference]);

  const fetchBreadcrumbs = useCallback(async () => {
    if (!currentFolderId) {
      setBreadcrumbs([]);
      return;
    }
    try {
      const response = await axios.get(
        `${API}/projects/${projectId}/library/folders/${currentFolderId}/path`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setBreadcrumbs(response.data.path || []);
    } catch (error) {
      console.error('Failed to load breadcrumbs');
    }
  }, [projectId, token, currentFolderId]);

  useEffect(() => {
    fetchLibrary();
  }, [fetchLibrary]);

  useEffect(() => {
    fetchBreadcrumbs();
  }, [fetchBreadcrumbs]);

  const handleCreateFolder = async (e) => {
    e.preventDefault();
    if (!folderName.trim()) return;
    
    setSaving(true);
    try {
      await axios.post(
        `${API}/projects/${projectId}/library/folders`,
        { name: folderName, parent_id: currentFolderId },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success('Folder created!');
      setFolderDialogOpen(false);
      setFolderName('');
      fetchLibrary();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create folder');
    } finally {
      setSaving(false);
    }
  };

  const handleSaveEntry = async (e) => {
    e.preventDefault();
    if (!entryForm.title.trim()) return;
    
    setSaving(true);
    try {
      const payload = {
        ...entryForm,
        folder_id: currentFolderId
      };
      
      if (editingEntry) {
        await axios.put(
          `${API}/projects/${projectId}/library/entries/${editingEntry.id}`,
          payload,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        toast.success('Entry updated!');
      } else {
        await axios.post(
          `${API}/projects/${projectId}/library/entries`,
          payload,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        toast.success('Entry created!');
      }
      
      setEntryDialogOpen(false);
      resetEntryForm();
      fetchLibrary();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to save entry');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!itemToDelete) return;
    
    setSaving(true);
    try {
      if (itemToDelete.type === 'folder') {
        await axios.delete(
          `${API}/projects/${projectId}/library/folders/${itemToDelete.id}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        toast.success('Folder deleted!');
      } else {
        await axios.delete(
          `${API}/projects/${projectId}/library/entries/${itemToDelete.id}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        toast.success('Entry deleted!');
      }
      setDeleteDialogOpen(false);
      setItemToDelete(null);
      fetchLibrary();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to delete');
    } finally {
      setSaving(false);
    }
  };

  const openEditDialog = (entry) => {
    setEditingEntry(entry);
    setEntryForm({
      title: entry.title,
      description: entry.description || '',
      is_public: entry.is_public
    });
    setEntryDialogOpen(true);
  };

  const resetEntryForm = () => {
    setEntryForm({ title: '', description: '', is_public: false });
    setEditingEntry(null);
  };

  const navigateToFolder = (folderId) => {
    setCurrentFolderId(folderId);
    setLoading(true);
  };

  const navigateUp = () => {
    if (breadcrumbs.length > 1) {
      setCurrentFolderId(breadcrumbs[breadcrumbs.length - 2].id);
    } else {
      setCurrentFolderId(null);
    }
    setLoading(true);
  };

  return (
    <div className="p-6 md:p-12 lg:p-16" data-testid="library-page">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-display font-bold tracking-tight">Library</h1>
          <p className="text-muted-foreground">Manage your project knowledge base</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" className="rounded-full gap-2" onClick={() => setFolderDialogOpen(true)} data-testid="create-folder-btn">
            <FolderPlus className="w-4 h-4" /> New Folder
          </Button>
          <Button className="rounded-full gap-2" onClick={() => { resetEntryForm(); setEntryDialogOpen(true); }} data-testid="create-entry-btn">
            <Plus className="w-4 h-4" /> New Entry
          </Button>
        </div>
      </div>

      {/* Breadcrumbs */}
      <div className="flex items-center gap-2 mb-4 p-3 bg-muted/50 rounded-lg overflow-x-auto" data-testid="breadcrumbs">
        <Button 
          variant="ghost" 
          size="sm" 
          className="gap-1 flex-shrink-0"
          onClick={() => { setCurrentFolderId(null); setLoading(true); }}
          data-testid="breadcrumb-root"
        >
          <Home className="w-4 h-4" /> Root
        </Button>
        {breadcrumbs.map((folder, idx) => (
          <div key={folder.id} className="flex items-center gap-2 flex-shrink-0">
            <ChevronRight className="w-4 h-4 text-muted-foreground" />
            <Button
              variant={idx === breadcrumbs.length - 1 ? "secondary" : "ghost"}
              size="sm"
              onClick={() => navigateToFolder(folder.id)}
              data-testid={`breadcrumb-${folder.id}`}
            >
              {folder.name}
            </Button>
          </div>
        ))}
      </div>

      {/* Search and Sort */}
      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input 
            placeholder="Search entries and folders..." 
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10 rounded-full"
            data-testid="search-input"
          />
        </div>
        <Select value={`${sortPreference.sortBy}-${sortPreference.sortOrder}`} onValueChange={(v) => {
          const [sortBy, sortOrder] = v.split('-');
          setSortPreference({ sortBy, sortOrder });
        }}>
          <SelectTrigger className="w-48 rounded-full" data-testid="sort-select">
            <ArrowUpDown className="w-4 h-4 mr-2" />
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="created_at-desc">Newest First</SelectItem>
            <SelectItem value="created_at-asc">Oldest First</SelectItem>
            <SelectItem value="title-asc">Title A-Z</SelectItem>
            <SelectItem value="title-desc">Title Z-A</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {loading ? (
        <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>
      ) : folders.length === 0 && entries.length === 0 ? (
        <Card className="border border-border/50">
          <CardContent className="py-12 text-center">
            <FileText className="w-16 h-16 mx-auto text-muted-foreground/30 mb-4" />
            <h3 className="text-xl font-display font-semibold mb-2">
              {currentFolderId ? 'This folder is empty' : 'No entries yet'}
            </h3>
            <p className="text-muted-foreground mb-6">
              {currentFolderId ? 'Create entries or subfolders' : 'Start building your knowledge base'}
            </p>
            <div className="flex justify-center gap-2">
              <Button variant="outline" onClick={() => setFolderDialogOpen(true)}>
                <FolderPlus className="w-4 h-4 mr-2" /> New Folder
              </Button>
              <Button onClick={() => { resetEntryForm(); setEntryDialogOpen(true); }}>
                <Plus className="w-4 h-4 mr-2" /> New Entry
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-6">
          {/* Folders */}
          {(currentFolderId || folders.length > 0) && (
            <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-4">
              {currentFolderId && (
                <Card 
                  className="border border-border/50 cursor-pointer hover:shadow-md transition-all group"
                  onClick={navigateUp}
                  data-testid="folder-back"
                >
                  <CardContent className="p-4 text-center">
                    <FolderOpen className="w-10 h-10 mx-auto text-primary/60 mb-2" />
                    <p className="text-sm font-medium">..</p>
                  </CardContent>
                </Card>
              )}
              {folders.map((folder) => (
                <Card 
                  key={folder.id} 
                  className="border border-border/50 cursor-pointer hover:shadow-md transition-all group"
                  data-testid={`folder-${folder.id}`}
                >
                  <CardContent className="p-4 text-center relative">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity h-6 w-6"
                      onClick={(e) => { e.stopPropagation(); setItemToDelete({ type: 'folder', id: folder.id, name: folder.name }); setDeleteDialogOpen(true); }}
                    >
                      <Trash2 className="w-3 h-3 text-destructive" />
                    </Button>
                    <div onClick={() => navigateToFolder(folder.id)}>
                      <Folder className="w-10 h-10 mx-auto text-amber-500 mb-2" />
                      <p className="text-sm font-medium truncate">{folder.name}</p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
          
          {/* Entries */}
          {entries.length > 0 && (
            <div className="space-y-4">
              <h3 className="text-lg font-medium text-muted-foreground">Entries</h3>
              <div className="grid gap-4">
                {entries.map((entry) => (
                  <Card 
                    key={entry.id} 
                    className="border border-border/50 hover:shadow-md transition-all"
                    data-testid={`entry-${entry.id}`}
                  >
                    <CardHeader className="pb-2">
                      <div className="flex items-start justify-between">
                        <div className="flex items-center gap-2">
                          <FileText className="w-5 h-5 text-primary" />
                          <CardTitle className="font-display text-lg">{entry.title}</CardTitle>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge variant={entry.is_public ? "default" : "secondary"} className="gap-1">
                            {entry.is_public ? <Globe className="w-3 h-3" /> : <Lock className="w-3 h-3" />}
                            {entry.is_public ? 'Public' : 'Private'}
                          </Badge>
                          {entry.views > 0 && (
                            <Badge variant="outline" className="gap-1">
                              <Eye className="w-3 h-3" />
                              {entry.views}
                            </Badge>
                          )}
                          <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => openEditDialog(entry)}>
                            <Edit className="w-4 h-4" />
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="icon" 
                            className="h-8 w-8"
                            onClick={() => { setItemToDelete({ type: 'entry', id: entry.id, name: entry.title }); setDeleteDialogOpen(true); }}
                          >
                            <Trash2 className="w-4 h-4 text-destructive" />
                          </Button>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div 
                        className="prose-content text-sm text-muted-foreground line-clamp-2"
                        dangerouslySetInnerHTML={{ __html: entry.description?.slice(0, 200) || 'No description' }}
                      />
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Create Folder Dialog */}
      <Dialog open={folderDialogOpen} onOpenChange={setFolderDialogOpen}>
        <DialogContent>
          <form onSubmit={handleCreateFolder}>
            <DialogHeader>
              <DialogTitle className="font-display">New Folder</DialogTitle>
              <DialogDescription>Create a new folder {currentFolderId ? 'in this location' : 'in the root'}</DialogDescription>
            </DialogHeader>
            <div className="py-4">
              <Label htmlFor="folderName">Folder Name</Label>
              <Input 
                id="folderName"
                value={folderName}
                onChange={(e) => setFolderName(e.target.value)}
                placeholder="Enter folder name"
                className="mt-2"
                data-testid="folder-name-input"
              />
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setFolderDialogOpen(false)}>Cancel</Button>
              <Button type="submit" disabled={saving || !folderName.trim()} data-testid="save-folder-btn">
                {saving && <Loader2 className="w-4 h-4 animate-spin mr-2" />}
                Create Folder
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Create/Edit Entry Dialog */}
      <Dialog open={entryDialogOpen} onOpenChange={(open) => { setEntryDialogOpen(open); if (!open) resetEntryForm(); }}>
        <DialogContent className="sm:max-w-2xl">
          <form onSubmit={handleSaveEntry}>
            <DialogHeader>
              <DialogTitle className="font-display">{editingEntry ? 'Edit Entry' : 'New Entry'}</DialogTitle>
              <DialogDescription>{editingEntry ? 'Update your library entry' : 'Create a new knowledge base entry'}</DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="entryTitle">Title</Label>
                <Input 
                  id="entryTitle"
                  value={entryForm.title}
                  onChange={(e) => setEntryForm({ ...entryForm, title: e.target.value })}
                  placeholder="Entry title"
                  data-testid="entry-title-input"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="entryDescription">Content</Label>
                <RichTextEditor 
                  content={entryForm.description}
                  onChange={(html) => setEntryForm({ ...entryForm, description: html })}
                />
              </div>
              <div className="flex items-center justify-between">
                <Label htmlFor="entryPublic">Make Public</Label>
                <Switch 
                  id="entryPublic"
                  checked={entryForm.is_public}
                  onCheckedChange={(c) => setEntryForm({ ...entryForm, is_public: c })}
                  data-testid="entry-public-switch"
                />
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => { setEntryDialogOpen(false); resetEntryForm(); }}>Cancel</Button>
              <Button type="submit" disabled={saving || !entryForm.title.trim()} data-testid="save-entry-btn">
                {saving && <Loader2 className="w-4 h-4 animate-spin mr-2" />}
                {editingEntry ? 'Update Entry' : 'Create Entry'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete {itemToDelete?.type === 'folder' ? 'Folder' : 'Entry'}</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete "{itemToDelete?.name}"? 
              {itemToDelete?.type === 'folder' && ' This will also delete all contents inside.'}
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete} className="bg-destructive text-destructive-foreground hover:bg-destructive/90" data-testid="confirm-delete-btn">
              {saving && <Loader2 className="w-4 h-4 animate-spin mr-2" />}
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default LibraryPage;
