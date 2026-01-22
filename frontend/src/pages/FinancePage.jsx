import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter, DialogClose } from '../components/ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { Badge } from '../components/ui/badge';
import { Textarea } from '../components/ui/textarea';
import { 
  Plus, Trash2, Edit, Wallet, TrendingUp, TrendingDown, 
  PiggyBank, Calculator, Calendar, AlertTriangle, RefreshCw,
  ArrowUpCircle, ArrowDownCircle, Building, Landmark, Coins, Package
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Account type icons
const accountTypeIcons = {
  bank: Landmark,
  cash: Wallet,
  crypto: Coins,
  asset: Package
};

export const FinancePage = () => {
  const { token } = useAuth();
  const [activeTab, setActiveTab] = useState('transactions');
  const [projects, setProjects] = useState([]);
  const [selectedProjectId, setSelectedProjectId] = useState('all');
  const [accounts, setAccounts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [recurringTransactions, setRecurringTransactions] = useState([]);
  const [savingsGoals, setSavingsGoals] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Dashboard state
  const [projectSummary, setProjectSummary] = useState(null);
  const [monthlyOverview, setMonthlyOverview] = useState(null);
  const [runway, setRunway] = useState(null);
  const [selectedMonth, setSelectedMonth] = useState(() => {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
  });

  // Dialog states
  const [accountDialog, setAccountDialog] = useState({ open: false, data: null });
  const [categoryDialog, setCategoryDialog] = useState({ open: false, data: null });
  const [transactionDialog, setTransactionDialog] = useState({ open: false, data: null });
  const [recurringDialog, setRecurringDialog] = useState({ open: false, data: null });
  const [savingsGoalDialog, setSavingsGoalDialog] = useState({ open: false, data: null });

  const headers = { Authorization: `Bearer ${token}` };

  // Fetch projects
  const fetchProjects = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/projects`, { headers });
      setProjects(res.data.projects || []);
    } catch (err) {
      console.error('Failed to fetch projects:', err);
    }
  }, [token]);

  // Fetch accounts
  const fetchAccounts = useCallback(async () => {
    try {
      const url = selectedProjectId === 'all' 
        ? `${API}/finance/accounts`
        : `${API}/finance/accounts?project_id=${selectedProjectId}`;
      const res = await axios.get(url, { headers });
      setAccounts(res.data.accounts || []);
    } catch (err) {
      console.error('Failed to fetch accounts:', err);
    }
  }, [token, selectedProjectId]);

  // Fetch categories
  const fetchCategories = useCallback(async () => {
    try {
      const url = selectedProjectId === 'all'
        ? `${API}/finance/categories`
        : `${API}/finance/categories?project_id=${selectedProjectId}`;
      const res = await axios.get(url, { headers });
      setCategories(res.data.categories || []);
    } catch (err) {
      console.error('Failed to fetch categories:', err);
    }
  }, [token, selectedProjectId]);

  // Fetch transactions
  const fetchTransactions = useCallback(async () => {
    try {
      const url = selectedProjectId === 'all'
        ? `${API}/finance/transactions?limit=100`
        : `${API}/finance/transactions?project_id=${selectedProjectId}&limit=100`;
      const res = await axios.get(url, { headers });
      setTransactions(res.data.transactions || []);
    } catch (err) {
      console.error('Failed to fetch transactions:', err);
    }
  }, [token, selectedProjectId]);

  // Fetch recurring transactions
  const fetchRecurring = useCallback(async () => {
    try {
      const url = selectedProjectId === 'all'
        ? `${API}/finance/recurring`
        : `${API}/finance/recurring?project_id=${selectedProjectId}`;
      const res = await axios.get(url, { headers });
      setRecurringTransactions(res.data.recurring_transactions || []);
    } catch (err) {
      console.error('Failed to fetch recurring:', err);
    }
  }, [token, selectedProjectId]);

  // Fetch savings goals
  const fetchSavingsGoals = useCallback(async () => {
    try {
      const url = selectedProjectId === 'all'
        ? `${API}/finance/savings-goals`
        : `${API}/finance/savings-goals?project_id=${selectedProjectId}`;
      const res = await axios.get(url, { headers });
      setSavingsGoals(res.data.savings_goals || []);
    } catch (err) {
      console.error('Failed to fetch savings goals:', err);
    }
  }, [token, selectedProjectId]);

  // Fetch dashboard data
  const fetchDashboard = useCallback(async () => {
    if (selectedProjectId === 'all') {
      setProjectSummary(null);
    } else {
      try {
        const res = await axios.get(`${API}/finance/dashboard/${selectedProjectId}`, { headers });
        setProjectSummary(res.data);
      } catch (err) {
        console.error('Failed to fetch dashboard:', err);
      }
    }
  }, [token, selectedProjectId]);

  // Fetch monthly overview
  const fetchMonthly = useCallback(async () => {
    try {
      const url = selectedProjectId === 'all'
        ? `${API}/finance/monthly?month=${selectedMonth}`
        : `${API}/finance/monthly?month=${selectedMonth}&project_id=${selectedProjectId}`;
      const res = await axios.get(url, { headers });
      setMonthlyOverview(res.data);
    } catch (err) {
      console.error('Failed to fetch monthly:', err);
    }
  }, [token, selectedMonth, selectedProjectId]);

  // Fetch runway
  const fetchRunway = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/finance/runway`, { headers });
      setRunway(res.data);
    } catch (err) {
      console.error('Failed to fetch runway:', err);
    }
  }, [token]);

  // Initial data load
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await fetchProjects();
      await Promise.all([
        fetchAccounts(),
        fetchCategories(),
        fetchTransactions(),
        fetchRecurring(),
        fetchSavingsGoals(),
        fetchRunway()
      ]);
      setLoading(false);
    };
    loadData();
  }, []);

  // Refresh when project changes
  useEffect(() => {
    fetchAccounts();
    fetchCategories();
    fetchTransactions();
    fetchRecurring();
    fetchSavingsGoals();
    fetchDashboard();
    fetchMonthly();
  }, [selectedProjectId]);

  // Refresh monthly when month changes
  useEffect(() => {
    fetchMonthly();
  }, [selectedMonth]);

  // CRUD handlers
  const handleSaveAccount = async (data) => {
    try {
      if (accountDialog.data?.id) {
        await axios.put(`${API}/finance/accounts/${accountDialog.data.id}`, data, { headers });
        toast.success('Account updated');
      } else {
        await axios.post(`${API}/finance/accounts`, data, { headers });
        toast.success('Account created');
      }
      setAccountDialog({ open: false, data: null });
      fetchAccounts();
      fetchRunway();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to save account');
    }
  };

  const handleDeleteAccount = async (id) => {
    if (!window.confirm('Delete this account?')) return;
    try {
      await axios.delete(`${API}/finance/accounts/${id}`, { headers });
      toast.success('Account deleted');
      fetchAccounts();
      fetchRunway();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to delete account');
    }
  };

  const handleSeedCategories = async (projectId) => {
    try {
      await axios.post(`${API}/finance/categories/seed/${projectId}`, {}, { headers });
      toast.success('Default categories created');
      fetchCategories();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to seed categories');
    }
  };

  const handleSaveTransaction = async (data) => {
    try {
      if (transactionDialog.data?.id) {
        await axios.put(`${API}/finance/transactions/${transactionDialog.data.id}`, data, { headers });
        toast.success('Transaction updated');
      } else {
        await axios.post(`${API}/finance/transactions`, data, { headers });
        toast.success('Transaction created');
      }
      setTransactionDialog({ open: false, data: null });
      fetchTransactions();
      fetchAccounts();
      fetchDashboard();
      fetchMonthly();
      fetchRunway();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to save transaction');
    }
  };

  const handleDeleteTransaction = async (id) => {
    if (!window.confirm('Delete this transaction?')) return;
    try {
      await axios.delete(`${API}/finance/transactions/${id}`, { headers });
      toast.success('Transaction deleted');
      fetchTransactions();
      fetchAccounts();
      fetchDashboard();
      fetchMonthly();
      fetchRunway();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to delete transaction');
    }
  };

  const handleSaveRecurring = async (data) => {
    try {
      if (recurringDialog.data?.id) {
        await axios.put(`${API}/finance/recurring/${recurringDialog.data.id}`, data, { headers });
        toast.success('Recurring transaction updated');
      } else {
        await axios.post(`${API}/finance/recurring`, data, { headers });
        toast.success('Recurring transaction created');
      }
      setRecurringDialog({ open: false, data: null });
      fetchRecurring();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to save recurring transaction');
    }
  };

  const handleDeleteRecurring = async (id) => {
    if (!window.confirm('Delete this recurring transaction?')) return;
    try {
      await axios.delete(`${API}/finance/recurring/${id}`, { headers });
      toast.success('Recurring transaction deleted');
      fetchRecurring();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to delete recurring transaction');
    }
  };

  const handleSaveSavingsGoal = async (data) => {
    try {
      if (savingsGoalDialog.data?.id) {
        await axios.put(`${API}/finance/savings-goals/${savingsGoalDialog.data.id}`, data, { headers });
        toast.success('Savings goal updated');
      } else {
        await axios.post(`${API}/finance/savings-goals`, data, { headers });
        toast.success('Savings goal created');
      }
      setSavingsGoalDialog({ open: false, data: null });
      fetchSavingsGoals();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to save savings goal');
    }
  };

  const handleDeleteSavingsGoal = async (id) => {
    if (!window.confirm('Delete this savings goal? Transactions will be unlinked but not deleted.')) return;
    try {
      await axios.delete(`${API}/finance/savings-goals/${id}`, { headers });
      toast.success('Savings goal deleted');
      fetchSavingsGoals();
      fetchTransactions();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to delete savings goal');
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(amount);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <RefreshCw className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="p-6 md:p-8 lg:p-12 space-y-6" data-testid="finance-page">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Finance</h1>
          <p className="text-muted-foreground">Track income, expenses, and runway</p>
        </div>
        
        <div className="flex items-center gap-2">
          <Label className="text-sm">Project:</Label>
          <Select value={selectedProjectId} onValueChange={setSelectedProjectId}>
            <SelectTrigger className="w-[200px]" data-testid="project-filter">
              <SelectValue placeholder="All Projects" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Projects</SelectItem>
              {projects.map(p => (
                <SelectItem key={p.id} value={p.id}>{p.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
                <TrendingUp className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Balance</p>
                <p className="text-xl font-bold">{formatCurrency(accounts.reduce((s, a) => s + a.balance, 0))}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                <Landmark className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Accounts</p>
                <p className="text-xl font-bold">{accounts.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-orange-100 dark:bg-orange-900/30 rounded-lg">
                <Calculator className="w-5 h-5 text-orange-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Avg Monthly Burn</p>
                <p className="text-xl font-bold">{runway ? formatCurrency(runway.avg_monthly_burn) : '—'}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className={runway?.is_below_threshold ? 'border-red-500' : ''}>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-lg ${runway?.is_below_threshold ? 'bg-red-100 dark:bg-red-900/30' : 'bg-purple-100 dark:bg-purple-900/30'}`}>
                {runway?.is_below_threshold ? (
                  <AlertTriangle className="w-5 h-5 text-red-600" />
                ) : (
                  <PiggyBank className="w-5 h-5 text-purple-600" />
                )}
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Runway</p>
                <p className="text-xl font-bold">{runway ? `${runway.runway_months.toFixed(1)} months` : '—'}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="transactions" data-testid="tab-transactions">Transactions</TabsTrigger>
          <TabsTrigger value="accounts" data-testid="tab-accounts">Accounts</TabsTrigger>
          <TabsTrigger value="savings" data-testid="tab-savings">Savings</TabsTrigger>
          <TabsTrigger value="recurring" data-testid="tab-recurring">Recurring</TabsTrigger>
          <TabsTrigger value="monthly" data-testid="tab-monthly">Monthly</TabsTrigger>
          <TabsTrigger value="runway" data-testid="tab-runway">Runway</TabsTrigger>
        </TabsList>

        {/* Transactions Tab */}
        <TabsContent value="transactions" className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Transactions</h2>
            <Button onClick={() => setTransactionDialog({ open: true, data: null })} data-testid="add-transaction-btn">
              <Plus className="w-4 h-4 mr-2" /> Add Transaction
            </Button>
          </div>
          
          {transactions.length === 0 ? (
            <Card>
              <CardContent className="p-8 text-center text-muted-foreground">
                No transactions yet. Add your first transaction to start tracking.
              </CardContent>
            </Card>
          ) : (
            <Card>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Date</TableHead>
                    <TableHead>Project</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead>Account</TableHead>
                    <TableHead>Notes</TableHead>
                    <TableHead className="text-right">Amount</TableHead>
                    <TableHead></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {transactions.map(tx => (
                    <TableRow key={tx.id}>
                      <TableCell>{tx.date}</TableCell>
                      <TableCell>{tx.project_name}</TableCell>
                      <TableCell>
                        <Badge variant={tx.category_type === 'income' ? 'default' : tx.category_type === 'investment' ? 'secondary' : 'destructive'}>
                          {tx.category_name}
                        </Badge>
                      </TableCell>
                      <TableCell>{tx.account_name}</TableCell>
                      <TableCell className="max-w-[200px] truncate">{tx.notes}</TableCell>
                      <TableCell className={`text-right font-medium ${tx.amount >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {tx.amount >= 0 ? '+' : ''}{formatCurrency(tx.amount)}
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-1">
                          <Button size="icon" variant="ghost" onClick={() => setTransactionDialog({ open: true, data: tx })}>
                            <Edit className="w-4 h-4" />
                          </Button>
                          <Button size="icon" variant="ghost" onClick={() => handleDeleteTransaction(tx.id)}>
                            <Trash2 className="w-4 h-4 text-red-500" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Card>
          )}
        </TabsContent>

        {/* Accounts Tab */}
        <TabsContent value="accounts" className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Accounts</h2>
            <Button onClick={() => setAccountDialog({ open: true, data: null })} data-testid="add-account-btn">
              <Plus className="w-4 h-4 mr-2" /> Add Account
            </Button>
          </div>
          
          {accounts.length === 0 ? (
            <Card>
              <CardContent className="p-8 text-center text-muted-foreground">
                No accounts yet. Create an account to start tracking your finances.
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {accounts.map(acc => {
                const Icon = accountTypeIcons[acc.type] || Wallet;
                return (
                  <Card key={acc.id}>
                    <CardHeader className="pb-2">
                      <div className="flex justify-between items-start">
                        <div className="flex items-center gap-2">
                          <Icon className="w-5 h-5 text-muted-foreground" />
                          <CardTitle className="text-lg">{acc.name}</CardTitle>
                        </div>
                        <div className="flex gap-1">
                          <Button size="icon" variant="ghost" onClick={() => setAccountDialog({ open: true, data: acc })}>
                            <Edit className="w-4 h-4" />
                          </Button>
                          <Button size="icon" variant="ghost" onClick={() => handleDeleteAccount(acc.id)}>
                            <Trash2 className="w-4 h-4 text-red-500" />
                          </Button>
                        </div>
                      </div>
                      <CardDescription>{acc.type}</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <p className={`text-2xl font-bold ${acc.balance >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {formatCurrency(acc.balance)}
                      </p>
                      {acc.notes && <p className="text-sm text-muted-foreground mt-2">{acc.notes}</p>}
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          )}

          {/* Categories Section */}
          <div className="mt-8">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Categories</h2>
              {selectedProjectId !== 'all' && categories.filter(c => c.project_id === selectedProjectId).length === 0 && (
                <Button variant="outline" onClick={() => handleSeedCategories(selectedProjectId)}>
                  Seed Default Categories
                </Button>
              )}
            </div>
            
            <div className="flex flex-wrap gap-2">
              {categories.map(cat => (
                <Badge 
                  key={cat.id} 
                  variant={cat.type === 'income' ? 'default' : cat.type === 'investment' ? 'secondary' : 'destructive'}
                >
                  {cat.name}
                </Badge>
              ))}
              {categories.length === 0 && (
                <p className="text-muted-foreground">No categories. Select a project and seed default categories.</p>
              )}
            </div>
          </div>
        </TabsContent>

        {/* Recurring Tab */}
        <TabsContent value="recurring" className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Recurring Transactions</h2>
            <Button onClick={() => setRecurringDialog({ open: true, data: null })} data-testid="add-recurring-btn">
              <Plus className="w-4 h-4 mr-2" /> Add Recurring
            </Button>
          </div>
          
          {recurringTransactions.length === 0 ? (
            <Card>
              <CardContent className="p-8 text-center text-muted-foreground">
                No recurring transactions. Add monthly bills or regular income here.
              </CardContent>
            </Card>
          ) : (
            <Card>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Project</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead>Frequency</TableHead>
                    <TableHead>Next Date</TableHead>
                    <TableHead className="text-right">Amount</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {recurringTransactions.map(rec => (
                    <TableRow key={rec.id}>
                      <TableCell className="font-medium">{rec.name}</TableCell>
                      <TableCell>{rec.project_name}</TableCell>
                      <TableCell>{rec.category_name}</TableCell>
                      <TableCell className="capitalize">{rec.frequency}</TableCell>
                      <TableCell>{rec.next_execution_date}</TableCell>
                      <TableCell className={`text-right font-medium ${rec.amount >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {rec.amount >= 0 ? '+' : ''}{formatCurrency(rec.amount)}
                      </TableCell>
                      <TableCell>
                        <Badge variant={rec.active ? 'default' : 'secondary'}>
                          {rec.active ? 'Active' : 'Paused'}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-1">
                          <Button size="icon" variant="ghost" onClick={() => setRecurringDialog({ open: true, data: rec })}>
                            <Edit className="w-4 h-4" />
                          </Button>
                          <Button size="icon" variant="ghost" onClick={() => handleDeleteRecurring(rec.id)}>
                            <Trash2 className="w-4 h-4 text-red-500" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Card>
          )}
        </TabsContent>

        {/* Monthly Overview Tab */}
        <TabsContent value="monthly" className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Monthly Overview</h2>
            <Input 
              type="month" 
              value={selectedMonth} 
              onChange={(e) => setSelectedMonth(e.target.value)}
              className="w-[180px]"
              data-testid="month-picker"
            />
          </div>
          
          {monthlyOverview ? (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center gap-2">
                      <ArrowUpCircle className="w-5 h-5 text-green-500" />
                      <div>
                        <p className="text-sm text-muted-foreground">Income</p>
                        <p className="text-xl font-bold text-green-600">{formatCurrency(monthlyOverview.total_income)}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center gap-2">
                      <ArrowDownCircle className="w-5 h-5 text-red-500" />
                      <div>
                        <p className="text-sm text-muted-foreground">Expenses</p>
                        <p className="text-xl font-bold text-red-600">{formatCurrency(monthlyOverview.total_expenses)}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center gap-2">
                      <Building className="w-5 h-5 text-blue-500" />
                      <div>
                        <p className="text-sm text-muted-foreground">Investments</p>
                        <p className="text-xl font-bold text-blue-600">{formatCurrency(monthlyOverview.total_investments)}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                <Card className={monthlyOverview.net_result >= 0 ? 'border-green-500' : 'border-red-500'}>
                  <CardContent className="p-4">
                    <div className="flex items-center gap-2">
                      <TrendingUp className={`w-5 h-5 ${monthlyOverview.net_result >= 0 ? 'text-green-500' : 'text-red-500'}`} />
                      <div>
                        <p className="text-sm text-muted-foreground">Net Result</p>
                        <p className={`text-xl font-bold ${monthlyOverview.net_result >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {formatCurrency(monthlyOverview.net_result)}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card>
                  <CardHeader>
                    <CardTitle>By Project</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {monthlyOverview.by_project.length === 0 ? (
                      <p className="text-muted-foreground">No transactions this month</p>
                    ) : (
                      <div className="space-y-2">
                        {monthlyOverview.by_project.map((p, i) => (
                          <div key={i} className="flex justify-between items-center">
                            <span>{p.name}</span>
                            <div className="text-sm">
                              <span className="text-green-600">+{formatCurrency(p.income)}</span>
                              {' / '}
                              <span className="text-red-600">-{formatCurrency(p.expenses)}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>By Category</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {monthlyOverview.by_category.length === 0 ? (
                      <p className="text-muted-foreground">No transactions this month</p>
                    ) : (
                      <div className="space-y-2">
                        {monthlyOverview.by_category.map((c, i) => (
                          <div key={i} className="flex justify-between items-center">
                            <Badge variant={c.type === 'income' ? 'default' : c.type === 'investment' ? 'secondary' : 'destructive'}>
                              {c.name}
                            </Badge>
                            <span className={c.type === 'income' ? 'text-green-600' : 'text-red-600'}>
                              {formatCurrency(c.total)}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            </div>
          ) : (
            <Card>
              <CardContent className="p-8 text-center text-muted-foreground">
                Loading monthly overview...
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Runway Tab */}
        <TabsContent value="runway" className="space-y-4">
          <h2 className="text-xl font-semibold">Financial Runway</h2>
          
          {runway ? (
            <div className="space-y-4">
              <Card className={runway.is_below_threshold ? 'border-red-500 bg-red-50 dark:bg-red-900/10' : ''}>
                <CardContent className="p-6">
                  {runway.is_below_threshold && (
                    <div className="flex items-center gap-2 text-red-600 mb-4">
                      <AlertTriangle className="w-5 h-5" />
                      <span className="font-medium">Warning: Cash is below safety threshold!</span>
                    </div>
                  )}
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="text-center">
                      <p className="text-sm text-muted-foreground">Liquid Cash</p>
                      <p className="text-3xl font-bold text-green-600">{formatCurrency(runway.total_liquid_cash)}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-sm text-muted-foreground">Avg Monthly Burn</p>
                      <p className="text-3xl font-bold text-orange-600">{formatCurrency(runway.avg_monthly_burn)}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-sm text-muted-foreground">Runway</p>
                      <p className={`text-3xl font-bold ${runway.runway_months < 3 ? 'text-red-600' : runway.runway_months < 6 ? 'text-orange-600' : 'text-green-600'}`}>
                        {runway.runway_months.toFixed(1)} months
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Accounts Included</CardTitle>
                  <CardDescription>Bank and cash accounts used for runway calculation</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {runway.accounts_included.map((acc, i) => (
                      <div key={i} className="flex justify-between items-center p-2 bg-muted rounded-lg">
                        <div className="flex items-center gap-2">
                          {acc.type === 'bank' ? <Landmark className="w-4 h-4" /> : <Wallet className="w-4 h-4" />}
                          <span>{acc.name}</span>
                          <Badge variant="outline">{acc.type}</Badge>
                        </div>
                        <span className={`font-medium ${acc.balance >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {formatCurrency(acc.balance)}
                        </span>
                      </div>
                    ))}
                    {runway.accounts_included.length === 0 && (
                      <p className="text-muted-foreground">No liquid accounts found. Create bank or cash accounts to calculate runway.</p>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : (
            <Card>
              <CardContent className="p-8 text-center text-muted-foreground">
                Loading runway calculation...
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Savings Goals Tab */}
        <TabsContent value="savings" className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Savings Goals</h2>
            <Button onClick={() => setSavingsGoalDialog({ open: true, data: null })} data-testid="add-savings-goal-btn">
              <Plus className="w-4 h-4 mr-2" /> Add Savings Goal
            </Button>
          </div>
          
          {savingsGoals.length === 0 ? (
            <Card>
              <CardContent className="p-8 text-center text-muted-foreground">
                No savings goals yet. Create a goal and attach transactions to track your progress.
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {savingsGoals.map(goal => (
                <Card key={goal.id}>
                  <CardHeader className="pb-2">
                    <div className="flex justify-between items-start">
                      <div className="flex items-center gap-2">
                        <PiggyBank className="w-5 h-5 text-primary" />
                        <CardTitle className="text-lg">{goal.name}</CardTitle>
                      </div>
                      <div className="flex gap-1">
                        <Button size="icon" variant="ghost" onClick={() => setSavingsGoalDialog({ open: true, data: goal })}>
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button size="icon" variant="ghost" onClick={() => handleDeleteSavingsGoal(goal.id)}>
                          <Trash2 className="w-4 h-4 text-red-500" />
                        </Button>
                      </div>
                    </div>
                    <CardDescription>{goal.project_name}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Progress</span>
                        <span className="font-medium">{goal.progress_percent}%</span>
                      </div>
                      <div className="w-full bg-muted rounded-full h-3">
                        <div 
                          className={`h-3 rounded-full transition-all ${goal.progress_percent >= 100 ? 'bg-green-500' : 'bg-primary'}`}
                          style={{ width: `${Math.min(goal.progress_percent, 100)}%` }}
                        />
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-muted-foreground">Saved</span>
                        <span className="font-medium text-green-600">{formatCurrency(goal.current_amount)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-muted-foreground">Target</span>
                        <span className="font-medium">{formatCurrency(goal.target_amount)}</span>
                      </div>
                      <div className="flex justify-between border-t pt-2">
                        <span className="text-sm text-muted-foreground">Remaining</span>
                        <span className={`font-medium ${goal.target_amount - goal.current_amount <= 0 ? 'text-green-600' : 'text-orange-600'}`}>
                          {formatCurrency(Math.max(0, goal.target_amount - goal.current_amount))}
                        </span>
                      </div>
                      {goal.description && (
                        <p className="text-sm text-muted-foreground mt-2 border-t pt-2">{goal.description}</p>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Account Dialog */}
      <AccountDialog 
        open={accountDialog.open}
        data={accountDialog.data}
        projects={projects}
        selectedProjectId={selectedProjectId}
        onClose={() => setAccountDialog({ open: false, data: null })}
        onSave={handleSaveAccount}
      />

      {/* Transaction Dialog */}
      <TransactionDialog
        open={transactionDialog.open}
        data={transactionDialog.data}
        projects={projects}
        accounts={accounts}
        categories={categories}
        savingsGoals={savingsGoals}
        selectedProjectId={selectedProjectId}
        onClose={() => setTransactionDialog({ open: false, data: null })}
        onSave={handleSaveTransaction}
      />

      {/* Recurring Dialog */}
      <RecurringDialog
        open={recurringDialog.open}
        data={recurringDialog.data}
        projects={projects}
        accounts={accounts}
        categories={categories}
        selectedProjectId={selectedProjectId}
        onClose={() => setRecurringDialog({ open: false, data: null })}
        onSave={handleSaveRecurring}
      />

      {/* Savings Goal Dialog */}
      <SavingsGoalDialog
        open={savingsGoalDialog.open}
        data={savingsGoalDialog.data}
        projects={projects}
        selectedProjectId={selectedProjectId}
        onClose={() => setSavingsGoalDialog({ open: false, data: null })}
        onSave={handleSaveSavingsGoal}
      />
    </div>
  );
};

// Account Dialog Component
const AccountDialog = ({ open, data, projects, selectedProjectId, onClose, onSave }) => {
  const [form, setForm] = useState({
    project_id: '',
    name: '',
    type: 'bank',
    notes: ''
  });

  useEffect(() => {
    if (data) {
      setForm({
        project_id: data.project_id,
        name: data.name,
        type: data.type,
        notes: data.notes || ''
      });
    } else {
      setForm({
        project_id: selectedProjectId !== 'all' ? selectedProjectId : '',
        name: '',
        type: 'bank',
        notes: ''
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
          <DialogTitle>{data ? 'Edit Account' : 'New Account'}</DialogTitle>
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
            <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="e.g., Main Bank Account" />
          </div>
          <div className="space-y-2">
            <Label>Type *</Label>
            <Select value={form.type} onValueChange={(v) => setForm({ ...form, type: v })}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="bank">Bank</SelectItem>
                <SelectItem value="cash">Cash</SelectItem>
                <SelectItem value="crypto">Crypto</SelectItem>
                <SelectItem value="asset">Asset</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Notes</Label>
            <Textarea value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} placeholder="Optional notes..." />
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

// Transaction Dialog Component
const TransactionDialog = ({ open, data, projects, accounts, categories, savingsGoals, selectedProjectId, onClose, onSave }) => {
  const [form, setForm] = useState({
    date: '',
    amount: '',
    account_id: '',
    project_id: '',
    category_id: '',
    savings_goal_id: '',
    notes: ''
  });
  const [isExpense, setIsExpense] = useState(true);

  useEffect(() => {
    if (data) {
      setForm({
        date: data.date,
        amount: Math.abs(data.amount).toString(),
        account_id: data.account_id,
        project_id: data.project_id,
        category_id: data.category_id,
        savings_goal_id: data.savings_goal_id || '',
        notes: data.notes || ''
      });
      setIsExpense(data.amount < 0);
    } else {
      const today = new Date().toISOString().split('T')[0];
      setForm({
        date: today,
        amount: '',
        account_id: accounts[0]?.id || '',
        project_id: selectedProjectId !== 'all' ? selectedProjectId : '',
        category_id: '',
        savings_goal_id: '',
        notes: ''
      });
      setIsExpense(true);
    }
  }, [data, selectedProjectId, accounts, open]);

  // Filter categories by selected project
  const projectCategories = categories.filter(c => c.project_id === form.project_id);
  // Filter savings goals by selected project
  const projectSavingsGoals = savingsGoals?.filter(g => g.project_id === form.project_id) || [];

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!form.project_id || !form.account_id || !form.category_id || !form.amount || !form.date) {
      toast.error('Please fill all required fields');
      return;
    }
    const amount = parseFloat(form.amount);
    onSave({
      ...form,
      savings_goal_id: form.savings_goal_id || null,
      amount: isExpense ? -Math.abs(amount) : Math.abs(amount)
    });
  };

  return (
    <Dialog open={open} onOpenChange={(o) => !o && onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{data ? 'Edit Transaction' : 'New Transaction'}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="flex gap-2">
            <Button type="button" variant={!isExpense ? 'default' : 'outline'} className="flex-1" onClick={() => setIsExpense(false)}>
              <ArrowUpCircle className="w-4 h-4 mr-2" /> Income
            </Button>
            <Button type="button" variant={isExpense ? 'destructive' : 'outline'} className="flex-1" onClick={() => setIsExpense(true)}>
              <ArrowDownCircle className="w-4 h-4 mr-2" /> Expense
            </Button>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Date *</Label>
              <Input type="date" value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} />
            </div>
            <div className="space-y-2">
              <Label>Amount (EUR) *</Label>
              <Input type="number" step="0.01" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} placeholder="0.00" />
            </div>
          </div>
          <div className="space-y-2">
            <Label>Project *</Label>
            <Select value={form.project_id} onValueChange={(v) => setForm({ ...form, project_id: v, category_id: '' })}>
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
            <Label>Account *</Label>
            <Select value={form.account_id} onValueChange={(v) => setForm({ ...form, account_id: v })}>
              <SelectTrigger>
                <SelectValue placeholder="Select account" />
              </SelectTrigger>
              <SelectContent>
                {accounts.map(a => (
                  <SelectItem key={a.id} value={a.id}>{a.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Category *</Label>
            <Select value={form.category_id} onValueChange={(v) => setForm({ ...form, category_id: v })} disabled={!form.project_id}>
              <SelectTrigger>
                <SelectValue placeholder={form.project_id ? "Select category" : "Select project first"} />
              </SelectTrigger>
              <SelectContent>
                {projectCategories.map(c => (
                  <SelectItem key={c.id} value={c.id}>{c.name} ({c.type})</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Savings Goal (Optional)</Label>
            <Select value={form.savings_goal_id} onValueChange={(v) => setForm({ ...form, savings_goal_id: v })} disabled={!form.project_id}>
              <SelectTrigger>
                <SelectValue placeholder="Attach to savings goal..." />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">None</SelectItem>
                {projectSavingsGoals.map(g => (
                  <SelectItem key={g.id} value={g.id}>{g.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Notes</Label>
            <Textarea value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} placeholder="Optional notes..." />
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

// Recurring Transaction Dialog Component
const RecurringDialog = ({ open, data, projects, accounts, categories, selectedProjectId, onClose, onSave }) => {
  const [form, setForm] = useState({
    name: '',
    amount: '',
    frequency: 'monthly',
    start_date: '',
    account_id: '',
    project_id: '',
    category_id: '',
    active: true
  });
  const [isExpense, setIsExpense] = useState(true);

  useEffect(() => {
    if (data) {
      setForm({
        name: data.name,
        amount: Math.abs(data.amount).toString(),
        frequency: data.frequency,
        start_date: data.start_date,
        account_id: data.account_id,
        project_id: data.project_id,
        category_id: data.category_id,
        active: data.active
      });
      setIsExpense(data.amount < 0);
    } else {
      const today = new Date().toISOString().split('T')[0];
      setForm({
        name: '',
        amount: '',
        frequency: 'monthly',
        start_date: today,
        account_id: accounts[0]?.id || '',
        project_id: selectedProjectId !== 'all' ? selectedProjectId : '',
        category_id: '',
        active: true
      });
      setIsExpense(true);
    }
  }, [data, selectedProjectId, accounts, open]);

  const projectCategories = categories.filter(c => c.project_id === form.project_id);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!form.name || !form.project_id || !form.account_id || !form.category_id || !form.amount || !form.start_date) {
      toast.error('Please fill all required fields');
      return;
    }
    const amount = parseFloat(form.amount);
    onSave({
      ...form,
      amount: isExpense ? -Math.abs(amount) : Math.abs(amount)
    });
  };

  return (
    <Dialog open={open} onOpenChange={(o) => !o && onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{data ? 'Edit Recurring Transaction' : 'New Recurring Transaction'}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label>Name *</Label>
            <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="e.g., Monthly Rent" />
          </div>
          <div className="flex gap-2">
            <Button type="button" variant={!isExpense ? 'default' : 'outline'} className="flex-1" onClick={() => setIsExpense(false)}>
              <ArrowUpCircle className="w-4 h-4 mr-2" /> Income
            </Button>
            <Button type="button" variant={isExpense ? 'destructive' : 'outline'} className="flex-1" onClick={() => setIsExpense(true)}>
              <ArrowDownCircle className="w-4 h-4 mr-2" /> Expense
            </Button>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Amount (EUR) *</Label>
              <Input type="number" step="0.01" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} placeholder="0.00" />
            </div>
            <div className="space-y-2">
              <Label>Frequency *</Label>
              <Select value={form.frequency} onValueChange={(v) => setForm({ ...form, frequency: v })}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="monthly">Monthly</SelectItem>
                  <SelectItem value="yearly">Yearly</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="space-y-2">
            <Label>Start Date *</Label>
            <Input type="date" value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })} />
          </div>
          <div className="space-y-2">
            <Label>Project *</Label>
            <Select value={form.project_id} onValueChange={(v) => setForm({ ...form, project_id: v, category_id: '' })}>
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
            <Label>Account *</Label>
            <Select value={form.account_id} onValueChange={(v) => setForm({ ...form, account_id: v })}>
              <SelectTrigger>
                <SelectValue placeholder="Select account" />
              </SelectTrigger>
              <SelectContent>
                {accounts.map(a => (
                  <SelectItem key={a.id} value={a.id}>{a.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Category *</Label>
            <Select value={form.category_id} onValueChange={(v) => setForm({ ...form, category_id: v })} disabled={!form.project_id}>
              <SelectTrigger>
                <SelectValue placeholder={form.project_id ? "Select category" : "Select project first"} />
              </SelectTrigger>
              <SelectContent>
                {projectCategories.map(c => (
                  <SelectItem key={c.id} value={c.id}>{c.name} ({c.type})</SelectItem>
                ))}
              </SelectContent>
            </Select>
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

// Savings Goal Dialog Component
const SavingsGoalDialog = ({ open, data, projects, selectedProjectId, onClose, onSave }) => {
  const [form, setForm] = useState({
    project_id: '',
    name: '',
    description: '',
    target_amount: ''
  });

  useEffect(() => {
    if (data) {
      setForm({
        project_id: data.project_id,
        name: data.name,
        description: data.description || '',
        target_amount: data.target_amount.toString()
      });
    } else {
      setForm({
        project_id: selectedProjectId !== 'all' ? selectedProjectId : '',
        name: '',
        description: '',
        target_amount: ''
      });
    }
  }, [data, selectedProjectId, open]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!form.project_id || !form.name || !form.target_amount) {
      toast.error('Please fill all required fields');
      return;
    }
    onSave({
      ...form,
      target_amount: parseFloat(form.target_amount)
    });
  };

  return (
    <Dialog open={open} onOpenChange={(o) => !o && onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{data ? 'Edit Savings Goal' : 'New Savings Goal'}</DialogTitle>
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
              placeholder="e.g., New Tractor, Solar Panels" 
            />
          </div>
          <div className="space-y-2">
            <Label>Target Amount (EUR) *</Label>
            <Input 
              type="number" 
              step="0.01" 
              value={form.target_amount} 
              onChange={(e) => setForm({ ...form, target_amount: e.target.value })} 
              placeholder="0.00" 
            />
          </div>
          <div className="space-y-2">
            <Label>Description</Label>
            <Textarea 
              value={form.description} 
              onChange={(e) => setForm({ ...form, description: e.target.value })} 
              placeholder="Optional description (max 2000 characters)..."
              maxLength={2000}
            />
            <p className="text-xs text-muted-foreground">{form.description.length}/2000 characters</p>
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

export default FinancePage;
