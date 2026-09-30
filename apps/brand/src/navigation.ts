import { getPermalink, getBlogPermalink, getAsset } from './utils/permalinks';
import { CONTACT } from './contact';

export const headerData = {
  links: [
    {
      text: '项目',
      href: getPermalink('/#projects'),
    },
    {
      text: '架构',
      href: getPermalink('/#architecture'),
    },
    {
      text: '开发手记',
      href: getBlogPermalink(),
    },
    {
      text: '关于',
      href: getPermalink('/about'),
    },
  ],
  actions: [{ text: '联系我', href: getPermalink('/contact') }],
};

export const footerData = {
  links: [
    {
      title: '产品',
      links: [
        { text: '项目介绍', href: getPermalink('/#projects') },
        { text: '架构', href: getPermalink('/#architecture') },
        { text: '关键决策', href: getPermalink('/#decisions') },
      ],
    },
    {
      title: '内容',
      links: [
        { text: '开发手记', href: getBlogPermalink() },
        { text: '关于我', href: getPermalink('/about') },
        { text: '联系', href: getPermalink('/contact') },
      ],
    },
  ],
  secondaryLinks: [],
  socialLinks: [
    { ariaLabel: '邮件', icon: 'tabler:mail', href: `mailto:${CONTACT.email}` },
    { ariaLabel: '手机', icon: 'tabler:phone', href: `tel:${CONTACT.phoneE164}` },
    { ariaLabel: '微信', icon: 'tabler:brand-wechat', href: getPermalink('/contact') },
    { ariaLabel: 'RSS', icon: 'tabler:rss', href: getAsset('/rss.xml') },
  ],
  footNote: `
    独立开发 · 以开源模板 <a class="text-blue-600 underline dark:text-muted" href="https://github.com/arthelokyo/astrowind">AstroWind</a>（MIT）构建
  `,
};
