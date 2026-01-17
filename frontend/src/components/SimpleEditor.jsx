import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Link from '@tiptap/extension-link';
import Placeholder from '@tiptap/extension-placeholder';
import TextAlign from '@tiptap/extension-text-align';
import Underline from '@tiptap/extension-underline';
import TextStyle from '@tiptap/extension-text-style';
import Color from '@tiptap/extension-color';
import { 
  Bold, 
  Italic, 
  Underline as UnderlineIcon, 
  Strikethrough,
  List,
  ListOrdered,
  Quote,
  Heading1,
  Heading2,
  Heading3,
  AlignLeft,
  AlignCenter,
  AlignRight,
  Link as LinkIcon,
  Unlink,
  Undo,
  Redo,
  Palette
} from 'lucide-react';
import { Toggle } from './ui/toggle';
import { Separator } from './ui/separator';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from './ui/popover';
import { cn } from '../lib/utils';

// Predefined colors for the color picker
const COLORS = [
  '#000000', '#374151', '#6B7280', '#9CA3AF',
  '#DC2626', '#EA580C', '#D97706', '#CA8A04',
  '#16A34A', '#059669', '#0D9488', '#0891B2',
  '#2563EB', '#4F46E5', '#7C3AED', '#9333EA',
  '#C026D3', '#DB2777', '#E11D48', '#F43F5E',
];

