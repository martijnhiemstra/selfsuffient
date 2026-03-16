import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Switch } from '../components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Badge } from '../components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../components/ui/table';
import {
  Shield,
  Mail,
  Send,
  Users,
  Plus,
  Trash2,
  User,
  Loader2,
  Settings
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Email Configuration Tab Content
const EmailConfigTab = ({ token, userEmail }) => {
  const [sendingTestEmail, setSendingTestEmail] = useState(false);
  const headers = { Authorization: `Bearer ${token}` };

  const handleSendTestEmail = async () => {
    setSendingTestEmail(true);
    try {
      const response = await axios.post(`${API}/auth/test-email`, {}, { headers });
      toast.success(response.data.message || 'Test email sent successfully!');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to send test email');
    } finally {
      setSendingTestEmail(false);
    }
  };

  return (
    <Card className="border border-border/50">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Settings className="w-5 h-5" />
          Email Configuration
        </CardTitle>
        <CardDescription>Test your SMTP email settings</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-sm text-muted-foreground">
          Send a test email to verify that your SMTP configuration is working correctly.
          The test email will be sent to your email address: <strong>{userEmail}</strong>
        </p>
        <div className="bg-muted/50 rounded-lg p-4 text-sm space-y-2">
          <p className="font-medium text-foreground">SMTP settings are configured via environment variables:</p>
          <ul className="list-disc list-inside text-muted-foreground space-y-1">
            <li>SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD</li>
            <li>SMTP_FROM_EMAIL, SMTP_FROM_NAME</li>
            <li>Update these in your server's environment or docker-compose configuration</li>
          </ul>
        </div>
        <Button
          onClick={handleSendTestEmail}
          disabled={sendingTestEmail}
          variant="outline"
          data-testid="send-test-email-button"
        >
          {sendingTestEmail ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Send className="w-4 h-4 mr-2" />}
          Send Test Email
        </Button>
      </CardContent>
    </Card>
  );
};

// User Management Tab Content
const UserManagementTab = ({ token, currentUserId }) => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [creating, setCreating] = useState(false);
  const [deletingId, setDeletingId] = useState(null);
  const [newUser, setNewUser] = useState({ name: '', email: '', password: '', is_admin: false });
  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API}/admin/users`, { headers });
      setUsers(response.data);
    } catch (error) {
      toast.error('Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!newUser.name.trim() || !newUser.email.trim() || !newUser.password.trim()) {
      toast.error('All fields are required');
      return;
    }
    setCreating(true);
    try {
      await axios.post(`${API}/admin/users`, newUser, { headers });
      toast.success('User created!');
      setDialogOpen(false);
      setNewUser({ name: '', email: '', password: '', is_admin: false });
      fetchUsers();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create user');
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (userId) => {
    setDeletingId(userId);
    try {
      await axios.delete(`${API}/admin/users/${userId}`, { headers });
      toast.success('User deleted');
      setUsers(users.filter(u => u.id !== userId));
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to delete user');
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div />
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button className="rounded-full gap-2" data-testid="create-user-button">
              <Plus className="w-4 h-4" />
              New User
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-md">
            <form onSubmit={handleCreate}>
              <DialogHeader>
                <DialogTitle className="font-display">Create New User</DialogTitle>
                <DialogDescription>Add a new user to the system</DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Full Name</Label>
                  <Input id="name" placeholder="John Doe" value={newUser.name} onChange={(e) => setNewUser({ ...newUser, name: e.target.value })} data-testid="new-user-name" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input id="email" type="email" placeholder="user@example.com" value={newUser.email} onChange={(e) => setNewUser({ ...newUser, email: e.target.value })} data-testid="new-user-email" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <Input id="password" type="password" placeholder="Enter password" value={newUser.password} onChange={(e) => setNewUser({ ...newUser, password: e.target.value })} data-testid="new-user-password" />
                </div>
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="admin">Admin Access</Label>
                    <p className="text-sm text-muted-foreground">Can manage users</p>
                  </div>
                  <Switch id="admin" checked={newUser.is_admin} onCheckedChange={(checked) => setNewUser({ ...newUser, is_admin: checked })} data-testid="new-user-admin" />
                </div>
              </div>
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button>
                <Button type="submit" disabled={creating} data-testid="submit-user-button">
                  {creating ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                  Create User
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Card className="border border-border/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="w-5 h-5" />
            Users ({users.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-8 h-8 animate-spin text-primary" />
            </div>
          ) : users.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">No users found</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>User</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead className="w-[80px]">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {users.map((user) => (
                  <TableRow key={user.id} data-testid={`user-row-${user.id}`}>
                    <TableCell>
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                          <User className="w-4 h-4 text-primary" />
                        </div>
                        <span className="font-medium">{user.name}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2 text-muted-foreground">
                        <Mail className="w-4 h-4" />{user.email}
                      </div>
                    </TableCell>
                    <TableCell>
                      {user.is_admin ? (
                        <Badge variant="default" className="gap-1"><Shield className="w-3 h-3" />Admin</Badge>
                      ) : (
                        <Badge variant="secondary">User</Badge>
                      )}
                    </TableCell>
                    <TableCell className="font-mono-data text-sm text-muted-foreground">
                      {new Date(user.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      {user.id !== currentUserId ? (
                        <AlertDialog>
                          <AlertDialogTrigger asChild>
                            <Button variant="ghost" size="icon" className="text-destructive hover:text-destructive" data-testid={`delete-user-${user.id}`}>
                              {deletingId === user.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <Trash2 className="w-4 h-4" />}
                            </Button>
                          </AlertDialogTrigger>
                          <AlertDialogContent>
                            <AlertDialogHeader>
                              <AlertDialogTitle>Delete User?</AlertDialogTitle>
                              <AlertDialogDescription>This will permanently delete {user.name}'s account. This action cannot be undone.</AlertDialogDescription>
                            </AlertDialogHeader>
                            <AlertDialogFooter>
                              <AlertDialogCancel>Cancel</AlertDialogCancel>
                              <AlertDialogAction onClick={() => handleDelete(user.id)} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">Delete User</AlertDialogAction>
                            </AlertDialogFooter>
                          </AlertDialogContent>
                        </AlertDialog>
                      ) : (
                        <span className="text-xs text-muted-foreground">You</span>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

// Main Admin Page
export const AdminPage = () => {
  const { user, token } = useAuth();
  const [activeTab, setActiveTab] = useState('email');
  const [usersTabLoaded, setUsersTabLoaded] = useState(false);

  // Lazy load: only render UserManagementTab when first selected
  useEffect(() => {
    if (activeTab === 'users' && !usersTabLoaded) {
      setUsersTabLoaded(true);
    }
  }, [activeTab, usersTabLoaded]);

  return (
    <div className="p-6 md:p-12 lg:p-16 max-w-4xl" data-testid="admin-page">
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-1">
          <Shield className="w-6 h-6 text-primary" />
          <h1 className="text-3xl font-display font-bold tracking-tight">Admin</h1>
        </div>
        <p className="text-muted-foreground">System administration and user management</p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-2 mb-6" data-testid="admin-tabs">
          <TabsTrigger value="email" data-testid="admin-tab-email">
            <Mail className="w-4 h-4 mr-2" />Email Configuration
          </TabsTrigger>
          <TabsTrigger value="users" data-testid="admin-tab-users">
            <Users className="w-4 h-4 mr-2" />User Management
          </TabsTrigger>
        </TabsList>

        <TabsContent value="email">
          <EmailConfigTab token={token} userEmail={user?.email} />
        </TabsContent>

        <TabsContent value="users">
          {usersTabLoaded ? (
            <UserManagementTab token={token} currentUserId={user?.id} />
          ) : null}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AdminPage;
