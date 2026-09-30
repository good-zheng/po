import { DeleteOutlined, UploadOutlined } from '@ant-design/icons';
import { Button, Input, message, Upload } from 'antd';
import { useState } from 'react';
import { type UploadDir, uploadImage } from '@/services/file';

const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
const MAX_IMAGE_SIZE = 10 * 1024 * 1024;

type ImageFieldProps = {
  /** 由 Form.Item 注入 */
  value?: string;
  /** 由 Form.Item 注入 */
  onChange?: (value?: string) => void;
  /** COS 业务子目录 */
  dir: UploadDir;
};

/**
 * 图片表单控件：上传到腾讯云 COS 后把公网 URL 写回受控字段，
 * 同时保留手动粘贴 URL 的能力（管理员录入外部图片时用）。
 */
export function ImageField({ value, onChange, dir }: ImageFieldProps) {
  const [messageApi, contextHolder] = message.useMessage();
  const [uploading, setUploading] = useState(false);

  const handleFile = (file: File) => {
    if (!ALLOWED_TYPES.includes(file.type)) {
      messageApi.error('仅支持 jpg/png/gif/webp 格式的图片');
      return;
    }
    if (file.size > MAX_IMAGE_SIZE) {
      messageApi.error('图片不能超过 10MB');
      return;
    }
    setUploading(true);
    uploadImage(file, dir, { skipErrorHandler: true })
      .then((res) => onChange?.(res.data))
      .catch((err: unknown) =>
        messageApi.error(
          err instanceof Error && err.message ? err.message : '图片上传失败',
        ),
      )
      .finally(() => setUploading(false));
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      {contextHolder}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        {value ? (
          <img
            src={value}
            alt=""
            style={{
              width: 120,
              height: 90,
              objectFit: 'cover',
              borderRadius: 6,
              border: '1px solid #d9d9d9',
            }}
          />
        ) : null}
        <Upload
          showUploadList={false}
          accept="image/jpeg,image/png,image/gif,image/webp"
          beforeUpload={(file) => {
            handleFile(file as unknown as File);
            return false; // 阻止组件自动上传，改走 COS 接口
          }}
        >
          <Button loading={uploading} icon={<UploadOutlined />}>
            {value ? '更换图片' : '上传图片'}
          </Button>
        </Upload>
        {value ? (
          <Button
            type="text"
            danger
            icon={<DeleteOutlined />}
            onClick={() => onChange?.(undefined)}
          >
            移除
          </Button>
        ) : null}
      </div>
      <Input
        placeholder="或直接粘贴图片 URL"
        allowClear
        value={value}
        onChange={(e) => onChange?.(e.target.value || undefined)}
      />
    </div>
  );
}

export default ImageField;
