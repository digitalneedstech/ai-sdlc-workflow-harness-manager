import type {ReactNode} from 'react';
import {useState} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';

import styles from './index.module.css';

type Mode = 'kit' | 'orchestrator';

const kitCommand = `uv tool install git+<repo-url>
cd /path/to/your-app
pipeline-kit init --ide cursor
pipeline-kit doctor --ide cursor`;

const orchestratorCommand = `uv tool install -e ".[orchestrator]"
cd /path/to/your-app
pipeline-kit init --mode orchestrator --ide cursor
pipeline-kit run --slug preview --workflow feature-development --dry-run`;

const cards = [
  {
    title: 'Allowlists',
    body: 'The loader writes allowed_reads for the current step. BA does not ingest the deploy runbook; the developer does not ingest Jira intake.',
    foot: 'allowed_reads',
  },
  {
    title: 'Model classifier',
    body: 'Jev picks the Cursor model from the step. Planning and review mark Composer a poor fit. Implementation marks it good.',
    foot: 'candidates',
  },
  {
    title: 'Thin adapters',
    body: 'Cursor, Claude Code, and GitHub get the same pack. The IDE folder exposes run-workflow only.',
    foot: '--ide cursor',
  },
  {
    title: 'Knowledge',
    body: 'knowledge init does not run Graphify. Extract writes graphify-out/graph.json. A human promotes the model.',
    foot: 'pipeline-kit knowledge init',
  },
  {
    title: 'Plugins',
    body: 'Graphify and Archify stay off until you install them. Init never turns these on.',
    foot: 'plugins install',
  },
  {
    title: 'Observability',
    body: 'obs install merges hooks into a local ledger, then Langfuse. Scores are deterministic.',
    foot: 'pipeline-kit obs install',
  },
];

const workflow = [
  {label: 'classify', to: '/docs/workflows/feature-development'},
  {label: 'plan', to: '/docs/workflows/feature-development'},
  {label: 'implement', to: '/docs/workflows/feature-development'},
  {label: 'verify', to: '/docs/workflows/feature-development'},
  {label: 'retro', to: '/docs/workflows/feature-development'},
];

const commands = [
  {
    command: 'pipeline-kit init',
    purpose: 'Install or update the project pack and its IDE adapter.',
  },
  {
    command: 'pipeline-kit update',
    purpose: 'Refresh managed files and keep local config.json values.',
  },
  {
    command: 'pipeline-kit doctor',
    purpose: 'Check Python, pack, config, loader, marker, and the IDE adapter.',
  },
  {
    command: 'pipeline-kit workflows',
    purpose: 'List workflows from the active project or user pack.',
  },
  {
    command: 'pipeline-kit run',
    purpose: 'Start or continue a code-owned orchestrator run.',
  },
];

const explore = [
  {
    title: 'Install',
    body: 'Install the CLI once per machine, then initialize a project.',
    to: '/docs/getting-started/install-cli',
  },
  {
    title: 'How it works',
    body: 'Portable pack, thin IDE adapter, per-step allowlists, config overlay.',
    to: '/docs/intro/how-it-works',
  },
  {
    title: 'Two kits',
    body: 'Markdown pack or Python engine. Same workflow names.',
    to: '/docs/capabilities/modes',
  },
  {
    title: 'Capabilities',
    body: 'What is on after init, and what stays opt-in.',
    to: '/docs/capabilities/overview',
  },
  {
    title: 'Workflows',
    body: 'Named procedures: ask, feature-development, Jira, knowledge bootstrap.',
    to: '/docs/capabilities/workflows',
  },
  {
    title: 'CLI',
    body: 'Pack, orchestrator, knowledge, plugins, and observability commands.',
    to: '/docs/reference/cli',
  },
];

function Terminal({text}: {text: string}): ReactNode {
  const lines = text.split('\n');
  return (
    <div className={styles.terminal}>
      <div className={styles.dots} aria-hidden="true">
        <span />
        <span />
        <span />
      </div>
      <pre>
        <code>
          {lines.map((line, index) => (
            <span key={`${index}-${line}`} className={styles.line}>
              <span className={styles.prompt}>$</span> {line}
              {index < lines.length - 1 ? '\n' : null}
            </span>
          ))}
        </code>
      </pre>
    </div>
  );
}

