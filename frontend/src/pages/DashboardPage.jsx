import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { 
  Leaf, 
  FolderOpen, 
  Calendar, 
  Sun, 
  Moon, 
  CheckCircle2,
  Circle,
  Plus,
  ArrowRight
} from 'lucide-react';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const DashboardPage = () => {
  const { user, token } = useAuth();
  const [projects, setProjects] = useState([]);
  const [todayTasks, setTodayTasks] = useState([]);
  const [startupTasks, setStartupTasks] = useState([]);
  const [shutdownTasks, setShutdownTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Fetch projects
        const projectsRes = await axios.get(`${API}/projects`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setProjects(projectsRes.data.projects || []);
        
        // Startup/shutdown tasks and today's tasks will be fetched once those features are implemented
        setTodayTasks([]);
        setStartupTasks([]);
        setShutdownTasks([]);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    if (token) {
      fetchDashboardData();
    }
  }, [token]);

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 18) return 'Good Afternoon';
    return 'Good Evening';
  };

  const formatDate = () => {
    return new Date().toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <div className="min-h-screen bg-background" data-testid="dashboard-page">
      {/* Header */}
      <div className="p-6 md:p-12 lg:p-16 pb-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <p className="label-overline mb-2">{formatDate()}</p>
            <h1 className="text-3xl md:text-4xl font-display font-bold tracking-tight">
              {getGreeting()}, {user?.name || 'Friend'}
            </h1>
            <p className="text-muted-foreground mt-2">
              Your self-sufficient lifestyle dashboard
            </p>
          </div>
          <Link to="/projects/new">
            <Button className="rounded-full gap-2" data-testid="new-project-button">
              <Plus className="w-4 h-4" />
              New Project
            </Button>
          </Link>
        </div>
      </div>

      {/* Main Content - Bento Grid */}
      <div className="px-6 md:px-12 lg:px-16 pb-12">
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {/* Startup Tasks */}
          <Card className="md:col-span-2 border border-border/50 shadow-soft hover:shadow-md transition-all duration-300" data-testid="startup-tasks-card">
            <CardHeader className="flex flex-row items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-amber-100 flex items-center justify-center">
                <Sun className="w-5 h-5 text-amber-600" />
              </div>
              <div>
                <CardTitle className="text-lg font-display">Morning Startup</CardTitle>
                <CardDescription>Tasks to start your day</CardDescription>
              </div>
            </CardHeader>
            <CardContent>
              {startupTasks.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <Sun className="w-12 h-12 mx-auto mb-3 opacity-30" />
                  <p>No startup tasks configured</p>
                  <p className="text-sm">Create a project to add daily routines</p>
                </div>
              ) : (
                <ul className="space-y-3">
                  {startupTasks.map((task, index) => (
                    <li key={index} className="flex items-center gap-3">
                      {task.done ? (
                        <CheckCircle2 className="w-5 h-5 text-primary" />
                      ) : (
                        <Circle className="w-5 h-5 text-muted-foreground" />
                      )}
                      <span className={task.done ? 'line-through text-muted-foreground' : ''}>
                        {task.title}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>

          {/* Shutdown Tasks */}
          <Card className="md:col-span-2 border border-border/50 shadow-soft hover:shadow-md transition-all duration-300" data-testid="shutdown-tasks-card">
            <CardHeader className="flex flex-row items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center">
                <Moon className="w-5 h-5 text-indigo-600" />
              </div>
              <div>
                <CardTitle className="text-lg font-display">Evening Shutdown</CardTitle>
                <CardDescription>Tasks to end your day</CardDescription>
              </div>
            </CardHeader>
            <CardContent>
              {shutdownTasks.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <Moon className="w-12 h-12 mx-auto mb-3 opacity-30" />
                  <p>No shutdown tasks configured</p>
                  <p className="text-sm">Create a project to add evening routines</p>
                </div>
              ) : (
                <ul className="space-y-3">
                  {shutdownTasks.map((task, index) => (
                    <li key={index} className="flex items-center gap-3">
                      {task.done ? (
                        <CheckCircle2 className="w-5 h-5 text-primary" />
                      ) : (
                        <Circle className="w-5 h-5 text-muted-foreground" />
                      )}
                      <span className={task.done ? 'line-through text-muted-foreground' : ''}>
                        {task.title}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>

          {/* Today's Tasks */}
          <Card className="md:col-span-2 lg:col-span-2 border border-border/50 shadow-soft hover:shadow-md transition-all duration-300" data-testid="today-tasks-card">
            <CardHeader className="flex flex-row items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                  <Calendar className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <CardTitle className="text-lg font-display">Today's Tasks</CardTitle>
                  <CardDescription>Scheduled for today</CardDescription>
                </div>
              </div>
              <Link to="/calendar">
                <Button variant="ghost" size="sm" className="gap-1">
                  View Calendar
                  <ArrowRight className="w-4 h-4" />
                </Button>
              </Link>
            </CardHeader>
            <CardContent>
              {todayTasks.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <Calendar className="w-12 h-12 mx-auto mb-3 opacity-30" />
                  <p>No tasks scheduled for today</p>
                  <p className="text-sm">Add tasks from your projects</p>
                </div>
              ) : (
                <ul className="space-y-3">
                  {todayTasks.map((task, index) => (
                    <li key={index} className="flex items-center justify-between p-3 bg-muted/30 rounded-lg">
                      <div className="flex items-center gap-3">
                        <Circle className="w-4 h-4 text-muted-foreground" />
                        <span>{task.title}</span>
                      </div>
                      <span className="text-sm text-muted-foreground font-mono-data">
                        {task.time}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>

          {/* Projects */}
          <Card className="md:col-span-3 lg:col-span-2 border border-border/50 shadow-soft hover:shadow-md transition-all duration-300" data-testid="projects-card">
            <CardHeader className="flex flex-row items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-secondary/20 flex items-center justify-center">
                  <FolderOpen className="w-5 h-5 text-secondary" />
                </div>
                <div>
                  <CardTitle className="text-lg font-display">Your Projects</CardTitle>
                  <CardDescription>Active self-sufficiency projects</CardDescription>
                </div>
              </div>
              <Link to="/projects">
                <Button variant="ghost" size="sm" className="gap-1">
                  View All
                  <ArrowRight className="w-4 h-4" />
                </Button>
              </Link>
            </CardHeader>
            <CardContent>
              {projects.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <FolderOpen className="w-12 h-12 mx-auto mb-3 opacity-30" />
                  <p>No projects yet</p>
                  <p className="text-sm mb-4">Start your self-sufficient journey</p>
                  <Link to="/projects/new">
                    <Button variant="outline" className="rounded-full gap-2">
                      <Plus className="w-4 h-4" />
                      Create First Project
                    </Button>
                  </Link>
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {projects.slice(0, 4).map((project, index) => (
                    <Link key={index} to={`/projects/${project.id}`}>
                      <div className="p-4 bg-muted/30 rounded-xl hover:bg-muted/50 transition-colors">
                        <div className="w-full h-24 rounded-lg bg-muted mb-3 overflow-hidden">
                          {project.image && (
                            <img 
                              src={project.image} 
                              alt={project.name}
                              className="w-full h-full object-cover"
                            />
                          )}
                        </div>
                        <h3 className="font-medium truncate">{project.name}</h3>
                        <p className="text-sm text-muted-foreground truncate">
                          {project.description}
                        </p>
                      </div>
                    </Link>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Quick Stats */}
          <Card className="border border-border/50 shadow-soft hover:shadow-md transition-all duration-300" data-testid="quick-stats-card">
            <CardHeader>
              <CardTitle className="text-lg font-display">Quick Stats</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Projects</span>
                <span className="font-mono-data font-medium">{projects.length}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Tasks Today</span>
                <span className="font-mono-data font-medium">{todayTasks.length}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Startup Done</span>
                <span className="font-mono-data font-medium">
                  {startupTasks.filter(t => t.done).length}/{startupTasks.length || 0}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Shutdown Done</span>
                <span className="font-mono-data font-medium">
                  {shutdownTasks.filter(t => t.done).length}/{shutdownTasks.length || 0}
                </span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