export const SimpleEditor = ({ 
  content, 
  onChange, 
  placeholder = 'Start writing...',
  className,
  editable = true
}) => {
  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        heading: { levels: [1, 2, 3] },
      }),
      Link.configure({
        openOnClick: false,
        HTMLAttributes: { class: 'text-primary underline' },
      }),
      Placeholder.configure({ placeholder }),
      TextAlign.configure({ types: ['heading', 'paragraph'] }),
      Underline,
      TextStyle,
      Color,
    ],
    content,
    editable,
    onUpdate: ({ editor }) => onChange?.(editor.getHTML()),
  });

  if (!editor) return null;

  const setLink = () => {
    const previousUrl = editor.getAttributes('link').href;
    const url = window.prompt('URL', previousUrl);
    if (url === null) return;
    if (url === '') {
      editor.chain().focus().extendMarkRange('link').unsetLink().run();
      return;
    }
    editor.chain().focus().extendMarkRange('link').setLink({ href: url }).run();
  };

  const setColor = (color) => {
    editor.chain().focus().setColor(color).run();
  };

  const ToolbarButton = ({ onClick, isActive, children, title }) => (
    <Toggle size="sm" pressed={isActive} onPressedChange={onClick} title={title} className="h-8 w-8 p-0">
      {children}
    </Toggle>
  );

  return (
    <div className={cn("border border-input rounded-lg overflow-hidden", className)}>
      {editable && (
        <div className="flex flex-wrap items-center gap-1 p-2 border-b border-input bg-muted/30">
          <ToolbarButton onClick={() => editor.chain().focus().undo().run()} isActive={false} title="Undo">
            <Undo className="h-4 w-4" />
          </ToolbarButton>
          <ToolbarButton onClick={() => editor.chain().focus().redo().run()} isActive={false} title="Redo">
            <Redo className="h-4 w-4" />
          </ToolbarButton>
          <Separator orientation="vertical" className="mx-1 h-6" />
          
          {/* Headings */}
          <ToolbarButton onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()} isActive={editor.isActive('heading', { level: 1 })} title="Heading 1">
            <Heading1 className="h-4 w-4" />
          </ToolbarButton>
          <ToolbarButton onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()} isActive={editor.isActive('heading', { level: 2 })} title="Heading 2">
            <Heading2 className="h-4 w-4" />
          </ToolbarButton>
          <ToolbarButton onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()} isActive={editor.isActive('heading', { level: 3 })} title="Heading 3">
            <Heading3 className="h-4 w-4" />
          </ToolbarButton>
          <Separator orientation="vertical" className="mx-1 h-6" />
          
          {/* Text Formatting */}
          <ToolbarButton onClick={() => editor.chain().focus().toggleBold().run()} isActive={editor.isActive('bold')} title="Bold">
            <Bold className="h-4 w-4" />
          </ToolbarButton>
          <ToolbarButton onClick={() => editor.chain().focus().toggleItalic().run()} isActive={editor.isActive('italic')} title="Italic">
            <Italic className="h-4 w-4" />
          </ToolbarButton>
          <ToolbarButton onClick={() => editor.chain().focus().toggleUnderline().run()} isActive={editor.isActive('underline')} title="Underline">
            <UnderlineIcon className="h-4 w-4" />
          </ToolbarButton>
          <ToolbarButton onClick={() => editor.chain().focus().toggleStrike().run()} isActive={editor.isActive('strike')} title="Strikethrough">
            <Strikethrough className="h-4 w-4" />
          </ToolbarButton>
          
          {/* Color Picker */}
          <Popover>
            <PopoverTrigger asChild>
              <Toggle size="sm" className="h-8 w-8 p-0" title="Text Color">
                <Palette className="h-4 w-4" />
              </Toggle>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-2">
              <div className="grid grid-cols-5 gap-1">
                {COLORS.map((color) => (
                  <button
                    key={color}
                    className="w-6 h-6 rounded border border-gray-200 hover:scale-110 transition-transform"
                    style={{ backgroundColor: color }}
                    onClick={() => setColor(color)}
                    title={color}
                  />
                ))}
              </div>
              <button
                className="w-full mt-2 text-xs text-muted-foreground hover:text-foreground"
                onClick={() => editor.chain().focus().unsetColor().run()}
              >
                Reset color
              </button>
            </PopoverContent>
          </Popover>
          
          <Separator orientation="vertical" className="mx-1 h-6" />
          
          {/* Lists */}
          <ToolbarButton onClick={() => editor.chain().focus().toggleBulletList().run()} isActive={editor.isActive('bulletList')} title="Bullet List">
            <List className="h-4 w-4" />
          </ToolbarButton>
          <ToolbarButton onClick={() => editor.chain().focus().toggleOrderedList().run()} isActive={editor.isActive('orderedList')} title="Numbered List">
            <ListOrdered className="h-4 w-4" />
          </ToolbarButton>
          <ToolbarButton onClick={() => editor.chain().focus().toggleBlockquote().run()} isActive={editor.isActive('blockquote')} title="Quote">
            <Quote className="h-4 w-4" />
          </ToolbarButton>
          <Separator orientation="vertical" className="mx-1 h-6" />
          
          {/* Alignment */}
          <ToolbarButton onClick={() => editor.chain().focus().setTextAlign('left').run()} isActive={editor.isActive({ textAlign: 'left' })} title="Align Left">
            <AlignLeft className="h-4 w-4" />
          </ToolbarButton>
          <ToolbarButton onClick={() => editor.chain().focus().setTextAlign('center').run()} isActive={editor.isActive({ textAlign: 'center' })} title="Align Center">
            <AlignCenter className="h-4 w-4" />
          </ToolbarButton>
          <ToolbarButton onClick={() => editor.chain().focus().setTextAlign('right').run()} isActive={editor.isActive({ textAlign: 'right' })} title="Align Right">
            <AlignRight className="h-4 w-4" />
          </ToolbarButton>
          <Separator orientation="vertical" className="mx-1 h-6" />
          
          {/* Links */}
          <ToolbarButton onClick={setLink} isActive={editor.isActive('link')} title="Add Link">
            <LinkIcon className="h-4 w-4" />
          </ToolbarButton>
          {editor.isActive('link') && (
            <ToolbarButton onClick={() => editor.chain().focus().unsetLink().run()} isActive={false} title="Remove Link">
              <Unlink className="h-4 w-4" />
            </ToolbarButton>
          )}
        </div>
      )}
      <EditorContent 
        editor={editor} 
        className="prose-content min-h-[200px] max-h-[500px] overflow-y-auto p-4 focus:outline-none" 
      />
    </div>
  );
};

export default SimpleEditor;
