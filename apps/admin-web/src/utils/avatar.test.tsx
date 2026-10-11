import { describe, expect, it } from 'vitest';
import { DEFAULT_AVATAR, headerAvatarProps } from './avatar';

/**
 * ProLayout 的 `ActionsContent` 判的是 `src || srcSet || icon || children` 至少一个非空，
 * 全空时渲染 `null`——头像不是「一张空圆圈」，而是整块消失、只剩昵称文字。
 * 测试就把这条判据原样抄过来：只断言 src 非空会在库里换成另一种写法时报绿。
 */
const proLayoutRendersAvatar = (props: {
  src?: string;
  srcSet?: string;
  icon?: unknown;
  children?: unknown;
}) => Boolean(props.src || props.srcSet || props.icon || props.children);

describe('headerAvatarProps', () => {
  it('still renders an avatar for an account that never uploaded one', () => {
    const props = headerAvatarProps({ nickname: '管理员' });
    expect(props.src).toBe(DEFAULT_AVATAR);
    expect(proLayoutRendersAvatar(props)).toBe(true);
    expect(props.title).toBe('管理员');
  });

  it('treats an empty avatar string as missing', () => {
    expect(headerAvatarProps({ avatar: '', nickname: 'a' }).src).toBe(
      DEFAULT_AVATAR,
    );
  });

  it('keeps the uploaded avatar when there is one', () => {
    expect(
      headerAvatarProps({ avatar: 'https://cdn.example.com/me.png' }).src,
    ).toBe('https://cdn.example.com/me.png');
  });

  it('carries an icon so a dead avatar url falls back instead of vanishing', () => {
    // antd Avatar 在 <img> 加载失败时回落到 icon；没有 icon 就是一片空白
    expect(
      headerAvatarProps({ avatar: 'https://cdn.example.com/gone.png' }).icon,
    ).toBeTruthy();
  });

  it('renders a default avatar with no user at all (guest / pre-session)', () => {
    expect(proLayoutRendersAvatar(headerAvatarProps())).toBe(true);
  });
});
