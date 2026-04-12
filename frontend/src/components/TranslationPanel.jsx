import { useState } from 'react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { SimpleEditor } from './SimpleEditor';
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from './ui/dialog';
import { Languages, Loader2, Check, Pencil, Trash2 } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const LANG_NAMES = {
  en: 'English', nl: 'Dutch', de: 'German', fr: 'French', es: 'Spanish',
  pt: 'Portuguese', it: 'Italian', pl: 'Polish', sv: 'Swedish', da: 'Danish',
  no: 'Norwegian', fi: 'Finnish', cs: 'Czech', ro: 'Romanian', hu: 'Hungarian',
  el: 'Greek', tr: 'Turkish', ja: 'Japanese', zh: 'Chinese', ko: 'Korean',
  ar: 'Arabic', hi: 'Hindi', ru: 'Russian', uk: 'Ukrainian', th: 'Thai',
  vi: 'Vietnamese', id: 'Indonesian',
};

const FLAG_EMOJI = {
  en: '🇬🇧', nl: '🇳🇱', de: '🇩🇪', fr: '🇫🇷', es: '🇪🇸', pt: '🇵🇹',
  it: '🇮🇹', pl: '🇵🇱', sv: '🇸🇪', da: '🇩🇰', no: '🇳🇴', fi: '🇫🇮',
  cs: '🇨🇿', ro: '🇷🇴', hu: '🇭🇺', el: '🇬🇷', tr: '🇹🇷', ja: '🇯🇵',
  zh: '🇨🇳', ko: '🇰🇷', ar: '🇸🇦', hi: '🇮🇳', ru: '🇷🇺', uk: '🇺🇦',
  th: '🇹🇭', vi: '🇻🇳', id: '🇮🇩',
};

export { LANG_NAMES, FLAG_EMOJI };

export const TranslationPanel = ({
  projectId,
  entryId,
  entryType,
  translations = {},
  projectLanguages = ['en'],
  primaryLanguage = 'en',
  contentField = 'description',
  token,
  onUpdate,
}) => {
  const [translating, setTranslating] = useState(null);
  const [editLang, setEditLang] = useState(null);
  const [editTitle, setEditTitle] = useState('');
  const [editContent, setEditContent] = useState('');
  const [saving, setSaving] = useState(false);

  const targetLangs = projectLanguages.filter((l) => l !== primaryLanguage);

  if (targetLangs.length === 0) return null;

  const getTranslateUrl = () => {
    if (entryType === 'library') return `${API}/projects/${projectId}/library/entries/${entryId}/translate`;
    if (entryType === 'diary') return `${API}/projects/${projectId}/diary/${entryId}/translate`;
    return `${API}/projects/${projectId}/blog/${entryId}/translate`;
  };

  const getUpdateUrl = (lang) => `${getTranslateUrl()}/${lang}`;

  const handleTranslate = async (lang) => {
    setTranslating(lang);
    try {
      const res = await axios.post(getTranslateUrl(), { target_language: lang }, {
        headers: { Authorization: `Bearer ${token}` },
      });
      toast.success(`Translated to ${LANG_NAMES[lang]}`);
      onUpdate?.();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Translation failed');
    } finally {
      setTranslating(null);
    }
  };

  const handleEditOpen = (lang) => {
    const t = translations[lang] || {};
    setEditLang(lang);
    setEditTitle(t.title || '');
    setEditContent(t[contentField] || t.description || t.story || '');
  };

  const handleEditSave = async () => {
    setSaving(true);
    try {
      await axios.put(getUpdateUrl(editLang), { title: editTitle, content: editContent }, {
        headers: { Authorization: `Bearer ${token}` },
      });
      toast.success('Translation updated');
      setEditLang(null);
      onUpdate?.();
    } catch (err) {
      toast.error('Failed to save translation');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (lang) => {
    try {
      await axios.delete(getUpdateUrl(lang), { headers: { Authorization: `Bearer ${token}` } });
      toast.success(`${LANG_NAMES[lang]} translation removed`);
      onUpdate?.();
    } catch (err) {
      toast.error('Failed to delete translation');
    }
  };

  return (
    <div className="space-y-3" data-testid="translation-panel">
      <div className="flex items-center gap-2">
        <Languages className="w-4 h-4 text-muted-foreground" />
        <span className="text-sm font-medium">Translations</span>
      </div>
      <div className="space-y-2">
        {targetLangs.map((lang) => {
          const exists = !!translations[lang];
          return (
            <div key={lang} className="flex items-center justify-between p-2 rounded-lg border bg-card" data-testid={`translation-row-${lang}`}>
              <div className="flex items-center gap-2">
                <span className="text-lg">{FLAG_EMOJI[lang]}</span>
                <span className="text-sm font-medium">{LANG_NAMES[lang]}</span>
                {exists && <Badge variant="outline" className="gap-1 text-xs"><Check className="w-3 h-3" /> Done</Badge>}
              </div>
              <div className="flex gap-1">
                {exists && (
                  <>
                    <Button variant="ghost" size="sm" onClick={() => handleEditOpen(lang)} data-testid={`edit-translation-${lang}`}>
                      <Pencil className="w-3 h-3" />
                    </Button>
                    <Button variant="ghost" size="sm" className="text-destructive" onClick={() => handleDelete(lang)} data-testid={`delete-translation-${lang}`}>
                      <Trash2 className="w-3 h-3" />
                    </Button>
                  </>
                )}
                <Button
                  variant={exists ? 'outline' : 'default'}
                  size="sm"
                  disabled={translating === lang}
                  onClick={() => handleTranslate(lang)}
                  data-testid={`translate-btn-${lang}`}
                >
                  {translating === lang ? <Loader2 className="w-3 h-3 animate-spin mr-1" /> : null}
                  {exists ? 'Re-translate' : 'Translate'}
                </Button>
              </div>
            </div>
          );
        })}
      </div>

      <Dialog open={!!editLang} onOpenChange={(open) => !open && setEditLang(null)}>
        <DialogContent className="sm:max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Edit {LANG_NAMES[editLang]} Translation</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div className="space-y-2">
              <Label>Title</Label>
              <Input value={editTitle} onChange={(e) => setEditTitle(e.target.value)} data-testid="edit-translation-title" />
            </div>
            <div className="space-y-2">
              <Label>Content</Label>
              <SimpleEditor content={editContent} onChange={setEditContent} />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditLang(null)}>Cancel</Button>
            <Button onClick={handleEditSave} disabled={saving} data-testid="save-translation">
              {saving && <Loader2 className="w-3 h-3 animate-spin mr-1" />}
              Save
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};
