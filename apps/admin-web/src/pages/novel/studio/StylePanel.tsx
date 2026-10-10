import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Form, Input, InputNumber, Modal, message, Select, Spin } from 'antd';
import { useEffect } from 'react';
import {
  getStyleProfile,
  type StyleProfileRequest,
  updateStyleProfile,
} from '@/services/novel';

/**
 * 文风契约面板（§5.5）：作者手改的那一份，会盖掉派生契约进 L1 与两道闸门。
 *
 * 提交走整份 PUT：三个词表数组每次都带上——服务端把「未提供」当保留原值、
 * 把「空数组」当明确清空，表单里的空列表必须发成 `[]` 而不是 `undefined`，
 * 否则作者删干净一个禁用词却删不掉。
 */
const StylePanel: React.FC<{
  bookId: number;
  open: boolean;
  onClose: () => void;
}> = ({ bookId, open, onClose }) => {
  const [messageApi, contextHolder] = message.useMessage();
  const [form] = Form.useForm<StyleProfileRequest>();
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['novel-style', bookId],
    queryFn: () => getStyleProfile(bookId),
    enabled: open,
  });
  const profile = data?.data;

  useEffect(() => {
    if (!open) return;
    form.setFieldsValue({
      person: profile?.person ?? undefined,
      tense: profile?.tense ?? undefined,
      sentenceLenMin: profile?.sentenceLenMin ?? undefined,
      sentenceLenMax: profile?.sentenceLenMax ?? undefined,
      chapterWordsMin: profile?.chapterWordsMin ?? undefined,
      chapterWordsMax: profile?.chapterWordsMax ?? undefined,
      forbiddenWords: profile?.forbiddenWords ?? [],
      tics: profile?.tics ?? [],
      taboo: profile?.taboo ?? [],
    });
  }, [open, profile, form]);

  const mutation = useMutation({
    mutationFn: (body: StyleProfileRequest) => updateStyleProfile(bookId, body),
    onSuccess: () => {
      messageApi.success('文风契约已保存，下一轮生成与闸门按这份走');
      queryClient.invalidateQueries({ queryKey: ['novel-style', bookId] });
      onClose();
    },
    onError: (err: Error) => messageApi.error(err.message || '保存失败'),
  });

  return (
    <>
      {contextHolder}
      <Modal
        title="文风契约"
        open={open}
        onCancel={onClose}
        confirmLoading={mutation.isPending}
        okText="保存"
        cancelText="取消"
        onOk={() => {
          form.validateFields().then((values) => {
            mutation.mutate({
              ...values,
              forbiddenWords: values.forbiddenWords ?? [],
              tics: values.tics ?? [],
              taboo: values.taboo ?? [],
            });
          });
        }}
      >
        {isLoading ? (
          <Spin />
        ) : (
          <Form form={form} layout="vertical">
            <Form.Item
              name="person"
              label="人称"
              tooltip="如「第三人称限知」。留空表示沿用派生契约"
            >
              <Input placeholder="第三人称限知" />
            </Form.Item>
            <Form.Item name="tense" label="时态">
              <Input placeholder="过去时" />
            </Form.Item>
            <Form.Item name="sentenceLenMin" label="句长下限">
              <InputNumber min={1} style={{ width: '100%' }} />
            </Form.Item>
            <Form.Item name="sentenceLenMax" label="句长上限">
              <InputNumber min={1} style={{ width: '100%' }} />
            </Form.Item>
            <Form.Item name="chapterWordsMin" label="本章字数下限">
              <InputNumber min={1} style={{ width: '100%' }} />
            </Form.Item>
            <Form.Item name="chapterWordsMax" label="本章字数上限">
              <InputNumber min={1} style={{ width: '100%' }} />
            </Form.Item>
            <Form.Item
              name="forbiddenWords"
              label="禁用词"
              tooltip="规则闸门按这份列表逐字拦；回车或逗号分隔录入"
            >
              <Select
                mode="tags"
                open={false}
                tokenSeparators={[',', '，']}
                placeholder="手机、地铁…"
              />
            </Form.Item>
            <Form.Item name="tics" label="口头禅">
              <Select mode="tags" open={false} tokenSeparators={[',', '，']} />
            </Form.Item>
            <Form.Item name="taboo" label="禁忌">
              <Select mode="tags" open={false} tokenSeparators={[',', '，']} />
            </Form.Item>
          </Form>
        )}
      </Modal>
    </>
  );
};

export default StylePanel;
