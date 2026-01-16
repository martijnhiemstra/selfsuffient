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
  CalendarDays
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

      await axios.post(`${API}/projects/${formData.project_id}/tasks`, payload, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Task created!');
      setDialogOpen(false);
      resetForm();
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create task');
    } finally {
      setSaving(false);
    }
  };

  const openCreateDialog = (date = null) => {
    resetForm();
    if (date) {
      setFormData(prev => ({
        ...prev,
        task_datetime: format(date, "yyyy-MM-dd'T'09:00")
      }));
    }
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
          
          return (
            <div
              key={idx}
              className={`min-h-[100px] p-1 border border-border/50 rounded-lg cursor-pointer hover:bg-muted/50 transition-colors ${
                !isCurrentMonth ? 'opacity-40' : ''
              } ${isToday ? 'bg-primary/5 border-primary' : ''}`}
              onClick={() => openCreateDialog(day)}
            >
              <div className={`text-sm font-medium mb-1 ${isToday ? 'text-primary' : ''}`}>
                {format(day, 'd')}
              </div>
              <div className="space-y-1">
                {dayTasks.slice(0, 3).map(task => (
                  <div
                    key={task.id}
                    className={`text-xs p-1 rounded truncate ${
                      task.recurrence ? 'bg-secondary/20 text-secondary-foreground' : 'bg-primary/20 text-primary'
                    }`}
                    title={`${task.title} (${task.projectName})`}
                  >
                    {task.title}
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
                  >
                    {dayTasks.map(task => (
                      <div key={task.id} className="text-xs p-1 bg-primary/20 rounded mb-1 truncate" title={task.projectName}>
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
            <div key={hour} className="flex gap-4 border-b pb-2">
              <div className="w-20 text-sm text-muted-foreground">
                {format(new Date().setHours(hour, 0), 'h:mm a')}
              </div>
              <div className="flex-1 min-h-[40px]">
                {hourTasks.map(task => (
                  <Card key={task.id} className="mb-2">
                    <CardContent className="p-3">
                      <div className="font-medium">{task.title}</div>
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
          <p className="text-muted-foreground">View tasks across all projects</p>
        </div>
        <Button className="rounded-full gap-2" onClick={() => openCreateDialog()} data-testid="create-task-btn" disabled={projects.length === 0}>
          <Plus className="w-4 h-4" /> New Task
        </Button>
      </div>

      {/* Calendar Controls */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <Button variant="outline" size="icon" onClick={() => navigate('prev')}><ChevronLeft className="w-4 h-4" /></Button>
          <Button variant="outline" size="icon" onClick={() => navigate('next')}><ChevronRight className="w-4 h-4" /></Button>
          <Button variant="outline" onClick={() => setCurrentDate(new Date())}>Today</Button>
          <h2 className="text-xl font-display font-semibold ml-4">
            {view === 'day' ? format(currentDate, 'EEEE, MMMM d, yyyy') : 
             view === 'week' ? `Week of ${format(startOfWeek(currentDate), 'MMM d')}` :
             format(currentDate, 'MMMM yyyy')}
          </h2>
        </div>
        <div className="flex gap-1 bg-muted rounded-lg p-1">
          <Button variant={view === 'month' ? 'secondary' : 'ghost'} size="sm" onClick={() => setView('month')}>
            <LayoutGrid className="w-4 h-4 mr-1" /> Month
          </Button>
          <Button variant={view === 'week' ? 'secondary' : 'ghost'} size="sm" onClick={() => setView('week')}>
            <CalendarDays className="w-4 h-4 mr-1" /> Week
          </Button>
          <Button variant={view === 'day' ? 'secondary' : 'ghost'} size="sm" onClick={() => setView('day')}>
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

      {/* Task Dialog */}
      <Dialog open={dialogOpen} onOpenChange={(open) => { setDialogOpen(open); if (!open) resetForm(); }}>
        <DialogContent className="sm:max-w-lg">
          <form onSubmit={handleSubmit}>
            <DialogHeader>
              <DialogTitle className="font-display">New Task</DialogTitle>
              <DialogDescription>Add a task to your calendar</DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="project">Project</Label>
                <Select value={formData.project_id} onValueChange={(v) => setFormData({ ...formData, project_id: v })}>
                  <SelectTrigger><SelectValue placeholder="Select project" /></SelectTrigger>
                  <SelectContent>
                    {projects.map(p => (
                      <SelectItem key={p.id} value={p.id}>{p.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="title">Title</Label>
                <Input id="title" value={formData.title} onChange={(e) => setFormData({ ...formData, title: e.target.value })} placeholder="Task title" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea id="description" value={formData.description} onChange={(e) => setFormData({ ...formData, description: e.target.value })} rows={2} />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="datetime">Date & Time</Label>
                  <Input id="datetime" type="datetime-local" value={formData.task_datetime} onChange={(e) => setFormData({ ...formData, task_datetime: e.target.value })} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="recurrence">Repeat</Label>
                  <Select value={formData.recurrence || 'none'} onValueChange={(v) => setFormData({ ...formData, recurrence: v })}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
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
                <Switch id="allday" checked={formData.is_all_day} onCheckedChange={(c) => setFormData({ ...formData, is_all_day: c })} />
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button>
              <Button type="submit" disabled={saving}>
                {saving && <Loader2 className="w-4 h-4 animate-spin mr-2" />}
                Create Task
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default CalendarPage;
