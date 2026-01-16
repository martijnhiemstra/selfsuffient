import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { Card, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Switch } from '../components/ui/switch';
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
} from '../components/ui/alert-dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import { 
  Plus, 
  ChevronLeft,
  ChevronRight,
  Repeat,
  Loader2,
  LayoutGrid,
  List,
  CalendarDays,
  Trash2,
  GripVertical
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';
import { format, startOfMonth, endOfMonth, startOfWeek, endOfWeek, addDays, addMonths, subMonths, isSameMonth, isSameDay, parseISO, addWeeks, subWeeks } from 'date-fns';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const CalendarPage = () => {
  const { token } = useAuth();
  
  const [projects, setProjects] = useState([]);
  const [allTasks, setAllTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentDate, setCurrentDate] = useState(new Date());
  const [view, setView] = useState('month');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [selectedTask, setSelectedTask] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [draggedTask, setDraggedTask] = useState(null);
  
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    task_datetime: '',
    is_all_day: false,
    recurrence: null,
    project_id: ''
  });

  const fetchData = useCallback(async () => {
    try {
      // First get all projects
      const projectsRes = await axios.get(`${API}/projects`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const projectsList = projectsRes.data.projects || [];
      setProjects(projectsList);

      // Calculate date range
      let startDate, endDate;
      if (view === 'month') {
        const monthStart = startOfMonth(currentDate);
        const monthEnd = endOfMonth(currentDate);
        startDate = format(startOfWeek(monthStart), "yyyy-MM-dd'T'00:00:00");
        endDate = format(endOfWeek(monthEnd), "yyyy-MM-dd'T'23:59:59");
      } else if (view === 'week') {
        startDate = format(startOfWeek(currentDate), "yyyy-MM-dd'T'00:00:00");
        endDate = format(endOfWeek(currentDate), "yyyy-MM-dd'T'23:59:59");
      } else {
        startDate = format(currentDate, "yyyy-MM-dd'T'00:00:00");
        endDate = format(currentDate, "yyyy-MM-dd'T'23:59:59");
      }

      // Fetch tasks from all projects
      const tasksPromises = projectsList.map(project =>
        axios.get(`${API}/projects/${project.id}/tasks?start_date=${startDate}&end_date=${endDate}`, {
          headers: { Authorization: `Bearer ${token}` }
        }).then(res => res.data.tasks.map(t => ({ ...t, projectName: project.name })))
      );

      const tasksResults = await Promise.all(tasksPromises);
      setAllTasks(tasksResults.flat());
    } catch (error) {
      toast.error('Failed to load calendar data');
    } finally {
      setLoading(false);
    }
  }, [token, currentDate, view]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.title.trim() || !formData.project_id) {
      toast.error('Title and project are required');
      return;
    }

    setSaving(true);
    try {
      const payload = {
        title: formData.title,
        description: formData.description,
        task_datetime: formData.task_datetime,
        is_all_day: formData.is_all_day,
        recurrence: formData.recurrence === 'none' ? null : formData.recurrence
      };

      if (editMode && selectedTask) {
        // Update existing task
        await axios.put(`${API}/projects/${selectedTask.project_id}/tasks/${selectedTask.id}`, payload, {
          headers: { Authorization: `Bearer ${token}` }
        });
        toast.success('Task updated!');
      } else {
        // Create new task
        await axios.post(`${API}/projects/${formData.project_id}/tasks`, payload, {
          headers: { Authorization: `Bearer ${token}` }
        });
        toast.success('Task created!');
      }
      
      setDialogOpen(false);
      resetForm();
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to save task');
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteTask = async () => {
    if (!selectedTask) return;
    
    setSaving(true);
    try {
      await axios.delete(`${API}/projects/${selectedTask.project_id}/tasks/${selectedTask.id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Task deleted!');
      setDeleteDialogOpen(false);
      setDialogOpen(false);
      resetForm();
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to delete task');
    } finally {
      setSaving(false);
    }
  };

  const openCreateDialog = (date = null) => {
    setEditMode(false);
    setSelectedTask(null);
    resetForm();
    if (date) {
      setFormData(prev => ({
        ...prev,
        task_datetime: format(date, "yyyy-MM-dd'T'09:00")
      }));
    }
    setDialogOpen(true);
  };

  const openEditDialog = (task, e) => {
    if (e) {
      e.stopPropagation();
    }
    setEditMode(true);
    setSelectedTask(task);
    setFormData({
      title: task.title,
      description: task.description || '',
      task_datetime: task.task_datetime.slice(0, 16),
      is_all_day: task.is_all_day,
      recurrence: task.recurrence || 'none',
      project_id: task.project_id
    });
    setDialogOpen(true);
  };

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      task_datetime: format(new Date(), "yyyy-MM-dd'T'09:00"),
      is_all_day: false,
      recurrence: null,
      project_id: projects.length > 0 ? projects[0].id : ''
    });
    setEditMode(false);
    setSelectedTask(null);
  };

  const navigate = (direction) => {
    if (view === 'month') {
      setCurrentDate(direction === 'next' ? addMonths(currentDate, 1) : subMonths(currentDate, 1));
    } else if (view === 'week') {
      setCurrentDate(direction === 'next' ? addWeeks(currentDate, 1) : subWeeks(currentDate, 1));
    } else {
      setCurrentDate(direction === 'next' ? addDays(currentDate, 1) : addDays(currentDate, -1));
    }
  };

  const getTasksForDate = (date) => {
    const dateStr = format(date, 'yyyy-MM-dd');
    return allTasks.filter(task => {
      const taskDate = task.task_datetime.split('T')[0];
      if (taskDate === dateStr) return true;
      
      if (task.recurrence) {
        const taskDt = parseISO(task.task_datetime);
        if (task.recurrence === 'daily') return true;
        if (task.recurrence === 'weekly' && taskDt.getDay() === date.getDay()) return true;
        if (task.recurrence === 'monthly' && taskDt.getDate() === date.getDate()) return true;
        if (task.recurrence === 'yearly' && taskDt.getMonth() === date.getMonth() && taskDt.getDate() === date.getDate()) return true;
      }
      return false;
    });
  };

  // Drag and drop handlers
  const handleDragStart = (e, task) => {
    // Don't allow dragging recurring tasks
    if (task.recurrence) {
      e.preventDefault();
      toast.info('Recurring tasks cannot be moved by drag-and-drop');
      return;
    }
    setDraggedTask(task);
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', task.id);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDrop = async (e, targetDate, targetHour = null) => {
    e.preventDefault();
    if (!draggedTask) return;

    // Build new datetime
    let newDateTime;
    if (targetHour !== null) {
      const newDate = new Date(targetDate);
      newDate.setHours(targetHour, 0, 0, 0);
      newDateTime = format(newDate, "yyyy-MM-dd'T'HH:mm:ss");
    } else {
      // Keep the original time, just change the date
      const originalTime = draggedTask.task_datetime.split('T')[1];
      newDateTime = `${format(targetDate, 'yyyy-MM-dd')}T${originalTime}`;
    }

    try {
      await axios.put(
        `${API}/projects/${draggedTask.project_id}/tasks/${draggedTask.id}`,
        { task_datetime: newDateTime },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success('Task rescheduled!');
      fetchData();
    } catch (error) {
      toast.error('Failed to reschedule task');
    } finally {
      setDraggedTask(null);
    }
  };

  const handleDragEnd = () => {
    setDraggedTask(null);
  };

  const renderMonthView = () => {
    const monthStart = startOfMonth(currentDate);
    const monthEnd = endOfMonth(currentDate);
    const startDate = startOfWeek(monthStart);
    const endDate = endOfWeek(monthEnd);
    
    const days = [];
    let day = startDate;
    while (day <= endDate) {
      days.push(day);
      day = addDays(day, 1);
    }

    return (
      <div className="grid grid-cols-7 gap-1">
        {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(d => (
          <div key={d} className="text-center text-sm font-medium text-muted-foreground py-2">{d}</div>
        ))}
        {days.map((day, idx) => {
          const dayTasks = getTasksForDate(day);
          const isCurrentMonth = isSameMonth(day, currentDate);
          const isToday = isSameDay(day, new Date());
          const isDragOver = draggedTask !== null;
          
          return (
            <div
              key={idx}
              className={`min-h-[100px] p-1 border border-border/50 rounded-lg cursor-pointer hover:bg-muted/50 transition-colors ${
                !isCurrentMonth ? 'opacity-40' : ''
              } ${isToday ? 'bg-primary/5 border-primary' : ''} ${isDragOver ? 'hover:bg-primary/10' : ''}`}
              onClick={() => openCreateDialog(day)}
              onDragOver={handleDragOver}
              onDrop={(e) => handleDrop(e, day)}
              data-testid={`calendar-day-${format(day, 'yyyy-MM-dd')}`}
            >
              <div className={`text-sm font-medium mb-1 ${isToday ? 'text-primary' : ''}`}>
                {format(day, 'd')}
              </div>
              <div className="space-y-1">
                {dayTasks.slice(0, 3).map(task => (
                  <div
                    key={task.id}
                    draggable={!task.recurrence}
                    onDragStart={(e) => handleDragStart(e, task)}
                    onDragEnd={handleDragEnd}
                    onClick={(e) => openEditDialog(task, e)}
                    className={`text-xs p-1 rounded truncate cursor-pointer hover:opacity-80 transition-opacity flex items-center gap-1 ${
                      task.recurrence ? 'bg-secondary/20 text-secondary-foreground' : 'bg-primary/20 text-primary'
                    } ${!task.recurrence ? 'cursor-grab active:cursor-grabbing' : ''}`}
                    title={`${task.title} (${task.projectName})${task.recurrence ? ' - Click to edit' : ' - Drag to reschedule'}`}
                    data-testid={`task-${task.id}`}
                  >
                    {!task.recurrence && <GripVertical className="w-3 h-3 flex-shrink-0 opacity-50" />}
                    {task.recurrence && <Repeat className="w-3 h-3 flex-shrink-0" />}
                    <span className="truncate">{task.title}</span>
                  </div>
                ))}
                {dayTasks.length > 3 && (
                  <div className="text-xs text-muted-foreground">+{dayTasks.length - 3} more</div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  const renderWeekView = () => {
    const weekStart = startOfWeek(currentDate);
    const days = Array.from({ length: 7 }, (_, i) => addDays(weekStart, i));
    const hours = Array.from({ length: 24 }, (_, i) => i);

    return (
      <div className="overflow-auto">
        <div className="grid grid-cols-8 min-w-[800px]">
          <div className="border-b border-r p-2"></div>
          {days.map(day => (
            <div key={day.toString()} className={`border-b p-2 text-center ${isSameDay(day, new Date()) ? 'bg-primary/5' : ''}`}>
              <div className="text-sm text-muted-foreground">{format(day, 'EEE')}</div>
              <div className={`text-lg font-medium ${isSameDay(day, new Date()) ? 'text-primary' : ''}`}>{format(day, 'd')}</div>
            </div>
          ))}
          {hours.map(hour => (
            <div key={`row-${hour}`} className="contents">
              <div className="border-r p-2 text-xs text-muted-foreground">
                {format(new Date().setHours(hour, 0), 'ha')}
              </div>
              {days.map(day => {
                const dayTasks = getTasksForDate(day).filter(t => {
                  if (t.is_all_day) return hour === 0;
                  const taskHour = parseInt(t.task_datetime.split('T')[1].split(':')[0]);
                  return taskHour === hour;
                });
                return (
                  <div
                    key={`${day}-${hour}`}
                    className="border-b border-r p-1 min-h-[40px] cursor-pointer hover:bg-muted/50"
                    onClick={() => {
                      const newDate = new Date(day);
                      newDate.setHours(hour);
                      openCreateDialog(newDate);
                    }}
                    onDragOver={handleDragOver}
                    onDrop={(e) => handleDrop(e, day, hour)}
                  >
                    {dayTasks.map(task => (
                      <div 
                        key={task.id} 
                        draggable={!task.recurrence}
                        onDragStart={(e) => handleDragStart(e, task)}
                        onDragEnd={handleDragEnd}
                        onClick={(e) => openEditDialog(task, e)}
                        className={`text-xs p-1 rounded mb-1 truncate cursor-pointer hover:opacity-80 ${
                          task.recurrence ? 'bg-secondary/20' : 'bg-primary/20'
                        } ${!task.recurrence ? 'cursor-grab active:cursor-grabbing' : ''}`}
                        title={task.projectName}
                        data-testid={`task-week-${task.id}`}
                      >
                        {task.title}
                      </div>
                    ))}
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderDayView = () => {
    const dayTasks = getTasksForDate(currentDate);
    const hours = Array.from({ length: 24 }, (_, i) => i);

    return (
      <div className="space-y-2">
        {hours.map(hour => {
          const hourTasks = dayTasks.filter(t => {
            if (t.is_all_day) return hour === 0;
            const taskHour = parseInt(t.task_datetime.split('T')[1].split(':')[0]);
            return taskHour === hour;
          });
          
          return (
            <div 
              key={hour} 
              className="flex gap-4 border-b pb-2"
              onDragOver={handleDragOver}
              onDrop={(e) => handleDrop(e, currentDate, hour)}
            >
              <div className="w-20 text-sm text-muted-foreground">
                {format(new Date().setHours(hour, 0), 'h:mm a')}
              </div>
              <div className="flex-1 min-h-[40px]">
                {hourTasks.map(task => (
                  <Card 
                    key={task.id} 
                    className={`mb-2 cursor-pointer hover:shadow-md transition-shadow ${!task.recurrence ? 'cursor-grab active:cursor-grabbing' : ''}`}
                    draggable={!task.recurrence}
                    onDragStart={(e) => handleDragStart(e, task)}
                    onDragEnd={handleDragEnd}
                    onClick={() => openEditDialog(task)}
                    data-testid={`task-day-${task.id}`}
                  >
                    <CardContent className="p-3">
                      <div className="font-medium flex items-center gap-2">
                        {!task.recurrence && <GripVertical className="w-4 h-4 text-muted-foreground" />}
                        {task.title}
                      </div>
                      <div className="text-xs text-muted-foreground">{task.projectName}</div>
                      {task.recurrence && (
                        <div className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                          <Repeat className="w-3 h-3" /> {task.recurrence}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="p-6 md:p-12 lg:p-16" data-testid="calendar-page">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-display font-bold tracking-tight">Calendar</h1>
          <p className="text-muted-foreground">View and manage tasks across all projects</p>
        </div>
        <Button className="rounded-full gap-2" onClick={() => openCreateDialog()} data-testid="create-task-btn" disabled={projects.length === 0}>
          <Plus className="w-4 h-4" /> New Task
        </Button>
      </div>

      {/* Calendar Controls */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <Button variant="outline" size="icon" onClick={() => navigate('prev')} data-testid="prev-btn"><ChevronLeft className="w-4 h-4" /></Button>
          <Button variant="outline" size="icon" onClick={() => navigate('next')} data-testid="next-btn"><ChevronRight className="w-4 h-4" /></Button>
          <Button variant="outline" onClick={() => setCurrentDate(new Date())} data-testid="today-btn">Today</Button>
          <h2 className="text-xl font-display font-semibold ml-4">
            {view === 'day' ? format(currentDate, 'EEEE, MMMM d, yyyy') : 
             view === 'week' ? `Week of ${format(startOfWeek(currentDate), 'MMM d')}` :
             format(currentDate, 'MMMM yyyy')}
          </h2>
        </div>
        <div className="flex gap-1 bg-muted rounded-lg p-1">
          <Button variant={view === 'month' ? 'secondary' : 'ghost'} size="sm" onClick={() => setView('month')} data-testid="month-view-btn">
            <LayoutGrid className="w-4 h-4 mr-1" /> Month
          </Button>
          <Button variant={view === 'week' ? 'secondary' : 'ghost'} size="sm" onClick={() => setView('week')} data-testid="week-view-btn">
            <CalendarDays className="w-4 h-4 mr-1" /> Week
          </Button>
          <Button variant={view === 'day' ? 'secondary' : 'ghost'} size="sm" onClick={() => setView('day')} data-testid="day-view-btn">
            <List className="w-4 h-4 mr-1" /> Day
          </Button>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>
      ) : projects.length === 0 ? (
        <Card className="border border-border/50">
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground">Create a project first to add tasks to the calendar</p>
          </CardContent>
        </Card>
      ) : (
        <Card className="border border-border/50">
          <CardContent className="p-4">
            {view === 'month' && renderMonthView()}
            {view === 'week' && renderWeekView()}
            {view === 'day' && renderDayView()}
          </CardContent>
        </Card>
      )}

      {/* Drag hint */}
      {allTasks.some(t => !t.recurrence) && (
        <p className="text-xs text-muted-foreground text-center mt-4">
          Tip: Drag non-recurring tasks to reschedule them. Click any task to edit.
        </p>
      )}

      {/* Task Dialog */}
      <Dialog open={dialogOpen} onOpenChange={(open) => { setDialogOpen(open); if (!open) resetForm(); }}>
        <DialogContent className="sm:max-w-lg">
          <form onSubmit={handleSubmit}>
            <DialogHeader>
              <DialogTitle className="font-display">{editMode ? 'Edit Task' : 'New Task'}</DialogTitle>
              <DialogDescription>{editMode ? 'Update task details' : 'Add a task to your calendar'}</DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="project">Project</Label>
                <Select 
                  value={formData.project_id} 
                  onValueChange={(v) => setFormData({ ...formData, project_id: v })}
                  disabled={editMode}
                >
                  <SelectTrigger data-testid="project-select"><SelectValue placeholder="Select project" /></SelectTrigger>
                  <SelectContent>
                    {projects.map(p => (
                      <SelectItem key={p.id} value={p.id}>{p.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="title">Title</Label>
                <Input 
                  id="title" 
                  value={formData.title} 
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })} 
                  placeholder="Task title"
                  data-testid="task-title-input"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea 
                  id="description" 
                  value={formData.description} 
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })} 
                  rows={2}
                  data-testid="task-description-input"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="datetime">Date & Time</Label>
                  <Input 
                    id="datetime" 
                    type="datetime-local" 
                    value={formData.task_datetime} 
                    onChange={(e) => setFormData({ ...formData, task_datetime: e.target.value })}
                    data-testid="task-datetime-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="recurrence">Repeat</Label>
                  <Select value={formData.recurrence || 'none'} onValueChange={(v) => setFormData({ ...formData, recurrence: v })}>
                    <SelectTrigger data-testid="recurrence-select"><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">No repeat</SelectItem>
                      <SelectItem value="daily">Daily</SelectItem>
                      <SelectItem value="weekly">Weekly</SelectItem>
                      <SelectItem value="monthly">Monthly</SelectItem>
                      <SelectItem value="yearly">Yearly</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <Label htmlFor="allday">All day event</Label>
                <Switch 
                  id="allday" 
                  checked={formData.is_all_day} 
                  onCheckedChange={(c) => setFormData({ ...formData, is_all_day: c })}
                  data-testid="allday-switch"
                />
              </div>
            </div>
            <DialogFooter className="flex justify-between">
              {editMode && (
                <Button 
                  type="button" 
                  variant="destructive" 
                  onClick={() => setDeleteDialogOpen(true)}
                  data-testid="delete-task-btn"
                >
                  <Trash2 className="w-4 h-4 mr-2" /> Delete
                </Button>
              )}
              <div className="flex gap-2 ml-auto">
                <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button>
                <Button type="submit" disabled={saving} data-testid="save-task-btn">
                  {saving && <Loader2 className="w-4 h-4 animate-spin mr-2" />}
                  {editMode ? 'Update Task' : 'Create Task'}
                </Button>
              </div>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Task</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete "{selectedTask?.title}"? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDeleteTask} className="bg-destructive text-destructive-foreground hover:bg-destructive/90" data-testid="confirm-delete-btn">
              {saving && <Loader2 className="w-4 h-4 animate-spin mr-2" />}
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default CalendarPage;
