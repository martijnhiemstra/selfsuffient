import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { APP_NAME } from '../config';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { 
  Leaf,
  FolderOpen, 
  Globe,
  FileText,
  Library,
  Loader2,
  ExternalLink,
  Home
} from 'lucide-react';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const PublicUserPage = () => {
  const { userId } = useParams();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await axios.get(`${API}/public/users/${userId}/profile`);
        setProfile(response.data);
      } catch (err) {
        setError(err.response?.data?.detail || 'User not found');
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [userId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Loader2 className="w-10 h-10 animate-spin text-primary" />
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center" data-testid="public-user-error">
        <Card className="border border-border/50 max-w-md">
          <CardContent className="py-12 text-center">
            <FolderOpen className="w-16 h-16 mx-auto text-muted-foreground/30 mb-4" />
            <h2 className="text-xl font-display font-semibold mb-2">User Not Found</h2>
            <p className="text-muted-foreground mb-6">{error || 'This profile does not exist'}</p>
            <Link to="/">
              <Button className="rounded-full gap-2">
                <Home className="w-4 h-4" /> Go Home
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background" data-testid="public-user-page">
      {/* Header */}
      <nav className="glass-nav px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-full bg-primary flex items-center justify-center">
              <Leaf className="w-5 h-5 text-primary-foreground" />
            </div>
            <span className="font-display font-bold text-lg hidden sm:inline">
              {APP_NAME}
            </span>
          </Link>
          <Link to="/">
            <Button variant="outline" className="rounded-full gap-2">
              <Home className="w-4 h-4" /> Explore All
            </Button>
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="bg-muted/30 py-16 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-6">
            <Leaf className="w-10 h-10 text-primary" />
          </div>
          <h1 className="text-3xl md:text-4xl font-display font-bold mb-4" data-testid="user-name-heading">
            {profile.name}'s Homestead
          </h1>
          <p className="text-muted-foreground max-w-xl mx-auto">
            Welcome to my self-sufficient lifestyle journey. Explore my public projects, blog posts, and experiences.
          </p>
          <p className="text-sm text-muted-foreground mt-4">
            {profile.projects.length} public project{profile.projects.length !== 1 ? 's' : ''}
          </p>
        </div>
      </div>

      {/* Public Projects */}
      <div className="max-w-7xl mx-auto px-6 py-12">
        <h2 className="text-2xl font-display font-bold mb-6">Public Projects</h2>
        
        {profile.projects.length === 0 ? (
          <Card className="border border-border/50">
            <CardContent className="py-12 text-center">
              <FolderOpen className="w-16 h-16 mx-auto text-muted-foreground/30 mb-4" />
              <h3 className="text-xl font-display font-semibold mb-2">No Public Projects Yet</h3>
              <p className="text-muted-foreground">
                This user hasn't made any projects public yet
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {profile.projects.map((project) => (
              <Card 
                key={project.id} 
                className="border border-border/50 overflow-hidden hover:shadow-md transition-all group"
                data-testid={`project-card-${project.id}`}
              >
                <div className="h-48 bg-muted overflow-hidden relative">
                  {project.image ? (
                    <img 
                      src={`${process.env.REACT_APP_BACKEND_URL}${project.image}`}
                      alt={project.name}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center">
                      <FolderOpen className="w-12 h-12 text-muted-foreground/30" />
                    </div>
                  )}
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
                    <Link to={`/public/project/${project.id}`}>
                      <Button size="sm" className="gap-1">
                        View <ExternalLink className="w-3 h-3" />
                      </Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="border-t border-border/40 py-8 px-6 mt-auto">
        <div className="max-w-7xl mx-auto text-center text-sm text-muted-foreground">
          <p>Powered by {APP_NAME}</p>
          <Link to="/" className="text-primary hover:underline mt-2 inline-block">
            Start your own journey
          </Link>
        </div>
      </footer>
    </div>
  );
};

export default PublicUserPage;
