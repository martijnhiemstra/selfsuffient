import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useSortPreference } from '../hooks/useSortPreference';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../components/ui/dialog';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Switch } from '../components/ui/switch';
import { 
  Plus, 
  Search, 
  FolderOpen, 
  Globe, 
  Lock, 
  ArrowUpDown,
  Loader2
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';
import { getImageUrl } from '../utils';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const ProjectsPage = () => {
  const { token } = useAuth();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const { sortBy, setSortBy, sortOrder, toggleSortOrder } = useSortPreference('projects', 'created_at', 'desc');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [creating, setCreating] = useState(false);
  const [newProject, setNewProject] = useState({
    name: '',
    description: '',
    is_public: false
  });

  const fetchProjects = useCallback(async () => {
    try {
      const params = new URLSearchParams();
      if (search) params.append('search', search);
      params.append('sort_by', sortBy);
      params.append('sort_order', sortOrder);

      const response = await axios.get(`${API}/projects?${params}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setProjects(response.data.projects);
    } catch (error) {
      toast.error('Failed to load projects');
    } finally {
      setLoading(false);
    }
  }, [token, search, sortBy, sortOrder]);

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!newProject.name.trim()) {
      toast.error('Project name is required');
      return;
    }

    setCreating(true);
    try {
      await axios.post(`${API}/projects`, newProject, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Project created!');
      setDialogOpen(false);
      setNewProject({ name: '', description: '', is_public: false });
      fetchProjects();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create project');
    } finally {
      setCreating(false);
    }
  };

  const toggleSort = () => {
    toggleSortOrder();
  };

  return (
    <div className="p-6 md:p-12 lg:p-16" data-testid="projects-page">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-display font-bold tracking-tight">Projects</h1>
          <p className="text-muted-foreground mt-1">
            Manage your self-sufficiency projects
          </p>
        </div>
        
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button className="rounded-full gap-2" data-testid="create-project-button">
              <Plus className="w-4 h-4" />
              New Project
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-lg">
            <form onSubmit={handleCreate}>
              <DialogHeader>
                <DialogTitle className="font-display">Create New Project</DialogTitle>
                <DialogDescription>
                  Start a new self-sufficiency project to track your journey
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Project Name</Label>
                  <Input
                    id="name"
                    placeholder="e.g., Backyard Garden"
                    value={newProject.name}
                    onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                    data-testid="project-name-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    placeholder="Describe your project..."
                    value={newProject.description}
                    onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                    rows={4}
                    data-testid="project-description-input"
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="public">Make Public</Label>
                    <p className="text-sm text-muted-foreground">
                      Others can view this project
                    </p>
                  </div>
                  <Switch
                    id="public"
                    checked={newProject.is_public}
                    onCheckedChange={(checked) => setNewProject({ ...newProject, is_public: checked })}
                    data-testid="project-public-switch"
                  />
                </div>
              </div>
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={creating} data-testid="submit-project-button">
                  {creating ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                  Create Project
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
            placeholder="Search projects..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
            data-testid="search-projects-input"
          />
        </div>
        <div className="flex gap-2">
          <Select value={sortBy} onValueChange={setSortBy}>
            <SelectTrigger className="w-[160px]" data-testid="sort-by-select">
              <SelectValue placeholder="Sort by" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="created_at">Date Created</SelectItem>
              <SelectItem value="updated_at">Last Updated</SelectItem>
              <SelectItem value="name">Name</SelectItem>
            </SelectContent>
          </Select>
          <Button 
            variant="outline" 
            size="icon" 
            onClick={toggleSort}
            data-testid="toggle-sort-button"
          >
            <ArrowUpDown className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Projects Grid */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
        </div>
      ) : projects.length === 0 ? (
        <Card className="border border-border/50">
          <CardContent className="py-12 text-center">
            <FolderOpen className="w-16 h-16 mx-auto text-muted-foreground/30 mb-4" />
            <h3 className="text-xl font-display font-semibold mb-2">No Projects Yet</h3>
            <p className="text-muted-foreground mb-6">
              Create your first project to start documenting your journey
            </p>
            <Button 
              onClick={() => setDialogOpen(true)} 
              className="rounded-full gap-2"
              data-testid="empty-create-button"
            >
              <Plus className="w-4 h-4" />
              Create First Project
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => (
            <Link key={project.id} to={`/projects/${project.id}`}>
              <Card 
                className="border border-border/50 overflow-hidden hover:shadow-md hover:-translate-y-1 transition-all duration-300 h-full group"
                data-testid={`project-card-${project.id}`}
              >
                <div className="h-40 bg-muted overflow-hidden">
                  {project.image ? (
                    <img 
                      src={getImageUrl(project.image)}
                      alt={project.name}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                      onError={(e) => {
                        e.target.style.display = 'none';
                        e.target.nextSibling.style.display = 'flex';
                      }}
                    />
                  ) : null}
                  <div className={`w-full h-full items-center justify-center ${project.image ? 'hidden' : 'flex'}`}>
                    <FolderOpen className="w-12 h-12 text-muted-foreground/30" />
                  </div>
                </div>
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between">
                    <CardTitle className="font-display text-lg group-hover:text-primary transition-colors">
                      {project.name}
                    </CardTitle>
                    {project.is_public ? (
                      <Globe className="w-4 h-4 text-primary flex-shrink-0" />
                    ) : (
                      <Lock className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                    )}
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground line-clamp-2">
                    {project.description || 'No description'}
                  </p>
                  <p className="text-xs text-muted-foreground mt-3 font-mono-data">
                    Created {new Date(project.created_at).toLocaleDateString()}
                  </p>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};

export default ProjectsPage;
