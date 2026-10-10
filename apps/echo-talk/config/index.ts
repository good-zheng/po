import path from 'node:path';
import type { UserConfigExport } from '@tarojs/cli';

export default {
  projectName: 'echo-talk',
  date: '2024-01-01',
  designWidth: 750,
  compiler: 'webpack5',
  framework: 'react',
  sourceRoot: 'src',
  outputRoot: 'dist',
  alias: {
    '@': path.resolve(__dirname, '..', 'src'),
  },
  cache: {
    enable: false,
  },
  mini: {
    postcss: {
      pxtransform: {
        enable: true,
        config: {},
      },
    },
  },
  h5: {
    publicPath: '/',
    staticDirectory: 'static',
    postcss: {
      autoprefixer: {
        enable: true,
      },
    },
  },
} satisfies UserConfigExport;
