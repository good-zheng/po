import {
  type ActionType,
  ModalForm,
  type ProColumns,
  ProForm,
  ProFormDependency,
  ProFormRadio,
  ProFormSelect,
  ProFormText,
  ProFormTextArea,
  ProTable,
} from '@ant-design/pro-components';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { history } from '@umijs/max';
import {
  Alert,
  Badge,
  Button,
  Descriptions,
  message,
  Space,
  Tag,
  Typography,
} from 'antd';
import { useRef, useState } from 'react';
import {
  adjudicateFinding,
  type CanonKind,
  type Finding,
  type FindingAdjudicationRequest,
  getBooks,
  getChapters,
  getFindings,
} from '@/services/novel';
import {
  canonKindMap,
  chapterStatusMap,
  checkerMap,
  findingStatusMap,
  severityMap,
  toOptions,
  toValueEnum,
} from '../vocab';

/** 编码全集与 Python 侧 schemas.FindingCode 一一对应——闸门外的编码不会入库 */
const codeMap: Record<string, string> = {
  attribute_conflict: '实体属性漂移',
  death_speaks: '已死角色发言',
  resurrection: '已死角色复活',
  knowledge_leak: '知情集合越界',
  alias_drift: '称谓指向多实体',
  unregistered_entity: '白名单外新实体',
  timeline_break: '时间区间越界',
  world_rule_break: '世界规则违反',
  foreshadow_missing: '伏笔编号不存在',
  unknown_ref: '引用未注入的设定',
  motivation_break: '情节与动机矛盾',
  style_drift: '视角与文风漂移',
  length_out_of_band: '字数越带',
  forbidden_word: '命中禁用词',
  // 闸门永不产这一码：它只由作者改正文时写入，用来区分「模型报的」与「作者自己改出来的」
  source_orphaned: '出处已失效',
};

const codeOptions = Object.entries(codeMap).map(([value, label]) => ({
  value,
  label,
}));

type Adjudication = {
  action: FindingAdjudicationRequest['action'];
  basis?: string;
  kind?: CanonKind;
  subjectKey?: string;
  predicate?: string;
  objectText?: string;
  restatement?: string;
};

/**
 * 冲突台账：闸门的产物在这里变成作者的裁定（§10.6）。
 *
 * 单本书的 Tab 与全站页共用这张表，只差 bookId 是否固定——裁定动作两边一样，
 * 拆成两份实现迟早会出现「一处能采纳、另一处不能」。
 */
