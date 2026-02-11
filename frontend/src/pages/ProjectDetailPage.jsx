import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Switch } from '../components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
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
  AlertDialogTrigger,
} from '../components/ui/alert-dialog';
import { 
  ArrowLeft, 
  Edit, 
  Trash2, 
  Upload, 
  Image as ImageIcon,
  BookOpen,
  Images,
  FileText,
  Library,
  Calendar,
  Sun,
  Moon,
  Globe,
  Lock,
  Loader2,
  FolderOpen,
  Settings,
  ListChecks
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';
import { getImageUrl, validateImageFile } from '../utils';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const ProjectDetailPage = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const { token } = useAuth();
  const fileInputRef = useRef(null);
  
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editData, setEditData] = useState({ name: '', description: '', is_public: false });
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchProject();
  }, [projectId]);

  const fetchProject = async () => {
    try {
      const response = await axios.get(`${API}/projects/${projectId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setProject(response.data);
      setEditData({
        name: response.data.name,
        description: response.data.description,
        is_public: response.data.is_public
      });
    } catch (error) {
      toast.error('Failed to load project');
      navigate('/projects');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    if (!editData.name.trim()) {
      toast.error('Project name is required');
      return;
    }

    setSaving(true);
    try {
      const response = await axios.put(`${API}/projects/${projectId}`, editData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setProject(response.data);
      setEditDialogOpen(false);
      toast.success('Project updated!');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to update project');
    } finally {
      setSaving(false);
    }
  };

  const handleImageUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file before upload
    const validation = validateImageFile(file);
    if (!validation.valid) {
      toast.error(validation.error);
      if (fileInputRef.current) fileInputRef.current.value = '';
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    setUploading(true);
    try {
      const response = await axios.post(`${API}/projects/${projectId}/image`, formData, {
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });
      setProject(response.data);
      toast.success('Image uploaded!');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to upload image');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await axios.delete(`${API}/projects/${projectId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Project deleted');
      navigate('/projects');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to delete project');
      setDeleting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!project) return null;

  const featureCards = [
    { id: 'diary', label: 'Diary', icon: BookOpen, description: 'Document your daily progress', path: `/projects/${projectId}/diary` },
    { id: 'gallery', label: 'Gallery', icon: Images, description: 'Store photos and images', path: `/projects/${projectId}/gallery` },
    { id: 'blog', label: 'Blog', icon: FileText, description: 'Share public updates', path: `/projects/${projectId}/blog` },
    { id: 'library', label: 'Library', icon: Library, description: 'Store experiences & knowledge', path: `/projects/${projectId}/library` },
    { id: 'tasks', label: 'Tasks', icon: Calendar, description: 'Plan and track activities', path: `/projects/${projectId}/tasks` },
    { id: 'startup', label: 'Daily Routines', icon: Sun, description: 'Startup & shutdown lists', path: `/projects/${projectId}/routines` },
  ];

  return (
    <div className="p-6 md:p-12 lg:p-16" data-testid="project-detail-page">
      {/* Back Button & Actions */}
      <div className="flex items-center justify-between mb-6">
        <Link to="/projects">
          <Button variant="ghost" className="gap-2" data-testid="back-to-projects">
            <ArrowLeft className="w-4 h-4" />
            Back to Projects
          </Button>
        </Link>
        <div className="flex gap-2">
          <Button 
            variant="outline" 
            size="icon"
            onClick={() => setEditDialogOpen(true)}
            data-testid="edit-project-button"
          >
            <Edit className="w-4 h-4" />
          </Button>
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button variant="outline" size="icon" className="text-destructive" data-testid="delete-project-button">
                <Trash2 className="w-4 h-4" />
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Delete Project?</AlertDialogTitle>
                <AlertDialogDescription>
                  This will permanently delete "{project.name}" and all its data including diary entries, gallery images, blog posts, and tasks. This action cannot be undone.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction 
                  onClick={handleDelete}
                  className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                  disabled={deleting}
                  data-testid="confirm-delete-button"
                >
                  {deleting ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                  Delete Project
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </div>
      </div>

      {/* Project Header */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Cover Image */}
        <div className="lg:col-span-1">
          <Card className="border border-border/50 overflow-hidden">
            <div className="aspect-video bg-muted relative group">
              {project.image ? (
                <img 
                  src={getImageUrl(project.image)}
                  alt={project.name}
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'flex';
                  }}
                />
              ) : null}
              <div className={`w-full h-full items-center justify-center ${project.image ? 'hidden' : 'flex'}`}>
                <FolderOpen className="w-16 h-16 text-muted-foreground/30" />
              </div>
              <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                  className="hidden"
                />
                <Button 
                  variant="secondary"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={uploading}
                  data-testid="upload-image-button"
                >
                  {uploading ? (
                    <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  ) : (
                    <Upload className="w-4 h-4 mr-2" />
                  )}
                  {project.image ? 'Change Image' : 'Upload Image'}
                </Button>
              </div>
            </div>
          </Card>
        </div>

        {/* Project Info */}
        <div className="lg:col-span-2">
          <Card className="border border-border/50 h-full">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-2xl font-display">{project.name}</CardTitle>
                  <div className="flex items-center gap-2 mt-2">
                    {project.is_public ? (
                      <span className="inline-flex items-center gap-1 text-sm text-primary">
                        <Globe className="w-4 h-4" />
                        Public
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-sm text-muted-foreground">
                        <Lock className="w-4 h-4" />
                        Private
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div 
                className="prose-content text-muted-foreground"
                dangerouslySetInnerHTML={{ __html: project.description || '<p>No description provided.</p>' }}
              />
              <div className="flex gap-4 mt-4 text-sm text-muted-foreground font-mono-data">
                <span>Created: {new Date(project.created_at).toLocaleDateString()}</span>
                <span>Updated: {new Date(project.updated_at).toLocaleDateString()}</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Features Grid */}
      <div className="mb-6">
        <h2 className="text-xl font-display font-semibold mb-4">Project Features</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {featureCards.map((feature) => (
            <Link key={feature.id} to={feature.path}>
              <Card 
                className="border border-border/50 hover:shadow-md hover:-translate-y-1 transition-all duration-300 h-full"
                data-testid={`feature-card-${feature.id}`}
              >
                <CardContent className="pt-6">
                  <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mb-4">
                    <feature.icon className="w-6 h-6 text-primary" />
                  </div>
                  <h3 className="font-semibold mb-1">{feature.label}</h3>
                  <p className="text-sm text-muted-foreground">{feature.description}</p>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </div>

      {/* Edit Dialog */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent className="sm:max-w-lg">
          <form onSubmit={handleSave}>
            <DialogHeader>
              <DialogTitle className="font-display">Edit Project</DialogTitle>
              <DialogDescription>
                Update your project details
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="edit-name">Project Name</Label>
                <Input
                  id="edit-name"
                  value={editData.name}
                  onChange={(e) => setEditData({ ...editData, name: e.target.value })}
                  data-testid="edit-project-name"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-description">Description</Label>
                <Textarea
                  id="edit-description"
                  value={editData.description}
                  onChange={(e) => setEditData({ ...editData, description: e.target.value })}
                  rows={6}
                  data-testid="edit-project-description"
                />
              </div>
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="edit-public">Make Public</Label>
                  <p className="text-sm text-muted-foreground">
                    Others can view this project
                  </p>
                </div>
                <Switch
                  id="edit-public"
                  checked={editData.is_public}
                  onCheckedChange={(checked) => setEditData({ ...editData, is_public: checked })}
                  data-testid="edit-project-public"
                />
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setEditDialogOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={saving} data-testid="save-project-button">
                {saving ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                Save Changes
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ProjectDetailPage;
