import { helpTopics } from '../i18n/en';

export function HelpTip({ topic }: { topic: keyof typeof helpTopics }) {
  return (
    <span className="help-tip" role="note">
      <span dangerouslySetInnerHTML={{ __html: helpTopics[topic] }} />
    </span>
  );
}
