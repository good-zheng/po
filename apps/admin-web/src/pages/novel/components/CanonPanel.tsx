import { PlusOutlined } from '@ant-design/icons';
import {
  type ActionType,
  ModalForm,
  ProFormDigit,
  ProFormSelect,
  ProFormText,
  ProFormTextArea,
  ProTable,
} from '@ant-design/pro-components';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Alert,
  Badge,
  Button,
  message,
  Popconfirm,
  Space,
  Tag,
  Typography,
} from 'antd';
import { useRef, useState } from 'react';
import {
  type CanonEntry,
  type CanonRequest,
  createCanon,
  getCanon,
  getCanonConflicts,
  retireCanon,
  updateCanon,
} from '@/services/novel';
import {
  canonAuthorityMap,
  canonKindMap,
  canonStatusMap,
  toOptions,
  toValueEnum,
} from '../vocab';

/** 生效区间：NULL 的右端点写「至今」，闭掉的写章号——作者扫一眼就知道哪条还活着 */
const rangeText = (row: CanonEntry) =>
  `第 ${row.validFromChapter} 章 ~ ${
    row.validUntilChapter == null ? '至今' : `第 ${row.validUntilChapter} 章`
  }`;

type Editing =
  | { mode: 'create' }
  | { mode: 'update'; target: CanonEntry }
  | null;

