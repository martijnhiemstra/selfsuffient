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
import { toast } from 'sonner';
import { getImageUrl } from '../utils';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const DashboardPage = () => {
  const { user, token } = useAuth();
  const [projects, setProjects] = useState([]);
  const [todayTasks, setTodayTasks] = useState([]);
  const [startupTasks, setStartupTasks] = useState([]);
  const [shutdownTasks, setShutdownTasks] = useState([]);
  const [startupCompletions, setStartupCompletions] = useState([]);
  const [shutdownCompletions, setShutdownCompletions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [projectsRes, dashboardRes] = await Promise.all([
          axios.get(`${API}/projects`, { headers: { Authorization: `Bearer ${token}` } }),
          axios.get(`${API}/dashboard/data`, { headers: { Authorization: `Bearer ${token}` } })
        ]);
        
        setProjects(projectsRes.data.projects || []);
        setTodayTasks(dashboardRes.data.today_tasks || []);
        setStartupTasks(dashboardRes.data.incomplete_startup_tasks || []);
        setShutdownTasks(dashboardRes.data.incomplete_shutdown_tasks || []);
        // Completions are already filtered out in the backend response
        setStartupCompletions([]);
        setShutdownCompletions([]);
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

  const toggleStartupCompletion = async (task) => {
    try {
      await axios.post(`${API}/projects/${task.project_id}/routines/startup/${task.id}/complete`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (startupCompletions.includes(task.id)) {
        setStartupCompletions(startupCompletions.filter(id => id !== task.id));
      } else {
        setStartupCompletions([...startupCompletions, task.id]);
      }
    } catch (error) {
      toast.error('Failed to update task');
    }
  };

  const toggleShutdownCompletion = async (task) => {
    try {
      await axios.post(`${API}/projects/${task.project_id}/routines/shutdown/${task.id}/complete`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (shutdownCompletions.includes(task.id)) {
        setShutdownCompletions(shutdownCompletions.filter(id => id !== task.id));
      } else {
        setShutdownCompletions([...shutdownCompletions, task.id]);
      }
    } catch (error) {
      toast.error('Failed to update task');
    }
  };

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

  const incompleteStartup = startupTasks.filter(t => !startupCompletions.includes(t.id));
  const incompleteShutdown = shutdownTasks.filter(t => !shutdownCompletions.includes(t.id));

  return (
    <div className="min-h-screen bg-background" data-testid="dashboard-page">
      <div className="p-6 md:p-12 lg:p-16 pb-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <p className="label-overline mb-2">{formatDate()}</p>
            <h1 className="text-3xl md:text-4xl font-display font-bold tracking-tight">
              {getGreeting()}, {user?.name || 'Friend'}
            </h1>
            <p className="text-muted-foreground mt-2">Your self-sufficient lifestyle dashboard</p>
          </div>
          <Link to="/projects/new">
            <Button className="rounded-full gap-2" data-testid="new-project-button">
              <Plus className="w-4 h-4" /> New Project
            </Button>
          </Link>
        </div>
      </div>

      <div className="px-6 md:px-12 lg:px-16 pb-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Startup Tasks */}
          <Card className="md:col-span-1 lg:col-span-2 border border-border/50 shadow-soft" data-testid="startup-tasks-card">
            <CardHeader className="flex flex-row items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-amber-100 flex items-center justify-center">
                <Sun className="w-5 h-5 text-amber-600" />
              </div>
              <div className="flex-1">
                <CardTitle className="text-lg font-display">Start of Day Items</CardTitle>
                <CardDescription>
                  {incompleteStartup.length === 0 ? 'All done!' : `${incompleteStartup.length} remaining`}
                </CardDescription>
              </div>
            </CardHeader>
            <CardContent>
              {startupTasks.length === 0 ? (
                <div className="text-center py-6 text-muted-foreground">
                  <Sun className="w-10 h-10 mx-auto mb-2 opacity-30" />
                  <p className="text-sm">No start of day items configured</p>
                </div>
              ) : (
                <ul className="space-y-2">
                  {startupTasks.slice(0, 5).map((task) => {
                    const done = startupCompletions.includes(task.id);
                    return (
                      <li key={task.id} className="flex items-center gap-3">
                        <button onClick={() => toggleStartupCompletion(task)} className="flex-shrink-0">
                          {done ? <CheckCircle2 className="w-5 h-5 text-primary" /> : <Circle className="w-5 h-5 text-muted-foreground hover:text-primary" />}
                        </button>
                        <span className={done ? 'line-through text-muted-foreground' : ''}>{task.title}</span>
                      </li>
                    );
                  })}
                </ul>
              )}
            </CardContent>
          </Card>

          {/* Shutdown Tasks */}
          <Card className="md:col-span-1 lg:col-span-2 border border-border/50 shadow-soft" data-testid="shutdown-tasks-card">
            <CardHeader className="flex flex-row items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center">
                <Moon className="w-5 h-5 text-indigo-600" />
              </div>
              <div className="flex-1">
                <CardTitle className="text-lg font-display">End of Day Items</CardTitle>
                <CardDescription>
                  {incompleteShutdown.length === 0 ? 'All done!' : `${incompleteShutdown.length} remaining`}
                </CardDescription>
              </div>
            </CardHeader>
            <CardContent>
              {shutdownTasks.length === 0 ? (
                <div className="text-center py-6 text-muted-foreground">
                  <Moon className="w-10 h-10 mx-auto mb-2 opacity-30" />
                  <p className="text-sm">No end of day items configured</p>
                </div>
              ) : (
                <ul className="space-y-2">
                  {shutdownTasks.slice(0, 5).map((task) => {
                    const done = shutdownCompletions.includes(task.id);
                    return (
                      <li key={task.id} className="flex items-center gap-3">
                        <button onClick={() => toggleShutdownCompletion(task)} className="flex-shrink-0">
                          {done ? <CheckCircle2 className="w-5 h-5 text-primary" /> : <Circle className="w-5 h-5 text-muted-foreground hover:text-primary" />}
                        </button>
                        <span className={done ? 'line-through text-muted-foreground' : ''}>{task.title}</span>
                      </li>
                    );
                  })}
                </ul>
              )}
            </CardContent>
          </Card>

          {/* Today's Tasks */}
          <Card className="md:col-span-2 border border-border/50 shadow-soft" data-testid="today-tasks-card">
            <CardHeader className="flex flex-row items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                  <Calendar className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <CardTitle className="text-lg font-display">Today's Tasks</CardTitle>
                  <CardDescription>{todayTasks.length} scheduled</CardDescription>
                </div>
              </div>
              <Link to="/calendar">
                <Button variant="ghost" size="sm" className="gap-1">View Calendar <ArrowRight className="w-4 h-4" /></Button>
              </Link>
            </CardHeader>
            <CardContent>
              {todayTasks.length === 0 ? (
                <div className="text-center py-6 text-muted-foreground">
                  <Calendar className="w-10 h-10 mx-auto mb-2 opacity-30" />
                  <p className="text-sm">No tasks scheduled for today</p>
                </div>
              ) : (
                <ul className="space-y-2">
                  {todayTasks.slice(0, 5).map((task) => (
                    <li key={task.id} className="flex items-center justify-between p-3 bg-muted/30 rounded-lg">
                      <div className="flex items-center gap-3">
                        <Circle className="w-4 h-4 text-muted-foreground" />
                        <span>{task.title}</span>
                      </div>
                      <span className="text-sm text-muted-foreground font-mono-data">
                        {task.is_all_day ? 'All day' : task.task_datetime.split('T')[1]?.slice(0, 5)}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>

          {/* Projects */}
          <Card className="md:col-span-2 border border-border/50 shadow-soft" data-testid="projects-card">
            <CardHeader className="flex flex-row items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-secondary/20 flex items-center justify-center">
                  <FolderOpen className="w-5 h-5 text-secondary" />
                </div>
                <div>
                  <CardTitle className="text-lg font-display">Your Projects</CardTitle>
                  <CardDescription>{projects.length} active</CardDescription>
                </div>
              </div>
              <Link to="/projects">
                <Button variant="ghost" size="sm" className="gap-1">View All <ArrowRight className="w-4 h-4" /></Button>
              </Link>
            </CardHeader>
            <CardContent>
              {projects.length === 0 ? (
                <div className="text-center py-6 text-muted-foreground">
                  <FolderOpen className="w-10 h-10 mx-auto mb-2 opacity-30" />
                  <p className="text-sm mb-4">No projects yet</p>
                  <Link to="/projects">
                    <Button variant="outline" className="rounded-full gap-2">
                      <Plus className="w-4 h-4" /> Create First Project
                    </Button>
                  </Link>
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {projects.slice(0, 4).map((project) => (
                    <Link key={project.id} to={`/projects/${project.id}`}>
                      <div className="p-4 bg-muted/30 rounded-xl hover:bg-muted/50 transition-colors">
                        <div className="w-full h-20 rounded-lg bg-muted mb-3 overflow-hidden">
                          {project.image && (
                            <img src={`${process.env.REACT_APP_BACKEND_URL}${project.image}`} alt={project.name} className="w-full h-full object-cover" />
                          )}
                        </div>
                        <h3 className="font-medium truncate">{project.name}</h3>
                      </div>
                    </Link>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
