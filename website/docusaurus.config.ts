import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';
import pkg from './package.json';

const config: Config = {
  title: 'Pipeline Kit',
  tagline: 'A portable operating model for coding agents',
  favicon: 'img/logo.svg',

  future: {
    v4: true,
  },

  url: 'http://127.0.0.1:3000',
  baseUrl: '/',

  onBrokenLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  markdown: {
    mermaid: true,
    hooks: {
      onBrokenMarkdownLinks: 'warn',
    },
  },

  themes: [
    '@docusaurus/theme-mermaid',
    [
      require.resolve('@easyops-cn/docusaurus-search-local'),
      {
        hashed: true,
        language: ['en'],
        indexBlog: false,
        docsRouteBasePath: '/docs',
        highlightSearchTermsOnTargetPage: true,
        searchBarShortcut: true,
        searchBarShortcutHint: true,
      },
    ],
  ],

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          routeBasePath: 'docs',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: 'img/logo.svg',
    colorMode: {
      defaultMode: 'light',
      disableSwitch: true,
      respectPrefersColorScheme: false,
    },
    docs: {
      sidebar: {
        hideable: true,
        autoCollapseCategories: true,
      },
    },
    navbar: {
      title: 'Pipeline Kit',
      logo: {
        alt: 'Pipeline Kit',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'html',
          position: 'left',
          value: `<span class="pk-version">${pkg.version}</span>`,
        },
        {
          type: 'search',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'light',
      links: [],
      copyright: `<div class="pk-foot">
        <p class="pk-footer-version">${pkg.version} · Cursor · Claude Code · GitHub</p>
        <div class="pk-footer-bar">
          <span>Pipeline Kit documentation.</span>
          <nav class="pk-footer-links">
            <a href="/docs/reference/cli">CLI</a>
            <a href="/docs/troubleshooting">Troubleshooting</a>
            <a href="/docs/intro/how-it-works">How it works</a>
          </nav>
        </div>
      </div>`,
    },
    prism: {
      theme: prismThemes.vsDark,
      darkTheme: prismThemes.vsDark,
      additionalLanguages: ['bash', 'json', 'python'],
    },
    mermaid: {
      theme: {light: 'neutral', dark: 'neutral'},
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
