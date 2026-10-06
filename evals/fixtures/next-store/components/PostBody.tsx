'use client';

import DOMPurify from 'dompurify';
import { marked } from 'marked';
import { useMemo } from 'react';

function linkMentions(html: string): string {
  return html.replace(/@([^\s<]+)/g, '<a class="mention" href="/u/$1">@$1</a>');
}

export function PostBody({ markdown }: { markdown: string }) {
  const html = useMemo(() => linkMentions(DOMPurify.sanitize(marked.parse(markdown) as string)), [markdown]);
  return <div className="post-body" dangerouslySetInnerHTML={{ __html: html }} />;
}
