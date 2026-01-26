import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Switch } from '../components/ui/switch';
import { Separator } from '../components/ui/separator';
import { 
  User, 
  Lock, 
  Loader2,
  CheckCircle,
  Bell,
  Mail,
  Send,
  Settings,
  Calendar,
  Link,
  Unlink,
  RefreshCw,
  ExternalLink
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const SettingsPage = () => {
  const { user, token, refreshUser } = useAuth();
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [changing, setChanging] = useState(false);
  const [savingReminders, setSavingReminders] = useState(false);
  const [sendingTestEmail, setSendingTestEmail] = useState(false);
  const [dailyReminders, setDailyReminders] = useState(user?.daily_reminders || false);
  
  // Google Calendar state
  const [googleCalendarStatus, setGoogleCalendarStatus] = useState(null);
  const [googleClientId, setGoogleClientId] = useState('');
  const [googleClientSecret, setGoogleClientSecret] = useState('');
  const [syncTasks, setSyncTasks] = useState(true);
  const [syncRoutines, setSyncRoutines] = useState(true);
  const [syncEvents, setSyncEvents] = useState(true);
  const [savingGoogleSettings, setSavingGoogleSettings] = useState(false);
  const [connectingGoogle, setConnectingGoogle] = useState(false);
  const [syncingTasks, setSyncingTasks] = useState(false);
  const [syncingRoutines, setSyncingRoutines] = useState(false);

  const headers = { Authorization: `Bearer ${token}` };

  // Check for Google OAuth callback result
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('google_connected') === 'true') {
      toast.success('Google Calendar connected successfully!');
      // Clean URL
      window.history.replaceState({}, '', window.location.pathname);
      fetchGoogleCalendarStatus();
    } else if (params.get('google_error')) {
      toast.error('Failed to connect Google Calendar. Please try again.');
      window.history.replaceState({}, '', window.location.pathname);
    }
  }, []);

  // Fetch Google Calendar status on mount
  useEffect(() => {
    fetchGoogleCalendarStatus();
  }, [token]);

  const fetchGoogleCalendarStatus = async () => {
    try {
      const res = await axios.get(`${API}/google-calendar/status`, { headers });
      setGoogleCalendarStatus(res.data);
      setSyncTasks(res.data.sync_tasks);
      setSyncRoutines(res.data.sync_routines);
      setSyncEvents(res.data.sync_events);
    } catch (err) {
      console.error('Failed to fetch Google Calendar status:', err);
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();

    if (newPassword !== confirmPassword) {
      toast.error('New passwords do not match');
      return;
    }

    if (newPassword.length < 6) {
      toast.error('Password must be at least 6 characters');
      return;
    }

    setChanging(true);
    try {
      await axios.post(`${API}/auth/change-password`, {
        current_password: currentPassword,
        new_password: newPassword
      }, { headers: { Authorization: `Bearer ${token}` } });
      toast.success('Password changed successfully!');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to change password');
    } finally {
      setChanging(false);
    }
  };

  const handleToggleDailyReminders = async (checked) => {
    setSavingReminders(true);
    try {
      await axios.put(`${API}/auth/settings`, {
        daily_reminders: checked
      }, { headers: { Authorization: `Bearer ${token}` } });
      setDailyReminders(checked);
      if (refreshUser) {
        await refreshUser();
      }
      toast.success(checked ? 'Daily reminders enabled!' : 'Daily reminders disabled');
    } catch (error) {
      toast.error('Failed to update settings');
      setDailyReminders(!checked); // Revert on error
    } finally {
      setSavingReminders(false);
    }
  };

  const handleSendTestEmail = async () => {
    setSendingTestEmail(true);
    try {
      const response = await axios.post(`${API}/auth/test-email`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success(response.data.message || 'Test email sent successfully!');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to send test email');
    } finally {
      setSendingTestEmail(false);
    }
  };

  const handleSaveGoogleSettings = async () => {
    if (!googleClientId || !googleClientSecret) {
      toast.error('Please enter both Client ID and Client Secret');
      return;
    }
    
    setSavingGoogleSettings(true);
    try {
      await axios.post(`${API}/google-calendar/settings`, {
        client_id: googleClientId,
        client_secret: googleClientSecret,
        sync_tasks: syncTasks,
        sync_routines: syncRoutines,
        sync_events: syncEvents
      }, { headers });
      toast.success('Google Calendar settings saved');
      setGoogleClientId('');
      setGoogleClientSecret('');
      fetchGoogleCalendarStatus();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to save settings');
    } finally {
      setSavingGoogleSettings(false);
    }
  };

  const handleUpdateSyncSettings = async () => {
    if (!googleCalendarStatus?.has_credentials) {
      toast.error('Please save your credentials first');
      return;
    }
    
    setSavingGoogleSettings(true);
    try {
      // We need to send the existing credentials with updated sync settings
      await axios.post(`${API}/google-calendar/settings`, {
        client_id: googleCalendarStatus.client_id || 'unchanged',
        client_secret: googleCalendarStatus.client_secret || 'unchanged',
        sync_tasks: syncTasks,
        sync_routines: syncRoutines,
        sync_events: syncEvents
      }, { headers });
      toast.success('Sync settings updated');
      fetchGoogleCalendarStatus();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to update settings');
    } finally {
      setSavingGoogleSettings(false);
    }
  };

  const handleConnectGoogle = async () => {
    setConnectingGoogle(true);
    try {
      const res = await axios.get(`${API}/google-calendar/connect`, { headers });
      // Redirect to Google OAuth
      window.location.href = res.data.authorization_url;
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to start Google connection');
      setConnectingGoogle(false);
    }
  };

  const handleDisconnectGoogle = async () => {
    if (!window.confirm('Disconnect Google Calendar? Tasks will no longer sync.')) return;
    
    try {
      await axios.post(`${API}/google-calendar/disconnect`, {}, { headers });
      toast.success('Google Calendar disconnected');
      fetchGoogleCalendarStatus();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to disconnect');
    }
  };

  const handleSyncTasks = async () => {
    setSyncingTasks(true);
    try {
      const res = await axios.post(`${API}/google-calendar/sync-all-tasks`, {}, { headers });
      toast.success(res.data.message);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to sync tasks');
    } finally {
      setSyncingTasks(false);
    }
  };

  const handleSyncRoutines = async () => {
    setSyncingRoutines(true);
    try {
      const res = await axios.post(`${API}/google-calendar/sync-all-routines`, {}, { headers });
      toast.success(res.data.message);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to sync routines');
    } finally {
      setSyncingRoutines(false);
    }
  };

  return (
    <div className="p-6 md:p-12 lg:p-16 max-w-3xl" data-testid="settings-page">
      <div className="mb-8">
        <h1 className="text-3xl font-display font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground mt-1">
          Manage your account settings
        </p>
      </div>

      {/* Profile Info */}
      <Card className="border border-border/50 mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="w-5 h-5" />
            Profile Information
          </CardTitle>
          <CardDescription>Your account details</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label className="text-muted-foreground text-sm">Name</Label>
              <p className="font-medium">{user?.name}</p>
            </div>
            <div>
              <Label className="text-muted-foreground text-sm">Email</Label>
              <p className="font-medium">{user?.email}</p>
            </div>
            <div>
              <Label className="text-muted-foreground text-sm">Role</Label>
              <p className="font-medium">{user?.is_admin ? 'Administrator' : 'User'}</p>
            </div>
            <div>
              <Label className="text-muted-foreground text-sm">Member Since</Label>
              <p className="font-medium font-mono-data">
                {user?.created_at ? new Date(user.created_at).toLocaleDateString() : '-'}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Notifications */}
      <Card className="border border-border/50 mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="w-5 h-5" />
            Notifications
          </CardTitle>
          <CardDescription>Configure how you want to be notified</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <Mail className="w-4 h-4 text-muted-foreground" />
                <Label htmlFor="daily-reminders" className="font-medium">Daily Reminders</Label>
              </div>
              <p className="text-sm text-muted-foreground">
                Receive a daily email each morning with your Start of Day items, daily tasks, and End of Day items
              </p>
            </div>
            <Switch
              id="daily-reminders"
              checked={dailyReminders}
              onCheckedChange={handleToggleDailyReminders}
              disabled={savingReminders}
              data-testid="daily-reminders-switch"
            />
          </div>
          {dailyReminders && (
            <div className="bg-muted/50 p-4 rounded-lg text-sm text-muted-foreground">
              <p className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-primary" />
                You'll receive daily task summaries at your configured email: <strong>{user?.email}</strong>
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Change Password */}
      <Card className="border border-border/50 mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lock className="w-5 h-5" />
            Change Password
          </CardTitle>
          <CardDescription>Update your password to keep your account secure</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleChangePassword} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="currentPassword">Current Password</Label>
              <Input
                id="currentPassword"
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                placeholder="Enter current password"
                required
                data-testid="current-password-input"
              />
            </div>
            <Separator />
            <div className="space-y-2">
              <Label htmlFor="newPassword">New Password</Label>
              <Input
                id="newPassword"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="Enter new password"
                required
                minLength={6}
                data-testid="new-password-input"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Confirm New Password</Label>
              <Input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Confirm new password"
                required
                minLength={6}
                data-testid="confirm-password-input"
              />
            </div>
            <Button type="submit" disabled={changing} data-testid="change-password-button">
              {changing ? (
                <Loader2 className="w-4 h-4 animate-spin mr-2" />
              ) : (
                <CheckCircle className="w-4 h-4 mr-2" />
              )}
              Change Password
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Google Calendar Integration */}
      <Card className="border border-border/50 mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="w-5 h-5" />
            Google Calendar Sync
          </CardTitle>
          <CardDescription>
            Sync your tasks and routines to Google Calendar
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Connection Status */}
          {googleCalendarStatus?.connected ? (
            <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                  <div>
                    <p className="font-medium text-green-800 dark:text-green-200">Connected to Google Calendar</p>
                    {googleCalendarStatus.google_email && (
                      <p className="text-sm text-green-600 dark:text-green-400">{googleCalendarStatus.google_email}</p>
                    )}
                  </div>
                </div>
                <Button variant="outline" size="sm" onClick={handleDisconnectGoogle}>
                  <Unlink className="w-4 h-4 mr-2" />
                  Disconnect
                </Button>
              </div>
            </div>
          ) : googleCalendarStatus?.has_credentials ? (
            <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-yellow-800 dark:text-yellow-200">Credentials saved, not connected</p>
                  <p className="text-sm text-yellow-600 dark:text-yellow-400">Click Connect to authorize access</p>
                </div>
                <Button onClick={handleConnectGoogle} disabled={connectingGoogle}>
                  {connectingGoogle ? (
                    <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  ) : (
                    <Link className="w-4 h-4 mr-2" />
                  )}
                  Connect
                </Button>
              </div>
            </div>
          ) : (
            <div className="bg-muted/50 rounded-lg p-4">
              <p className="text-sm text-muted-foreground">
                Enter your Google Cloud OAuth credentials below to enable calendar sync.
              </p>
            </div>
          )}

          {/* Credentials Form */}
          {!googleCalendarStatus?.connected && (
            <>
              <Separator />
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium">Google Cloud Credentials</h4>
                  <a 
                    href="https://console.cloud.google.com/apis/credentials" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-sm text-primary hover:underline flex items-center gap-1"
                  >
                    Google Cloud Console <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
                <div className="text-sm text-muted-foreground space-y-1">
                  <p>1. Create a new OAuth 2.0 Client ID (Web application)</p>
                  <p>2. Add redirect URI: <code className="bg-muted px-1 rounded">{window.location.origin}/api/google-calendar/callback</code></p>
                  <p>3. Copy the Client ID and Client Secret below</p>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="googleClientId">Client ID</Label>
                  <Input
                    id="googleClientId"
                    value={googleClientId}
                    onChange={(e) => setGoogleClientId(e.target.value)}
                    placeholder="xxxxx.apps.googleusercontent.com"
                    data-testid="google-client-id"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="googleClientSecret">Client Secret</Label>
                  <Input
                    id="googleClientSecret"
                    type="password"
                    value={googleClientSecret}
                    onChange={(e) => setGoogleClientSecret(e.target.value)}
                    placeholder="GOCSPX-xxxxx"
                    data-testid="google-client-secret"
                  />
                </div>
                <Button 
                  onClick={handleSaveGoogleSettings} 
                  disabled={savingGoogleSettings || !googleClientId || !googleClientSecret}
                >
                  {savingGoogleSettings ? (
                    <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  ) : (
                    <CheckCircle className="w-4 h-4 mr-2" />
                  )}
                  Save Credentials
                </Button>
              </div>
            </>
          )}

          {/* Sync Settings */}
          {googleCalendarStatus?.connected && (
            <>
              <Separator />
              <div className="space-y-4">
                <h4 className="font-medium">Sync Settings</h4>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="sync-tasks">Sync Tasks</Label>
                      <p className="text-sm text-muted-foreground">Tasks with due dates appear in your calendar</p>
                    </div>
                    <Switch
                      id="sync-tasks"
                      checked={syncTasks}
                      onCheckedChange={setSyncTasks}
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="sync-routines">Sync Routines</Label>
                      <p className="text-sm text-muted-foreground">Daily routines appear at their scheduled times</p>
                    </div>
                    <Switch
                      id="sync-routines"
                      checked={syncRoutines}
                      onCheckedChange={setSyncRoutines}
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="sync-events">Sync Calendar Events</Label>
                      <p className="text-sm text-muted-foreground">Custom calendar events (future feature)</p>
                    </div>
                    <Switch
                      id="sync-events"
                      checked={syncEvents}
                      onCheckedChange={setSyncEvents}
                      disabled
                    />
                  </div>
                </div>
              </div>

              <Separator />
              <div className="space-y-4">
                <h4 className="font-medium">Manual Sync</h4>
                <div className="flex gap-2">
                  <Button variant="outline" onClick={handleSyncTasks} disabled={syncingTasks || !syncTasks}>
                    {syncingTasks ? (
                      <Loader2 className="w-4 h-4 animate-spin mr-2" />
                    ) : (
                      <RefreshCw className="w-4 h-4 mr-2" />
                    )}
                    Sync All Tasks
                  </Button>
                  <Button variant="outline" onClick={handleSyncRoutines} disabled={syncingRoutines || !syncRoutines}>
                    {syncingRoutines ? (
                      <Loader2 className="w-4 h-4 animate-spin mr-2" />
                    ) : (
                      <RefreshCw className="w-4 h-4 mr-2" />
                    )}
                    Sync Today's Routines
                  </Button>
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* Admin: Email Configuration Test */}
      {user?.is_admin && (
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
              The test email will be sent to your email address: <strong>{user?.email}</strong>
            </p>
            <Button 
              onClick={handleSendTestEmail} 
              disabled={sendingTestEmail}
              variant="outline"
              data-testid="send-test-email-button"
            >
              {sendingTestEmail ? (
                <Loader2 className="w-4 h-4 animate-spin mr-2" />
              ) : (
                <Send className="w-4 h-4 mr-2" />
              )}
              Send Test Email
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default SettingsPage;
