import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { 
  ArrowLeft, 
  Leaf,
  FolderOpen, 
  FileText, 
  Library,
  Eye,
  Calendar,
  Loader2,
  Globe
} from 'lucide-react';
import axios from 'axios';
import { format, parseISO } from 'date-fns';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const PublicProjectPage = () => {
  const { projectId } = useParams();
  const [project, setProject] = useState(null);
  const [blogEntries, setBlogEntries] = useState([]);
  const [libraryEntries, setLibraryEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('blog');
  const [selectedEntry, setSelectedEntry] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [projectRes, blogRes, libraryRes] = await Promise.all([
          axios.get(`${API}/public/projects/${projectId}`),
          axios.get(`${API}/public/projects/${projectId}/blog`),
          axios.get(`${API}/public/projects/${projectId}/library`)
        ]);
        
        setProject(projectRes.data);
        setBlogEntries(blogRes.data.entries || []);
        setLibraryEntries(libraryRes.data.entries || []);
      } catch (error) {
        console.error('Error fetching project:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [projectId]);

  const viewEntry = async (entry, type) => {
    try {
      if (type === 'blog') {
        const res = await axios.get(`${API}/public/projects/${projectId}/blog/${entry.id}`);
        setSelectedEntry({ ...res.data, type: 'blog' });
      } else {
        const res = await axios.get(`${API}/public/projects/${projectId}/library/entries/${entry.id}`);
        setSelectedEntry({ ...res.data, type: 'library' });
      }
    } catch (error) {
      console.error('Error fetching entry:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!project) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <FolderOpen className="w-16 h-16 mx-auto text-muted-foreground/30 mb-4" />
          <h2 className="text-xl font-display font-semibold mb-2">Project Not Found</h2>
          <Link to="/"><Button variant="outline">Back to Home</Button></Link>
        </div>
      </div>
    );
  }

  if (selectedEntry) {
    return (
      <div className="min-h-screen bg-background">
        <nav className="glass-nav px-6 py-4">
          <div className="max-w-4xl mx-auto flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => setSelectedEntry(null)}>
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center">
                <Leaf className="w-4 h-4 text-primary-foreground" />
              </div>
              <span className="font-display font-bold">{project.name}</span>
            </div>
          </div>
        </nav>
        
        <div className="max-w-4xl mx-auto px-6 py-12">
          <article>
            <Badge variant="secondary" className="mb-4">
              {selectedEntry.type === 'blog' ? 'Blog Post' : 'Library Entry'}
            </Badge>
            <h1 className="text-3xl md:text-4xl font-display font-bold mb-4">{selectedEntry.title}</h1>
            <div className="flex items-center gap-4 text-muted-foreground mb-8">
              <span className="flex items-center gap-1">
                <Calendar className="w-4 h-4" />
                {format(parseISO(selectedEntry.created_at), 'PPP')}
              </span>
              <span className="flex items-center gap-1">
                <Eye className="w-4 h-4" />
                {selectedEntry.views} views
              </span>
            </div>
            <div 
              className="prose-content"
              dangerouslySetInnerHTML={{ __html: selectedEntry.description || '<p>No content</p>' }}
            />
          </article>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background" data-testid="public-project-page">
      {/* Navigation */}
      <nav className="glass-nav px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link to="/">
              <Button variant="ghost" size="icon"><ArrowLeft className="w-5 h-5" /></Button>
            </Link>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center">
                <Leaf className="w-4 h-4 text-primary-foreground" />
              </div>
              <span className="font-display font-bold">Self-Sufficient Life</span>
            </div>
          </div>
          <Link to="/login">
            <Button className="rounded-full">Sign In</Button>
          </Link>
        </div>
      </nav>

      {/* Project Header */}
      <div className="relative">
        {project.image ? (
          <div className="h-64 md:h-80 overflow-hidden">
            <img 
              src={`${process.env.REACT_APP_BACKEND_URL}${project.image}`}
              alt={project.name}
              className="w-full h-full object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-background via-background/50 to-transparent" />
          </div>
        ) : (
          <div className="h-32 bg-muted" />
        )}
        
        <div className="max-w-7xl mx-auto px-6 -mt-16 relative z-10">
          <Card className="border border-border/50 shadow-soft">
            <CardContent className="p-6 md:p-8">
              <div className="flex items-start gap-4">
                <div className="w-16 h-16 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
                  <FolderOpen className="w-8 h-8 text-primary" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h1 className="text-2xl md:text-3xl font-display font-bold">{project.name}</h1>
                    <Badge variant="secondary" className="gap-1">
                      <Globe className="w-3 h-3" /> Public
                    </Badge>
                  </div>
                  <div 
                    className="prose-content text-muted-foreground"
                    dangerouslySetInnerHTML={{ __html: project.description || '<p>No description</p>' }}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 py-12">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="mb-6">
            <TabsTrigger value="blog" className="gap-2">
              <FileText className="w-4 h-4" /> Blog ({blogEntries.length})
            </TabsTrigger>
            <TabsTrigger value="library" className="gap-2">
              <Library className="w-4 h-4" /> Library ({libraryEntries.length})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="blog">
            {blogEntries.length === 0 ? (
              <Card className="border border-border/50">
                <CardContent className="py-12 text-center">
                  <FileText className="w-12 h-12 mx-auto text-muted-foreground/30 mb-4" />
                  <p className="text-muted-foreground">No public blog posts yet</p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-6">
                {blogEntries.map((entry) => (
                  <Card 
                    key={entry.id} 
                    className="border border-border/50 hover:shadow-md transition-all cursor-pointer"
                    onClick={() => viewEntry(entry, 'blog')}
                  >
                    <CardHeader>
                      <CardTitle className="font-display">{entry.title}</CardTitle>
                      <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        <span>{format(parseISO(entry.created_at), 'PP')}</span>
                        <span className="flex items-center gap-1"><Eye className="w-3 h-3" /> {entry.views} views</span>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div 
                        className="prose-content text-muted-foreground line-clamp-3"
                        dangerouslySetInnerHTML={{ __html: entry.description?.slice(0, 300) || '' }}
                      />
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="library">
            {libraryEntries.length === 0 ? (
              <Card className="border border-border/50">
                <CardContent className="py-12 text-center">
                  <Library className="w-12 h-12 mx-auto text-muted-foreground/30 mb-4" />
                  <p className="text-muted-foreground">No public library entries yet</p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-6">
                {libraryEntries.map((entry) => (
                  <Card 
                    key={entry.id} 
                    className="border border-border/50 hover:shadow-md transition-all cursor-pointer"
                    onClick={() => viewEntry(entry, 'library')}
                  >
                    <CardHeader>
                      <CardTitle className="font-display">{entry.title}</CardTitle>
                      <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        <span>{format(parseISO(entry.created_at), 'PP')}</span>
                        <span className="flex items-center gap-1"><Eye className="w-3 h-3" /> {entry.views} views</span>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div 
                        className="prose-content text-muted-foreground line-clamp-3"
                        dangerouslySetInnerHTML={{ __html: entry.description?.slice(0, 300) || '' }}
                      />
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>

      {/* Footer */}
      <footer className="border-t border-border/40 py-8 px-6">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center">
              <Leaf className="w-4 h-4 text-primary-foreground" />
            </div>
            <span className="font-display font-semibold">Self-Sufficient Life</span>
          </div>
          <p className="text-sm text-muted-foreground">© {new Date().getFullYear()} Self-Sufficient Life</p>
        </div>
      </footer>
    </div>
  );
};

export default PublicProjectPage;
