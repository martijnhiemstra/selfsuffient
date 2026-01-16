import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useSortPreference } from '../hooks/useSortPreference';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
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
import { 
  Plus, 
  FolderPlus,
  Folder,
  FolderOpen,
  Image,
  Search,
  ArrowUpDown,
  Trash2,
  Loader2,
  ChevronRight,
  Home,
  Upload
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const GalleryPage = () => {
  const { projectId } = useParams();
  const { token } = useAuth();
  
  const [folders, setFolders] = useState([]);
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentFolderId, setCurrentFolderId] = useState(null);
  const [breadcrumbs, setBreadcrumbs] = useState([]);
  const [search, setSearch] = useState('');
  const { sortBy, setSortBy, sortOrder, setSortOrder } = useSortPreference('gallery', 'created_at', 'desc');
  
  const [folderDialogOpen, setFolderDialogOpen] = useState(false);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [folderName, setFolderName] = useState('');
  const [folderIsPublic, setFolderIsPublic] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [itemToDelete, setItemToDelete] = useState(null);
  const [uploading, setUploading] = useState(false);

  const fetchGallery = useCallback(async () => {
    try {
      let url = `${API}/projects/${projectId}/gallery?sort_by=${sortBy}&sort_order=${sortOrder}`;
      if (currentFolderId) url += `&folder_id=${currentFolderId}`;
      if (search) url += `&search=${encodeURIComponent(search)}`;
      
      const response = await axios.get(url, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setFolders(response.data.folders || []);
      setImages(response.data.images || []);
    } catch (error) {
      toast.error('Failed to load gallery');
    } finally {
      setLoading(false);
    }
  }, [projectId, token, currentFolderId, search, sortBy, sortOrder]);

  const fetchBreadcrumbs = useCallback(async () => {
    if (!currentFolderId) {
      setBreadcrumbs([]);
      return;
    }
    try {
      const response = await axios.get(
        `${API}/projects/${projectId}/gallery/folders/${currentFolderId}/path`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setBreadcrumbs(response.data.path || []);
    } catch (error) {
      console.error('Failed to load breadcrumbs');
    }
  }, [projectId, token, currentFolderId]);

  useEffect(() => {
    fetchGallery();
  }, [fetchGallery]);

  useEffect(() => {
    fetchBreadcrumbs();
  }, [fetchBreadcrumbs]);

  const handleCreateFolder = async (e) => {
    e.preventDefault();
    if (!folderName.trim()) return;
    
    setSaving(true);
    try {
      await axios.post(
        `${API}/projects/${projectId}/gallery/folders`,
        { name: folderName, parent_id: currentFolderId, is_public: folderIsPublic },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success('Folder created!');
      setFolderDialogOpen(false);
      setFolderName('');
      setFolderIsPublic(false);
      fetchGallery();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create folder');
    } finally {
      setSaving(false);
    }
  };

  const handleUploadImage = async (e) => {
    e.preventDefault();
    if (!selectedFile) return;
    
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      if (currentFolderId) formData.append('folder_id', currentFolderId);
      
      await axios.post(
        `${API}/projects/${projectId}/gallery/images`,
        formData,
        { headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'multipart/form-data' } }
      );
      toast.success('Image uploaded!');
      setUploadDialogOpen(false);
      setSelectedFile(null);
      fetchGallery();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to upload image');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async () => {
    if (!itemToDelete) return;
    
    setSaving(true);
    try {
      if (itemToDelete.type === 'folder') {
        await axios.delete(
          `${API}/projects/${projectId}/gallery/folders/${itemToDelete.id}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        toast.success('Folder deleted!');
      } else {
        await axios.delete(
          `${API}/projects/${projectId}/gallery/images/${itemToDelete.id}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        toast.success('Image deleted!');
      }
      setDeleteDialogOpen(false);
      setItemToDelete(null);
      fetchGallery();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to delete');
    } finally {
      setSaving(false);
    }
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
    <div className="p-6 md:p-12 lg:p-16" data-testid="gallery-page">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-display font-bold tracking-tight">Gallery</h1>
          <p className="text-muted-foreground">Manage your project images</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" className="rounded-full gap-2" onClick={() => setFolderDialogOpen(true)} data-testid="create-folder-btn">
            <FolderPlus className="w-4 h-4" /> New Folder
          </Button>
          <Button className="rounded-full gap-2" onClick={() => setUploadDialogOpen(true)} data-testid="upload-image-btn">
            <Upload className="w-4 h-4" /> Upload Image
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
            placeholder="Search images and folders..." 
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10 rounded-full"
            data-testid="search-input"
          />
        </div>
        <Select value={`${sortBy}-${sortOrder}`} onValueChange={(v) => {
          const [newSortBy, newSortOrder] = v.split('-');
          setSortBy(newSortBy);
          setSortOrder(newSortOrder);
        }}>
          <SelectTrigger className="w-48 rounded-full" data-testid="sort-select">
            <ArrowUpDown className="w-4 h-4 mr-2" />
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="created_at-desc">Newest First</SelectItem>
            <SelectItem value="created_at-asc">Oldest First</SelectItem>
            <SelectItem value="name-asc">Name A-Z</SelectItem>
            <SelectItem value="name-desc">Name Z-A</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {loading ? (
        <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>
      ) : folders.length === 0 && images.length === 0 ? (
        <Card className="border border-border/50">
          <CardContent className="py-12 text-center">
            <Image className="w-16 h-16 mx-auto text-muted-foreground/30 mb-4" />
            <h3 className="text-xl font-display font-semibold mb-2">
              {currentFolderId ? 'This folder is empty' : 'No images yet'}
            </h3>
            <p className="text-muted-foreground mb-6">
              {currentFolderId ? 'Upload images or create subfolders' : 'Create folders and upload your first images'}
            </p>
            <div className="flex justify-center gap-2">
              <Button variant="outline" onClick={() => setFolderDialogOpen(true)}>
                <FolderPlus className="w-4 h-4 mr-2" /> New Folder
              </Button>
              <Button onClick={() => setUploadDialogOpen(true)}>
                <Plus className="w-4 h-4 mr-2" /> Upload Image
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          {/* Back button if in subfolder */}
          {currentFolderId && (
            <Card 
              className="border border-border/50 cursor-pointer hover:shadow-md transition-all group"
              onClick={navigateUp}
              data-testid="folder-back"
            >
              <CardContent className="p-4 text-center">
                <FolderOpen className="w-12 h-12 mx-auto text-primary/60 mb-2" />
                <p className="text-sm font-medium">..</p>
                <p className="text-xs text-muted-foreground">Go back</p>
              </CardContent>
            </Card>
          )}
          
          {/* Folders */}
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
                  className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity h-8 w-8"
                  onClick={(e) => { e.stopPropagation(); setItemToDelete({ type: 'folder', id: folder.id, name: folder.name }); setDeleteDialogOpen(true); }}
                  data-testid={`delete-folder-${folder.id}`}
                >
                  <Trash2 className="w-4 h-4 text-destructive" />
                </Button>
                <div onClick={() => navigateToFolder(folder.id)}>
                  <Folder className="w-12 h-12 mx-auto text-amber-500 mb-2" />
                  <p className="text-sm font-medium truncate">{folder.name}</p>
                </div>
              </CardContent>
            </Card>
          ))}
          
          {/* Images */}
          {images.map((image) => (
            <Card 
              key={image.id} 
              className="border border-border/50 overflow-hidden group"
              data-testid={`image-${image.id}`}
            >
              <div className="aspect-square relative">
                <img 
                  src={`${process.env.REACT_APP_BACKEND_URL}${image.url}`}
                  alt={image.filename}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
                <Button
                  variant="secondary"
                  size="icon"
                  className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity h-8 w-8"
                  onClick={() => { setItemToDelete({ type: 'image', id: image.id, name: image.filename }); setDeleteDialogOpen(true); }}
                  data-testid={`delete-image-${image.id}`}
                >
                  <Trash2 className="w-4 h-4 text-destructive" />
                </Button>
              </div>
              <CardContent className="p-2">
                <p className="text-xs truncate text-muted-foreground">{image.filename}</p>
              </CardContent>
            </Card>
          ))}
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

      {/* Upload Image Dialog */}
      <Dialog open={uploadDialogOpen} onOpenChange={setUploadDialogOpen}>
        <DialogContent>
          <form onSubmit={handleUploadImage}>
            <DialogHeader>
              <DialogTitle className="font-display">Upload Image</DialogTitle>
              <DialogDescription>Upload an image {currentFolderId ? 'to this folder' : 'to the root'}</DialogDescription>
            </DialogHeader>
            <div className="py-4">
              <Label htmlFor="imageFile">Select Image</Label>
              <Input 
                id="imageFile"
                type="file"
                accept="image/*"
                onChange={(e) => setSelectedFile(e.target.files[0])}
                className="mt-2"
                data-testid="image-file-input"
              />
              {selectedFile && (
                <p className="text-sm text-muted-foreground mt-2">Selected: {selectedFile.name}</p>
              )}
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => { setUploadDialogOpen(false); setSelectedFile(null); }}>Cancel</Button>
              <Button type="submit" disabled={uploading || !selectedFile} data-testid="upload-btn">
                {uploading && <Loader2 className="w-4 h-4 animate-spin mr-2" />}
                Upload
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete {itemToDelete?.type === 'folder' ? 'Folder' : 'Image'}</AlertDialogTitle>
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

export default GalleryPage;
