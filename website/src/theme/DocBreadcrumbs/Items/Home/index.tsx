import {type ReactNode} from 'react';
import Link from '@docusaurus/Link';
import {useHomePageRoute} from '@docusaurus/theme-common/internal';

export default function HomeBreadcrumbItem(): ReactNode {
  const home = useHomePageRoute();
  if (!home) {
    return null;
  }
  return (
    <li className="breadcrumbs__item">
      <Link className="breadcrumbs__link" to={home.to}>
        Home
      </Link>
    </li>
  );
}