const FindingTable: React.FC<{ bookId?: number }> = ({ bookId }) => {
  const [messageApi, contextHolder] = message.useMessage();
  const actionRef = useRef<ActionType>(null);
  const queryClient = useQueryClient();
  const [target, setTarget] = useState<Finding | null>(null);

  const crossBook = bookId == null;
  const { data: booksRes } = useQuery({
    queryKey: ['books-all'],
    queryFn: () => getBooks({ page: 0, size: 200 }),
    staleTime: 5 * 60 * 1000,
    enabled: crossBook,
  });
  const books = booksRes?.data?.content ?? [];

  // 章节下拉只在单书面板里出现：跨书台账的章号属于另一本书，筛了会串书
  const { data: chaptersRes } = useQuery({
    queryKey: ['book-chapters', bookId],
    queryFn: () => getChapters(bookId as number),
    staleTime: 60 * 1000,
    enabled: !crossBook,
  });
  const chapters = chaptersRes?.data ?? [];

  const invalidate = (canonBookId?: number) => {
    queryClient.invalidateQueries({ queryKey: ['novel-findings'] });
    queryClient.invalidateQueries({ queryKey: ['novel-progress'] });
    // 打回会把章节退回草稿，章节列表与工作台左栏读的都是这份缓存
    queryClient.invalidateQueries({ queryKey: ['book-chapters'] });
    // 采纳写的就是 canon_entry（插一条新的 + 闭掉被违反的旧区间）：「设定」Tab 与工作台中栏
    // 的设定卡都挂在这份缓存上，不失效就会出现「台账说已采纳、设定页查无此条」那种假象
    queryClient.invalidateQueries({
      queryKey:
        canonBookId == null ? ['novel-canon'] : ['novel-canon', canonBookId],
    });
    // 中栏按 id 单取的那一条，生效区间可能刚被这次裁定闭掉
    queryClient.invalidateQueries({ queryKey: ['novel-canon-entry'] });
  };

  const adjudicateMutation = useMutation({
    mutationFn: (vars: {
      findingId: number;
      body: FindingAdjudicationRequest;
    }) => adjudicateFinding(vars.findingId, vars.body),
    onSuccess: (res) => {
      const view = res.data;
      if (view?.chapterBackToDraft) {
        messageApi.info('已打回：章节退回草稿重写');
      } else {
        messageApi.success('裁定已记录');
      }
      setTarget(null);
      invalidate(target?.bookId ?? bookId);
      actionRef.current?.reload();
    },
    onError: (err: Error) => messageApi.error(err.message || '裁定失败'),
  });

  const columns: ProColumns<Finding>[] = [
    {
      title: '作品',
      dataIndex: 'bookId',
      hideInTable: !crossBook,
      valueType: 'select',
      width: 140,
      fieldProps: {
        showSearch: true,
        optionFilterProp: 'label',
        options: books.map((b) => ({ label: b.title, value: b.id })),
      },
      render: (_, row) =>
        books.find((b) => b.id === row.bookId)?.title ?? `#${row.bookId}`,
    },
    {
      title: '章节',
      dataIndex: 'chapterIndex',
      search: false,
      width: 190,
      ellipsis: true,
      render: (_, row) => (
        <Space size={4}>
          <Typography.Link
            onClick={() =>
              // 落点是创作台不是书详情页：只有中栏带章节上下文，详情页没有章的坐标系
              history.push(
                row.chapterId == null
                  ? `/novel/book/${row.bookId}/studio`
                  : `/novel/book/${row.bookId}/studio?chapterId=${row.chapterId}`,
              )
            }
          >
            第 {row.chapterIndex ?? '?'} 章 {row.chapterTitle ?? ''}
          </Typography.Link>
          {row.chapterStatus === 'draft' && (
            <Tag color={chapterStatusMap.draft.color}>
              {chapterStatusMap.draft.label}
            </Tag>
          )}
        </Space>
      ),
    },
    {
      title: '按章筛',
      dataIndex: 'chapterId',
      hideInTable: true,
      valueType: 'select',
      fieldProps: {
        showSearch: true,
        optionFilterProp: 'label',
        options: chapters.map((c) => ({
          label: `第 ${c.chapterIndex} 章 ${c.title}`,
          value: c.id,
        })),
      },
      // 跨书台账里章号不属于同一本书，筛了会串书
      search: !crossBook,
    },
    {
      title: '编码',
      dataIndex: 'code',
      valueType: 'select',
      width: 140,
      fieldProps: { options: codeOptions, showSearch: true },
      render: (_, row) => <Tag>{codeMap[row.code] ?? row.code}</Tag>,
    },
    {
      title: '严重度',
      dataIndex: 'severity',
      valueType: 'select',
      width: 90,
      valueEnum: toValueEnum(severityMap),
      render: (_, row) => {
        const s = severityMap[row.severity];
        return (
          <Badge
            status={s?.badge ?? 'default'}
            text={s?.label ?? row.severity}
          />
        );
      },
    },
    {
      title: '来源',
      dataIndex: 'checker',
      valueType: 'select',
      width: 90,
      valueEnum: toValueEnum(checkerMap),
      render: (_, row) => checkerMap[row.checker]?.label ?? row.checker,
    },
    {
      title: '证据',
      dataIndex: 'evidenceQuote',
      search: false,
      ellipsis: true,
      render: (_, row) => row.evidenceQuote ?? '-',
    },
    {
      title: '状态',
      dataIndex: 'status',
      valueType: 'select',
      width: 100,
      valueEnum: toValueEnum(findingStatusMap),
      render: (_, row) => {
        const s = findingStatusMap[row.status];
        return (
          <Tag color={s?.color ?? 'default'}>{s?.label ?? row.status}</Tag>
        );
      },
    },
    {
      title: '裁定依据',
      dataIndex: 'basis',
      search: false,
      ellipsis: true,
      render: (_, row) => row.basis ?? '-',
    },
    {
      title: '发现时间',
      dataIndex: 'createdAt',
      search: false,
      valueType: 'dateTime',
      width: 165,
    },
    {
      title: '操作',
      key: 'action',
      width: 80,
      search: false,
      render: (_, row) => (
        <a onClick={() => setTarget(row)}>
          {row.status === 'open' ? '裁定' : '查看'}
        </a>
      ),
    },
  ];

  return (
    <>
      {contextHolder}
      <ProTable<Finding>
        rowKey="id"
        size="small"
        actionRef={actionRef}
        search={{ labelWidth: 'auto' }}
        pagination={{ pageSize: 20, showSizeChanger: true }}
        toolBarRender={() => [
          <Button key="refresh" onClick={() => actionRef.current?.reload()}>
            刷新
          </Button>,
        ]}
        // 固定筛选放这里（换书时自动重查）；搜索表单里的同名字段会覆盖它
        params={{ bookId } as { bookId?: number; chapterId?: number }}
        request={async (params) => {
          try {
            const res = await getFindings({
              bookId: params.bookId ?? bookId,
              chapterId: params.chapterId,
              severity: params.severity,
              status: params.status,
              checker: params.checker,
              code: params.code,
              page: (params.current ?? 1) - 1,
              size: params.pageSize ?? 20,
            });
            return {
              data: res.data?.content ?? [],
              total: res.data?.totalElements ?? 0,
              success: true,
            };
          } catch (err) {
            messageApi.error(
              err instanceof Error ? err.message : '加载冲突台账失败',
            );
            return { data: [], total: 0, success: false };
          }
        }}
        expandable={{
          expandedRowRender: (row) => (
            <Descriptions column={1} size="small">
              <Descriptions.Item label="闸门说明">
                {row.explanation ?? '-'}
              </Descriptions.Item>
              <Descriptions.Item label="证据原文">
                {row.evidenceQuote ?? '-'}
              </Descriptions.Item>
              <Descriptions.Item label="修补指令">
                {row.fixInstruction ?? '-'}
              </Descriptions.Item>
              <Descriptions.Item label="被违反的设定条目">
                {row.canonRefs ?? '-'}
              </Descriptions.Item>
              <Descriptions.Item label="落点">
                {row.textStart == null
                  ? '-'
                  : `第 ${row.chapterIndex ?? '?'} 章 r${row.revision}，字符 ${row.textStart}-${row.textEnd}`}
              </Descriptions.Item>
            </Descriptions>
          ),
        }}
        columns={columns}
      />

      <ModalForm<Adjudication>
        key={target ? `finding-${target.id}` : 'finding-none'}
        title={target ? `裁定冲突 #${target.id}` : '裁定冲突'}
        width={640}
        open={!!target}
        onOpenChange={(open) => {
          if (!open) setTarget(null);
        }}
        modalProps={{ destroyOnClose: true, maskClosable: false }}
        submitter={{
          searchConfig: {
            submitText: target?.status === 'open' ? '提交裁定' : '关闭',
            resetText: '取消',
          },
          submitButtonProps: { disabled: target?.status !== 'open' },
        }}
        initialValues={{ action: 'adopt', kind: 'character' }}
        onFinish={async (values) => {
          if (!target) return false;
          const body: FindingAdjudicationRequest = {
            action: values.action,
            basis: values.basis,
            assertion:
              values.action === 'adopt'
                ? {
                    kind: values.kind,
                    subjectKey: values.subjectKey,
                    predicate: values.predicate,
                    objectText: values.objectText,
                    restatement: values.restatement,
                  }
                : undefined,
          };
          await adjudicateMutation.mutateAsync({
            findingId: target.id,
            body,
          });
          return true;
        }}
      >
        {target && (
          <Alert
            type="info"
            style={{ marginBottom: 16 }}
            message={`${codeMap[target.code] ?? target.code}｜第 ${target.chapterIndex ?? '?'} 章`}
            description={
              <Space direction="vertical" size={2}>
                <Typography.Text>
                  说明：{target.explanation ?? target.code}
                </Typography.Text>
                {target.evidenceQuote && (
                  <Typography.Text type="secondary">
                    证据：{target.evidenceQuote}
                  </Typography.Text>
                )}
                {target.canonRefs && (
                  <Typography.Text type="secondary">
                    被违反的设定条目：{target.canonRefs}
                  </Typography.Text>
                )}
              </Space>
            }
          />
        )}
        <ProFormRadio.Group
          name="action"
          label="裁定动作"
          rules={[{ required: true, message: '请选择裁定动作' }]}
          fieldProps={{ disabled: target?.status !== 'open' }}
          options={[
            { label: '采纳（写作者裁定并闭旧区间）', value: 'adopt' },
            { label: '驳回（冲突不成立）', value: 'reject' },
            { label: '豁免（成立但这一章不改）', value: 'waive' },
            { label: '打回重写（章节退回草稿）', value: 'rewrite' },
          ]}
        />
        <ProFormDependency name={['action']}>
          {({ action }) => {
            const needBasis = action === 'reject' || action === 'waive';
            return (
              <>
                {action === 'adopt' && (
                  <>
                    <ProFormText
                      name="subjectKey"
                      label="实体键"
                      placeholder="char:shenqing"
                      tooltip="用别名归一后的键，与要覆盖的那条既有设定条目对齐"
                      rules={[{ required: true, message: '请输入实体键' }]}
                    />
                    <ProFormText
                      name="predicate"
                      label="谓词"
                      placeholder="eye_color"
                      rules={[{ required: true, message: '请输入谓词' }]}
                    />
                    <ProFormText
                      name="objectText"
                      label="值（你认定的设定条目）"
                      placeholder="灰蓝色"
                      rules={[{ required: true, message: '请输入值' }]}
                    />
                    <ProFormTextArea
                      name="restatement"
                      label="自然语言表述"
                      placeholder="注入提示词时读的那一句"
                      fieldProps={{ rows: 2 }}
                    />
                    <ProFormSelect
                      name="kind"
                      label="类型"
                      options={toOptions(canonKindMap)}
                    />
                  </>
                )}
                <ProFormTextArea
                  name="basis"
                  label={
                    action === 'reject'
                      ? '驳回理由（必填）'
                      : action === 'waive'
                        ? '豁免理由（必填）'
                        : '裁定依据'
                  }
                  placeholder={
                    needBasis
                      ? '写下理由：这条台账是给未来的你复查的'
                      : '可选，会一起写进裁定记录'
                  }
                  rules={
                    needBasis
                      ? [{ required: true, message: '请填写理由' }]
                      : undefined
                  }
                  fieldProps={{ rows: 3, maxLength: 500, showCount: true }}
                />
              </>
            );
          }}
        </ProFormDependency>
        {target && target.status !== 'open' && (
          <ProForm.Item label="裁定记录">
            <Typography.Text type="secondary">
              {target.decidedBy ? `#${target.decidedBy}` : '-'}（
              {target.decidedAt?.replace('T', ' ').slice(0, 19) ?? '-'}）
            </Typography.Text>
          </ProForm.Item>
        )}
      </ModalForm>
    </>
  );
};

export default FindingTable;
