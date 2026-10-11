import { UserOutlined } from '@ant-design/icons';
import React from 'react';

/** 未设置头像时的默认图，「个人设置」页与顶栏共用同一来源 */
export const DEFAULT_AVATAR =
  'https://gw.alipayobjects.com/zos/rmsportal/BiazfanxmamNRoxxVxka.png';

type AvatarFields = {
  src?: string;
  icon?: React.ReactNode;
  title?: string;
};

/**
 * 顶栏头像的取值。ProLayout 的判据是 `src || srcSet || icon || children` 至少一个非空，
 * 全空时它渲染的是 `null` 而不是一个空圆圈——没上传过头像的账号就这样把整块头像丢了，
 * 所以下面两个兜底缺一不可：默认图补「从没传过」，icon 补「传了但图 404」（antd Avatar
 * 在图片加载失败时会回落到 icon）。
 */
export function headerAvatarProps(user?: {
  avatar?: string;
  nickname?: string;
}): AvatarFields {
  return {
    src: user?.avatar || DEFAULT_AVATAR,
    icon: <UserOutlined />,
    title: user?.nickname,
  };
}
