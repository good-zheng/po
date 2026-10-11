// 真实库里的顶栏头像渲染器：深导入是为了让「头像整块消失」这个现象能被复现，
// 而不是只在测试里抄一遍它的判据。包没有 exports 限制，es 子路径可直接引。
import { ActionsContent } from '@ant-design/pro-components/es/layout/components/GlobalHeader/ActionsContent.js';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { describe, expect, it } from 'vitest';
import { headerAvatarProps } from './avatar';

describe('顶栏头像（真实 ProLayout 渲染器）', () => {
  it('没上传过头像也渲染得出头像', () => {
    render(
      <ActionsContent
        avatarProps={headerAvatarProps({ nickname: '管理员' })}
        actionsRender={() => []}
      />,
    );
    expect(screen.getByRole('img')).toBeTruthy();
  });

  it('只有昵称时什么都不渲染——这就是修复前的现象', () => {
    const { container } = render(
      <ActionsContent
        avatarProps={{ title: '管理员' }}
        actionsRender={() => []}
      />,
    );
    expect(container.querySelector('.ant-avatar')).toBeNull();
  });
});
