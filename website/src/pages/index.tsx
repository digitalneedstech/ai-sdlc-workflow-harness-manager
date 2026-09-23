import type {ReactNode} from 'react';
import {useEffect, useState} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';

import styles from './index.module.css';

type Mode = 'kit' | 'orchestrator';

const sections = [
  {id: 'problems', label: 'Problems'},
  {id: 'kits', label: 'Two kits'},
  {id: 'models', label: 'Model choice'},
  {id: 'wiring', label: 'How it runs'},
  {id: 'capabilities', label: 'Capabilities'},
  {id: 'start', label: 'Start'},
];

const kitCommand = `uv tool install git+<repo-url>
cd /path/to/your-app
pipeline-kit init --ide cursor
pipeline-kit doctor --ide cursor
pipeline-kit workflows`;

const orchestratorCommand = `uv tool install -e ".[orchestrator]"
cd /path/to/your-app
pipeline-kit init --mode orchestrator --ide cursor
pipeline-kit run --slug preview --workflow feature-development \\
  --change-class feature --dry-run --request "redesign checkout"`;

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

const agents = [
  {
    id: 'pm',
    label: 'Product manager',
    need: 'planning: write requirements, scope, and acceptance criteria.',
    prefer: 'claude-opus-5 · gpt-5.5 · gpt-5.6-sol',
    composer: 'Poor fit for this agent. Do not pick for planning.',
    reasoning: 'Good fit for this agent. Prefer this over Composer.',
  },
  {
    id: 'architect',
    label: 'Architect',
    need: 'architecture: choose structure, boundaries, and tradeoffs.',
    prefer: 'claude-opus-5 · gpt-5.5 · gpt-5.6-sol',
    composer: 'Poor fit for this agent. Do not pick for architecture.',
    reasoning: 'Good fit for this agent. Prefer this over Composer.',
  },
  {
    id: 'dev',
    label: 'Developer',
    need: 'implementation: edit code and fix defects.',
    prefer: 'composer-2.5',
    composer: 'Good fit for this agent.',
    reasoning: 'Capable but heavier than needed. Prefer Composer.',
  },
  {
    id: 'critic',
    label: 'Critic',
    need: 'review: find gaps, contradictions, and missing acceptance criteria.',
    prefer: 'claude-opus-5 · gpt-5.5',
    composer: 'Poor fit for this agent. Do not pick for review.',
    reasoning: 'Good fit for this agent. Prefer this over Composer.',
  },
  {
    id: 'tester',
    label: 'Tester',
    need: 'verification: follow test instructions and inspect code.',
    prefer: 'composer-2.5',
    composer: 'Good fit for this agent.',
    reasoning: 'Capable but heavier than needed. Prefer Composer.',
  },
];

const sentModels = [
  'composer-2.5',
  'grok-4.5',
  'grok-4.6',
  'grok-4.7',
  'claude-opus-5',
  'gpt-5.5',
  'gpt-5.6-sol',
];

const flow = [
  {title: 'Adapter', body: 'One IDE skill — Cursor, Claude Code, GitHub, or none.'},
  {title: 'Control', body: 'Kit: run-workflow. Orchestrator: pipeline-kit run / approve / resume.'},
  {title: 'Process', body: 'Same workflow names. Pack files or the sealed Python graph.'},
  {title: 'Artifacts', body: 'features/{slug}/ plus the project config overlay.'},
];

function CopyButton({text}: {text: string}): ReactNode {
  const [copied, setCopied] = useState(false);

  return (
    <button
      type="button"
      className={styles.copyBtn}
      onClick={() => {
        if (!navigator.clipboard) {
          return;
        }
        navigator.clipboard.writeText(text).then(() => {
          setCopied(true);
          window.setTimeout(() => setCopied(false), 1600);
        });
      }}>
      {copied ? 'Copied' : 'Copy'}
    </button>
  );
}

