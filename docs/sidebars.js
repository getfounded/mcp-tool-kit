/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */

// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  // By default, Docusaurus generates a sidebar from the docs folder structure
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Getting Started',
      items: [
        'getting-started/installation',
        'getting-started/quick-start',
        'getting-started/configuration',
      ],
    },
    {
      type: 'category',
      label: 'Tool Development',
      items: [
        'development/creating-tools',
        'development/base-tool-class',
        'development/tool-registration',
        'development/best-practices',
      ],
    },
    {
      type: 'category',
      label: 'Available Tools',
      items: [
        'tools/overview',
        'tools/filesystem',
        'tools/time-tools',
        'tools/browser-automation',
        'tools/document-management',
        'tools/data-tools',
      ],
    },
    {
      type: 'category',
      label: 'Deployment',
      items: [
        'deployment/docker',
        'deployment/sse-transport',
        'deployment/claude-desktop',
      ],
    },
    {
      type: 'category',
      label: 'API Reference',
      items: [
        'api/tool-interface',
        'api/registry',
        'api/configuration',
      ],
    },
  ],
};

export default sidebars;