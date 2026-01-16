import { useState, useEffect } from 'react';

export const useSortPreference = (pageKey, defaultSortBy = 'created_at', defaultSortOrder = 'desc') => {
  const storageKey = `sort_pref_${pageKey}`;
  
  const [sortBy, setSortBy] = useState(() => {
    const saved = localStorage.getItem(storageKey);
    if (saved) {
      const parsed = JSON.parse(saved);
      return parsed.sortBy || defaultSortBy;
    }
    return defaultSortBy;
  });
  
  const [sortOrder, setSortOrder] = useState(() => {
    const saved = localStorage.getItem(storageKey);
    if (saved) {
      const parsed = JSON.parse(saved);
      return parsed.sortOrder || defaultSortOrder;
    }
    return defaultSortOrder;
  });

  useEffect(() => {
    localStorage.setItem(storageKey, JSON.stringify({ sortBy, sortOrder }));
  }, [sortBy, sortOrder, storageKey]);

  const toggleSortOrder = () => {
    setSortOrder(prev => prev === 'desc' ? 'asc' : 'desc');
  };

  return { sortBy, setSortBy, sortOrder, setSortOrder, toggleSortOrder };
};

export default useSortPreference;
