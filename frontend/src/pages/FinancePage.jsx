import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../components/ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { Badge } from '../components/ui/badge';
import { Textarea } from '../components/ui/textarea';
import { Checkbox } from '../components/ui/checkbox';
import { 
  Plus, Trash2, Edit, Wallet, TrendingUp, 
  PiggyBank, Calculator, AlertTriangle, RefreshCw,
  ArrowUpCircle, ArrowDownCircle, Landmark, Coins, Package,
  CheckCircle2, Circle, CalendarRange, Upload, FileSpreadsheet, X,
  Sparkles, Loader2, CheckCircle
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

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
  const [savingsGoals, setSavingsGoals] = useState([]);
  const [expensePeriods, setExpensePeriods] = useState([]);
  const [budgetComparison, setBudgetComparison] = useState(null);
  const [loading, setLoading] = useState(true);
  
  const [monthlyOverview, setMonthlyOverview] = useState(null);
  const [runway, setRunway] = useState(null);
  const [selectedMonth, setSelectedMonth] = useState(() => {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
  });
  const [budgetMonth, setBudgetMonth] = useState(() => {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
  });

  const [accountDialog, setAccountDialog] = useState({ open: false, data: null });
  const [transactionDialog, setTransactionDialog] = useState({ open: false, data: null });
  const [periodDialog, setPeriodDialog] = useState({ open: false, data: null });
  const [expectedItemDialog, setExpectedItemDialog] = useState({ open: false, data: null, periodId: null });
  const [savingsGoalDialog, setSavingsGoalDialog] = useState({ open: false, data: null });
  const [importDialog, setImportDialog] = useState({ open: false });

  const headers = { Authorization: `Bearer ${token}` };

  const fetchProjects = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/projects`, { headers });
      setProjects(res.data.projects || []);
    } catch (err) {
      console.error('Failed to fetch projects:', err);
    }
  }, [token]);

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

  const fetchExpensePeriods = useCallback(async () => {
    try {
      const url = selectedProjectId === 'all'
        ? `${API}/budget/periods`
        : `${API}/budget/periods?project_id=${selectedProjectId}`;
      const res = await axios.get(url, { headers });
      setExpensePeriods(res.data.periods || []);
    } catch (err) {
      console.error('Failed to fetch expense periods:', err);
    }
  }, [token, selectedProjectId]);

  const fetchBudgetComparison = useCallback(async () => {
    try {
      const url = selectedProjectId === 'all'
        ? `${API}/budget/comparison?month=${budgetMonth}`
        : `${API}/budget/comparison?month=${budgetMonth}&project_id=${selectedProjectId}`;
      const res = await axios.get(url, { headers });
      setBudgetComparison(res.data);
    } catch (err) {
      console.error('Failed to fetch budget comparison:', err);
    }
  }, [token, budgetMonth, selectedProjectId]);

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

  const fetchRunway = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/finance/runway`, { headers });
      setRunway(res.data);
    } catch (err) {
      console.error('Failed to fetch runway:', err);
    }
  }, [token]);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await fetchProjects();
      await Promise.all([
        fetchAccounts(),
        fetchCategories(),
        fetchTransactions(),
        fetchSavingsGoals(),
        fetchExpensePeriods(),
        fetchBudgetComparison(),
        fetchRunway()
      ]);
      setLoading(false);
    };
    loadData();
  }, []);

  useEffect(() => {
    fetchAccounts();
    fetchCategories();
    fetchTransactions();
    fetchSavingsGoals();
    fetchExpensePeriods();
    fetchBudgetComparison();
    fetchMonthly();
  }, [selectedProjectId]);

  useEffect(() => {
    fetchMonthly();
  }, [selectedMonth]);

  useEffect(() => {
    fetchBudgetComparison();
  }, [budgetMonth]);

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
      fetchMonthly();
      fetchRunway();
      fetchBudgetComparison();
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
      fetchMonthly();
      fetchRunway();
      fetchBudgetComparison();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to delete transaction');
    }
  };

  const handleSavePeriod = async (data) => {
    try {
      if (periodDialog.data?.id) {
        await axios.put(`${API}/budget/periods/${periodDialog.data.id}`, data, { headers });
        toast.success('Period updated');
      } else {
        await axios.post(`${API}/budget/periods`, data, { headers });
        toast.success('Period created');
      }
      setPeriodDialog({ open: false, data: null });
      fetchExpensePeriods();
      fetchBudgetComparison();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to save period');
    }
  };

  const handleDeletePeriod = async (id) => {
    if (!window.confirm('Delete this expense period and all its expected items?')) return;
    try {
      await axios.delete(`${API}/budget/periods/${id}`, { headers });
      toast.success('Period deleted');
      fetchExpensePeriods();
      fetchBudgetComparison();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to delete period');
    }
  };

  const handleSaveExpectedItem = async (data) => {
    try {
      if (expectedItemDialog.data?.id) {
        await axios.put(`${API}/budget/items/${expectedItemDialog.data.id}`, data, { headers });
        toast.success('Item updated');
      } else {
        await axios.post(`${API}/budget/items`, data, { headers });
        toast.success('Item created');
      }
      setExpectedItemDialog({ open: false, data: null, periodId: null });
      fetchExpensePeriods();
      fetchBudgetComparison();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to save item');
    }
  };

  const handleDeleteExpectedItem = async (id) => {
    if (!window.confirm('Delete this expected item?')) return;
    try {
      await axios.delete(`${API}/budget/items/${id}`, { headers });
      toast.success('Item deleted');
      fetchExpensePeriods();
      fetchBudgetComparison();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to delete item');
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
        <TabsList className="grid w-full grid-cols-7">
          <TabsTrigger value="transactions" data-testid="tab-transactions">Transactions</TabsTrigger>
          <TabsTrigger value="accounts" data-testid="tab-accounts">Accounts</TabsTrigger>
          <TabsTrigger value="savings" data-testid="tab-savings">Savings</TabsTrigger>
          <TabsTrigger value="budget" data-testid="tab-budget">Budget</TabsTrigger>
          <TabsTrigger value="periods" data-testid="tab-periods">Expense Periods</TabsTrigger>
          <TabsTrigger value="monthly" data-testid="tab-monthly">Monthly</TabsTrigger>
          <TabsTrigger value="runway" data-testid="tab-runway">Runway</TabsTrigger>
        </TabsList>

        {/* Transactions Tab */}
        <TabsContent value="transactions" className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Transactions</h2>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => setImportDialog({ open: true })} data-testid="import-transactions-btn">
                <Upload className="w-4 h-4 mr-2" /> Import
              </Button>
              <Button onClick={() => setTransactionDialog({ open: true, data: null })} data-testid="add-transaction-btn">
                <Plus className="w-4 h-4 mr-2" /> Add Transaction
              </Button>
            </div>
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
                      {acc.starting_balance > 0 && (
                        <p className="text-xs text-muted-foreground mt-1">
                          Starting: {formatCurrency(acc.starting_balance)}
                        </p>
                      )}
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

        {/* Budget Tab */}
        <TabsContent value="budget" className="space-y-6">
          {/* Budget Comparison Section */}
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold">Budget vs Actual</h2>
              <Input 
                type="month" 
                value={budgetMonth} 
                onChange={(e) => setBudgetMonth(e.target.value)}
                className="w-[180px]"
                data-testid="budget-month-picker"
              />
            </div>
            
            {budgetComparison ? (
              <div className="space-y-4">
                {/* Summary Cards */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  <Card className="bg-muted/50">
                    <CardContent className="p-3">
                      <div className="flex items-center gap-2">
                        <ArrowUpCircle className="w-4 h-4 text-green-500" />
                        <span className="text-sm text-muted-foreground">Expected Income</span>
                      </div>
                      <p className="text-xl font-bold text-green-600">{formatCurrency(budgetComparison.expected_income)}</p>
                      <p className="text-xs text-muted-foreground">
                        Actual: {formatCurrency(budgetComparison.actual_income)} 
                        <span className={budgetComparison.income_difference >= 0 ? 'text-green-500' : 'text-red-500'}>
                          {' '}({budgetComparison.income_difference >= 0 ? '+' : ''}{formatCurrency(budgetComparison.income_difference)})
                        </span>
                      </p>
                    </CardContent>
                  </Card>
                  <Card className="bg-muted/50">
                    <CardContent className="p-3">
                      <div className="flex items-center gap-2">
                        <ArrowDownCircle className="w-4 h-4 text-red-500" />
                        <span className="text-sm text-muted-foreground">Expected Expenses</span>
                      </div>
                      <p className="text-xl font-bold text-red-600">{formatCurrency(budgetComparison.expected_expenses)}</p>
                      <p className="text-xs text-muted-foreground">
                        Actual: {formatCurrency(budgetComparison.actual_expenses)}
                        <span className={budgetComparison.expense_difference <= 0 ? 'text-green-500' : 'text-red-500'}>
                          {' '}({budgetComparison.expense_difference >= 0 ? '+' : ''}{formatCurrency(budgetComparison.expense_difference)})
                        </span>
                      </p>
                    </CardContent>
                  </Card>
                  <Card className="bg-muted/50">
                    <CardContent className="p-3">
                      <div className="flex items-center gap-2">
                        <Calculator className="w-4 h-4 text-blue-500" />
                        <span className="text-sm text-muted-foreground">Expected Profit</span>
                      </div>
                      <p className={`text-xl font-bold ${budgetComparison.expected_profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {formatCurrency(budgetComparison.expected_profit)}
                      </p>
                    </CardContent>
                  </Card>
                  <Card className="bg-muted/50">
                    <CardContent className="p-3">
                      <div className="flex items-center gap-2">
                        <TrendingUp className="w-4 h-4 text-purple-500" />
                        <span className="text-sm text-muted-foreground">Actual Profit</span>
                      </div>
                      <p className={`text-xl font-bold ${budgetComparison.actual_profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {formatCurrency(budgetComparison.actual_profit)}
                      </p>
                    </CardContent>
                  </Card>
                </div>

                {/* Budget Items Table */}
                {budgetComparison.items.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Budget Items</CardTitle>
                      <CardDescription>Expected vs actual for {budgetMonth}</CardDescription>
                    </CardHeader>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead className="w-12">Status</TableHead>
                          <TableHead>Item</TableHead>
                          <TableHead>Type</TableHead>
                          <TableHead>Frequency</TableHead>
                          <TableHead className="text-right">Expected</TableHead>
                          <TableHead className="text-right">Actual</TableHead>
                          <TableHead className="text-right">Diff</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {budgetComparison.items.map(item => {
                          // For expenses: actual < expected is GOOD (under budget)
                          // For income: actual > expected is GOOD (over target)
                          const isUnderBudget = item.item_type === 'expense' && item.actual_amount > 0 && item.actual_amount < item.expected_amount;
                          const isOverTarget = item.item_type === 'income' && item.actual_amount > item.expected_amount;
                          const isPositive = isUnderBudget || isOverTarget;
                          
                          return (
                            <TableRow key={item.expected_item_id} className={item.is_matched ? 'bg-green-50 dark:bg-green-900/10' : 'bg-orange-50 dark:bg-orange-900/10'}>
                              <TableCell>
                                {item.is_matched ? (
                                  <CheckCircle2 className="w-5 h-5 text-green-500" />
                                ) : (
                                  <Circle className="w-5 h-5 text-orange-400" />
                                )}
                              </TableCell>
                              <TableCell className="font-medium">{item.name}</TableCell>
                              <TableCell>
                                <Badge variant={item.item_type === 'income' ? 'default' : 'destructive'}>
                                  {item.item_type}
                                </Badge>
                              </TableCell>
                              <TableCell className="capitalize">{item.frequency}</TableCell>
                              <TableCell className={`text-right font-medium ${item.item_type === 'income' ? 'text-green-600' : 'text-red-600'}`}>
                                {formatCurrency(item.expected_amount)}
                              </TableCell>
                              <TableCell className={`text-right ${isPositive ? 'font-bold text-green-600' : (item.actual_amount > 0 ? (item.item_type === 'income' ? 'font-medium text-green-600' : 'font-medium text-red-600') : 'text-muted-foreground')}`}>
                                {item.actual_amount > 0 ? formatCurrency(item.actual_amount) : '—'}
                              </TableCell>
                              <TableCell className={`text-right ${isPositive ? 'font-bold text-green-600' : (item.difference > 0 ? 'font-medium text-green-600' : item.difference < 0 ? 'font-medium text-red-600' : '')}`}>
                                {item.difference !== 0 ? (item.difference > 0 ? '+' : '') + formatCurrency(item.difference) : '—'}
                              </TableCell>
                            </TableRow>
                          );
                        })}
                      </TableBody>
                    </Table>
                  </Card>
                )}

                {/* Unmatched Transactions */}
                {budgetComparison.unmatched_transactions.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Unbudgeted Transactions</CardTitle>
                      <CardDescription>Transactions not matching any budget item</CardDescription>
                    </CardHeader>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Date</TableHead>
                          <TableHead>Category</TableHead>
                          <TableHead>Notes</TableHead>
                          <TableHead className="text-right">Amount</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {budgetComparison.unmatched_transactions.map(tx => (
                          <TableRow key={tx.id}>
                            <TableCell>{tx.date}</TableCell>
                            <TableCell>{tx.category}</TableCell>
                            <TableCell className="max-w-[200px] truncate">{tx.notes || '—'}</TableCell>
                            <TableCell className={`text-right font-medium ${tx.amount >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                              {formatCurrency(tx.amount)}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </Card>
                )}

                {budgetComparison.items.length === 0 && !budgetComparison.period_id && (
                  <Card>
                    <CardContent className="p-6 text-center text-muted-foreground">
                      No active budget period for {budgetMonth}. Create an expense period in the "Expense Periods" tab that covers this month.
                    </CardContent>
                  </Card>
                )}
              </div>
            ) : (
              <Card>
                <CardContent className="p-6 text-center text-muted-foreground">
                  Loading budget comparison...
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        {/* Expense Periods Tab */}
        <TabsContent value="periods" className="space-y-4">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-xl font-semibold">Expense Periods</h2>
              <p className="text-sm text-muted-foreground">Define time periods with expected income and expenses</p>
            </div>
            <Button onClick={() => setPeriodDialog({ open: true, data: null })} data-testid="add-period-btn">
              <Plus className="w-4 h-4 mr-2" /> Add Period
            </Button>
          </div>
          
          {expensePeriods.length === 0 ? (
            <Card>
              <CardContent className="p-8 text-center text-muted-foreground">
                No expense periods yet. Create a period to start budgeting your income and expenses.
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {expensePeriods.map(period => (
                <ExpensePeriodCard
                  key={period.id}
                  period={period}
                  categories={categories}
                  projects={projects}
                  onEditPeriod={() => setPeriodDialog({ open: true, data: period })}
                  onDeletePeriod={() => handleDeletePeriod(period.id)}
                  onAddItem={() => setExpectedItemDialog({ open: true, data: null, periodId: period.id })}
                  onEditItem={(item) => setExpectedItemDialog({ open: true, data: item, periodId: period.id })}
                  onDeleteItem={handleDeleteExpectedItem}
                  onItemsChanged={fetchExpensePeriods}
                  token={token}
                  formatCurrency={formatCurrency}
                />
              ))}
            </div>
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
                      <TrendingUp className="w-5 h-5 text-blue-500" />
                      <div>
                        <p className="text-sm text-muted-foreground">Investments</p>
                        <p className="text-xl font-bold text-blue-600">{formatCurrency(monthlyOverview.total_investments)}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center gap-2">
                      <Calculator className="w-5 h-5 text-purple-500" />
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
                    <CardTitle className="text-lg">By Project</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {monthlyOverview.by_project.length === 0 ? (
                      <p className="text-muted-foreground">No data for this month</p>
                    ) : (
                      <div className="space-y-2">
                        {monthlyOverview.by_project.map((proj, i) => (
                          <div key={i} className="flex justify-between items-center p-2 bg-muted rounded-lg">
                            <span className="font-medium">{proj.name}</span>
                            <span className={`font-medium ${proj.income - proj.expenses >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                              {formatCurrency(proj.income - proj.expenses)}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">By Category</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {monthlyOverview.by_category.length === 0 ? (
                      <p className="text-muted-foreground">No data for this month</p>
                    ) : (
                      <div className="space-y-2">
                        {monthlyOverview.by_category.map((cat, i) => (
                          <div key={i} className="flex justify-between items-center p-2 bg-muted rounded-lg">
                            <div className="flex items-center gap-2">
                              <span className="font-medium">{cat.name}</span>
                              <Badge variant={cat.type === 'income' ? 'default' : cat.type === 'investment' ? 'secondary' : 'destructive'}>
                                {cat.type}
                              </Badge>
                            </div>
                            <span className={`font-medium ${cat.type === 'income' ? 'text-green-600' : cat.type === 'investment' ? 'text-blue-600' : 'text-red-600'}`}>
                              {cat.type === 'income' ? '+' : '-'}{formatCurrency(cat.total)}
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

      {/* Dialogs */}
      <AccountDialog 
        open={accountDialog.open}
        data={accountDialog.data}
        projects={projects}
        selectedProjectId={selectedProjectId}
        onClose={() => setAccountDialog({ open: false, data: null })}
        onSave={handleSaveAccount}
      />

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
        onCategoryCreated={fetchCategories}
        token={token}
      />

      <PeriodDialog
        open={periodDialog.open}
        data={periodDialog.data}
        projects={projects}
        selectedProjectId={selectedProjectId}
        onClose={() => setPeriodDialog({ open: false, data: null })}
        onSave={handleSavePeriod}
      />

      <ExpectedItemDialog
        open={expectedItemDialog.open}
        data={expectedItemDialog.data}
        periodId={expectedItemDialog.periodId}
        periods={expensePeriods}
        categories={categories}
        onClose={() => setExpectedItemDialog({ open: false, data: null, periodId: null })}
        onSave={handleSaveExpectedItem}
        onDelete={handleDeleteExpectedItem}
        token={token}
        onCategoryCreated={fetchCategories}
        projects={projects}
      />

      <SavingsGoalDialog
        open={savingsGoalDialog.open}
        data={savingsGoalDialog.data}
        projects={projects}
        selectedProjectId={selectedProjectId}
        onClose={() => setSavingsGoalDialog({ open: false, data: null })}
        onSave={handleSaveSavingsGoal}
      />

      <ImportDialog
        open={importDialog.open}
        projects={projects}
        accounts={accounts}
        categories={categories}
        selectedProjectId={selectedProjectId}
        onClose={() => setImportDialog({ open: false })}
        onImportComplete={() => {
          fetchTransactions();
          fetchAccounts();
          fetchMonthly();
          fetchRunway();
          fetchBudgetComparison();
        }}
        token={token}
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
    starting_balance: '',
    notes: ''
  });

  useEffect(() => {
    if (data) {
      setForm({
        project_id: data.project_id,
        name: data.name,
        type: data.type,
        starting_balance: data.starting_balance?.toString() || '0',
        notes: data.notes || ''
      });
    } else {
      setForm({
        project_id: selectedProjectId !== 'all' ? selectedProjectId : '',
        name: '',
        type: 'bank',
        starting_balance: '0',
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
    onSave({
      ...form,
      starting_balance: parseFloat(form.starting_balance) || 0
    });
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
            <Label>Starting Balance (EUR)</Label>
            <Input 
              type="number" 
              step="0.01" 
              value={form.starting_balance} 
              onChange={(e) => setForm({ ...form, starting_balance: e.target.value })} 
              placeholder="0.00"
            />
            <p className="text-xs text-muted-foreground">Initial capital already in this account</p>
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
const TransactionDialog = ({ open, data, projects, accounts, categories, savingsGoals, selectedProjectId, onClose, onSave, onCategoryCreated, token }) => {
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
  const [showNewCategory, setShowNewCategory] = useState(false);
  const [newCategoryName, setNewCategoryName] = useState('');
  const [newCategoryType, setNewCategoryType] = useState('expense');
  const [creatingCategory, setCreatingCategory] = useState(false);

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
    setShowNewCategory(false);
    setNewCategoryName('');
  }, [data, selectedProjectId, accounts, open]);

  const projectCategories = categories.filter(c => c.project_id === form.project_id);
  const projectSavingsGoals = savingsGoals?.filter(g => g.project_id === form.project_id) || [];

  const handleCreateCategory = async () => {
    if (!newCategoryName || !form.project_id) {
      toast.error('Please enter a category name');
      return;
    }
    setCreatingCategory(true);
    try {
      const res = await axios.post(`${API}/finance/categories`, {
        project_id: form.project_id,
        name: newCategoryName,
        type: newCategoryType
      }, { headers: { Authorization: `Bearer ${token}` } });
      toast.success('Category created');
      setForm({ ...form, category_id: res.data.id });
      setShowNewCategory(false);
      setNewCategoryName('');
      if (onCategoryCreated) onCategoryCreated();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to create category');
    } finally {
      setCreatingCategory(false);
    }
  };

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
            <div className="flex items-center justify-between">
              <Label>Category *</Label>
              {form.project_id && (
                <Button type="button" variant="ghost" size="sm" onClick={() => setShowNewCategory(!showNewCategory)}>
                  <Plus className="w-3 h-3 mr-1" /> New
                </Button>
              )}
            </div>
            {showNewCategory ? (
              <div className="space-y-2 p-3 border rounded-lg bg-muted/50">
                <Input 
                  value={newCategoryName} 
                  onChange={(e) => setNewCategoryName(e.target.value)} 
                  placeholder="Category name"
                />
                <div className="flex gap-2">
                  <Select value={newCategoryType} onValueChange={setNewCategoryType}>
                    <SelectTrigger className="flex-1">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="income">Income</SelectItem>
                      <SelectItem value="expense">Expense</SelectItem>
                      <SelectItem value="investment">Investment</SelectItem>
                    </SelectContent>
                  </Select>
                  <Button type="button" size="sm" onClick={handleCreateCategory} disabled={creatingCategory}>
                    {creatingCategory ? 'Creating...' : 'Add'}
                  </Button>
                  <Button type="button" size="sm" variant="ghost" onClick={() => setShowNewCategory(false)}>
                    Cancel
                  </Button>
                </div>
              </div>
            ) : (
              <Select value={form.category_id} onValueChange={(v) => setForm({ ...form, category_id: v })} disabled={!form.project_id}>
                <SelectTrigger>
                  <SelectValue placeholder={form.project_id ? (projectCategories.length === 0 ? "No categories - create one" : "Select category") : "Select project first"} />
                </SelectTrigger>
                <SelectContent>
                  {projectCategories.map(c => (
                    <SelectItem key={c.id} value={c.id}>{c.name} ({c.type})</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          </div>
          <div className="space-y-2">
            <Label>Savings Goal (Optional)</Label>
            <Select value={form.savings_goal_id || "none"} onValueChange={(v) => setForm({ ...form, savings_goal_id: v === "none" ? "" : v })} disabled={!form.project_id}>
              <SelectTrigger>
                <SelectValue placeholder="Attach to savings goal..." />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">None</SelectItem>
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

// Period Dialog Component
const PeriodDialog = ({ open, data, projects, selectedProjectId, onClose, onSave }) => {
  const [form, setForm] = useState({
    project_id: '',
    name: '',
    start_month: '',
    end_month: '',
    notes: ''
  });

  useEffect(() => {
    if (data) {
      setForm({
        project_id: data.project_id,
        name: data.name,
        start_month: data.start_month,
        end_month: data.end_month,
        notes: data.notes || ''
      });
    } else {
      const now = new Date();
      const currentMonth = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
      const endMonth = `${now.getFullYear()}-12`;
      setForm({
        project_id: selectedProjectId !== 'all' ? selectedProjectId : '',
        name: `${now.getFullYear()}`,
        start_month: currentMonth,
        end_month: endMonth,
        notes: ''
      });
    }
  }, [data, selectedProjectId, open]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!form.project_id || !form.name || !form.start_month || !form.end_month) {
      toast.error('Please fill all required fields');
      return;
    }
    if (form.start_month > form.end_month) {
      toast.error('Start month must be before end month');
      return;
    }
    onSave(form);
  };

  return (
    <Dialog open={open} onOpenChange={(o) => !o && onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{data ? 'Edit Expense Period' : 'New Expense Period'}</DialogTitle>
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
            <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="e.g., 2024, First Year" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Start Month *</Label>
              <Input type="month" value={form.start_month} onChange={(e) => setForm({ ...form, start_month: e.target.value })} />
            </div>
            <div className="space-y-2">
              <Label>End Month *</Label>
              <Input type="month" value={form.end_month} onChange={(e) => setForm({ ...form, end_month: e.target.value })} />
            </div>
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

// Expected Item Dialog Component
const ExpectedItemDialog = ({ open, data, periodId, periods, categories, onClose, onSave, onDelete, token, onCategoryCreated, projects }) => {
  const [form, setForm] = useState({
    period_id: '',
    name: '',
    amount: '',
    item_type: 'expense',
    frequency: 'monthly',
    category_id: '',
    month: '',
    notes: ''
  });
  const [showNewCategory, setShowNewCategory] = useState(false);
  const [newCategoryName, setNewCategoryName] = useState('');
  const [newCategoryType, setNewCategoryType] = useState('expense');
  const [creatingCategory, setCreatingCategory] = useState(false);

  const selectedPeriod = periods.find(p => p.id === form.period_id);
  const projectCategories = categories.filter(c => selectedPeriod && c.project_id === selectedPeriod.project_id);

  useEffect(() => {
    if (data) {
      setForm({
        period_id: data.period_id,
        name: data.name,
        amount: data.amount.toString(),
        item_type: data.item_type,
        frequency: data.frequency,
        category_id: data.category_id || '',
        month: data.month || '',
        notes: data.notes || ''
      });
    } else {
      setForm({
        period_id: periodId || '',
        name: '',
        amount: '',
        item_type: 'expense',
        frequency: 'monthly',
        category_id: '',
        month: '',
        notes: ''
      });
    }
    setShowNewCategory(false);
    setNewCategoryName('');
  }, [data, periodId, open]);

  const handleCreateCategory = async () => {
    if (!newCategoryName || !selectedPeriod) {
      toast.error('Please enter a category name');
      return;
    }
    setCreatingCategory(true);
    try {
      const res = await axios.post(`${API}/finance/categories`, {
        project_id: selectedPeriod.project_id,
        name: newCategoryName,
        type: newCategoryType
      }, { headers: { Authorization: `Bearer ${token}` } });
      toast.success('Category created');
      setForm({ ...form, category_id: res.data.id });
      setShowNewCategory(false);
      setNewCategoryName('');
      if (onCategoryCreated) onCategoryCreated();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to create category');
    } finally {
      setCreatingCategory(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!form.period_id || !form.name || !form.amount) {
      toast.error('Please fill all required fields');
      return;
    }
    onSave({
      ...form,
      amount: parseFloat(form.amount),
      category_id: form.category_id || null,
      month: form.month || null
    });
  };

  return (
    <Dialog open={open} onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>{data ? 'Edit Expected Item' : 'New Expected Item'}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label>Expense Period *</Label>
            <Select value={form.period_id} onValueChange={(v) => setForm({ ...form, period_id: v, category_id: '' })} disabled={!!data}>
              <SelectTrigger>
                <SelectValue placeholder="Select period" />
              </SelectTrigger>
              <SelectContent>
                {periods.map(p => (
                  <SelectItem key={p.id} value={p.id}>{p.name} ({p.start_month} to {p.end_month})</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Name *</Label>
            <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="e.g., Monthly Rent, Salary" />
          </div>
          <div className="flex gap-2">
            <Button type="button" variant={form.item_type === 'income' ? 'default' : 'outline'} className="flex-1" onClick={() => setForm({ ...form, item_type: 'income' })}>
              <ArrowUpCircle className="w-4 h-4 mr-2" /> Income
            </Button>
            <Button type="button" variant={form.item_type === 'expense' ? 'destructive' : 'outline'} className="flex-1" onClick={() => setForm({ ...form, item_type: 'expense' })}>
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
                  <SelectItem value="one_time">One-time</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          {(form.frequency === 'yearly' || form.frequency === 'one_time') && (
            <div className="space-y-2">
              <Label>Month (for yearly/one-time)</Label>
              <Input type="month" value={form.month} onChange={(e) => setForm({ ...form, month: e.target.value })} />
              <p className="text-xs text-muted-foreground">Specify which month this applies to</p>
            </div>
          )}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label>Category (Optional)</Label>
              {form.period_id && (
                <Button type="button" variant="ghost" size="sm" onClick={() => setShowNewCategory(!showNewCategory)}>
                  <Plus className="w-3 h-3 mr-1" /> New
                </Button>
              )}
            </div>
            {showNewCategory ? (
              <div className="space-y-2 p-3 border rounded-lg bg-muted/50">
                <Input 
                  value={newCategoryName} 
                  onChange={(e) => setNewCategoryName(e.target.value)} 
                  placeholder="Category name"
                />
                <div className="flex gap-2">
                  <Select value={newCategoryType} onValueChange={setNewCategoryType}>
                    <SelectTrigger className="flex-1">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="income">Income</SelectItem>
                      <SelectItem value="expense">Expense</SelectItem>
                      <SelectItem value="investment">Investment</SelectItem>
                    </SelectContent>
                  </Select>
                  <Button type="button" size="sm" onClick={handleCreateCategory} disabled={creatingCategory}>
                    {creatingCategory ? 'Creating...' : 'Add'}
                  </Button>
                  <Button type="button" size="sm" variant="ghost" onClick={() => setShowNewCategory(false)}>
                    Cancel
                  </Button>
                </div>
              </div>
            ) : (
              <Select value={form.category_id || "none"} onValueChange={(v) => setForm({ ...form, category_id: v === "none" ? "" : v })} disabled={!form.period_id}>
                <SelectTrigger>
                  <SelectValue placeholder="Select category for matching" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">None (match by amount)</SelectItem>
                  {projectCategories.map(c => (
                    <SelectItem key={c.id} value={c.id}>{c.name} ({c.type})</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
            <p className="text-xs text-muted-foreground">Used to match with actual transactions</p>
          </div>
          <div className="space-y-2">
            <Label>Notes</Label>
            <Textarea value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} placeholder="Optional notes..." />
          </div>
          <DialogFooter className="flex justify-between">
            {data && (
              <Button type="button" variant="destructive" onClick={() => { onDelete(data.id); onClose(); }}>
                Delete
              </Button>
            )}
            <div className="flex gap-2">
              <Button type="button" variant="outline" onClick={onClose}>Cancel</Button>
              <Button type="submit">{data ? 'Update' : 'Create'}</Button>
            </div>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

// Expense Period Card Component with inline items editing
const ExpensePeriodCard = ({ period, categories, projects, onEditPeriod, onDeletePeriod, onAddItem, onEditItem, onDeleteItem, onItemsChanged, token, formatCurrency }) => {
  const [expanded, setExpanded] = useState(false);
  const [items, setItems] = useState([]);
  const [loadingItems, setLoadingItems] = useState(false);

  const headers = { Authorization: `Bearer ${token}` };

  const fetchItems = async () => {
    if (!expanded) return;
    setLoadingItems(true);
    try {
      const res = await axios.get(`${API}/budget/periods/${period.id}/items`, { headers });
      setItems(res.data.items || []);
    } catch (err) {
      console.error('Failed to fetch items:', err);
    } finally {
      setLoadingItems(false);
    }
  };

  useEffect(() => {
    if (expanded) {
      fetchItems();
    }
  }, [expanded, period.id]);

  // Refresh items when period changes (e.g., after adding an item)
  useEffect(() => {
    if (expanded) {
      fetchItems();
    }
  }, [period.expected_items_count]);

  const handleDeleteItem = async (itemId) => {
    await onDeleteItem(itemId);
    fetchItems();
    onItemsChanged();
  };

  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex justify-between items-start">
          <div>
            <div className="flex items-center gap-2">
              <CalendarRange className="w-5 h-5 text-muted-foreground" />
              <CardTitle className="text-lg">{period.name}</CardTitle>
            </div>
            <CardDescription>
              {period.start_month} to {period.end_month} • {period.project_name}
            </CardDescription>
          </div>
          <div className="flex gap-1">
            <Button size="icon" variant="ghost" onClick={onEditPeriod}>
              <Edit className="w-4 h-4" />
            </Button>
            <Button size="icon" variant="ghost" onClick={onDeletePeriod}>
              <Trash2 className="w-4 h-4 text-red-500" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex gap-4 mb-4">
          <div className="flex-1">
            <p className="text-sm text-muted-foreground">Monthly Income</p>
            <p className="text-lg font-bold text-green-600">{formatCurrency(period.total_monthly_income)}</p>
          </div>
          <div className="flex-1">
            <p className="text-sm text-muted-foreground">Monthly Expenses</p>
            <p className="text-lg font-bold text-red-600">{formatCurrency(period.total_monthly_expenses)}</p>
          </div>
          <div className="flex-1">
            <p className="text-sm text-muted-foreground">Net Monthly</p>
            <p className={`text-lg font-bold ${period.total_monthly_income - period.total_monthly_expenses >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {formatCurrency(period.total_monthly_income - period.total_monthly_expenses)}
            </p>
          </div>
          <div className="flex-1">
            <p className="text-sm text-muted-foreground">Items</p>
            <p className="text-lg font-bold">{period.expected_items_count}</p>
          </div>
        </div>
        
        {period.notes && (
          <p className="text-sm text-muted-foreground mb-4">{period.notes}</p>
        )}
        
        <div className="flex gap-2">
          <Button 
            size="sm" 
            variant="outline" 
            onClick={onAddItem}
            data-testid={`add-item-${period.id}`}
          >
            <Plus className="w-3 h-3 mr-1" /> Add Item
          </Button>
          <Button 
            size="sm" 
            variant={expanded ? "secondary" : "outline"}
            onClick={() => setExpanded(!expanded)}
            data-testid={`toggle-items-${period.id}`}
          >
            {expanded ? 'Hide Items' : `Show Items (${period.expected_items_count})`}
          </Button>
        </div>

        {/* Expanded Items List */}
        {expanded && (
          <div className="mt-4 border-t pt-4">
            {loadingItems ? (
              <div className="flex items-center justify-center py-4">
                <RefreshCw className="w-5 h-5 animate-spin text-muted-foreground" />
              </div>
            ) : items.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-4">No expected items yet.</p>
            ) : (
              <div className="space-y-2">
                {items.map(item => (
                  <div 
                    key={item.id} 
                    className="flex items-center justify-between p-3 bg-muted/50 rounded-lg hover:bg-muted transition-colors cursor-pointer"
                    onClick={() => onEditItem(item)}
                    data-testid={`item-${item.id}`}
                  >
                    <div className="flex items-center gap-3">
                      {item.item_type === 'income' ? (
                        <ArrowUpCircle className="w-4 h-4 text-green-500" />
                      ) : (
                        <ArrowDownCircle className="w-4 h-4 text-red-500" />
                      )}
                      <div>
                        <p className="font-medium">{item.name}</p>
                        <p className="text-xs text-muted-foreground">
                          {item.frequency} {item.category_name && `• ${item.category_name}`}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`font-medium ${item.item_type === 'income' ? 'text-green-600' : 'text-red-600'}`}>
                        {item.item_type === 'income' ? '+' : '-'}{formatCurrency(item.amount)}
                      </span>
                      <Button 
                        size="icon" 
                        variant="ghost" 
                        className="h-8 w-8"
                        onClick={(e) => { e.stopPropagation(); onEditItem(item); }}
                      >
                        <Edit className="w-3 h-3" />
                      </Button>
                      <Button 
                        size="icon" 
                        variant="ghost" 
                        className="h-8 w-8"
                        onClick={(e) => { e.stopPropagation(); handleDeleteItem(item.id); }}
                      >
                        <Trash2 className="w-3 h-3 text-red-500" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
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

// Import Dialog Component
const ImportDialog = ({ open, projects, accounts, categories, selectedProjectId, onClose, onImportComplete, token }) => {
  const [step, setStep] = useState('upload'); // upload, mapping, preview, confirm
  const [fileType, setFileType] = useState(null); // csv or ofx
  const [file, setFile] = useState(null);
  const [columns, setColumns] = useState([]);
  const [columnMapping, setColumnMapping] = useState({
    date_column: '',
    amount_column: '',
    description_column: '',
    date_format: '%Y-%m-%d',
    delimiter: ',',
    has_header: true
  });
  const [previewData, setPreviewData] = useState([]);
  const [selectedTransactions, setSelectedTransactions] = useState([]);
  const [warnings, setWarnings] = useState([]);
  const [importSettings, setImportSettings] = useState({
    project_id: '',
    account_id: '',
    category_id: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [aiAnalyzed, setAiAnalyzed] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [duplicatesChecked, setDuplicatesChecked] = useState(false);
  const [isCheckingDuplicates, setIsCheckingDuplicates] = useState(false);

  const headers = { Authorization: `Bearer ${token}` };

  // Reset on open
  useEffect(() => {
    if (open) {
      setStep('upload');
      setFileType(null);
      setFile(null);
      setColumns([]);
      setColumnMapping({
        date_column: '',
        amount_column: '',
        description_column: '',
        date_format: '%Y-%m-%d',
        delimiter: ',',
        has_header: true
      });
      setPreviewData([]);
      setSelectedTransactions([]);
      setWarnings([]);
      setImportSettings({
        project_id: selectedProjectId !== 'all' ? selectedProjectId : '',
        account_id: '',
        category_id: ''
      });
      setAiAnalyzed(false);
      setIsAnalyzing(false);
      setDuplicatesChecked(false);
      setIsCheckingDuplicates(false);
    }
  }, [open, selectedProjectId]);

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;
    
    const ext = selectedFile.name.toLowerCase().split('.').pop();
    if (ext === 'csv') {
      setFileType('csv');
      setFile(selectedFile);
    } else if (ext === 'ofx' || ext === 'qfx') {
      setFileType('ofx');
      setFile(selectedFile);
    } else {
      toast.error('Unsupported file format. Use CSV, OFX, or QFX files.');
    }
  };

  const handleUploadCSV = async (withMapping = false) => {
    if (!file) return;
    setIsLoading(true);
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('delimiter', columnMapping.delimiter);
    formData.append('has_header', columnMapping.has_header);
    
    if (withMapping) {
      formData.append('date_column', columnMapping.date_column);
      formData.append('amount_column', columnMapping.amount_column);
      if (columnMapping.description_column) {
        formData.append('description_column', columnMapping.description_column);
      }
      formData.append('date_format', columnMapping.date_format);
    }
    
    try {
      const res = await axios.post(`${API}/finance/import/preview/csv`, formData, { headers });
      
      if (res.data.columns && res.data.columns.length > 0) {
        setColumns(res.data.columns);
      }
      
      if (res.data.transactions && res.data.transactions.length > 0) {
        setPreviewData(res.data.transactions);
        setSelectedTransactions(res.data.transactions.map((_, i) => i));
        setStep('preview');
      } else if (!withMapping) {
        setStep('mapping');
      }
      
      setWarnings(res.data.warnings || []);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to parse CSV file');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUploadOFX = async () => {
    if (!file) return;
    setIsLoading(true);
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const res = await axios.post(`${API}/finance/import/preview/ofx`, formData, { headers });
      setPreviewData(res.data.transactions);
      setSelectedTransactions(res.data.transactions.map((_, i) => i));
      setWarnings(res.data.warnings || []);
      setStep('preview');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to parse OFX file');
    } finally {
      setIsLoading(false);
    }
  };

  const handleConfirmImport = async () => {
    if (!importSettings.project_id || !importSettings.account_id || !importSettings.category_id) {
      toast.error('Please select project, account, and category');
      return;
    }
    
    const transactionsToImport = selectedTransactions.map(i => previewData[i]);
    if (transactionsToImport.length === 0) {
      toast.error('No transactions selected');
      return;
    }
    
    setIsLoading(true);
    try {
      const res = await axios.post(`${API}/finance/import/confirm`, {
        transactions: transactionsToImport,
        project_id: importSettings.project_id,
        account_id: importSettings.account_id,
        default_category_id: importSettings.category_id
      }, { headers });
      
      toast.success(res.data.message);
      onImportComplete();
      onClose();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to import transactions');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAiAnalyze = async () => {
    setIsAnalyzing(true);
    try {
      const res = await axios.post(`${API}/finance/import/analyze`, {
        transactions: previewData,
        total: previewData.length,
        columns: columns,
        warnings: warnings
      }, { headers });
      
      setPreviewData(res.data.transactions);
      setAiAnalyzed(true);
      toast.success('AI analysis complete! Review the suggestions below.');
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'AI analysis failed';
      if (errorMsg.includes('not configured')) {
        toast.error('Please configure your OpenAI API key in Settings first.');
      } else {
        toast.error(errorMsg);
      }
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleCheckDuplicates = async () => {
    setIsCheckingDuplicates(true);
    try {
      const accountParam = importSettings.account_id ? `?account_id=${importSettings.account_id}` : '';
      const res = await axios.post(`${API}/finance/import/check-duplicates${accountParam}`, {
        transactions: previewData,
        total: previewData.length,
        columns: columns,
        warnings: warnings,
        ai_analyzed: aiAnalyzed
      }, { headers });
      
      setPreviewData(res.data.transactions);
      setWarnings(res.data.warnings || []);
      setDuplicatesChecked(true);
      
      // Auto-deselect duplicates
      const nonDupIndices = res.data.transactions
        .map((tx, i) => tx.is_potential_duplicate ? null : i)
        .filter(i => i !== null);
      setSelectedTransactions(nonDupIndices);
      
      const dupCount = res.data.transactions.filter(tx => tx.is_potential_duplicate).length;
      if (dupCount > 0) {
        toast.warning(`Found ${dupCount} potential duplicate(s). They've been deselected.`);
      } else {
        toast.success('No duplicates found!');
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to check duplicates');
    } finally {
      setIsCheckingDuplicates(false);
    }
  };

  const toggleSelectAll = () => {
    if (selectedTransactions.length === previewData.length) {
      setSelectedTransactions([]);
    } else {
      setSelectedTransactions(previewData.map((_, i) => i));
    }
  };

  const toggleTransaction = (index) => {
    if (selectedTransactions.includes(index)) {
      setSelectedTransactions(selectedTransactions.filter(i => i !== index));
    } else {
      setSelectedTransactions([...selectedTransactions, index]);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(amount);
  };

  const projectCategories = categories.filter(c => c.project_id === importSettings.project_id);

  return (
    <Dialog open={open} onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <FileSpreadsheet className="w-5 h-5" />
            Import Transactions
          </DialogTitle>
        </DialogHeader>

        {/* Step 1: Upload */}
        {step === 'upload' && (
          <div className="space-y-6">
            <div className="border-2 border-dashed rounded-lg p-8 text-center">
              <Upload className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="font-medium mb-2">Upload your bank statement</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Supported formats: CSV, OFX, QFX
              </p>
              <Input
                type="file"
                accept=".csv,.ofx,.qfx"
                onChange={handleFileSelect}
                className="max-w-xs mx-auto"
                data-testid="import-file-input"
              />
            </div>

            {file && (
              <div className="bg-muted p-4 rounded-lg">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <FileSpreadsheet className="w-5 h-5 text-primary" />
                    <span className="font-medium">{file.name}</span>
                    <Badge>{fileType?.toUpperCase()}</Badge>
                  </div>
                  <Button variant="ghost" size="sm" onClick={() => { setFile(null); setFileType(null); }}>
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            )}

            {fileType === 'csv' && (
              <div className="space-y-4 border-t pt-4">
                <h4 className="font-medium">CSV Options</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Delimiter</Label>
                    <Select value={columnMapping.delimiter} onValueChange={(v) => setColumnMapping({ ...columnMapping, delimiter: v })}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value=",">Comma (,)</SelectItem>
                        <SelectItem value=";">Semicolon (;)</SelectItem>
                        <SelectItem value="\t">Tab</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="flex items-center space-x-2 pt-6">
                    <Checkbox 
                      id="has-header"
                      checked={columnMapping.has_header} 
                      onCheckedChange={(c) => setColumnMapping({ ...columnMapping, has_header: c })}
                    />
                    <Label htmlFor="has-header">First row is header</Label>
                  </div>
                </div>
              </div>
            )}

            <DialogFooter>
              <Button variant="outline" onClick={onClose}>Cancel</Button>
              <Button 
                onClick={() => fileType === 'csv' ? handleUploadCSV(false) : handleUploadOFX()}
                disabled={!file || isLoading}
                data-testid="import-next-btn"
              >
                {isLoading ? 'Processing...' : 'Next'}
              </Button>
            </DialogFooter>
          </div>
        )}

        {/* Step 2: Column Mapping (CSV only) */}
        {step === 'mapping' && (
          <div className="space-y-6">
            <div className="space-y-4">
              <h4 className="font-medium">Map Columns</h4>
              <p className="text-sm text-muted-foreground">
                Select which columns contain the date, amount, and description.
              </p>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Date Column *</Label>
                  <Select value={columnMapping.date_column} onValueChange={(v) => setColumnMapping({ ...columnMapping, date_column: v })}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select column" />
                    </SelectTrigger>
                    <SelectContent>
                      {columns.map(col => (
                        <SelectItem key={col} value={col}>{col}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Amount Column *</Label>
                  <Select value={columnMapping.amount_column} onValueChange={(v) => setColumnMapping({ ...columnMapping, amount_column: v })}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select column" />
                    </SelectTrigger>
                    <SelectContent>
                      {columns.map(col => (
                        <SelectItem key={col} value={col}>{col}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Description Column (Optional)</Label>
                  <Select value={columnMapping.description_column || "none"} onValueChange={(v) => setColumnMapping({ ...columnMapping, description_column: v === "none" ? "" : v })}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select column" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">None</SelectItem>
                      {columns.map(col => (
                        <SelectItem key={col} value={col}>{col}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Date Format</Label>
                  <Select value={columnMapping.date_format} onValueChange={(v) => setColumnMapping({ ...columnMapping, date_format: v })}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="%Y-%m-%d">YYYY-MM-DD</SelectItem>
                      <SelectItem value="%d/%m/%Y">DD/MM/YYYY</SelectItem>
                      <SelectItem value="%m/%d/%Y">MM/DD/YYYY</SelectItem>
                      <SelectItem value="%d.%m.%Y">DD.MM.YYYY</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {columns.length > 0 && (
                <div className="bg-muted p-3 rounded-lg">
                  <p className="text-xs font-medium mb-1">Detected columns:</p>
                  <p className="text-xs text-muted-foreground">{columns.join(', ')}</p>
                </div>
              )}
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={() => setStep('upload')}>Back</Button>
              <Button 
                onClick={() => handleUploadCSV(true)}
                disabled={!columnMapping.date_column || !columnMapping.amount_column || isLoading}
              >
                {isLoading ? 'Processing...' : 'Parse'}
              </Button>
            </DialogFooter>
          </div>
        )}

        {/* Step 3: Preview */}
        {step === 'preview' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <div>
                <h4 className="font-medium">Preview ({previewData.length} transactions)</h4>
                <p className="text-sm text-muted-foreground">
                  {selectedTransactions.length} selected for import
                </p>
              </div>
              <div className="flex gap-2">
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={handleAiAnalyze}
                  disabled={isAnalyzing || aiAnalyzed}
                >
                  {isAnalyzing ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Analyzing...
                    </>
                  ) : aiAnalyzed ? (
                    <>
                      <CheckCircle className="w-4 h-4 mr-2 text-green-600" />
                      AI Analyzed
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4 mr-2" />
                      Analyze with AI
                    </>
                  )}
                </Button>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={handleCheckDuplicates}
                  disabled={isCheckingDuplicates || duplicatesChecked}
                >
                  {isCheckingDuplicates ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Checking...
                    </>
                  ) : duplicatesChecked ? (
                    <>
                      <CheckCircle className="w-4 h-4 mr-2 text-green-600" />
                      Duplicates Checked
                    </>
                  ) : (
                    <>
                      <AlertTriangle className="w-4 h-4 mr-2" />
                      Check Duplicates
                    </>
                  )}
                </Button>
                <Button variant="outline" size="sm" onClick={toggleSelectAll}>
                  {selectedTransactions.length === previewData.length ? 'Deselect All' : 'Select All'}
                </Button>
              </div>
            </div>

            {warnings.length > 0 && (
              <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-3">
                <div className="flex items-center gap-2 text-yellow-700 dark:text-yellow-400 mb-1">
                  <AlertTriangle className="w-4 h-4" />
                  <span className="text-sm font-medium">Warnings</span>
                </div>
                <ul className="text-xs text-yellow-600 dark:text-yellow-500 list-disc list-inside">
                  {warnings.slice(0, 5).map((w, i) => (
                    <li key={i}>{w}</li>
                  ))}
                  {warnings.length > 5 && <li>... and {warnings.length - 5} more</li>}
                </ul>
              </div>
            )}

            <div className="border rounded-lg max-h-[300px] overflow-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-10"></TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead>Description</TableHead>
                    <TableHead className="text-right">Amount</TableHead>
                    {aiAnalyzed && (
                      <>
                        <TableHead>AI Category</TableHead>
                        <TableHead>AI Insights</TableHead>
                      </>
                    )}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {previewData.map((tx, i) => (
                    <TableRow 
                      key={i} 
                      className={`${selectedTransactions.includes(i) ? '' : 'opacity-50'} ${tx.ai_is_unusual ? 'bg-orange-50 dark:bg-orange-900/20' : ''}`}
                      onClick={() => toggleTransaction(i)}
                      style={{ cursor: 'pointer' }}
                    >
                      <TableCell>
                        <Checkbox 
                          checked={selectedTransactions.includes(i)}
                          onCheckedChange={() => toggleTransaction(i)}
                        />
                      </TableCell>
                      <TableCell>{tx.date}</TableCell>
                      <TableCell className="max-w-[200px] truncate">
                        {tx.description || tx.memo || tx.payee || '—'}
                      </TableCell>
                      <TableCell className={`text-right font-medium ${tx.amount >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {formatCurrency(tx.amount)}
                      </TableCell>
                      {aiAnalyzed && (
                        <>
                          <TableCell>
                            <span className={`text-xs px-2 py-0.5 rounded-full ${
                              tx.ai_type === 'income' 
                                ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' 
                                : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
                            }`}>
                              {tx.ai_category || 'Unknown'}
                            </span>
                          </TableCell>
                          <TableCell>
                            <div className="flex items-center gap-1 flex-wrap">
                              {tx.ai_is_recurring && (
                                <span className="text-xs px-2 py-0.5 rounded-full bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">
                                  🔄 {tx.ai_recurring_frequency || 'Recurring'}
                                </span>
                              )}
                              {tx.ai_is_unusual && (
                                <span className="text-xs px-2 py-0.5 rounded-full bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400" title={tx.ai_unusual_reason}>
                                  ⚠️ Unusual
                                </span>
                              )}
                              {tx.ai_confidence && (
                                <span className="text-xs text-muted-foreground">
                                  {Math.round(tx.ai_confidence * 100)}%
                                </span>
                              )}
                            </div>
                          </TableCell>
                        </>
                      )}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={() => setStep(fileType === 'csv' ? 'mapping' : 'upload')}>Back</Button>
              <Button 
                onClick={() => setStep('confirm')}
                disabled={selectedTransactions.length === 0}
              >
                Continue ({selectedTransactions.length})
              </Button>
            </DialogFooter>
          </div>
        )}

        {/* Step 4: Confirm */}
        {step === 'confirm' && (
          <div className="space-y-6">
            <div>
              <h4 className="font-medium">Import Settings</h4>
              <p className="text-sm text-muted-foreground">
                Select where to import {selectedTransactions.length} transactions.
              </p>
            </div>

            <div className="grid grid-cols-1 gap-4">
              <div className="space-y-2">
                <Label>Project *</Label>
                <Select value={importSettings.project_id} onValueChange={(v) => setImportSettings({ ...importSettings, project_id: v, category_id: '' })}>
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
                <Select value={importSettings.account_id} onValueChange={(v) => setImportSettings({ ...importSettings, account_id: v })}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select account" />
                  </SelectTrigger>
                  <SelectContent>
                    {accounts.map(a => (
                      <SelectItem key={a.id} value={a.id}>{a.name} ({a.type})</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Default Category *</Label>
                <Select value={importSettings.category_id} onValueChange={(v) => setImportSettings({ ...importSettings, category_id: v })} disabled={!importSettings.project_id}>
                  <SelectTrigger>
                    <SelectValue placeholder={importSettings.project_id ? "Select category" : "Select project first"} />
                  </SelectTrigger>
                  <SelectContent>
                    {projectCategories.map(c => (
                      <SelectItem key={c.id} value={c.id}>{c.name} ({c.type})</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <p className="text-xs text-muted-foreground">
                  All imported transactions will use this category. You can change individual transactions later.
                </p>
              </div>
            </div>

            <div className="bg-muted rounded-lg p-4">
              <h5 className="font-medium mb-2">Summary</h5>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <span className="text-muted-foreground">Transactions:</span>
                <span>{selectedTransactions.length}</span>
                <span className="text-muted-foreground">Total Income:</span>
                <span className="text-green-600">
                  {formatCurrency(selectedTransactions.reduce((sum, i) => sum + (previewData[i].amount > 0 ? previewData[i].amount : 0), 0))}
                </span>
                <span className="text-muted-foreground">Total Expenses:</span>
                <span className="text-red-600">
                  {formatCurrency(selectedTransactions.reduce((sum, i) => sum + (previewData[i].amount < 0 ? previewData[i].amount : 0), 0))}
                </span>
              </div>
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={() => setStep('preview')}>Back</Button>
              <Button 
                onClick={handleConfirmImport}
                disabled={!importSettings.project_id || !importSettings.account_id || !importSettings.category_id || isLoading}
                data-testid="import-confirm-btn"
              >
                {isLoading ? 'Importing...' : `Import ${selectedTransactions.length} Transactions`}
              </Button>
            </DialogFooter>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
};

export default FinancePage;
