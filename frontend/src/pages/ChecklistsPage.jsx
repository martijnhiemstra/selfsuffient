import { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../components/ui/dialog';
import { Checkbox } from '../components/ui/checkbox';
import { Progress } from '../components/ui/progress';
import { 
  Plus, Trash2, Edit, RefreshCw,
  ListChecks, RotateCcw, ArrowLeft
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const ChecklistsPage = () => {
  const { token } = useAuth();
  const { projectId } = useParams();
  const [project, setProject] = useState(null);
  const [checklists, setChecklists] = useState([]);
  const [loading, setLoading] = useState(true);
  const [checklistDialog, setChecklistDialog] = useState({ open: false, data: null });
  const [itemDialog, setItemDialog] = useState({ open: false, checklistId: null, data: null });

  const headers = { Authorization: `Bearer ${token}` };

  const fetchProject = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/projects/${projectId}`, { headers });
      setProject(res.data);
    } catch (err) {
      console.error('Failed to fetch project:', err);
    }
  }, [token, projectId]);

  const fetchChecklists = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/checklists?project_id=${projectId}`, { headers });
      setChecklists(res.data.checklists || []);
    } catch (err) {
      console.error('Failed to fetch checklists:', err);
    }
  }, [token, projectId]);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await fetchProject();
      await fetchChecklists();
      setLoading(false);
    };
    loadData();
  }, [projectId]);

  const handleSaveChecklist = async (data) => {
    try {
      if (checklistDialog.data?.id) {
        await axios.put(`${API}/checklists/${checklistDialog.data.id}`, data, { headers });
        toast.success('Checklist updated');
      } else {
        await axios.post(`${API}/checklists`, { ...data, project_id: projectId }, { headers });
        toast.success('Checklist created');
      }
      setChecklistDialog({ open: false, data: null });
      fetchChecklists();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to save checklist');
    }
  };

  const handleDeleteChecklist = async (id) => {
    if (!window.confirm('Delete this checklist and all its items?')) return;
    try {
      await axios.delete(`${API}/checklists/${id}`, { headers });
      toast.success('Checklist deleted');
      fetchChecklists();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to delete checklist');
    }
  };

  const handleResetChecklist = async (id) => {
    try {
      await axios.post(`${API}/checklists/${id}/reset`, {}, { headers });
      toast.success('Checklist reset - all items unchecked');
      fetchChecklists();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to reset checklist');
    }
  };

  const handleToggleItem = async (itemId) => {
    try {
      await axios.post(`${API}/checklist-items/${itemId}/toggle`, {}, { headers });
      fetchChecklists();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to toggle item');
    }
  };

  const handleSaveItem = async (data) => {
    try {
      if (itemDialog.data?.id) {
        await axios.put(`${API}/checklist-items/${itemDialog.data.id}`, data, { headers });
        toast.success('Item updated');
      } else {
        await axios.post(`${API}/checklists/${itemDialog.checklistId}/items`, data, { headers });
        toast.success('Item added');
      }
      setItemDialog({ open: false, checklistId: null, data: null });
      fetchChecklists();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to save item');
    }
  };

  const handleDeleteItem = async (id) => {
    try {
      await axios.delete(`${API}/checklist-items/${id}`, { headers });
      toast.success('Item deleted');
      fetchChecklists();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to delete item');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <RefreshCw className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="p-6 md:p-8 lg:p-12 space-y-6" data-testid="checklists-page">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <Link 
            to={`/projects/${projectId}`} 
            className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground mb-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to {project?.name || 'Project'}
          </Link>
          <h1 className="text-3xl font-bold text-foreground">Checklists</h1>
          <p className="text-muted-foreground">Reusable checklists for {project?.name}</p>
        </div>
        
        <Button onClick={() => setChecklistDialog({ open: true, data: null })} data-testid="add-checklist-btn">
          <Plus className="w-4 h-4 mr-2" /> New Checklist
          </Button>
        </div>
      </div>

      {checklists.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <ListChecks className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium mb-2">No checklists yet</h3>
            <p className="text-muted-foreground mb-4">
              Create reusable checklists for recurring tasks like daily farm routines, harvest procedures, or maintenance checks.
            </p>
            <Button onClick={() => setChecklistDialog({ open: true, data: null })}>
              <Plus className="w-4 h-4 mr-2" /> Create Your First Checklist
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {checklists.map(checklist => (
            <Card key={checklist.id} className="flex flex-col">
              <CardHeader className="pb-2">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <ListChecks className="w-5 h-5 text-primary" />
                      <CardTitle className="text-lg">{checklist.name}</CardTitle>
                    </div>
                    <CardDescription className="mt-1">
                      {checklist.project_name}
                      {checklist.description && ` • ${checklist.description}`}
                    </CardDescription>
                  </div>
                  <div className="flex gap-1">
                    <Button 
                      size="icon" 
                      variant="ghost" 
                      onClick={() => handleResetChecklist(checklist.id)}
                      title="Reset checklist"
                      data-testid={`reset-checklist-${checklist.id}`}
                    >
                      <RotateCcw className="w-4 h-4" />
                    </Button>
                    <Button 
                      size="icon" 
                      variant="ghost" 
                      onClick={() => setChecklistDialog({ open: true, data: checklist })}
                    >
                      <Edit className="w-4 h-4" />
                    </Button>
                    <Button 
                      size="icon" 
                      variant="ghost" 
                      onClick={() => handleDeleteChecklist(checklist.id)}
                    >
                      <Trash2 className="w-4 h-4 text-red-500" />
                    </Button>
                  </div>
                </div>
                
                {/* Progress bar */}
                <div className="mt-3">
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-muted-foreground">Progress</span>
                    <span className="font-medium">
                      {checklist.completed_items}/{checklist.total_items}
                      {checklist.total_items > 0 && (
                        <span className="text-muted-foreground ml-1">
                          ({Math.round((checklist.completed_items / checklist.total_items) * 100)}%)
                        </span>
                      )}
                    </span>
                  </div>
                  <Progress 
                    value={checklist.total_items > 0 ? (checklist.completed_items / checklist.total_items) * 100 : 0} 
                    className="h-2"
                  />
                </div>
              </CardHeader>
              
              <CardContent className="flex-1">
                {checklist.items.length === 0 ? (
                  <p className="text-sm text-muted-foreground text-center py-4">
                    No items yet. Add some items to this checklist.
                  </p>
                ) : (
                  <div className="space-y-2">
                    {checklist.items.map(item => (
                      <div 
                        key={item.id}
                        className={`flex items-center gap-3 p-2 rounded-lg hover:bg-muted/50 transition-colors group ${item.is_done ? 'opacity-60' : ''}`}
                      >
                        <Checkbox
                          checked={item.is_done}
                          onCheckedChange={() => handleToggleItem(item.id)}
                          data-testid={`item-checkbox-${item.id}`}
                        />
                        <span className={`flex-1 ${item.is_done ? 'line-through text-muted-foreground' : ''}`}>
                          {item.text}
                        </span>
                        <div className="opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                          <Button 
                            size="icon" 
                            variant="ghost" 
                            className="h-7 w-7"
                            onClick={() => setItemDialog({ open: true, checklistId: checklist.id, data: item })}
                          >
                            <Edit className="w-3 h-3" />
                          </Button>
                          <Button 
                            size="icon" 
                            variant="ghost" 
                            className="h-7 w-7"
                            onClick={() => handleDeleteItem(item.id)}
                          >
                            <Trash2 className="w-3 h-3 text-red-500" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
                
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="w-full mt-4"
                  onClick={() => setItemDialog({ open: true, checklistId: checklist.id, data: null })}
                  data-testid={`add-item-${checklist.id}`}
                >
                  <Plus className="w-3 h-3 mr-1" /> Add Item
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Checklist Dialog */}
      <ChecklistDialog
        open={checklistDialog.open}
        data={checklistDialog.data}
        projects={projects}
        selectedProjectId={selectedProjectId}
        onClose={() => setChecklistDialog({ open: false, data: null })}
        onSave={handleSaveChecklist}
      />

      {/* Item Dialog */}
      <ItemDialog
        open={itemDialog.open}
        data={itemDialog.data}
        onClose={() => setItemDialog({ open: false, checklistId: null, data: null })}
        onSave={handleSaveItem}
      />
    </div>
  );
};

// Checklist Dialog
const ChecklistDialog = ({ open, data, projects, selectedProjectId, onClose, onSave }) => {
  const [form, setForm] = useState({
    project_id: '',
    name: '',
    description: ''
  });

  useEffect(() => {
    if (data) {
      setForm({
        project_id: data.project_id,
        name: data.name,
        description: data.description || ''
      });
    } else {
      setForm({
        project_id: selectedProjectId !== 'all' ? selectedProjectId : '',
        name: '',
        description: ''
      });
    }
  }, [data, selectedProjectId, open]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!form.project_id || !form.name) {
      toast.error('Please fill all required fields');
      return;
    }
    onSave(form);
  };

  return (
    <Dialog open={open} onOpenChange={(o) => !o && onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{data ? 'Edit Checklist' : 'New Checklist'}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label>Project *</Label>
            <Select value={form.project_id} onValueChange={(v) => setForm({ ...form, project_id: v })} disabled={!!data}>
              <SelectTrigger>
                <SelectValue placeholder="Select project" />
              </SelectTrigger>
              <SelectContent>
                {projects.map(p => (
                  <SelectItem key={p.id} value={p.id}>{p.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Name *</Label>
            <Input 
              value={form.name} 
              onChange={(e) => setForm({ ...form, name: e.target.value })} 
              placeholder="e.g., Daily Farm Tasks, Harvest Checklist"
            />
          </div>
          <div className="space-y-2">
            <Label>Description</Label>
            <Textarea 
              value={form.description} 
              onChange={(e) => setForm({ ...form, description: e.target.value })} 
              placeholder="Optional description..."
              rows={2}
            />
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>Cancel</Button>
            <Button type="submit">{data ? 'Update' : 'Create'}</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

// Item Dialog
const ItemDialog = ({ open, data, onClose, onSave }) => {
  const [text, setText] = useState('');

  useEffect(() => {
    if (data) {
      setText(data.text);
    } else {
      setText('');
    }
  }, [data, open]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!text.trim()) {
      toast.error('Please enter item text');
      return;
    }
    onSave({ text: text.trim() });
  };

  return (
    <Dialog open={open} onOpenChange={(o) => !o && onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{data ? 'Edit Item' : 'Add Item'}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label>Item Text *</Label>
            <Input 
              value={text} 
              onChange={(e) => setText(e.target.value)} 
              placeholder="e.g., Feed chickens, Water garden"
              autoFocus
            />
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>Cancel</Button>
            <Button type="submit">{data ? 'Update' : 'Add'}</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default ChecklistsPage;
