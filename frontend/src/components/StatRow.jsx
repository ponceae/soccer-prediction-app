import styles from './StatRow.module.css';

export default function StatRow({ label, home, away }) {
  const total = home + away;

  const homePct = total === 0 ? 50 : (home / total) * 100;
  const awayPct = total === 0 ? 50 : (away / total) * 100;

  return (
    <div className={styles['stat-row']}>
      <div className={styles['stat-values']}>
        <span className={styles['home-value']}>{home}</span>
        <span className={styles['stat-label']}>{label}</span>
        <span className={styles['away-value']}>{away}</span>
      </div>
      <div className={styles['bar-track']}>
        <span className={styles['home-bar']} style={{ width: `${homePct}%` }}/>
        <span className={styles['away-bar']} style={{ width: `${awayPct}%` }}/>
      </div>
    </div>
  )
}
