import { LANG_NAMES, FLAG_EMOJI } from './TranslationPanel';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select';
import { Globe } from 'lucide-react';

export const LanguageSwitcher = ({ languages = [], currentLang, onChange }) => {
  if (!languages || languages.length <= 1) return null;

  return (
    <div className="flex items-center gap-2" data-testid="language-switcher">
      <Globe className="w-4 h-4 text-muted-foreground" />
      <Select value={currentLang} onValueChange={onChange}>
        <SelectTrigger className="w-[180px] h-9" data-testid="language-select">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {languages.map((lang) => (
            <SelectItem key={lang} value={lang} data-testid={`lang-option-${lang}`}>
              <span className="flex items-center gap-2">
                <span>{FLAG_EMOJI[lang]}</span>
                <span>{LANG_NAMES[lang] || lang}</span>
              </span>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
};
