import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';

import styles from './index.module.css';

const problems = [
  {
    n: '01',
    title: 'Context explosion',
    body: 'Every skill, brief, and wiki page under the IDE folder is auto-discovered. Cost and quality drop as the pack grows.',
  },
  {
    n: '02',
    title: 'Glued to one IDE',
    body: 'Process mixed with editor wiring. Moving from Cursor to Claude Code meant copying and rewriting the tree.',
  },
  {
    n: '03',
    title: 'Customer leakage',
    body: 'Ports, tracker projects, and folder names baked into skills. The next engagement could not reuse the pack.',
  },
  {
    n: '04',
    title: 'No productized install',
    body: 'Copying last year’s .cursor folder does not scale. Architects need project, user, and later org scopes.',
  },
  {
    n: '05',
    title: 'One ladder for every ask',
    body: 'A “how does tax work?” question should not start PM → BA → developer. Workflows are first-class.',
  },
  {
    n: '06',
    title: 'Hard to add a process',
    body: 'A new architecture review should be a workflow JSON + skill + config chain — not a new platform.',
  },
];

const capabilities = [
  {to: '/docs/capabilities/modes', title: 'Two kits', body: 'Kit mode is the markdown pack. Orchestrator mode is the Python engine. Same workflow names.'},
  {to: '/docs/capabilities/extensions', title: 'Extensions', body: 'Add a workflow in kit mode (JSON + skill) or orchestrator mode (pipeline_extensions).'},
  {to: '/docs/capabilities/workflows', title: 'Workflows', body: 'ask, feature-development, Jira story/epic/bug, QA bootstrap.'},
  {to: '/docs/capabilities/knowledge', title: 'Knowledge base', body: 'Opt-in QA overlay from a Graphify graph, then human promote.'},
  {to: '/docs/capabilities/plugins', title: 'Plugins', body: 'Optional Graphify, Archify, and bundled agent-run observability. Init does not turn them on.'},
  {to: '/docs/capabilities/observability', title: 'Observability', body: 'Agent-run traces and scores to a local ledger, then Langfuse.'},
  {to: '/docs/capabilities/planning-gates', title: 'Planning gates', body: 'Human sign-off on requirements, architecture, and BA specs.'},
  {to: '/docs/capabilities/loader', title: 'Allowlist loader', body: 'Each specialist reads only the files for the current step.'},
  {to: '/docs/capabilities/feature-flags', title: 'Feature flags', body: 'Toggle test design, Playwright, telemetry, Jira, and obs.'},
  {to: '/docs/capabilities/wiki', title: 'Agent wiki', body: 'Trigger-routed operational memory. Load one page, not the folder.'},
];

const audiences = [
  {
    to: '/docs/getting-started/install-cli',
    title: 'New users',
    body: 'Install the CLI, init a project, run doctor, then try ask and a small change.',
  },
  {
    to: '/docs/capabilities/overview',
    title: 'Regular users',
    body: 'Workflows, knowledge, plugins, observability, and CLI reference.',
  },
  {
    to: '/docs/guides/agents-md',
    title: 'Architects & leads',
    body: 'Adapt AGENTS.md, config, deploy, and tests for each engagement.',
  },
];

