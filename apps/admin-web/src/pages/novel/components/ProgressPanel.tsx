import { ReloadOutlined } from '@ant-design/icons';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Alert, Button, Card, Descriptions, Space, Statistic, Tag } from 'antd';
import { getNovelProgress } from '@/services/novel';
import {
  canonAuthorityMap,
  canonStatusMap,
  chapterStatusMap,
  findingStatusMap,
  jobStageMap,
  severityMap,
  type VocabEntry,
} from '../vocab';

const Dots: React.FC<{
  data?: Record<string, number>;
  labels?: Record<string, VocabEntry>;
  danger?: string[];
}> = ({ data, labels, danger = [] }) => {
  const entries = Object.entries(data ?? {});
  if (entries.length === 0) return <>-</>;
  return (
    <Space size={4} wrap>
      {entries.map(([k, v]) => (
        <Tag key={k} color={danger.includes(k) ? 'red' : undefined}>
          {labels?.[k]?.label ?? k} {v}
        </Tag>
      ))}
    </Space>
  );
};

/**
 * 进度面板是作者的仪表盘：正典覆盖率、待裁定冲突、失败任务都要在这里露头。
 *
 * failed 的任务必须显红——链路自己会重试，作者看不见就会以为还在跑（§10.7）。
 */
const ProgressPanel: React.FC<{ bookId: number }> = ({ bookId }) => {
  const queryClient = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ['novel-progress', bookId],
    queryFn: () => getNovelProgress(bookId),
  });
  const view = data?.data;

  const failedJobs = view?.jobsByStage?.failed ?? 0;
  const openFindings = view?.findingsByStatus?.open ?? 0;
  const blockerFindings = view?.openFindingsBySeverity?.blocker ?? 0;
  const openForeshadows = view?.openForeshadows ?? 0;

  return (
    <Card
      title="写作进度"
      style={{ marginBottom: 16 }}
      loading={isLoading}
      extra={
        <Button
          size="small"
          icon={<ReloadOutlined />}
          onClick={() =>
            queryClient.invalidateQueries({
              queryKey: ['novel-progress', bookId],
            })
          }
        >
          刷新
        </Button>
      }
    >
      {failedJobs > 0 && (
        <Alert
          type="error"
          showIcon
          style={{ marginBottom: 16 }}
          message={`有 ${failedJobs} 个生成任务以失败收尾`}
          description="失败不会自动改写已定稿章节；要重跑还是放弃，由作者决定。"
        />
      )}
      {blockerFindings > 0 && (
        <Alert
          type="warning"
          showIcon
          style={{ marginBottom: 16 }}
          message={`有 ${blockerFindings} 条阻断级冲突待裁定`}
          description="阻断级未清空时章节不会自动定稿，去「冲突台账」处理。"
        />
      )}
      <Space size={48} wrap style={{ marginBottom: 16 }}>
        <Statistic title="章节数" value={view?.chapterCount ?? 0} />
        <Statistic title="总字数" value={view?.wordCount ?? 0} />
        <Statistic
          title="待裁定冲突"
          value={openFindings}
          valueStyle={openFindings > 0 ? { color: '#cf1322' } : undefined}
        />
        <Statistic
          title="未回收伏笔"
          value={openForeshadows}
          valueStyle={openForeshadows > 0 ? { color: '#fa8c16' } : undefined}
        />
      </Space>

      <Descriptions column={1} size="small" bordered>
        <Descriptions.Item label="章节状态">
          <Dots data={view?.chaptersByStatus} labels={chapterStatusMap} />
        </Descriptions.Item>
        <Descriptions.Item label="设定状态">
          <Dots
            data={view?.canonByStatus}
            labels={canonStatusMap}
            danger={['disputed', 'todo']}
          />
        </Descriptions.Item>
        <Descriptions.Item label="设定权威级">
          <Dots data={view?.canonByAuthority} labels={canonAuthorityMap} />
        </Descriptions.Item>
        <Descriptions.Item label="冲突裁定态">
          <Dots
            data={view?.findingsByStatus}
            labels={findingStatusMap}
            danger={['open']}
          />
        </Descriptions.Item>
        <Descriptions.Item label="未决冲突分级">
          <Dots
            data={view?.openFindingsBySeverity}
            labels={severityMap}
            danger={['blocker', 'major']}
          />
        </Descriptions.Item>
        <Descriptions.Item label="生成任务">
          <Dots
            data={view?.jobsByStage}
            labels={jobStageMap}
            danger={['failed']}
          />
        </Descriptions.Item>
      </Descriptions>
    </Card>
  );
};

export default ProgressPanel;
