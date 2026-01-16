import { useState, useEffect, useMemo } from 'react';
import { useParams, Link } from 'react-router-dom';
import { APP_NAME } from '../config';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import { 
  ArrowLeft, 
  Leaf,
  FolderOpen, 
  FileText, 
  Library,
  Eye,
  Calendar,
  Loader2,
  Globe,
  Search,
  ArrowUpDown,
  Image,
  Folder,
  Share2
} from 'lucide-react';
import axios from 'axios';
import { format, parseISO } from 'date-fns';
import { getImageUrl } from '../utils';
import { ShareButton, ShareIcons } from '../components/ShareButton';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const PublicProjectPage = () => {
  const { projectId } = useParams();
  const [project, setProject] = useState(null);
  const [blogEntries, setBlogEntries] = useState([]);
  const [libraryEntries, setLibraryEntries] = useState([]);
  const [galleryFolders, setGalleryFolders] = useState([]);
  const [galleryImages, setGalleryImages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('blog');
  const [selectedEntry, setSelectedEntry] = useState(null);
  
  // Search and sort state
  const [blogSearch, setBlogSearch] = useState('');
  const [blogSort, setBlogSort] = useState('created_at-desc');
  const [librarySearch, setLibrarySearch] = useState('');
  const [librarySort, setLibrarySort] = useState('created_at-desc');
  const [gallerySearch, setGallerySearch] = useState('');
  const [gallerySort, setGallerySort] = useState('created_at-desc');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [projectRes, blogRes, libraryRes, galleryRes] = await Promise.all([
          axios.get(`${API}/public/projects/${projectId}`),
          axios.get(`${API}/public/projects/${projectId}/blog`),
          axios.get(`${API}/public/projects/${projectId}/library`),
          axios.get(`${API}/public/projects/${projectId}/gallery`)
        ]);
        
        setProject(projectRes.data);
        setBlogEntries(blogRes.data.entries || []);
        setLibraryEntries(libraryRes.data.entries || []);
        setGalleryFolders(galleryRes.data.folders || []);
        setGalleryImages(galleryRes.data.images || []);
      } catch (error) {
        console.error('Error fetching project:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [projectId]);

  // Filter and sort blog entries
  const filteredBlogEntries = useMemo(() => {
    let entries = [...blogEntries];
    
    if (blogSearch) {
      const search = blogSearch.toLowerCase();
      entries = entries.filter(e => 
        e.title.toLowerCase().includes(search) || 
        (e.description && e.description.toLowerCase().includes(search))
      );
    }
    
    const [sortBy, sortOrder] = blogSort.split('-');
    entries.sort((a, b) => {
      let aVal = sortBy === 'title' ? a.title : a.created_at;
      let bVal = sortBy === 'title' ? b.title : b.created_at;
      if (sortOrder === 'desc') return bVal > aVal ? 1 : -1;
      return aVal > bVal ? 1 : -1;
    });
    
    return entries;
  }, [blogEntries, blogSearch, blogSort]);

  // Filter and sort library entries
  const filteredLibraryEntries = useMemo(() => {
    let entries = [...libraryEntries];
    
    if (librarySearch) {
      const search = librarySearch.toLowerCase();
      entries = entries.filter(e => 
        e.title.toLowerCase().includes(search) || 
        (e.description && e.description.toLowerCase().includes(search))
      );
    }
    
    const [sortBy, sortOrder] = librarySort.split('-');
    entries.sort((a, b) => {
      let aVal = sortBy === 'title' ? a.title : a.created_at;
      let bVal = sortBy === 'title' ? b.title : b.created_at;
      if (sortOrder === 'desc') return bVal > aVal ? 1 : -1;
      return aVal > bVal ? 1 : -1;
    });
    
    return entries;
  }, [libraryEntries, librarySearch, librarySort]);

  // Filter and sort gallery
  const filteredGallery = useMemo(() => {
    let folders = [...galleryFolders];
    let images = [...galleryImages];
    
    if (gallerySearch) {
      const search = gallerySearch.toLowerCase();
      folders = folders.filter(f => f.name.toLowerCase().includes(search));
      images = images.filter(i => i.filename.toLowerCase().includes(search));
    }
    
    const [sortBy, sortOrder] = gallerySort.split('-');
    const sortFn = (a, b) => {
      let aVal = sortBy === 'name' ? (a.name || a.filename) : a.created_at;
      let bVal = sortBy === 'name' ? (b.name || b.filename) : b.created_at;
      if (sortOrder === 'desc') return bVal > aVal ? 1 : -1;
      return aVal > bVal ? 1 : -1;
    };
    
    folders.sort(sortFn);
    images.sort(sortFn);
    
    return { folders, images };
  }, [galleryFolders, galleryImages, gallerySearch, gallerySort]);

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

  const SearchSortBar = ({ search, setSearch, sort, setSort, placeholder }) => (
    <div className="flex flex-col sm:flex-row gap-4 mb-6">
      <div className="relative flex-1">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <Input 
          placeholder={placeholder}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-10 rounded-full"
        />
      </div>
      <Select value={sort} onValueChange={setSort}>
        <SelectTrigger className="w-48 rounded-full">
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
  );

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
              <span className="font-display font-bold">{APP_NAME}</span>
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
              src={getImageUrl(project.image)}
              alt={project.name}
              className="w-full h-full object-cover"
              onError={(e) => {
                e.target.parentElement.style.display = 'none';
              }}
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
                    <ShareButton 
                      title={project.name}
                      description={project.description}
                      url={window.location.href}
                    />
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
            <TabsTrigger value="gallery" className="gap-2">
              <Image className="w-4 h-4" /> Gallery ({galleryFolders.length + galleryImages.length})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="blog">
            <SearchSortBar 
              search={blogSearch} 
              setSearch={setBlogSearch}
              sort={blogSort}
              setSort={setBlogSort}
              placeholder="Search blog posts..."
            />
            {filteredBlogEntries.length === 0 ? (
              <Card className="border border-border/50">
                <CardContent className="py-12 text-center">
                  <FileText className="w-12 h-12 mx-auto text-muted-foreground/30 mb-4" />
                  <p className="text-muted-foreground">
                    {blogSearch ? 'No blog posts match your search' : 'No public blog posts yet'}
                  </p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-6">
                {filteredBlogEntries.map((entry) => (
                  <Card 
                    key={entry.id} 
                    className="border border-border/50 hover:shadow-md transition-all"
                  >
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div className="cursor-pointer flex-1" onClick={() => viewEntry(entry, 'blog')}>
                          <CardTitle className="font-display">{entry.title}</CardTitle>
                          <div className="flex items-center gap-4 text-sm text-muted-foreground mt-1">
                            <span>{format(parseISO(entry.created_at), 'PP')}</span>
                            <span className="flex items-center gap-1"><Eye className="w-3 h-3" /> {entry.views || 0} views</span>
                          </div>
                        </div>
                        <ShareIcons 
                          title={entry.title}
                          description={entry.description}
                          url={`${window.location.origin}/public/project/${projectId}?entry=${entry.id}`}
                        />
                      </div>
                    </CardHeader>
                    <CardContent className="cursor-pointer" onClick={() => viewEntry(entry, 'blog')}>
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
            <SearchSortBar 
              search={librarySearch} 
              setSearch={setLibrarySearch}
              sort={librarySort}
              setSort={setLibrarySort}
              placeholder="Search library entries..."
            />
            {filteredLibraryEntries.length === 0 ? (
              <Card className="border border-border/50">
                <CardContent className="py-12 text-center">
                  <Library className="w-12 h-12 mx-auto text-muted-foreground/30 mb-4" />
                  <p className="text-muted-foreground">
                    {librarySearch ? 'No library entries match your search' : 'No public library entries yet'}
                  </p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-6">
                {filteredLibraryEntries.map((entry) => (
                  <Card 
                    key={entry.id} 
                    className="border border-border/50 hover:shadow-md transition-all"
                  >
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div className="cursor-pointer flex-1" onClick={() => viewEntry(entry, 'library')}>
                          <CardTitle className="font-display">{entry.title}</CardTitle>
                          <div className="flex items-center gap-4 text-sm text-muted-foreground mt-1">
                            <span>{format(parseISO(entry.created_at), 'PP')}</span>
                            <span className="flex items-center gap-1"><Eye className="w-3 h-3" /> {entry.views || 0} views</span>
                          </div>
                        </div>
                        <ShareIcons 
                          title={entry.title}
                          description={entry.description}
                          url={`${window.location.origin}/public/project/${projectId}?entry=${entry.id}`}
                        />
                      </div>
                    </CardHeader>
                    <CardContent className="cursor-pointer" onClick={() => viewEntry(entry, 'library')}>
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

          <TabsContent value="gallery">
            <SearchSortBar 
              search={gallerySearch} 
              setSearch={setGallerySearch}
              sort={gallerySort}
              setSort={setGallerySort}
              placeholder="Search gallery..."
            />
            {filteredGallery.folders.length === 0 && filteredGallery.images.length === 0 ? (
              <Card className="border border-border/50">
                <CardContent className="py-12 text-center">
                  <Image className="w-12 h-12 mx-auto text-muted-foreground/30 mb-4" />
                  <p className="text-muted-foreground">
                    {gallerySearch ? 'No gallery items match your search' : 'No public gallery items yet'}
                  </p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
                {/* Folders */}
                {filteredGallery.folders.map((folder) => (
                  <Card 
                    key={folder.id} 
                    className="border border-border/50 hover:shadow-md transition-all"
                  >
                    <CardContent className="p-4 text-center">
                      <Folder className="w-12 h-12 mx-auto text-amber-500 mb-2" />
                      <p className="text-sm font-medium truncate">{folder.name}</p>
                      <Badge variant="secondary" className="gap-1 mt-2 text-xs">
                        <Globe className="w-3 h-3" /> Public
                      </Badge>
                    </CardContent>
                  </Card>
                ))}
                
                {/* Images */}
                {filteredGallery.images.map((image) => (
                  <Card 
                    key={image.id} 
                    className="border border-border/50 overflow-hidden group"
                  >
                    <div className="aspect-square relative">
                      <img 
                        src={`${process.env.REACT_APP_BACKEND_URL}${image.url}`}
                        alt={image.filename}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                      />
                    </div>
                    <CardContent className="p-2">
                      <p className="text-xs truncate text-muted-foreground">{image.filename}</p>
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
            <span className="font-display font-semibold">{APP_NAME}</span>
          </div>
          <p className="text-sm text-muted-foreground">© {new Date().getFullYear()} {APP_NAME}</p>
        </div>
      </footer>
    </div>
  );
};

export default PublicProjectPage;
