import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { 
  Leaf, 
  ArrowRight, 
  FolderOpen, 
  BookOpen, 
  Image, 
  Calendar,
  Eye,
  ExternalLink
} from 'lucide-react';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const LandingPage = () => {
  const [publicProjects, setPublicProjects] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPublicProjects = async () => {
      try {
        // Will be implemented when projects API is ready
        // const response = await axios.get(`${API}/public/projects`);
        // setPublicProjects(response.data);
        setPublicProjects([]);
      } catch (error) {
        console.error('Error fetching public projects:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPublicProjects();
  }, []);

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="glass-nav px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-full bg-primary flex items-center justify-center">
              <Leaf className="w-5 h-5 text-primary-foreground" />
            </div>
            <span className="font-display font-bold text-lg">
              Self-Sufficient Life
            </span>
          </div>
          <Link to="/login">
            <Button className="rounded-full" data-testid="login-button">
              Sign In
            </Button>
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div 
          className="absolute inset-0 z-0"
          style={{
            backgroundImage: 'url(https://images.unsplash.com/photo-1666228347956-eec27310e2d2?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NTYxODh8MHwxfHNlYXJjaHwxfHxuYXR1cmUlMjBsYW5kc2NhcGUlMjBmb3Jlc3QlMjBnYXJkZW58ZW58MHx8fHwxNzY4NTQzNjA0fDA&ixlib=rb-4.1.0&q=85)',
            backgroundSize: 'cover',
            backgroundPosition: 'center',
          }}
        >
          <div className="absolute inset-0 bg-gradient-to-b from-background/80 via-background/60 to-background" />
        </div>
        
        <div className="relative z-10 max-w-7xl mx-auto px-6 py-24 md:py-32 lg:py-40">
          <div className="max-w-3xl">
            <p className="label-overline mb-4">Your Digital Homestead</p>
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-display font-bold tracking-tight mb-6">
              Document Your
              <br />
              <span className="text-primary">Self-Sufficient</span>
              <br />
              Journey
            </h1>
            <p className="text-lg md:text-xl text-muted-foreground mb-8 leading-relaxed max-w-xl">
              Track projects, maintain diaries, organize galleries, and share your homesteading knowledge with the world.
            </p>
            <div className="flex flex-wrap gap-4">
              <Link to="/login">
                <Button size="lg" className="rounded-full gap-2" data-testid="get-started-button">
                  Get Started
                  <ArrowRight className="w-4 h-4" />
                </Button>
              </Link>
              <a href="#projects">
                <Button size="lg" variant="outline" className="rounded-full">
                  Explore Projects
                </Button>
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 md:py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <p className="label-overline mb-3">Everything You Need</p>
            <h2 className="text-3xl md:text-4xl font-display font-bold tracking-tight">
              Manage Your Homestead Life
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="border border-border/50 shadow-soft hover:shadow-md hover:-translate-y-1 transition-all duration-300">
              <CardContent className="pt-6">
                <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mb-4">
                  <FolderOpen className="w-6 h-6 text-primary" />
                </div>
                <h3 className="font-display font-semibold text-lg mb-2">Projects</h3>
                <p className="text-muted-foreground">
                  Organize your homesteading activities into manageable projects with descriptions and images.
                </p>
              </CardContent>
            </Card>

            <Card className="border border-border/50 shadow-soft hover:shadow-md hover:-translate-y-1 transition-all duration-300">
              <CardContent className="pt-6">
                <div className="w-12 h-12 rounded-xl bg-secondary/20 flex items-center justify-center mb-4">
                  <BookOpen className="w-6 h-6 text-secondary" />
                </div>
                <h3 className="font-display font-semibold text-lg mb-2">Diary & Blog</h3>
                <p className="text-muted-foreground">
                  Document your journey with rich diary entries and share your experiences through a public blog.
                </p>
              </CardContent>
            </Card>

            <Card className="border border-border/50 shadow-soft hover:shadow-md hover:-translate-y-1 transition-all duration-300">
              <CardContent className="pt-6">
                <div className="w-12 h-12 rounded-xl bg-amber-100 flex items-center justify-center mb-4">
                  <Image className="w-6 h-6 text-amber-600" />
                </div>
                <h3 className="font-display font-semibold text-lg mb-2">Gallery</h3>
                <p className="text-muted-foreground">
                  Store and organize your photos in folders and subfolders. Capture every moment of your journey.
                </p>
              </CardContent>
            </Card>

            <Card className="border border-border/50 shadow-soft hover:shadow-md hover:-translate-y-1 transition-all duration-300">
              <CardContent className="pt-6">
                <div className="w-12 h-12 rounded-xl bg-indigo-100 flex items-center justify-center mb-4">
                  <Calendar className="w-6 h-6 text-indigo-600" />
                </div>
                <h3 className="font-display font-semibold text-lg mb-2">Calendar</h3>
                <p className="text-muted-foreground">
                  Plan and track tasks with a full calendar. Set recurring tasks and daily routines.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Public Projects Section */}
      <section id="projects" className="py-16 md:py-24 px-6 bg-muted/30">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <p className="label-overline mb-3">Community</p>
            <h2 className="text-3xl md:text-4xl font-display font-bold tracking-tight">
              Public Projects
            </h2>
            <p className="text-muted-foreground mt-3 max-w-xl mx-auto">
              Explore what others are building and sharing in the self-sufficiency community
            </p>
          </div>

          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3].map((i) => (
                <Card key={i} className="border border-border/50 overflow-hidden animate-pulse">
                  <div className="h-48 bg-muted" />
                  <CardContent className="pt-4">
                    <div className="h-6 bg-muted rounded mb-2 w-2/3" />
                    <div className="h-4 bg-muted rounded w-full" />
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : publicProjects.length === 0 ? (
            <div className="text-center py-16">
              <FolderOpen className="w-16 h-16 mx-auto text-muted-foreground/30 mb-4" />
              <h3 className="text-xl font-display font-semibold mb-2">No Public Projects Yet</h3>
              <p className="text-muted-foreground mb-6">
                Be the first to share your self-sufficiency journey!
              </p>
              <Link to="/login">
                <Button className="rounded-full" data-testid="create-project-cta">
                  Create Your Project
                </Button>
              </Link>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {publicProjects.map((project) => (
                <Link key={project.id} to={`/public/projects/${project.id}`}>
                  <Card className="border border-border/50 overflow-hidden hover:shadow-md hover:-translate-y-1 transition-all duration-300 group">
                    <div className="h-48 bg-muted overflow-hidden">
                      {project.image ? (
                        <img 
                          src={project.image} 
                          alt={project.name}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center">
                          <FolderOpen className="w-12 h-12 text-muted-foreground/30" />
                        </div>
                      )}
                    </div>
                    <CardContent className="pt-4">
                      <h3 className="font-display font-semibold text-lg mb-1 group-hover:text-primary transition-colors">
                        {project.name}
                      </h3>
                      <p className="text-muted-foreground text-sm line-clamp-2">
                        {project.description}
                      </p>
                      <div className="flex items-center gap-4 mt-4 text-sm text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <Eye className="w-4 h-4" />
                          {project.views || 0}
                        </span>
                        <span className="flex items-center gap-1">
                          <BookOpen className="w-4 h-4" />
                          {project.blog_count || 0} posts
                        </span>
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 md:py-24 px-6">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-display font-bold tracking-tight mb-4">
            Start Your Journey Today
          </h2>
          <p className="text-lg text-muted-foreground mb-8">
            Join the community of homesteaders documenting their self-sufficient lifestyle.
          </p>
          <Link to="/login">
            <Button size="lg" className="rounded-full gap-2" data-testid="cta-sign-in">
              Sign In to Get Started
              <ArrowRight className="w-4 h-4" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border/40 py-8 px-6">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center">
              <Leaf className="w-4 h-4 text-primary-foreground" />
            </div>
            <span className="font-display font-semibold">Self-Sufficient Life</span>
          </div>
          <p className="text-sm text-muted-foreground">
            © {new Date().getFullYear()} Self-Sufficient Life. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
