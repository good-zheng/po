import {
  ModalForm,
  ProFormSelect,
  ProFormSwitch,
} from '@ant-design/pro-components';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Card, message, Space, Table, Tag, Typography } from 'antd';
import { useMemo, useState } from 'react';
import {
  type AliasItem,
  type AliasRequest,
  getAliases,
  updateAlias,
} from '@/services/novel';

/**
 * 别名表是实体归一的落点：抽取只写候选，谁是谁由作者改判（§10.4）。
 *
 * 这里只有改判没有新增——称谓是从原文里长出来的，作者动的永远是「它属于哪个实体键」，
 * 凭空造一个键会让归一结果和正文对不上。
 */
const AliasPanel: React.FC<{ bookId: number }> = ({ bookId }) => {
  const [messageApi, contextHolder] = message.useMessage();
  const queryClient = useQueryClient();
  const [editTarget, setEditTarget] = useState<AliasItem | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ['novel-aliases', bookId],
    queryFn: () => getAliases(bookId),
  });
  const aliases = data?.data ?? [];

  const keyOptions = useMemo(() => {
    const set = new Set(aliases.map((a) => a.entityKey));
    return [...set].sort().map((value) => ({ value, label: value }));
  }, [aliases]);

  /** 按实体键聚拢，作者一眼看出「一个人挂了几个称谓」 */
  const rows = useMemo(
    () =>
      [...aliases].sort(
        (a, b) =>
          a.entityKey.localeCompare(b.entityKey) ||
          Number(b.isPrimary) - Number(a.isPrimary) ||
          a.aliasText.localeCompare(b.aliasText),
      ),
    [aliases],
  );

  const updateMutation = useMutation({
    mutationFn: (vars: { aliasId: number; body: AliasRequest }) =>
      updateAlias(bookId, vars.aliasId, vars.body),
    onSuccess: () => {
      messageApi.success('归属已改判');
      setEditTarget(null);
      queryClient.invalidateQueries({ queryKey: ['novel-aliases', bookId] });
    },
    onError: (err: Error) => messageApi.error(err.message || '改判失败'),
  });

  const columns = [
    {
      title: '称谓',
      dataIndex: 'aliasText',
      render: (_: unknown, record: AliasItem) => (
        <Space size={4}>
          <Typography.Link onClick={() => setEditTarget(record)}>
            {record.aliasText}
          </Typography.Link>
          {record.isPrimary && <Tag color="blue">主名</Tag>}
        </Space>
      ),
    },
    { title: '归属实体键', dataIndex: 'entityKey', width: 220 },
    {
      title: '首次出现章',
      dataIndex: 'firstSeenChapter',
      width: 130,
      render: (_: unknown, record: AliasItem) =>
        record.firstSeenChapter == null
          ? '-'
          : `第 ${record.firstSeenChapter} 章`,
    },
    {
      title: '操作',
      key: 'action',
      width: 80,
      render: (_: unknown, record: AliasItem) => (
        <a onClick={() => setEditTarget(record)}>改判</a>
      ),
    },
  ];

  return (
    <>
      {contextHolder}
      <Card title="别名与实体归一" style={{ marginBottom: 16 }}>
        <Table<AliasItem>
          rowKey="id"
          size="small"
          loading={isLoading}
          dataSource={rows}
          columns={columns}
          pagination={{ pageSize: 20, showSizeChanger: true }}
        />

        <ModalForm<AliasRequest>
          key={editTarget ? `alias-${editTarget.id}` : 'alias-none'}
          title={
            editTarget ? `改判称谓「${editTarget.aliasText}」` : '改判称谓'
          }
          width={520}
          open={!!editTarget}
          onOpenChange={(open) => {
            if (!open) setEditTarget(null);
          }}
          modalProps={{ destroyOnClose: true, maskClosable: false }}
          submitter={{
            searchConfig: { submitText: '保存', resetText: '取消' },
          }}
          initialValues={
            editTarget
              ? {
                  entityKey: editTarget.entityKey,
                  isPrimary: editTarget.isPrimary,
                }
              : undefined
          }
          onFinish={async (values) => {
            if (editTarget) {
              await updateMutation.mutateAsync({
                aliasId: editTarget.id,
                body: values,
              });
            }
            return true;
          }}
        >
          <ProFormSelect
            name="entityKey"
            label="归属实体键"
            options={keyOptions}
            tooltip="把两个称谓并到同一个键，模型才会把它们当同一个人写"
            rules={[{ required: true, message: '请选择实体键' }]}
            fieldProps={{ showSearch: true }}
          />
          <ProFormSwitch
            name="isPrimary"
            label="设为主名"
            tooltip="主名是提示词里指代该实体的那一个名字"
          />
        </ModalForm>
      </Card>
    </>
  );
};

export default AliasPanel;