export default function Home(): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  const [mode, setMode] = useState<Mode>('kit');
  const command = mode === 'kit' ? kitCommand : orchestratorCommand;

  return (
    <Layout
      title={`${siteConfig.title}`}
      description="An operating model for enterprise agent factories. Repeatable process, the right model per step, opt-in knowledge and plugins.">
      <main className={styles.page}>
        <header className={styles.hero}>
          <h1>Pipeline Kit</h1>
          <p className={styles.lead}>
            Enterprise teams already have coding agents. They do not have a
            repeatable factory: the right workflow, the right model, and a pack
            that survives the next customer.
          </p>
          <p className={styles.sub}>
            Same process on every engagement. Overlay the customer in config, not in skills.
          </p>
          <div className={styles.actions}>
            <Link className={styles.primary} to="/docs/getting-started/install-cli">
              Get started
            </Link>
            <Link className={styles.secondary} to="/docs/intro/how-it-works">
              How it works
            </Link>
          </div>
        </header>

        <section className={styles.section} aria-labelledby="quickstart">
          <h2 id="quickstart">Get started in 60 seconds</h2>
          <div className={styles.switch} role="tablist" aria-label="Runtime">
            <button
              type="button"
              role="tab"
              id="tab-kit"
              aria-selected={mode === 'kit'}
              className={clsx(mode === 'kit' && styles.on)}
              onClick={() => setMode('kit')}>
              Kit
            </button>
            <button
              type="button"
              role="tab"
              id="tab-orchestrator"
              aria-selected={mode === 'orchestrator'}
              className={clsx(mode === 'orchestrator' && styles.on)}
              onClick={() => setMode('orchestrator')}>
              Orchestrator
            </button>
          </div>
          <div
            role="tabpanel"
            aria-labelledby={mode === 'kit' ? 'tab-kit' : 'tab-orchestrator'}>
            <Terminal text={command} />
          </div>
          <p className={styles.caption}>
            Then open the IDE. Kit mode runs through <code>run-workflow</code>. Orchestrator
            mode passes the ask with <code>--request</code>.
          </p>
        </section>

        <section className={styles.section} aria-labelledby="provides">
          <h2 id="provides">What Pipeline Kit provides</h2>
          <p className={styles.sectionLead}>
            Core delivery is on after init. Knowledge, plugins, and traces stay opt-in.
          </p>
          <div className={styles.cards}>
            {cards.map((card) => (
              <article key={card.title} className={styles.card}>
                <h3>{card.title}</h3>
                <p>{card.body}</p>
                <code>{card.foot}</code>
              </article>
            ))}
          </div>
        </section>

        <section className={styles.section} aria-labelledby="workflow">
          <h2 id="workflow">The development workflow</h2>
          <p className={styles.sectionLead}>
            From the ask to the retro, feature development structures the feature class.
          </p>
          <ol className={styles.pills}>
            {workflow.map((step, index) => (
              <li key={step.label}>
                {index > 0 ? <span className={styles.arrow} aria-hidden="true">→</span> : null}
                <Link className={styles.pill} to={step.to}>
                  {step.label}
                </Link>
              </li>
            ))}
          </ol>
          <p className={styles.caption}>
            Artifacts land in <code>features/&#123;slug&#125;/</code>.
          </p>
        </section>

        <section className={styles.section} aria-labelledby="cli">
          <h2 id="cli">CLI at a glance</h2>
          <div className={styles.tableWrap}>
            <table>
              <thead>
                <tr>
                  <th scope="col">Command</th>
                  <th scope="col">What it does</th>
                </tr>
              </thead>
              <tbody>
                {commands.map((row) => (
                  <tr key={row.command}>
                    <td>
                      <code>{row.command}</code>
                    </td>
                    <td>{row.purpose}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className={styles.section} aria-labelledby="explore">
          <h2 id="explore">Explore the docs</h2>
          <div className={styles.cards}>
            {explore.map((item) => (
              <Link key={item.title} className={styles.explore} to={item.to}>
                <h3>{item.title}</h3>
                <p>{item.body}</p>
              </Link>
            ))}
          </div>
        </section>
      </main>
    </Layout>
  );
}
