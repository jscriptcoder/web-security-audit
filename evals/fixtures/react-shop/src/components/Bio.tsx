import DOMPurify from 'dompurify';
import { marked } from 'marked';

export function Bio({ markdown }: { markdown: string }) {
  const html = DOMPurify.sanitize(marked.parse(markdown) as string);
  return <div className="bio" dangerouslySetInnerHTML={{ __html: html }} />;
}
