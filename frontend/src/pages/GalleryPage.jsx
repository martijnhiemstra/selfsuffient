import { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Card, CardContent } from '../components/ui/card';
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
import { 
  ArrowLeft, 
  Plus, 
  Search, 
  Images,
  Folder,
  FolderPlus,
  Upload,
  Trash2,
  ArrowUpDown,
  Loader2,
  ImageIcon,
  X
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const GalleryPage = () => {
  const { projectId } = useParams();
  const { token } = useAuth();
  const fileInputRef = useRef(null);
  
  const [folders, setFolders] = useState([]);
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentFolder, setCurrentFolder] = useState(null);
  const [breadcrumbs, setBreadcrumbs] = useState([]);
  const [search, setSearch] = useState('');
  const [sortOrder, setSortOrder] = useState('desc');
  
  const [folderDialogOpen, setFolderDialogOpen] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  
  const [selectedImage, setSelectedImage] = useState(null);

  const fetchContents = useCallback(async () => {
    try {
      const params = new URLSearchParams();
      if (currentFolder) params.append('folder_id', currentFolder);
      if (search) params.append('search', search);
      params.append('sort_order', sortOrder);

      const response = await axios.get(`${API}/projects/${projectId}/gallery?${params}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setFolders(response.data.folders);
      setImages(response.data.images);
    } catch (error) {
      toast.error('Failed to load gallery');
    } finally {
      setLoading(false);
    }
  }, [projectId, token, currentFolder, search, sortOrder]);

  useEffect(() => {
    fetchContents();
  }, [fetchContents]);

  const buildBreadcrumbs = async (folderId) => {
    if (!folderId) {
      setBreadcrumbs([]);
      return;
    }
    
    const crumbs = [];
    let currentId = folderId;
    
    while (currentId) {
      try {
        const allFolders = await axios.get(`${API}/projects/${projectId}/gallery`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        const folder = allFolders.data.folders.find(f => f.id === currentId);
        if (folder) {
          crumbs.unshift({ id: folder.id, name: folder.name });
          currentId = folder.parent_id;
        } else {
          break;
        }
      } catch {
        break;
      }
    }
    
    setBreadcrumbs(crumbs);
  };

  const navigateToFolder = (folderId) => {
    setCurrentFolder(folderId);
    buildBreadcrumbs(folderId);
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
      await axios.post(`${API}/projects/${projectId}/gallery/folders`, {
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
      await axios.delete(`${API}/projects/${projectId}/gallery/folders/${folderId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Folder deleted');
      fetchContents();
    } catch (error) {
      toast.error('Failed to delete folder');
    }
  };

  const handleUploadImages = async (e) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setUploading(true);
    let successCount = 0;

    for (const file of files) {
      const formData = new FormData();
      formData.append('file', file);
      if (currentFolder) {
        formData.append('folder_id', currentFolder);
      }

      try {
        await axios.post(`${API}/projects/${projectId}/gallery/images?folder_id=${currentFolder || ''}`, formData, {
          headers: { 
            Authorization: `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        });
        successCount++;
      } catch (error) {
        toast.error(`Failed to upload ${file.name}`);
      }
    }

    if (successCount > 0) {
      toast.success(`${successCount} image(s) uploaded!`);
      fetchContents();
    }
    setUploading(false);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleDeleteImage = async (imageId) => {
    try {
      await axios.delete(`${API}/projects/${projectId}/gallery/images/${imageId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Image deleted');
      setImages(images.filter(i => i.id !== imageId));
    } catch (error) {
      toast.error('Failed to delete image');
    }
  };

  return (
    <div className="p-6 md:p-12 lg:p-16" data-testid="gallery-page">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <Link to={`/projects/${projectId}`}>
          <Button variant="ghost" size="icon">
            <ArrowLeft className="w-5 h-5" />
          </Button>
        </Link>
        <div className="flex-1">
          <h1 className="text-3xl font-display font-bold tracking-tight">Gallery</h1>
          <p className="text-muted-foreground">Store and organize your photos</p>
        </div>
        <div className="flex gap-2">
          <Dialog open={folderDialogOpen} onOpenChange={setFolderDialogOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" className="gap-2" data-testid="create-folder-btn">
                <FolderPlus className="w-4 h-4" />
                New Folder
              </Button>
            </DialogTrigger>
            <DialogContent>
              <form onSubmit={handleCreateFolder}>
                <DialogHeader>
                  <DialogTitle>Create Folder</DialogTitle>
                  <DialogDescription>Add a new folder to organize your images</DialogDescription>
                </DialogHeader>
                <div className="py-4">
                  <Label htmlFor="folderName">Folder Name</Label>
                  <Input
                    id="folderName"
                    value={newFolderName}
                    onChange={(e) => setNewFolderName(e.target.value)}
                    placeholder="Enter folder name"
                    data-testid="folder-name-input"
                  />
                </div>
                <DialogFooter>
                  <Button type="button" variant="outline" onClick={() => setFolderDialogOpen(false)}>Cancel</Button>
                  <Button type="submit" disabled={saving} data-testid="save-folder-btn">
                    {saving && <Loader2 className="w-4 h-4 animate-spin mr-2" />}
                    Create
                  </Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            multiple
            onChange={handleUploadImages}
            className="hidden"
          />
          <Button 
            className="rounded-full gap-2" 
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            data-testid="upload-images-btn"
          >
            {uploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
            Upload
          </Button>
        </div>
      </div>

      {/* Breadcrumbs */}
      {(breadcrumbs.length > 0 || currentFolder) && (
        <Breadcrumb className="mb-4">
          <BreadcrumbList>
            <BreadcrumbItem>
              <BreadcrumbLink 
                onClick={() => navigateToFolder(null)} 
                className="cursor-pointer hover:text-primary"
              >
                Gallery
              </BreadcrumbLink>
            </BreadcrumbItem>
            {breadcrumbs.map((crumb, index) => (
              <span key={crumb.id} className="flex items-center">
                <BreadcrumbSeparator />
                <BreadcrumbItem>
                  {index === breadcrumbs.length - 1 ? (
                    <BreadcrumbPage>{crumb.name}</BreadcrumbPage>
                  ) : (
                    <BreadcrumbLink 
                      onClick={() => navigateToFolder(crumb.id)}
                      className="cursor-pointer hover:text-primary"
                    >
                      {crumb.name}
                    </BreadcrumbLink>
                  )}
                </BreadcrumbItem>
              </span>
            ))}
          </BreadcrumbList>
        </Breadcrumb>
      )}

      {/* Search & Sort */}
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
      ) : folders.length === 0 && images.length === 0 ? (
        <Card className="border border-border/50">
          <CardContent className="py-12 text-center">
            <Images className="w-16 h-16 mx-auto text-muted-foreground/30 mb-4" />
            <h3 className="text-xl font-display font-semibold mb-2">Empty Gallery</h3>
            <p className="text-muted-foreground mb-6">Create folders and upload images</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          {/* Folders */}
          {folders.map((folder) => (
            <Card 
              key={folder.id}
              className="border border-border/50 cursor-pointer hover:shadow-md transition-all group"
              onClick={() => navigateToFolder(folder.id)}
              data-testid={`folder-${folder.id}`}
            >
              <CardContent className="p-4 text-center relative">
                <Folder className="w-12 h-12 mx-auto text-primary mb-2" />
                <p className="font-medium truncate">{folder.name}</p>
                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button 
                      variant="ghost" 
                      size="icon"
                      className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <Trash2 className="w-4 h-4 text-destructive" />
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent onClick={(e) => e.stopPropagation()}>
                    <AlertDialogHeader>
                      <AlertDialogTitle>Delete Folder?</AlertDialogTitle>
                      <AlertDialogDescription>
                        This will delete the folder and all its contents.
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>Cancel</AlertDialogCancel>
                      <AlertDialogAction 
                        onClick={() => handleDeleteFolder(folder.id)}
                        className="bg-destructive text-destructive-foreground"
                      >
                        Delete
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              </CardContent>
            </Card>
          ))}

          {/* Images */}
          {images.map((image) => (
            <Card 
              key={image.id}
              className="border border-border/50 overflow-hidden cursor-pointer hover:shadow-md transition-all group"
              onClick={() => setSelectedImage(image)}
              data-testid={`image-${image.id}`}
            >
              <div className="aspect-square bg-muted relative">
                <img 
                  src={`${process.env.REACT_APP_BACKEND_URL}${image.url}`}
                  alt={image.filename}
                  className="w-full h-full object-cover"
                />
                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button 
                      variant="secondary" 
                      size="icon"
                      className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <Trash2 className="w-4 h-4 text-destructive" />
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent onClick={(e) => e.stopPropagation()}>
                    <AlertDialogHeader>
                      <AlertDialogTitle>Delete Image?</AlertDialogTitle>
                      <AlertDialogDescription>This action cannot be undone.</AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>Cancel</AlertDialogCancel>
                      <AlertDialogAction 
                        onClick={() => handleDeleteImage(image.id)}
                        className="bg-destructive text-destructive-foreground"
                      >
                        Delete
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              </div>
              <CardContent className="p-2">
                <p className="text-xs text-muted-foreground truncate">{image.filename}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Image Lightbox */}
      <Dialog open={!!selectedImage} onOpenChange={(open) => !open && setSelectedImage(null)}>
        <DialogContent className="sm:max-w-4xl p-0 overflow-hidden">
          {selectedImage && (
            <div className="relative">
              <img 
                src={`${process.env.REACT_APP_BACKEND_URL}${selectedImage.url}`}
                alt={selectedImage.filename}
                className="w-full h-auto max-h-[80vh] object-contain"
              />
              <Button 
                variant="secondary" 
                size="icon"
                className="absolute top-4 right-4"
                onClick={() => setSelectedImage(null)}
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default GalleryPage;