export default function Home(): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  const [mode, setMode] = useState<Mode>('kit');
  const [active, setActive] = useState(sections[0].id);
  const [agentId, setAgentId] = useState(agents[0].id);
  const command = mode === 'kit' ? kitCommand : orchestratorCommand;
  const agent = agents.find((item) => item.id === agentId) ?? agents[0];

  useEffect(() => {
    const nodes = sections
      .map((item) => document.getElementById(item.id))
      .filter((node): node is HTMLElement => Boolean(node));
    if (!nodes.length) {
      return undefined;
    }
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((left, right) => right.intersectionRatio - left.intersectionRatio)[0];
        if (visible?.target.id) {
          setActive(visible.target.id);
        }
      },
      {rootMargin: '-28% 0px -55% 0px', threshold: [0.15, 0.4, 0.7]},
    );
    nodes.forEach((node) => observer.observe(node));
    return () => observer.disconnect();
  }, []);

  const goTo = (id: string) => {
    const node = document.getElementById(id);
    node?.scrollIntoView({behavior: 'smooth', block: 'start'});
  };

  return (
    <Layout
      title={`${siteConfig.title} documentation`}
      description="Portable workflow pack and installer for coding agents. Process lives in .pipeline. The IDE is a thin adapter.">
      <div className={styles.page}>
        <header className={styles.hero}>
          <div className={styles.heroInner}>
            <div>
              <p className={styles.kicker}>Portable operating model</p>
              <Heading as="h1" className={styles.heroTitle}>
                One product. Two ways to run it.
              </Heading>
              <p className={styles.heroLead}>
                Pipeline Kit is a repeatable process for coding agents.
                <strong> Kit mode</strong> is the markdown pack in
                <code> .pipeline</code>. <strong>Orchestrator mode</strong> is
                the same workflow names driven from Python, with a shortlist
                of Cursor models chosen per agent.
              </p>
              <div className={styles.actions}>
                <Link className={clsx('button button--lg', styles.primaryBtn)} to="/docs/getting-started/install-cli">
                  Install locally
                </Link>
                <Link className="button button--lg button--secondary" to="/docs/capabilities/modes">
                  Compare the two kits
                </Link>
              </div>
            </div>
            <div className={styles.panel}>
              <div className={styles.panelHead}>
                <div className={styles.switch} role="tablist" aria-label="Install mode">
                  <button
                    type="button"
                    role="tab"
                    aria-selected={mode === 'kit'}
                    className={clsx(styles.switchBtn, mode === 'kit' && styles.switchOn)}
                    onClick={() => setMode('kit')}>
                    Kit mode
                  </button>
                  <button
                    type="button"
                    role="tab"
                    aria-selected={mode === 'orchestrator'}
                    className={clsx(styles.switchBtn, mode === 'orchestrator' && styles.switchOn)}
                    onClick={() => setMode('orchestrator')}>
                    Orchestrator
                  </button>
                </div>
                <CopyButton text={command} />
              </div>
              <p className={styles.panelHint}>
                {mode === 'kit'
                  ? 'Default. Skills and the loader live in the project pack.'
                  : 'Sealed graph. Pass --request. Set CURSOR_API_KEY and TYPESAFE_API_KEY.'}
              </p>
              <pre>
                <code>{command}</code>
              </pre>
            </div>
          </div>
        </header>

        <nav className={styles.rail} aria-label="On this page">
          {sections.map((item) => (
            <button
              key={item.id}
              type="button"
              className={clsx(styles.railBtn, active === item.id && styles.railOn)}
              onClick={() => goTo(item.id)}>
              {item.label}
            </button>
          ))}
        </nav>

        <main>
          <section className={styles.stats}>
            <div className={styles.wrap}>
              <div className={styles.statGrid}>
                <div>
                  <strong>2</strong>
                  <span>runtimes, one set of workflow names</span>
                </div>
                <div>
                  <strong>7</strong>
                  <span>default models sent to Jev, not the full catalog</span>
                </div>
                <div>
                  <strong>1</strong>
                  <span>IDE skill. Process stays in the pack or the wheel</span>
                </div>
              </div>
            </div>
          </section>

          <section id="problems" className={styles.section}>
            <div className={styles.wrap}>
              <Heading as="h2" className={styles.sectionTitle}>Problems it solves</Heading>
              <p className={styles.sectionLead}>
                Teams already use coding agents. What they lack is a repeatable
                operating model.
              </p>
              <div className={styles.grid3}>
                {problems.map((item) => (
                  <article key={item.n} className={styles.card}>
                    <span className={styles.num}>{item.n}</span>
                    <h3>{item.title}</h3>
                    <p>{item.body}</p>
                  </article>
                ))}
              </div>
              <p className={styles.more}>
                <Link to="/docs/intro/problems">Full problem statement →</Link>
              </p>
            </div>
          </section>

          <section id="kits" className={clsx(styles.section, styles.sectionAlt)}>
            <div className={styles.wrap}>
              <Heading as="h2" className={styles.sectionTitle}>Two kits</Heading>
              <p className={styles.sectionLead}>
                Same first-party names — ask, feature-development, Jira.
                Different control surface. Choose one at init and stay there.
              </p>
              <div className={styles.grid2}>
                <button
                  type="button"
                  className={clsx(styles.choice, mode === 'kit' && styles.choiceOn)}
                  onClick={() => setMode('kit')}>
                  <span className={styles.num}>Kit mode — default</span>
                  <h3>The markdown pack</h3>
                  <p>
                    <code>pipeline-kit init --ide cursor</code>
                    <br />
                    Skills, briefs, and the loader live in <code>.pipeline/</code>.
                    The IDE only exposes <code>run-workflow</code>.
                  </p>
                </button>
                <button
                  type="button"
                  className={clsx(styles.choice, mode === 'orchestrator' && styles.choiceOn)}
                  onClick={() => setMode('orchestrator')}>
                  <span className={styles.num}>Orchestrator mode</span>
                  <h3>The Python engine</h3>
                  <p>
                    <code>pipeline-kit init --mode orchestrator --ide cursor</code>
                    <br />
                    Drive the chain with <code>run</code>, <code>approve</code>,
                    and <code>resume</code>. Pass <code>--request</code>. Chat
                    text is not inherited.
                  </p>
                </button>
              </div>
              <p className={styles.more}>
                <Link to="/docs/capabilities/modes">Full comparison and commands →</Link>
              </p>
            </div>
          </section>

          <section id="models" className={styles.section}>
            <div className={styles.wrap}>
              <Heading as="h2" className={styles.sectionTitle}>Model choice</Heading>
              <p className={styles.sectionLead}>
                In orchestrator mode, Jev picks a Cursor model per agent from a
                shortlist. Planning and review prefer Opus or GPT.
                Implementation prefers Composer. Add a model in
                <code> candidates</code> or in <code> cards</code> — not both.
              </p>
              <div className={styles.agentRow} role="tablist" aria-label="Agent capability">
                {agents.map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    role="tab"
                    aria-selected={agent.id === item.id}
                    className={clsx(styles.chip, agent.id === item.id && styles.chipOn)}
                    onClick={() => setAgentId(item.id)}>
                    {item.label}
                  </button>
                ))}
              </div>
              <div className={styles.modelPanel}>
                <div>
                  <h3>{agent.label}</h3>
                  <dl className={styles.meta}>
                    <div>
                      <dt>Need</dt>
                      <dd>{agent.need}</dd>
                    </div>
                    <div>
                      <dt>Prefer</dt>
                      <dd>{agent.prefer}</dd>
                    </div>
                    <div>
                      <dt>Sent to Jev</dt>
                      <dd>{sentModels.join(', ')}</dd>
                    </div>
                  </dl>
                </div>
                <div className={styles.fitList}>
                  <div>
                    <span>composer-2.5</span>
                    <p>{agent.composer}</p>
                  </div>
                  <div>
                    <span>claude-opus-5 / gpt-5.5</span>
                    <p>{agent.reasoning}</p>
                  </div>
                </div>
              </div>
              <p className={styles.more}>
                Handbook: <code>CUSTOMER-GUIDE.md</code> § Model choice ·{' '}
                <Link to="/docs/capabilities/modes">Two kits →</Link>
              </p>
            </div>
          </section>

          <section id="wiring" className={clsx(styles.section, styles.sectionAlt)}>
            <div className={styles.wrap}>
              <Heading as="h2" className={styles.sectionTitle}>How it runs</Heading>
              <p className={styles.sectionLead}>
                The IDE is a thin adapter. Process lives in the pack or the
                wheel. Run artifacts always land in this project’s
                <code> features/</code>.
              </p>
              <ol className={styles.flow}>
                {flow.map((item, index) => (
                  <li key={item.title}>
                    <span>{String(index + 1).padStart(2, '0')}</span>
                    <div>
                      <strong>{item.title}</strong>
                      <p>{item.body}</p>
                    </div>
                  </li>
                ))}
              </ol>
              <p className={styles.more}>
                <Link to="/docs/intro/how-it-works">Architecture in detail →</Link>
                {' · '}
                <Link to="/docs/intro/repo-layout">Repository layout →</Link>
              </p>
            </div>
          </section>

          <section id="capabilities" className={styles.section}>
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

          <section id="start" className={clsx(styles.section, styles.sectionAlt)}>
            <div className={styles.wrap}>
              <Heading as="h2" className={styles.sectionTitle}>Who this guide is for</Heading>
              <p className={styles.sectionLead}>
                Same handbook, three entry points. The customer adaptation
                guide stays in the repo as <code>CUSTOMER-GUIDE.md</code> and
                is copied on <code>init</code>.
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
      </div>
    </Layout>
  );
}
