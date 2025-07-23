import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

const FeatureList = [
  {
    title: 'Dynamic Tool Registration',
    description: (
      <>
        Tools are automatically discovered and registered at runtime. 
        Just drop your tool in the tools directory and it's ready to use!
      </>
    ),
  },
  {
    title: 'Multiple Transport Options',
    description: (
      <>
        Support for both stdio (Claude Desktop) and SSE (Server-Sent Events) 
        transports. Choose the best option for your use case.
      </>
    ),
  },
  {
    title: 'Easy to Extend',
    description: (
      <>
        Built on a standardized base class system that makes creating new tools 
        straightforward. Comprehensive documentation included.
      </>
    ),
  },
];

function Feature({title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}