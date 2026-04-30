import { useState, useEffect, useCallback } from 'react';
import { Clock, RotateCcw } from 'lucide-react';
import Button from '../../components/common/Button.jsx';
import Modal from '../../components/common/Modal.jsx';
import LoadingState from '../../components/common/LoadingState.jsx';
import EmptyState from '../../components/common/EmptyState.jsx';
import { useToast } from '../../components/common/Toast.jsx';
import { listVersions, createVersion, restoreVersion, compareVersions } from '../../api/versions.js';
import { formatDateTime } from '../../utils/date.js';
import './HistoryTab.css';

export default function HistoryTab({ contractId, onContractUpdate }) {
  const { showToast } = useToast();
  const [versions, setVersions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [snapshotLoading, setSnapshotLoading] = useState(false);
  const [restoreTarget, setRestoreTarget] = useState(null);
  const [diffData, setDiffData] = useState(null);
  const [diffLoading, setDiffLoading] = useState(false);

  const load = useCallback(() => {
    setLoading(true);
    listVersions(contractId)
      .then((d) => setVersions(Array.isArray(d) ? d : d?.versions || []))
      .catch(() => setVersions([]))
      .finally(() => setLoading(false));
  }, [contractId]);

  useEffect(() => { load(); }, [load]);

  const handleSnapshot = async () => {
    setSnapshotLoading(true);
    try {
      await createVersion(contractId);
      showToast('Snapshot created', 'success');
      load();
    } catch (err) { showToast(err.message, 'error'); }
    finally { setSnapshotLoading(false); }
  };

  const handleRestore = async () => {
    try {
      await restoreVersion(contractId, restoreTarget.version_number);
      showToast(`Restored to version ${restoreTarget.version_number}`, 'success');
      setRestoreTarget(null);
      onContractUpdate();
      load();
    } catch (err) { showToast(err.message, 'error'); }
  };

  const handleDiff = async (v1, v2) => {
    setDiffLoading(true);
    try {
      const d = await compareVersions(contractId, v1, v2);
      setDiffData(d);
    } catch (err) { showToast(err.message, 'error'); }
    finally { setDiffLoading(false); }
  };

  if (loading) return <LoadingState />;

  return (
    <div className="history-tab">
      <div className="history-header">
        <div>
          <h3>Version History</h3>
          <p>Each snapshot captures the current clause set and all parameter values.</p>
        </div>
        <Button
          variant="secondary"
          size="sm"
          icon={Clock}
          loading={snapshotLoading}
          onClick={handleSnapshot}
        >
          Save Snapshot
        </Button>
      </div>

      {versions.length === 0 ? (
        <EmptyState
          icon={Clock}
          title="No versions yet"
          description="Create a snapshot to save the current state of this contract."
          action={
            <Button loading={snapshotLoading} onClick={handleSnapshot} icon={Clock}>
              Save Snapshot
            </Button>
          }
        />
      ) : (
        <div className="version-list">
          {versions.map((v, idx) => (
            <div key={v.id} className="version-item">
              <div className="version-item__indicator">
                <div className="version-item__dot" />
                {idx < versions.length - 1 && <div className="version-item__line" />}
              </div>
              <div className="version-item__content">
                <div className="version-item__header">
                  <span className="version-item__num text-mono">v{v.version_number}</span>
                  <span className="version-item__date">{formatDateTime(v.created_at)}</span>
                </div>
                {v.change_summary && (
                  <p className="version-item__summary">{v.change_summary}</p>
                )}
                <div className="version-item__actions">
                  {idx > 0 && (
                    <Button variant="ghost" size="sm" onClick={() => handleDiff(v.version_number, versions[idx - 1].version_number)}>
                      Compare with v{versions[idx - 1].version_number}
                    </Button>
                  )}
                  <Button variant="ghost" size="sm" icon={RotateCcw} onClick={() => setRestoreTarget(v)}>
                    Restore
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Restore confirmation */}
      <Modal
        isOpen={!!restoreTarget}
        onClose={() => setRestoreTarget(null)}
        title="Restore Version"
        footer={
          <>
            <Button variant="ghost" onClick={() => setRestoreTarget(null)}>Cancel</Button>
            <Button variant="danger" onClick={handleRestore}>Restore</Button>
          </>
        }
      >
        <p>Restore to <strong>version {restoreTarget?.version_number}</strong>? Current changes will be overwritten.</p>
      </Modal>

      {/* Diff modal */}
      <Modal
        isOpen={!!diffData}
        onClose={() => setDiffData(null)}
        title="Version Comparison"
        size="xl"
      >
        {diffLoading ? <LoadingState /> : (
          <pre className="history-diff">{JSON.stringify(diffData, null, 2)}</pre>
        )}
      </Modal>
    </div>
  );
}
