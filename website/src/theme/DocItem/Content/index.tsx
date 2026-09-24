import {type ReactNode} from 'react';
import clsx from 'clsx';
import {ThemeClassNames} from '@docusaurus/theme-common';
import {useDoc} from '@docusaurus/plugin-content-docs/client';
import Heading from '@theme/Heading';
import MDXContent from '@theme/MDXContent';
import type {Props} from '@theme/DocItem/Content';

export default function DocItemContent({children}: Props): ReactNode {
  const {metadata, frontMatter, contentTitle} = useDoc();
  const syntheticTitle =
    !frontMatter.hide_title && typeof contentTitle === 'undefined' ? metadata.title : null;
  const description =
    typeof frontMatter.description === 'string' ? frontMatter.description : metadata.description;

  return (
    <div className={clsx(ThemeClassNames.docs.docMarkdown, 'markdown')}>
      {syntheticTitle ? (
        <header>
          <Heading as="h1">{syntheticTitle}</Heading>
          {description ? <p className="pk-doc-lede">{description}</p> : null}
        </header>
      ) : null}
      <MDXContent>{children}</MDXContent>
    </div>
  );
}