export default function Home(): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`${siteConfig.title} documentation`}
      description="Portable workflow pack and installer for coding agents. Process lives in .pipeline. The IDE is a thin adapter.">
      <header className={styles.hero}>
        <div className={styles.heroInner}>
          <div>
            <div className={styles.kicker}>Two kits. One product.</div>
            <Heading as="h1" className={styles.heroTitle}>
              One product. Two ways to run it.
            </Heading>
            <p className={styles.heroLead}>
              Pipeline Kit is a portable operating model for coding agents.
              <strong> Kit mode</strong> is the markdown pack in
              <code> .pipeline</code>. <strong> Orchestrator mode</strong> is
              the same workflow names driven from Python. Pick one per project
              at <code>init</code>.
            </p>
            <div className={styles.actions}>
              <Link className={clsx('button button--lg', styles.primaryBtn)} to="/docs/capabilities/modes">
                Compare the two kits
              </Link>
              <Link className="button button--lg button--secondary" to="/docs/getting-started/install-cli">
                Install locally
              </Link>
            </div>
          </div>
          <div className={styles.panel}>
            <div className={styles.panelLabel}>Quick start</div>
            <pre>
              <code>{`uv tool install git+<repo-url>
cd /path/to/your-app
pipeline-kit init --ide cursor
pipeline-kit doctor --ide cursor
pipeline-kit workflows`}</code>
            </pre>
          </div>
        </div>
      </header>

      <main>
        <section className={styles.section}>
          <div className={styles.wrap}>
            <Heading as="h2" className={styles.sectionTitle}>Problems it solves</Heading>
            <p className={styles.sectionLead}>
              Teams already use coding agents. What they lack is a repeatable
              operating model. Read the six failures, then how the architecture
              answers them.
            </p>
            <div className={styles.grid3}>
              {problems.map((item) => (
                <div key={item.n} className={styles.card}>
                  <span className={styles.num}>{item.n}</span>
                  <h3>{item.title}</h3>
                  <p>{item.body}</p>
                </div>
              ))}
            </div>
            <p style={{marginTop: '1.25rem'}}>
              <Link to="/docs/intro/problems">Full problem statement →</Link>
            </p>
          </div>
        </section>

        <section className={clsx(styles.section, styles.sectionAlt)}>
          <div className={styles.wrap}>
            <Heading as="h2" className={styles.sectionTitle}>Two kits</Heading>
            <p className={styles.sectionLead}>
              Same first-party names — ask, feature-development, Jira.
              Different control surface. Choose one at init and stay there.
            </p>
            <div className={styles.grid2}>
              <Link className={styles.card} to="/docs/capabilities/modes">
                <span className={styles.num}>KIT MODE — DEFAULT</span>
                <h3>The markdown pack</h3>
                <p>
                  <code>pipeline-kit init --ide cursor</code>
                  <br />
                  Skills, briefs, and the loader live in <code>.pipeline/</code>.
                  The IDE only exposes <code>run-workflow</code>. This is what
                  most customer engagements should use.
                </p>
              </Link>
              <Link className={styles.card} to="/docs/capabilities/modes">
                <span className={styles.num}>ORCHESTRATOR MODE</span>
                <h3>The Python engine</h3>
                <p>
                  <code>pipeline-kit init --mode orchestrator --ide cursor</code>
                  <br />
                  The chain lives in the wheel. You drive it with
                  <code> run</code>, <code>approve</code>, and
                  <code> resume</code>. Chat text is not inherited — pass
                  <code>--request</code>.
                </p>
              </Link>
            </div>
            <p style={{marginTop: '1.25rem'}}>
              <Link to="/docs/capabilities/modes">Full comparison, when to pick which, and commands →</Link>
            </p>
          </div>
        </section>

        <section className={styles.section}>
          <div className={styles.wrap}>
            <Heading as="h2" className={styles.sectionTitle}>How it is wired</Heading>
            <p className={styles.sectionLead}>
              Kit mode: a thin IDE adapter calls the receptionist; the pack
              owns process; the loader allowlists the current step.
              Orchestrator mode: <code>pipeline-kit run</code> drives the
              same names from the wheel.
            </p>
            <div className={styles.flow}>
              <div className={styles.flowRow}>IDE adapter — one skill (.cursor | .claude | .github | none)</div>
              <div className={styles.flowArrow}>↓</div>
              <div className={styles.flowRow}>run-workflow — pick a workflow, run the loader</div>
              <div className={styles.flowArrow}>↓</div>
              <div className={styles.flowRow}>.pipeline pack (kit) or orchestrator engine — same workflow names</div>
              <div className={styles.flowArrow}>↓</div>
              <div className={styles.flowRow}>config.json overlay + features/ artifacts for this run</div>
            </div>
            <p style={{marginTop: '1.25rem'}}>
              <Link to="/docs/intro/how-it-works">Architecture in detail →</Link>
              {' · '}
              <Link to="/docs/intro/repo-layout">Repository layout →</Link>
            </p>
          </div>
        </section>

        <section className={clsx(styles.section, styles.sectionAlt)}>
          <div className={styles.wrap}>
            <Heading as="h2" className={styles.sectionTitle}>Capabilities</Heading>
            <p className={styles.sectionLead}>
              Core delivery is installed with init. Knowledge, plugins, and
              agent-run observability are opt-in.
            </p>
            <div className={styles.grid4}>
              {capabilities.map((item) => (
                <Link key={item.to} className={styles.card} to={item.to}>
                  <h3>{item.title}</h3>
                  <p>{item.body}</p>
                </Link>
              ))}
            </div>
          </div>
        </section>

        <section className={styles.section}>
          <div className={styles.wrap}>
            <Heading as="h2" className={styles.sectionTitle}>Who this guide is for</Heading>
            <p className={styles.sectionLead}>
              Same handbook, three entry points — pick by what you need to do.
            </p>
            <div className={styles.audience}>
              {audiences.map((item) => (
                <Link key={item.to} className={styles.card} to={item.to}>
                  <h3>{item.title}</h3>
                  <p>{item.body}</p>
                </Link>
              ))}
            </div>
          </div>
        </section>
      </main>
    </Layout>
  );
}
