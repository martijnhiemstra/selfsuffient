import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { 
  Leaf,
  ArrowLeft,
  FolderOpen, 
  Globe,
  Eye,
  FileText,
  Library,
  Loader2,
  ExternalLink
} from 'lucide-react';
import axios from 'axios';
import { getImageUrl } from '../utils';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const MyPublicSitePage = () => {
  const { user, token } = useAuth();
  const [publicProjects, setPublicProjects] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPublicProjects = async () => {
      try {
        // Get all user's projects and filter to public ones
        const response = await axios.get(`${API}/projects`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        const projects = response.data.projects || [];
        setPublicProjects(projects.filter(p => p.is_public));
      } catch (error) {
        console.error('Error fetching projects:', error);
      } finally {
        setLoading(false);
      }
    };

    if (token) {
      fetchPublicProjects();
    }
  }, [token]);

  return (
    <div className="min-h-screen bg-background" data-testid="my-public-site-page">
      {/* Header */}
      <div className="glass-nav px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link to="/dashboard">
              <Button variant="ghost" size="icon"><ArrowLeft className="w-5 h-5" /></Button>
            </Link>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center">
                <Leaf className="w-4 h-4 text-primary-foreground" />
              </div>
              <span className="font-display font-bold">My Public Site</span>
            </div>
          </div>
          <Badge variant="secondary" className="gap-1">
            <Globe className="w-3 h-3" /> Preview Mode
          </Badge>
        </div>
      </div>

      {/* Hero Section */}
      <div className="bg-muted/30 py-16 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-6">
            <Leaf className="w-10 h-10 text-primary" />
          </div>
          <h1 className="text-3xl md:text-4xl font-display font-bold mb-4">
            {user?.name}'s Homestead
          </h1>
          <p className="text-muted-foreground max-w-xl mx-auto">
            Welcome to my self-sufficient lifestyle journey. Explore my public projects, blog posts, and experiences.
          </p>
          <p className="text-sm text-muted-foreground mt-4">
            {publicProjects.length} public project{publicProjects.length !== 1 ? 's' : ''}
          </p>
        </div>
      </div>

      {/* Public Projects */}
      <div className="max-w-7xl mx-auto px-6 py-12">
        <h2 className="text-2xl font-display font-bold mb-6">Public Projects</h2>
        
        {loading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
          </div>
        ) : publicProjects.length === 0 ? (
          <Card className="border border-border/50">
            <CardContent className="py-12 text-center">
              <FolderOpen className="w-16 h-16 mx-auto text-muted-foreground/30 mb-4" />
              <h3 className="text-xl font-display font-semibold mb-2">No Public Projects Yet</h3>
              <p className="text-muted-foreground mb-6">
                Make some of your projects public to share them with the world
              </p>
              <Link to="/projects">
                <Button className="rounded-full">Go to Projects</Button>
              </Link>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {publicProjects.map((project) => (
              <Card 
                key={project.id} 
                className="border border-border/50 overflow-hidden hover:shadow-md transition-all group"
              >
                <div className="h-48 bg-muted overflow-hidden relative">
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
                  <Badge className="absolute top-3 right-3 gap-1">
                    <Globe className="w-3 h-3" /> Public
                  </Badge>
                </div>
                <CardHeader className="pb-2">
                  <CardTitle className="font-display text-lg">{project.name}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div 
                    className="text-sm text-muted-foreground line-clamp-2 mb-4"
                    dangerouslySetInnerHTML={{ __html: project.description?.slice(0, 150) || 'No description' }}
                  />
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1"><FileText className="w-3 h-3" /> Blog</span>
                      <span className="flex items-center gap-1"><Library className="w-3 h-3" /> Library</span>
                    </div>
                    <div className="flex gap-2">
                      <Link to={`/projects/${project.id}`}>
                        <Button variant="outline" size="sm">Edit</Button>
                      </Link>
                      <Link to={`/public/project/${project.id}`} target="_blank">
                        <Button size="sm" className="gap-1">
                          View <ExternalLink className="w-3 h-3" />
                        </Button>
                      </Link>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Tips Section */}
        {publicProjects.length > 0 && (
          <Card className="border border-border/50 mt-8">
            <CardContent className="p-6">
              <h3 className="font-display font-semibold mb-4">Tips for Your Public Site</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>• Add compelling cover images to your projects to attract visitors</li>
                <li>• Write detailed descriptions using the rich text editor</li>
                <li>• Mark blog posts and library entries as "Public" to share them</li>
                <li>• Share the public project links on social media</li>
              </ul>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Footer */}
      <footer className="border-t border-border/40 py-8 px-6 mt-auto">
        <div className="max-w-7xl mx-auto text-center text-sm text-muted-foreground">
          <p>This is a preview of how visitors see your public projects</p>
        </div>
      </footer>
    </div>
  );
};

export default MyPublicSitePage;
