import React from 'react';

const ICONS = {
  book: (
    <path d="M26 11C21 6.6 14.5 5.4 6 7v27c8.5-1.6 15-.4 20 4 5-4.4 11.5-5.6 20-4V7c-8.5-1.6-15-.4-20 4Zm0 0v27" />
  ),
  error: (
    <>
      <circle cx="22" cy="22" r="16" />
      <path d="M22 13v10M22 28h.01" />
    </>
  ),
};

type StateCardProps = {
  kind?: keyof typeof ICONS;
  title: string;
  hint?: string;
  action?: React.ReactNode;
};

/** 空态/错误态统一出口：白屏和「加载中…」裸文本都不是设计。 */
const StateCard: React.FC<StateCardProps> = ({
  kind = 'book',
  title,
  hint,
  action,
}) => (
  <div className="state-card">
    <svg
      width="52"
      height="44"
      viewBox="0 0 52 44"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.3"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {ICONS[kind]}
    </svg>
    <p className="state-title">{title}</p>
    {hint ? <p className="state-hint">{hint}</p> : null}
    {action}
  </div>
);

export default StateCard;
