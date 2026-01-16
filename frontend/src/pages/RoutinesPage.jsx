import { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Checkbox } from '../components/ui/checkbox';
import {
  Dialog,
  DialogContent,
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { 
  ArrowLeft, 
  Plus, 
  Sun, 
  Moon, 
  GripVertical,
  Edit,
  Trash2,
  Loader2,
  CheckCircle2,
  Circle
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const RoutinesPage = () => {
  const { projectId } = useParams();
  const { token } = useAuth();
  
  const [startupTasks, setStartupTasks] = useState([]);
  const [shutdownTasks, setShutdownTasks] = useState([]);
  const [startupCompletions, setStartupCompletions] = useState([]);
  const [shutdownCompletions, setShutdownCompletions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('startup');
  
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({ title: '', description: '' });

  const fetchRoutines = useCallback(async () => {
    try {
      const [startupRes, shutdownRes] = await Promise.all([
        axios.get(`${API}/projects/${projectId}/routines/startup`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/projects/${projectId}/routines/shutdown`, { headers: { Authorization: `Bearer ${token}` } })
      ]);
      
      setStartupTasks(startupRes.data.tasks);
      setStartupCompletions(startupRes.data.completions_today);
      setShutdownTasks(shutdownRes.data.tasks);
      setShutdownCompletions(shutdownRes.data.completions_today);
    } catch (error) {
      toast.error('Failed to load routines');
    } finally {
      setLoading(false);
    }
  }, [projectId, token]);

  useEffect(() => {
    fetchRoutines();
  }, [fetchRoutines]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.title.trim()) {
      toast.error('Title is required');
      return;
    }

    setSaving(true);
    try {
      if (editingTask) {
        await axios.put(`${API}/projects/${projectId}/routines/${activeTab}/${editingTask.id}`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
        toast.success('Task updated!');
      } else {
        await axios.post(`${API}/projects/${projectId}/routines/${activeTab}`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
        toast.success('Task created!');
      }
      setDialogOpen(false);
      resetForm();
      fetchRoutines();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to save task');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (taskId, routineType) => {
    try {
      await axios.delete(`${API}/projects/${projectId}/routines/${routineType}/${taskId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Task deleted');
      fetchRoutines();
    } catch (error) {
      toast.error('Failed to delete task');
    }
  };

  const toggleCompletion = async (taskId, routineType) => {
    try {
      await axios.post(`${API}/projects/${projectId}/routines/${routineType}/${taskId}/complete`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchRoutines();
    } catch (error) {
      toast.error('Failed to update task');
    }
  };

  const openEditDialog = (task) => {
    setEditingTask(task);
    setFormData({ title: task.title, description: task.description });
    setDialogOpen(true);
  };

  const resetForm = () => {
    setEditingTask(null);
    setFormData({ title: '', description: '' });
  };

  const renderTaskList = (tasks, completions, routineType) => (
    <div className="space-y-3">
      {tasks.length === 0 ? (
        <div className="text-center py-8 text-muted-foreground">
          <p>No {routineType} tasks yet</p>
          <Button variant="outline" className="mt-4 gap-2" onClick={() => { setActiveTab(routineType); setDialogOpen(true); }}>
            <Plus className="w-4 h-4" /> Add First Task
          </Button>
        </div>
      ) : (
        tasks.map((task) => {
          const isCompleted = completions.includes(task.id);
          return (
            <Card key={task.id} className={`border transition-all ${isCompleted ? 'bg-muted/50 border-primary/30' : 'border-border/50'}`} data-testid={`routine-task-${task.id}`}>
              <CardContent className="p-4">
                <div className="flex items-center gap-4">
                  <button
                    onClick={() => toggleCompletion(task.id, routineType)}
                    className="flex-shrink-0"
                    data-testid={`toggle-${task.id}`}
                  >
                    {isCompleted ? (
                      <CheckCircle2 className="w-6 h-6 text-primary" />
                    ) : (
                      <Circle className="w-6 h-6 text-muted-foreground hover:text-primary transition-colors" />
                    )}
                  </button>
                  <div className="flex-1 min-w-0">
                    <h3 className={`font-medium ${isCompleted ? 'line-through text-muted-foreground' : ''}`}>
                      {task.title}
                    </h3>
                    {task.description && (
                      <p className="text-sm text-muted-foreground truncate">{task.description}</p>
                    )}
                  </div>
                  <div className="flex gap-1">
                    <Button variant="ghost" size="icon" onClick={() => openEditDialog(task)}>
                      <Edit className="w-4 h-4" />
                    </Button>
                    <AlertDialog>
                      <AlertDialogTrigger asChild>
                        <Button variant="ghost" size="icon" className="text-destructive">
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </AlertDialogTrigger>
                      <AlertDialogContent>
                        <AlertDialogHeader>
                          <AlertDialogTitle>Delete Task?</AlertDialogTitle>
                          <AlertDialogDescription>This will permanently delete this routine task.</AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                          <AlertDialogCancel>Cancel</AlertDialogCancel>
                          <AlertDialogAction onClick={() => handleDelete(task.id, routineType)} className="bg-destructive">Delete</AlertDialogAction>
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })
      )}
    </div>
  );

  const getProgress = (tasks, completions) => {
    if (tasks.length === 0) return 0;
    return Math.round((completions.length / tasks.length) * 100);
  };

  return (
    <div className="p-6 md:p-12 lg:p-16" data-testid="routines-page">
      <div className="flex items-center gap-4 mb-6">
        <Link to={`/projects/${projectId}`}>
          <Button variant="ghost" size="icon"><ArrowLeft className="w-5 h-5" /></Button>
        </Link>
        <div className="flex-1">
          <h1 className="text-3xl font-display font-bold tracking-tight">Daily Routines</h1>
          <p className="text-muted-foreground">Startup and shutdown checklists</p>
        </div>
        <Button className="rounded-full gap-2" onClick={() => setDialogOpen(true)} data-testid="create-routine-btn">
          <Plus className="w-4 h-4" /> Add Task
        </Button>
      </div>

      {loading ? (
        <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>
      ) : (
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-2 mb-6">
            <TabsTrigger value="startup" className="gap-2" data-testid="startup-tab">
              <Sun className="w-4 h-4" /> Morning Startup
              <span className="ml-2 text-xs bg-muted px-2 py-0.5 rounded-full">
                {getProgress(startupTasks, startupCompletions)}%
              </span>
            </TabsTrigger>
            <TabsTrigger value="shutdown" className="gap-2" data-testid="shutdown-tab">
              <Moon className="w-4 h-4" /> Evening Shutdown
              <span className="ml-2 text-xs bg-muted px-2 py-0.5 rounded-full">
                {getProgress(shutdownTasks, shutdownCompletions)}%
              </span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="startup">
            <Card className="border border-border/50">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-amber-100 flex items-center justify-center">
                    <Sun className="w-5 h-5 text-amber-600" />
                  </div>
                  <div>
                    <CardTitle>Morning Startup</CardTitle>
                    <CardDescription>Tasks to start your day right</CardDescription>
                  </div>
                </div>
                <div className="mt-4 h-2 bg-muted rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-primary transition-all duration-500" 
                    style={{ width: `${getProgress(startupTasks, startupCompletions)}%` }}
                  />
                </div>
              </CardHeader>
              <CardContent>
                {renderTaskList(startupTasks, startupCompletions, 'startup')}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="shutdown">
            <Card className="border border-border/50">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center">
                    <Moon className="w-5 h-5 text-indigo-600" />
                  </div>
                  <div>
                    <CardTitle>Evening Shutdown</CardTitle>
                    <CardDescription>Tasks to end your day peacefully</CardDescription>
                  </div>
                </div>
                <div className="mt-4 h-2 bg-muted rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-primary transition-all duration-500" 
                    style={{ width: `${getProgress(shutdownTasks, shutdownCompletions)}%` }}
                  />
                </div>
              </CardHeader>
              <CardContent>
                {renderTaskList(shutdownTasks, shutdownCompletions, 'shutdown')}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}

      {/* Task Dialog */}
      <Dialog open={dialogOpen} onOpenChange={(open) => { setDialogOpen(open); if (!open) resetForm(); }}>
        <DialogContent className="sm:max-w-md">
          <form onSubmit={handleSubmit}>
            <DialogHeader>
              <DialogTitle className="font-display capitalize">
                {editingTask ? 'Edit' : 'Add'} {activeTab} Task
              </DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="title">Task Title</Label>
                <Input id="title" value={formData.title} onChange={(e) => setFormData({ ...formData, title: e.target.value })} placeholder="e.g., Make bed" data-testid="routine-title-input" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">Description (optional)</Label>
                <Input id="description" value={formData.description} onChange={(e) => setFormData({ ...formData, description: e.target.value })} placeholder="Additional details..." />
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button>
              <Button type="submit" disabled={saving} data-testid="save-routine-btn">
                {saving && <Loader2 className="w-4 h-4 animate-spin mr-2" />}
                {editingTask ? 'Save' : 'Add Task'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default RoutinesPage;
