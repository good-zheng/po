import React from 'react';

/**
 * 封面占位。后端封面图目前大量为空，留灰块等于承认这页没做完，
 * 所以按书名哈希出一组纸墨配色、把书名竖排上去——同一本书永远同一张封面，
 * 刷新不会跳色。真封面到了就直接用 img。
 */
const PALETTES: ReadonlyArray<readonly [string, string]> = [
  ['#2f3f57', '#5d7695'], // 黛蓝
  ['#3c4a3a', '#68795c'], // 松绿
  ['#5a3a33', '#8b5c4d'], // 赭褐
  ['#443a5c', '#6d5f8a'], // 紫棠
  ['#54493f', '#7d7061'], // 石灰
  ['#2d4a4a', '#587c7a'], // 竹青
];

const hashOf = (text: string) => {
  let h = 0;
  for (let i = 0; i < text.length; i += 1) {
    h = (h * 31 + text.charCodeAt(i)) >>> 0;
  }
  return h;
};

type BookCoverProps = {
  src?: string | null;
  title?: string | null;
  author?: string | null;
  /** 列表里的封面属装饰性图片，书名已在卡片下方给出 */
  alt?: string;
};

const BookCover: React.FC<BookCoverProps> = ({ src, title, author, alt }) => {
  if (src) {
    return <img src={src} alt={alt ?? title ?? ''} loading="lazy" />;
  }
  const name = (title || '').trim() || '无名';
  const [from, to] = PALETTES[hashOf(name) % PALETTES.length];
  return (
    <div
      className="cover-ph"
      style={{ backgroundImage: `linear-gradient(150deg, ${from}, ${to})` }}
    >
      <span className="cover-ph-frame" />
      <span className="cover-ph-title">{name}</span>
      {author ? <span className="cover-ph-author">{author}</span> : null}
    </div>
  );
};

export default BookCover;