const CanonPanel: React.FC<{ bookId: number }> = ({ bookId }) => {
  const [messageApi, contextHolder] = message.useMessage();
  const queryClient = useQueryClient();
  const actionRef = useRef<ActionType>(null);
  const [editing, setEditing] = useState<Editing>(null);
  // 冲突预览未做过就为空：作者点头前必须先看到「要覆盖哪条、旧区间是否关闭」（§10.6）
  const [conflicts, setConflicts] = useState<CanonEntry[] | null>(null);

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ['novel-canon', bookId] });
    queryClient.invalidateQueries({ queryKey: ['novel-progress', bookId] });
  };

  const targetId = editing?.mode === 'update' ? editing.target.id : undefined;

  const saveMutation = useMutation({
    mutationFn: (vars: { canonId?: number; body: CanonRequest }) =>
      vars.canonId == null
        ? createCanon(bookId, vars.body)
        : updateCanon(vars.canonId, vars.body),
    onSuccess: () => {
      messageApi.success('已保存为设定（作者级）');
      setEditing(null);
      setConflicts(null);
      invalidate();
      actionRef.current?.reload();
    },
    onError: (err: Error) => messageApi.error(err.message || '保存失败'),
  });

  const retireMutation = useMutation({
    mutationFn: (canonId: number) => retireCanon(canonId, {}),
    onSuccess: () => {
      messageApi.success('已停用（闭有效期，不删历史）');
      invalidate();
      actionRef.current?.reload();
    },
    onError: (err: Error) => messageApi.error(err.message || '停用失败'),
  });

  const conflictMutation = useMutation({
    mutationFn: (body: CanonRequest) =>
      getCanonConflicts(bookId, {
        subjectKey: body.subjectKey,
        predicate: body.predicate,
        objectText: body.objectText,
        // 编辑自己不算撞车：库里存的还是旧值，不排除就会把这一条报成「与自己并存」
        excludeId: targetId,
      }),
    onSuccess: async (res, body) => {
      const rows = res.data ?? [];
      if (rows.length === 0) {
        // 没有撞车就直接落库，不让作者多点一次「确认」
        await saveMutation.mutateAsync({ canonId: targetId, body });
        return;
      }
      setConflicts(rows);
    },
    onError: (err: Error) => messageApi.error(err.message || '冲突预览失败'),
  });

  return (
    <>
      {contextHolder}
      <ProTable<CanonEntry>
        rowKey="id"
        size="small"
        actionRef={actionRef}
        search={{ labelWidth: 'auto' }}
        pagination={{ pageSize: 20, showSizeChanger: true }}
        toolBarRender={() => [
          <Button
            key="new"
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => {
              setConflicts(null);
              setEditing({ mode: 'create' });
            }}
          >
            新增设定
          </Button>,
        ]}
        request={async (params) => {
          try {
            const res = await getCanon(bookId, {
              page: (params.current ?? 1) - 1,
              size: params.pageSize ?? 20,
              subjectKey: params.subjectKey,
              kind: params.kind,
              status: params.status,
              authority: params.authority,
              keyword: params.keyword,
            });
            return {
              data: res.data?.content ?? [],
              total: res.data?.totalElements ?? 0,
              success: true,
            };
          } catch (err) {
            messageApi.error(
              err instanceof Error ? err.message : '加载设定失败',
            );
            return { data: [], total: 0, success: false };
          }
        }}
        columns={[
          {
            title: '实体键',
            dataIndex: 'subjectKey',
            width: 180,
            ellipsis: true,
            render: (_: unknown, row) => (
              <Typography.Text copyable>{row.subjectKey}</Typography.Text>
            ),
          },
          {
            title: '谓词',
            dataIndex: 'predicate',
            width: 140,
            ellipsis: true,
            search: false,
          },
          {
            title: '值',
            dataIndex: 'objectText',
            search: false,
            ellipsis: true,
          },
          {
            title: '关键词',
            dataIndex: 'keyword',
            hideInTable: true,
            fieldProps: { placeholder: '搜实体/谓词/值/自然语言' },
          },
          {
            title: '权威级',
            dataIndex: 'authority',
            width: 100,
            valueEnum: toValueEnum(canonAuthorityMap),
            render: (_: unknown, row) => {
              const a = canonAuthorityMap[row.authority];
              return (
                <Badge
                  status={a?.badge ?? 'default'}
                  text={a?.label ?? row.authority}
                />
              );
            },
          },
          {
            title: '类型',
            dataIndex: 'kind',
            width: 110,
            hideInTable: true,
            valueType: 'select',
            fieldProps: { options: toOptions(canonKindMap) },
          },
          {
            title: '生效区间',
            search: false,
            width: 180,
            render: (_: unknown, row) => rangeText(row),
          },
          {
            title: '状态',
            dataIndex: 'status',
            width: 90,
            valueEnum: toValueEnum(canonStatusMap),
            render: (_: unknown, row) => {
              const s = canonStatusMap[row.status];
              return (
                <Tag color={s?.color ?? 'default'}>
                  {s?.label ?? row.status}
                </Tag>
              );
            },
          },
          {
            title: '操作',
            key: 'action',
            width: 120,
            search: false,
            render: (_: unknown, row) => (
              <Space size="small">
                <a
                  onClick={() => {
                    setConflicts(null);
                    setEditing({ mode: 'update', target: row });
                  }}
                >
                  编辑
                </a>
                <Popconfirm
                  title="停用这条设定"
                  description="只闭有效期，不物理删除——历史章节的引用要保持可查。"
                  okText="确认"
                  cancelText="取消"
                  onConfirm={() => retireMutation.mutate(row.id)}
                >
                  <a style={{ color: '#ff4d4f' }}>停用</a>
                </Popconfirm>
              </Space>
            ),
          },
        ]}
      />

      <ModalForm<CanonRequest>
        key={targetId == null ? 'canon-new' : `canon-${targetId}`}
        title={targetId == null ? '新增设定条目' : '编辑设定条目'}
        width={640}
        open={!!editing}
        onOpenChange={(open) => {
          if (!open) {
            setEditing(null);
            setConflicts(null);
          }
        }}
        modalProps={{ destroyOnClose: true, maskClosable: false }}
        submitter={{
          searchConfig: { submitText: '保存为作者设定', resetText: '取消' },
          submitButtonProps: {
            loading: saveMutation.isPending || conflictMutation.isPending,
          },
        }}
        initialValues={
          editing?.mode === 'update'
            ? {
                kind: editing.target.kind,
                subjectKey: editing.target.subjectKey,
                predicate: editing.target.predicate,
                objectText: editing.target.objectText,
                restatement: editing.target.restatement ?? '',
                validFromChapter: editing.target.validFromChapter,
                validUntilChapter:
                  editing.target.validUntilChapter ?? undefined,
                status: editing.target.status,
              }
            : { kind: 'character', status: 'confirmed' }
        }
        // 冲突未确认前返回 false，让弹窗停在原地
        onFinish={async (values) => {
          if (conflicts === null) {
            conflictMutation.mutate(values);
            return false;
          }
          await saveMutation.mutateAsync({ canonId: targetId, body: values });
          return true;
        }}
      >
        {conflicts && conflicts.length > 0 && (
          <Alert
            type="warning"
            showIcon
            style={{ marginBottom: 16 }}
            message={`同主同谓的已生效设定条目有 ${conflicts.length} 条，保存后设定里会并存`}
            description={
              <Space direction="vertical" size={4}>
                {conflicts.map((c) => (
                  <Typography.Text key={c.id} type="secondary">
                    [{canonAuthorityMap[c.authority]?.label ?? c.authority}]{' '}
                    {c.subjectKey} · {c.predicate} = {c.objectText}（
                    {rangeText(c)}）
                  </Typography.Text>
                ))}
                <Typography.Text type="secondary">
                  要旧区间闭到本章，请在台账里对相应冲突做「采纳裁定」；确认并存请再点一次保存。
                </Typography.Text>
              </Space>
            }
          />
        )}
        <ProFormText
          name="subjectKey"
          label="实体键"
          placeholder="char:shenqing / loc:yuncheng"
          tooltip="别名归一后的稳定键，不是人物显示名"
          rules={[{ required: true, message: '请输入实体键' }]}
        />
        <ProFormText
          name="predicate"
          label="谓词"
          placeholder="eye_color / is_alive / cannot_use"
          tooltip="机器可比谓词：闸门按它判定「同一事实两个值」"
          rules={[{ required: true, message: '请输入谓词' }]}
        />
        <ProFormText
          name="objectText"
          label="值"
          placeholder="灰蓝色"
          rules={[{ required: true, message: '请输入值' }]}
        />
        <ProFormTextArea
          name="restatement"
          label="自然语言表述"
          placeholder="给提示词读的那一句"
          tooltip="注入提示词用的是这句话，比对用的是「值」"
          fieldProps={{ rows: 2 }}
        />
        <ProFormSelect
          name="kind"
          label="类型"
          options={toOptions(canonKindMap)}
          rules={[{ required: true, message: '请选择类型' }]}
        />
        <ProFormSelect
          name="status"
          label="状态"
          options={toOptions(canonStatusMap)}
        />
        <ProFormDigit
          name="validFromChapter"
          label="生效起始章"
          min={0}
          fieldProps={{ precision: 0 }}
          tooltip="留空按当前最新章入库；写 0 表示开篇即有"
        />
        <ProFormDigit
          name="validUntilChapter"
          label="失效章号"
          min={0}
          fieldProps={{ precision: 0 }}
          tooltip="留空表示至今有效"
        />
      </ModalForm>
    </>
  );
};

export default CanonPanel;
